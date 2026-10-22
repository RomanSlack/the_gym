"""The equipment modelling kit: geometry + materials for gym machines, true scale (metres, z up, the user faces -y).

Separate from construction/ on purpose (the equipment library runs on its own). A machine is built in
equipment/pieces/<piece>/model.py as `def build(k)`, where k is a Kit:

    k.sweep("frame", [(0,0,0.05), (0,0.9,0.05), (0,0.9,1.4)], k.rect(0.08, 0.08, 0.008), bend=0.12)   # bent rect tube
    k.tube("chrome", p0, p1, 0.0125)                                                                       # round bar
    k.pad("pad", centre, (0.36, 0.5, 0.08), r=0.03, rx=..)                                                 # upholstered pad
    k.stack(base, n=20)                                                                                    # weight stack

Geometry is collected per (material, softness); k.finish() makes one object per group. Materials are named by role
("frame", "pad", "chrome", ...) and given a look per piece via k.look(frame=(r,g,b), ...).
"""
import functools
import inspect
import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

# ---------------------------------------------------------------- materials


def _principled(name, color, rough, metal=0.0, coat=0.0, sheen=0.0, bump=None, aniso=0.0, grain=None, knurl=None, spec=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Sheen Weight"].default_value = sheen
    if aniso:
        b.inputs["Anisotropic"].default_value = aniso
    if spec is not None:  # matte rubber, raw wood: less of the studio's light mirrored off a flat top (0.5 = Blender's default)
        b.inputs["Specular IOR Level"].default_value = spec
    if bump:  # fine grain (vinyl, rubber, powder texture): noise -> bump, scale in 1/m
        scale, strength = bump
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = strength; bp.inputs["Distance"].default_value = 0.0004
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if grain:  # wood (plywood faces): wave bands along x, distorted, between color and grain["dark"]; scale in 1/m
        tc = nt.nodes.new("ShaderNodeTexCoord")
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = grain.get("scale", 6.0)
        wv.inputs["Distortion"].default_value = grain.get("distortion", 9.0); wv.inputs["Detail"].default_value = 3
        wv.bands_direction = grain.get("along", "X")
        ramp = nt.nodes.new("ShaderNodeMix"); ramp.data_type = "RGBA"
        ramp.inputs[6].default_value = (*color, 1); ramp.inputs[7].default_value = (*grain["dark"], 1)
        nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
        nt.links.new(wv.outputs["Fac"], ramp.inputs[0])
        nt.links.new(ramp.outputs[2], b.inputs["Base Color"])
    if knurl:  # diamond knurl round a bar along x through (y, z) = knurl["c"]: two crossed helices -> pyramids -> bump
        tc = nt.nodes.new("ShaderNodeTexCoord")
        xyz = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], xyz.inputs[0])
        cy, cz = knurl.get("c", (0.0, 0.0))
        p, r = knurl.get("pitch", 0.0016), knurl.get("r", 0.014)

        def op(kind, a, b=None):
            n = nt.nodes.new("ShaderNodeMath"); n.operation = kind
            for i, v in enumerate((a, b)):
                if v is None:
                    continue
                if isinstance(v, (int, float)):
                    n.inputs[i].default_value = v
                else:
                    nt.links.new(v, n.inputs[i])
            return n.outputs[0]
        th = op("ARCTAN2", op("SUBTRACT", xyz.outputs["Z"], cz), op("SUBTRACT", xyz.outputs["Y"], cy))
        arc = op("MULTIPLY", th, r)
        tri = [op("PINGPONG", op("DIVIDE", op(kind, xyz.outputs["X"], arc), p), 0.5) for kind in ("ADD", "SUBTRACT")]
        h = op("MINIMUM", *tri)
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = knurl.get("strength", 0.6)
        bp.inputs["Distance"].default_value = knurl.get("depth", 0.0005)
        nt.links.new(h, bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


LOOK = {  # defaults: a black commercial machine
    "frame": dict(color=(0.018, 0.018, 0.02), rough=0.38, metal=0.0, coat=0.25, bump=(900, 0.08)),     # powder coat
    "frame2": dict(color=(0.32, 0.33, 0.34), rough=0.35, metal=0.6, coat=0.2),                          # secondary (shrouds, accents)
    "pad": dict(color=(0.015, 0.015, 0.016), rough=0.55, sheen=0.25, bump=(1400, 0.12)),                 # vinyl upholstery
    "seam": dict(color=(0.006, 0.006, 0.007), rough=0.7),
    "chrome": dict(color=(0.9, 0.9, 0.9), rough=0.06, metal=1.0),
    "steel": dict(color=(0.62, 0.62, 0.62), rough=0.28, metal=1.0, aniso=0.5),                           # brushed / stainless
    "alu": dict(color=(0.78, 0.79, 0.8), rough=0.3, metal=1.0, aniso=0.4),
    "plate": dict(color=(0.05, 0.05, 0.055), rough=0.45, metal=0.3, coat=0.1),                           # stack plates
    "plastic": dict(color=(0.03, 0.03, 0.032), rough=0.45),
    "rubber": dict(color=(0.012, 0.012, 0.012), rough=0.85, bump=(700, 0.15)),
    "cable": dict(color=(0.02, 0.02, 0.02), rough=0.4),
    "label": dict(color=(0.85, 0.85, 0.85), rough=0.4),
    "accent": dict(color=(0.75, 0.05, 0.04), rough=0.4),
    "glass": dict(color=(0.05, 0.05, 0.05), rough=0.05, coat=1.0),                                       # console screens
}


# ---------------------------------------------------------------- profiles (closed loops in the tube's u-v plane)

def rect(w, h, r=0.0, seg=4):
    """w along u (sideways), h along v (the bend plane's normal side), corner radius r."""
    if r <= 0:
        return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def oval(w, h, seg=28):
    return [(w / 2 * math.cos(2 * math.pi * i / seg), h / 2 * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def circle(r, seg=20):
    return oval(2 * r, 2 * r, seg)


def stadium(w, h, seg=10):
    """Flat sides, round ends (oval tube as Life Fitness uses): w > h."""
    return rect(w, h, h / 2 - 1e-4, seg)


# ---------------------------------------------------------------- parts (for the connection check)

HARDWARE = {"bolt", "hole", "warn", "label", "seam", "weld"}   # sit on a member but never hold two members together
GAP = 0.006   # two members this close but not touching read as a mistake (floating by a few mm): reported
ROD = 0.020   # round bars this thin (axles, pins, rods) can't hold a part on their own: it needs a hub, a plate, a weld


def _part(fn):
    """Record each top-level geometry call as one part (its faces in each group + the model.py line that made it), so
    k.check() can tell which parts touch and which float."""
    @functools.wraps(fn)
    def w(self, *a, **kw):
        if self._depth:
            self._depth += 1
            try:
                return fn(self, *a, **kw)
            finally:
                self._depth -= 1
        before = {key: len(b.faces) for key, b in self.groups.items()}
        pid = len(self.parts) + 1
        self._depth = 1
        try:
            r = fn(self, *a, **kw)
        finally:
            self._depth = 0
        fr, where = inspect.currentframe().f_back, "?"
        while fr:
            if fr.f_code.co_filename.endswith("model.py"):
                where = f"{fr.f_code.co_name}():{fr.f_lineno}"; break
            fr = fr.f_back
        rng = []   # the groups it added faces to; its faces are tagged with its id (index ranges don't hold: bmesh reuses
        for key, b in self.groups.items():   # freed slots, e.g. after create_cone's caps)
            if len(b.faces) > before.get(key, 0):
                lay = b.faces.layers.int.get("part") or b.faces.layers.int.new("part")
                for f in b.faces:
                    if not f[lay]:
                        f[lay] = pid
                rng.append(key)
        if rng:
            role = a[0] if a and isinstance(a[0], str) else fn.__name__
            r_ = (a[3] if len(a) > 3 else kw.get("r")) if fn.__name__ == "tube" else None
            self.parts.append(dict(what=f"{fn.__name__} {role}", where=where, rng=rng, rod=bool(r_ and r_ <= ROD)))
        return r
    return w


# ---------------------------------------------------------------- the kit

class Kit:
    def __init__(self, name, coll=None, look=None):
        self.name, self.groups, self.subs, self.extra = name, {}, [], []
        self.pivot, self.rz = (0.0, 0.0, 0.0), 0.0
        self.parts, self._depth, self.floating = [], 0, []
        self.coll = coll or bpy.context.scene.collection
        self.looks = {k: dict(v) for k, v in LOOK.items()}
        if look:
            self.look(**look)
        self.rect, self.oval, self.circle, self.stadium = rect, oval, circle, stadium

    def look(self, **kw):
        """k.look(frame=(r,g,b)) or k.look(frame=dict(color=.., rough=..))."""
        for role, v in kw.items():
            d = self.looks.setdefault(role, dict(LOOK["frame"]))
            d.update(v if isinstance(v, dict) else {"color": tuple(v)})

    def bm(self, mat, soft=0.0015):
        return self.groups.setdefault((mat, soft), bmesh.new())

    # -- sweeps: the backbone (frames are tubes bent along a path)
    @_part
    def sweep(self, mat, path, profile, bend=0.0, up=(0, 0, 1), caps=True, soft=0.0015, bend_seg=10, twist=0.0,
              cut0=None, cut1=None, weld=False):
        """Sweep a closed profile along a polyline. bend > 0 rounds every corner with that centreline radius (bent tube).
        The profile's v axis starts on `up` projected off the first tangent (then parallel-transported).
        Joints: cut0 / cut1 = (point, normal), a plane the start / end is cut to (the face of the member it meets: a
        coped, mitred end sitting flush, not a square end poking through or stopping short); weld=True runs a fillet
        bead round each cut end (the joint is welded; powder-coated over, so the member's own material)."""
        P = [Vector(p) for p in path]
        if bend > 0 and len(P) > 2:
            P = _fillet(P, bend, bend_seg)
        n = len(P)
        T = []
        for i in range(n):
            a = (P[i] - P[i - 1]).normalized() if i > 0 else None
            b_ = (P[i + 1] - P[i]).normalized() if i < n - 1 else None
            t = (a + b_) if (a is not None and b_ is not None) else (a if b_ is None else b_)
            T.append(t.normalized())
        upv = Vector(up)
        if abs(upv.dot(T[0])) > 0.98:
            upv = Vector((0, 1, 0)) if abs(T[0].y) < 0.9 else Vector((1, 0, 0))
        V = (upv - T[0] * upv.dot(T[0])).normalized()
        U = T[0].cross(V)
        frames = [(U, V)]
        for i in range(1, n):  # parallel transport
            q = T[i - 1].rotation_difference(T[i])
            U, V = q @ U, q @ V
            frames.append((U, V))
        b = self.bm(mat, soft)
        rings = []
        for i, (p, (U, V)) in enumerate(zip(P, frames)):
            s = 1.0
            if 0 < i < n - 1:  # miter: keep the wall thickness at sharp joints
                a = (P[i] - P[i - 1]).normalized(); c = (P[i + 1] - P[i]).normalized()
                cosh = max(0.3, math.sqrt(max(0.0, (1 + a.dot(c)) / 2)))
                s = 1.0 / cosh
            if twist:
                ang = twist * i / max(1, n - 1)
                U, V = U * math.cos(ang) + V * math.sin(ang), -U * math.sin(ang) + V * math.cos(ang)
            ring = []
            for (u, v) in profile:
                off = U * u + V * v
                if s != 1.0:  # stretch along the bend direction only
                    bd = (P[i + 1] - P[i]).normalized() - (P[i] - P[i - 1]).normalized()  # in the bend plane, normal to T
                    bd = bd.normalized() if bd.length > 1e-6 else Vector()
                    off = off + bd * off.dot(bd) * (s - 1)
                ring.append(b.verts.new(p + off))
            rings.append(ring)
        m = len(profile)
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(m):
                b.faces.new((r0[j], r0[(j + 1) % m], r1[(j + 1) % m], r1[j]))
        if caps:
            b.faces.new(rings[0][::-1]); b.faces.new(rings[-1])
        for ring, cut, t_in, c0 in ((rings[0], cut0, T[0], P[0]), (rings[-1], cut1, -T[-1], P[-1])):
            if not cut:
                continue
            q, nv = Vector(cut[0]), Vector(cut[1]).normalized()
            if abs(t_in.dot(nv)) < 0.05:
                raise ValueError(f"sweep: cut plane {cut} is parallel to the member")
            for v in ring:   # slide each end vertex along the member's axis onto the plane
                v.co = v.co + t_in * ((q - v.co).dot(nv) / t_in.dot(nv))
            if weld:
                self.bead(mat, [v.co.copy() for v in ring], c0 + t_in * ((q - c0).dot(nv) / t_in.dot(nv)),
                          nv if nv.dot(t_in) > 0 else -nv)

    @_part
    def tube(self, mat, p0, p1, r, seg=20, soft=0.0008, caps=True, **joint):
        self.sweep(mat, [p0, p1], circle(r, seg), soft=soft, caps=caps, **joint)

    @_part
    def bar(self, mat, p0, p1, w, h=None, r=None, up=(0, 0, 1), soft=0.0015, **joint):
        """Straight rectangular tube between two points (h along `up`); joint = cut0 / cut1 / weld as in sweep."""
        h = w if h is None else h
        self.sweep(mat, [p0, p1], rect(w, h, w * 0.12 if r is None else r), up=up, soft=soft, **joint)

    @_part
    def bead(self, mat, loop, centre, out, r=0.0035):
        """A weld bead: a small round fillet along a closed loop (the edge of a member's end where it meets a face),
        tucked into the corner: pushed out from the member's axis (`centre`) and off the face (`out`, into the member)."""
        out = Vector(out).normalized(); cv = Vector(centre)
        pts = []
        for p in loop:
            rd = p - cv; rd = rd - out * rd.dot(out)
            pts.append(p + (rd.normalized() * r * 0.55 if rd.length > 1e-6 else Vector()) + out * r * 0.55)
        self.sweep(mat, pts + [pts[0]], circle(r, 6), caps=False, soft=0)

    @_part
    def bolt(self, c, axis, size=0.016, nut=None, mat="bolt"):
        """A hex bolt (size = its diameter) on a washer, on the face at c; axis ("+x", "-y", ...) points out of that face.
        nut = the grip length: the shank runs that far back through the parts and a washer + hex nut sit on the far face."""
        ax = axis[-1]; d = Vector({"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[ax]) * (-1 if axis[0] == "-" else 1)
        cv = Vector(c)
        ends = [(cv, d)] + ([(cv - d * nut, -d)] if nut else [])
        for at, o in ends:
            self.disc(mat, at + o * 0.0012, size * 0.95, size * 0.52, 0.0024, axis=ax, seg=20)               # washer
            self.cyl(mat, at + o * (0.0024 + size * 0.33), size * 0.866, size * 0.65, axis=ax, seg=6)          # hex head / nut
        self.tube(mat, cv - d * ((nut or 0.0) + (size * 0.5 if nut else 0.0)), cv + d * 0.004, size * 0.45, seg=10)

    # -- solids
    @_part
    def box(self, mat, c, size, rx=0.0, ry=0.0, rz=0.0, soft=0.0015):
        b = self.bm(mat, soft)
        g = bmesh.ops.create_cube(b, size=1.0)["verts"]
        bmesh.ops.scale(b, vec=size, verts=g)
        R = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X")
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=R)
        bmesh.ops.translate(b, verts=g, vec=c)

    @_part
    def pad(self, mat, c, size, r=0.03, rx=0.0, ry=0.0, rz=0.0, seam=True, board=True):
        """An upholstered pad: a soft rounded block (size = x, y, thickness along local z) on a thin base board,
        with a piping seam round the top face. Rotations turn the local z (the sitting / pressing face)."""
        sx, sy, sz = size
        R = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X")
        cv = Vector(c)
        self.box(mat, cv + R @ Vector((0, 0, 0.004)), (sx, sy, sz - 0.008), rx, ry, rz, soft=min(r, sz / 2 - 0.002))
        if board:
            self.box("plastic", cv + R @ Vector((0, 0, -sz / 2 + 0.006)), (sx - 0.01, sy - 0.01, 0.012), rx, ry, rz, soft=0.003)
        if seam:  # piping just inside the top edge
            inset = min(r, sz / 2) * 0.9
            loop = rect(sx - 2 * inset, sy - 2 * inset, max(0.004, r - inset), 6)
            z = sz / 2 + 0.0005
            pts = [cv + R @ Vector((u, v, z)) for u, v in loop] + [cv + R @ Vector((loop[0][0], loop[0][1], z))]
            self.sweep("seam", pts, circle(0.0015, 6), caps=False, soft=0)

    @_part
    def shaped_pad(self, mat, outline, c, normal, side, th, r=0.03, seam=True, board=True, cushion=0.0):
        """An upholstered pad of any plan shape (a seat narrowing to the back, a tapered back pad): `outline` is a list of
        (a, b) points in the pad's plane (a along `side`, b along normal x side), rounded by r at each corner; c is the
        centre of its thickness th; `normal` the pressing face's direction."""
        n = Vector(normal).normalized(); sd = Vector(side).normalized(); fw = n.cross(sd)
        loop = _round_poly(outline, r, 6)
        # a sweep along n with up = fw maps profile (u, v) to world u * (n x fw)... built directly instead:
        cv = Vector(c)
        if cushion:  # an upholstered cushion: the sides bulge, the top rolls over its edge into a crowned panel (`cushion` =
            # the panel's inset from the edge); the seam runs round the panel, like the stitched top of a real pad
            b = self.bm(mat, -1)   # soft -1: a subdivided, smooth group (see finish)
            prof = [(-th / 2 + 0.012, 0.004), (-th / 2 + 0.3 * th, -0.002), (0.0, -0.004), (th / 2 - 0.3 * th, -0.002),
                    (th / 2 - 0.12 * th, 0.005), (th / 2 - 0.03 * th, 0.016), (th / 2, cushion * 0.55), (th / 2 + 0.006, cushion),
                    (th / 2 + 0.009, cushion * 1.6)]
            rings = []
            for z, ins in prof:
                lp = _round_poly(_inset(outline, ins), max(0.006, r - ins), 6)
                rings.append([b.verts.new(cv + sd * a + fw * q + n * z) for a, q in lp])
            m_ = len(rings[0])
            for r0, r1 in zip(rings, rings[1:]):
                for i in range(m_):
                    j = (i + 1) % m_
                    b.faces.new((r0[i], r0[j], r1[j], r1[i]))
            b.faces.new(rings[-1]); b.faces.new(rings[0][::-1])
            if board:
                bb_ = self.bm("plastic", 0.003)
                inner = _round_poly([(a * 0.97, q * 0.97) for a, q in outline], r, 6)
                lo = [bb_.verts.new(cv + sd * a + fw * q + n * (-th / 2)) for a, q in inner]
                hi = [bb_.verts.new(cv + sd * a + fw * q + n * (-th / 2 + 0.012)) for a, q in inner]
                for i in range(len(inner)):
                    j = (i + 1) % len(inner)
                    bb_.faces.new((lo[i], lo[j], hi[j], hi[i]))
                bb_.faces.new(hi); bb_.faces.new(lo[::-1])
            if seam:
                sl = _round_poly(_inset(outline, cushion), max(0.006, r - cushion), 6)
                pts = [cv + sd * a + fw * q + n * (th / 2 + 0.0068) for a, q in sl]
                self.sweep("seam", pts + [pts[0]], circle(0.0016, 6), caps=False, soft=0)
                sl = _round_poly(_inset(outline, -0.004), r + 0.004, 6)       # the welt round the side
                pts = [cv + sd * a + fw * q + n * (-th / 2 + 0.3 * th) for a, q in sl]
                self.sweep("seam", pts + [pts[0]], circle(0.0016, 6), caps=False, soft=0)
            return
        b = self.bm(mat, min(r * 0.8, th / 2 - 0.002))
        for z0, z1, mm, shrink in ((-th / 2 + 0.012, th / 2, mat, 0.0),):
            lo = [b.verts.new(cv + sd * a + fw * bb + n * z0) for a, bb in loop]
            hi = [b.verts.new(cv + sd * a + fw * bb + n * z1) for a, bb in loop]
            m_ = len(loop)
            for i in range(m_):
                j = (i + 1) % m_
                b.faces.new((lo[i], lo[j], hi[j], hi[i]))
            b.faces.new(hi); b.faces.new(lo[::-1])
        if board:
            bb_ = self.bm("plastic", 0.003)
            inner = _round_poly([(a * 0.97, q * 0.97) for a, q in outline], r, 6)
            lo = [bb_.verts.new(cv + sd * a + fw * q + n * (-th / 2)) for a, q in inner]
            hi = [bb_.verts.new(cv + sd * a + fw * q + n * (-th / 2 + 0.012)) for a, q in inner]
            for i in range(len(inner)):
                j = (i + 1) % len(inner)
                bb_.faces.new((lo[i], lo[j], hi[j], hi[i]))
            bb_.faces.new(hi); bb_.faces.new(lo[::-1])
        if seam:
            ins = min(r, th / 2) * 0.9
            sl = _round_poly(_inset(outline, ins), max(0.004, r - ins), 6)
            pts = [cv + sd * a + fw * q + n * (th / 2 + 0.0005) for a, q in sl]
            self.sweep("seam", pts + [pts[0]], circle(0.0015, 6), caps=False, soft=0)

    @_part
    def cyl(self, mat, c, r, h, axis="z", seg=32, soft=0.001, r2=None):
        b = self.bm(mat, soft)
        g = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)["verts"]
        if axis == "x":
            bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
        elif axis == "y":
            bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(b, verts=g, vec=c)

    @_part
    def disc(self, mat, c, r_out, r_in, h, axis="x", seg=48, soft=0.0008):
        """A washer / pulley / plate ring (annulus) of thickness h."""
        b = self.bm(mat, soft)
        A = {"x": (Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0))), "y": (Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0))),
             "z": (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))}[axis]
        cv = Vector(c)
        loops = []
        for r, side in ((r_out, -1), (r_out, 1), (r_in, 1), (r_in, -1)):
            loops.append([b.verts.new(cv + A[0] * r * math.cos(2 * math.pi * i / seg) + A[1] * r * math.sin(2 * math.pi * i / seg) + A[2] * side * h / 2) for i in range(seg)])
        for k in range(4):
            L0, L1 = loops[k], loops[(k + 1) % 4]
            for i in range(seg):
                j = (i + 1) % seg
                b.faces.new((L0[i], L0[j], L1[j], L1[i]))
        bmesh.ops.recalc_face_normals(b, faces=b.faces)

    @_part
    def pulley(self, c, r, axis="x", w=0.025):
        """A cable pulley: grooved wheel in a plate housing hint (wheel only; housings are modelled by the piece)."""
        ax = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}[axis]
        cv = Vector(c)
        for s in (-1, 1):
            self.disc("plastic", cv + ax * s * w * 0.35, r, 0.012, w * 0.3, axis)
        self.disc("plastic", cv, r * 0.86, 0.012, w * 0.42, axis)
        self.cyl("chrome", cv, 0.008, w * 1.4, axis, seg=12)

    @_part
    def cable(self, pts, r=0.0028):
        self.sweep("cable", pts, circle(r, 8), caps=False, soft=0)

    @_part
    def stack(self, c, n=20, w=0.26, d=0.125, t=0.0254, gap=0.0, rods=0.47, rod_r=0.0127, top=1.45, pin_at=6, mat="plate"):
        """A selectorized weight stack standing on c (centre of its footprint, floor height): n plates of w x d x t,
        two chrome guide rods `rods` apart (x), a top plate with the lifting tube, a selector pin in plate `pin_at`,
        rubber bumpers under it. Returns the z of the top of the top plate."""
        cx, cy, cz = c
        cz0 = cz + 0.05
        self.box("rubber", (cx, cy, cz + 0.025), (w * 0.6, d * 0.6, 0.05), soft=0.006)
        for i in range(n):
            z = cz0 + i * (t + gap) + t / 2
            self.box(mat, (cx, cy, z), (w, d, t - 0.0012), soft=0.003)
            if i == pin_at:  # the pin: a steel shaft into the plate's front with a knob
                self.tube("chrome", (cx, cy - d / 2 - 0.045, z), (cx, cy - d / 2 + 0.01, z), 0.0055)
                self.cyl("plastic", (cx, cy - d / 2 - 0.055, z), 0.016, 0.03, axis="y")
        ztop = cz0 + n * (t + gap)
        self.box(mat, (cx, cy, ztop + 0.03), (w, d, 0.06), soft=0.006)  # top plate (thicker, with the cable eye)
        self.tube("chrome", (cx, cy, cz0), (cx, cy, ztop + 0.07), 0.0095)  # selector stem through the plates
        for sx in (-1, 1):
            self.tube("chrome", (cx + sx * rods / 2, cy, cz + 0.01), (cx + sx * rods / 2, cy, cz + top), rod_r)
        return ztop + 0.06

    @_part
    def text(self, mat, body, c, size, rz=0.0, rx=math.pi / 2, depth=0.001, spin=0.0):
        """Raised lettering (labels on shrouds, weight numbers). Default faces -y (the user); spin turns it in its own plane."""
        cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.size = size; cu.extrude = depth / 2
        cu.align_x = "CENTER"; cu.align_y = "CENTER"
        try:
            cu.font = bpy.data.fonts.load("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", check_existing=True)
        except (RuntimeError, OSError):
            pass
        ob = bpy.data.objects.new("txt", cu); bpy.context.scene.collection.objects.link(ob)
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
        me.transform(Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(rx, 4, "X") @ Matrix.Rotation(spin, 4, "Z"))
        self.bm(mat, 0).from_mesh(me); bpy.data.meshes.remove(me)

    def decal(self, img, c, w, h, facing="+x", rough=0.3):
        """A flat printed sheet (a placard, a label) with an image, centred on c, w wide and h tall, facing +x/-x/+y/-y.
        Made as its own object at once (it needs UVs); the image is ours, generated next to the piece's model.py."""
        me = bpy.data.meshes.new(f"{self.name}_decal")
        hw, hh = w / 2, h / 2
        right = {"+x": Vector((0, 1, 0)), "-x": Vector((0, -1, 0)), "+y": Vector((-1, 0, 0)), "-y": Vector((1, 0, 0))}[facing]  # the viewer's right
        cv, up = Vector(c), Vector((0, 0, 1))
        vs = [cv - right * hw - up * hh, cv + right * hw - up * hh, cv + right * hw + up * hh, cv - right * hw + up * hh]
        me.from_pydata([tuple(v) for v in vs], [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new(name="UVMap")
        for li, (u, v) in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[li].uv = (u, v)
        m = bpy.data.materials.new(f"{self.name}_decal_{len(bpy.data.materials)}"); m.use_nodes = True
        nt = m.node_tree; b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
        b.inputs["Coat Weight"].default_value = 0.6
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(img), check_existing=True)
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        me.materials.append(m)
        ob = bpy.data.objects.new(me.name, me); self.coll.objects.link(ob)
        self.extra.append(ob)
        return ob

    def sub(self, name, pivot=(0.0, 0.0, 0.0), rz=0.0):
        """A sub-assembly built in the same coordinates, then turned as one about a vertical axis through `pivot` by rz
        degrees (a stack tower set at an angle to the seat). Same looks; finished with the parent."""
        s = Kit(f"{self.name}_{name}", self.coll)
        s.looks, s.pivot, s.rz, s.is_sub = self.looks, tuple(pivot), rz, True
        self.subs.append(s)
        return s

    # -- connections
    def check(self, tol=0.002):
        """Every part must be held: touching (or within tol of) a part that leads, part by part, down to the floor.
        Hardware (bolts, labels, holes, seams) must sit on a member but never counts as holding two members together:
        a bolt head stuck on one plate does not bolt anything. Fills self.floating with the parts nothing holds."""
        items = []
        kits = [(self, Matrix())] + [(s_, Matrix.Translation(Vector(s_.pivot)) @ Matrix.Rotation(math.radians(s_.rz), 4, "Z")
                                      @ Matrix.Translation(-Vector(s_.pivot))) for s_ in self.subs]
        for kit, M in kits:
            faces = {}
            for b in kit.groups.values():
                lay = b.faces.layers.int.get("part")
                for f in (b.faces if lay else ()):
                    faces.setdefault(f[lay], []).append(f)
            for pid, pt in enumerate(kit.parts, 1):
                co, polys = [], []
                probe = []   # the face centres too: two faces flat on each other may share no vertex
                for f in faces.get(pid, ()):
                    polys.append(list(range(len(co), len(co) + len(f.verts))))
                    co.extend(M @ v.co for v in f.verts)
                    probe.append(M @ f.calc_center_median())
                if not polys:
                    continue
                A = np.array([tuple(v) for v in co])
                items.append(dict(pt, co=co, probe=co + probe, tree=BVHTree.FromPolygons(co, polys), lo=A.min(0) - tol, hi=A.max(0) + tol,
                                  c=A.mean(0), hw=all(key[0] in HARDWARE for key in pt["rng"])))
        n = len(items)
        par = list(range(n))

        def root(i):
            while par[i] != i:
                par[i] = par[par[i]]; i = par[i]
            return i

        def touch(a, b):
            if (a["lo"] > b["hi"]).any() or (b["lo"] > a["hi"]).any():
                return False
            if a["tree"].overlap(b["tree"]):
                return True
            return any(y["tree"].find_nearest(v, tol)[0] is not None for x, y in ((a, b), (b, a)) for v in x["probe"]
                       if (v.x >= y["lo"][0] and v.y >= y["lo"][1] and v.z >= y["lo"][2]
                           and v.x <= y["hi"][0] and v.y <= y["hi"][1] and v.z <= y["hi"][2]))

        def gap(a, b, most=GAP):
            """The smallest distance between two parts that don't touch, if under `most` (sampled vertices)."""
            if (a["lo"] - most > b["hi"]).any() or (b["lo"] - most > a["hi"]).any():
                return None
            best = None
            for sm, big in ((a, b), (b, a)):
                for v in sm["probe"]:
                    hit = big["tree"].find_nearest(v, most)
                    if hit[0] is not None and (best is None or hit[3] < best):
                        best = hit[3]
            return best

        seated, nb, near = set(), {}, []   # hardware on some structural part; who touches whom; gaps that look like misses
        for i in range(n):
            for j in range(i + 1, n):
                a, b = items[i], items[j]
                if a["hw"] and b["hw"]:
                    continue
                if (a["hw"] or b["hw"]) and ((i if a["hw"] else j) in seated):
                    continue
                if touch(a, b):
                    if a["hw"] or b["hw"]:
                        seated.add(i if a["hw"] else j)
                    else:
                        par[root(i)] = root(j)
                        nb.setdefault(i, []).append(j); nb.setdefault(j, []).append(i)
                elif not (a["hw"] or b["hw"]):
                    g = gap(a, b)
                    if g is not None:
                        near.append((g, i, j))
        ground = {root(i) for i, it in enumerate(items) if not it["hw"] and it["lo"][2] <= tol * 1.5}
        held = {i for i, it in enumerate(items) if not it["hw"] and root(i) in ground}
        self.floating = []
        for i, it in enumerate(items):
            if it["hw"]:
                ok = i in seated   # (seated on a part that is itself held: checked below)
            else:
                ok = i in held
            if not ok:
                self.floating.append((it["what"], it["where"], tuple(round(float(x), 3) for x in it["c"])))
        groups = {}
        for i in range(n):
            if not items[i]["hw"] and i not in held:
                groups.setdefault(root(i), []).append(i)
        print(f"connections: {n} parts, {len(held)} structural held to the floor, {len(self.floating)} floating"
              + (f" in {len(groups)} loose assemblies" if groups else ""), flush=True)
        for g, members in groups.items():
            print("  loose assembly:", flush=True)
            for i in members:
                print(f"    {items[i]['what']:<22} {items[i]['where']:<12} at {tuple(round(float(x), 3) for x in items[i]['c'])}", flush=True)
        for i, it in enumerate(items):
            if it["hw"] and i not in seated:
                print(f"  hardware on nothing: {it['what']} {it['where']} at {tuple(round(float(x), 3) for x in it['c'])}", flush=True)
        hung = [i for i, it in enumerate(items) if not it["hw"] and not it["rod"] and i in held and nb.get(i)
                and not it["what"].endswith(("rubber", "plastic"))   # end caps and grips do sit on a rod
                and all(items[j]["rod"] for j in nb[i])]
        for i in hung:
            it = items[i]
            self.floating.append((it["what"] + " (hung on a rod)", it["where"], tuple(round(float(x), 3) for x in it["c"])))
            print(f"  hung on a rod only: {it['what']} {it['where']} at {tuple(round(float(x), 3) for x in it['c'])}"
                  f" (on {', '.join(items[j]['where'] for j in nb[i])}): bolt it to a plate, give it a hub, or weld it", flush=True)
        for g, i, j in sorted(near):
            print(f"  gap {g * 1000:.0f} mm: {items[i]['what']} {items[i]['where']} / {items[j]['what']} {items[j]['where']}"
                  f" at {tuple(round(float(x), 3) for x in items[i]['c'])}: close it or open it up", flush=True)
        self.gaps = near
        return self.floating

    # -- output
    def finish(self):
        if not getattr(self, "is_sub", False):
            self.check()
        mats = {}
        obs = []
        for (role, soft), b in self.groups.items():
            if role not in mats:
                mats[role] = _principled(f"{self.name}_{role}", **self.looks.get(role, LOOK["frame"]))
            bmesh.ops.recalc_face_normals(b, faces=b.faces)
            me = bpy.data.meshes.new(f"{self.name}_{role}"); b.to_mesh(me); b.free()
            ob = bpy.data.objects.new(me.name, me); self.coll.objects.link(ob); me.materials.append(mats[role])
            if soft == -1:  # cushions: subdivided smooth
                sd_ = ob.modifiers.new("smooth", "SUBSURF"); sd_.levels = sd_.render_levels = 2
            elif soft:
                bv = ob.modifiers.new("soft", "BEVEL"); bv.width = soft; bv.segments = 4 if soft > 0.004 else 2
                bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(35); bv.harden_normals = soft <= 0.004
            me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
            if soft > 0.004:  # soft pads: smooth shading without hardened normals
                ob.modifiers.new("ws", "WEIGHTED_NORMAL")
            obs.append(ob)
        self.groups = {}
        obs += self.extra
        for s in self.subs:
            M = Matrix.Translation(Vector(s.pivot)) @ Matrix.Rotation(math.radians(s.rz), 4, "Z") @ Matrix.Translation(-Vector(s.pivot))
            for ob in s.finish():
                ob.matrix_world = M @ ob.matrix_world
                obs.append(ob)
        return obs


def _fillet(P, r, seg):
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        u, v = (a - b), (c - b)
        la, lc = u.length, v.length
        u.normalize(); v.normalize()
        ang = u.angle(v)
        if ang > math.pi - 1e-3:
            out.append(b); continue
        t = r / math.tan(ang / 2)
        t = min(t, la * 0.49, lc * 0.49)
        rr = t * math.tan(ang / 2)
        p0, p1 = b + u * t, b + v * t
        bis = (u + v).normalized()
        cen = b + bis * (rr / math.sin(ang / 2))
        a0, a1 = (p0 - cen), (p1 - cen)
        for k in range(seg + 1):
            f = k / seg
            q = a0.lerp(a1, f)  # slerp on the arc
            q = q.normalized() * rr
            out.append(cen + q)
    out.append(P[-1])
    return out


def _round_poly(pts, r, seg):
    """A closed polygon with every corner rounded by r (clipped to fit)."""
    P = [Vector((x, y)) for x, y in pts]
    out = []
    n = len(P)
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        u, v = (a - b), (c - b)
        la, lc = u.length, v.length
        u.normalize(); v.normalize()
        ang = u.angle(v)
        t = min(r / math.tan(ang / 2), la * 0.45, lc * 0.45)
        rr = t * math.tan(ang / 2)
        p0, p1 = b + u * t, b + v * t
        cen = b + (u + v).normalized() * (rr / math.sin(ang / 2))
        a0, a1 = p0 - cen, p1 - cen
        for k in range(seg + 1):
            q = a0.lerp(a1, k / seg).normalized() * rr
            out.append((cen + q).to_tuple())
    return out


def _inset(pts, d):
    """Shrink a convex polygon towards its centroid by about d."""
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for x, y in pts:
        v = Vector((x - cx, y - cy)); L = v.length
        out.append((cx + v.x * (L - d * 1.2) / L, cy + v.y * (L - d * 1.2) / L))
    return out

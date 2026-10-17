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
import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

# ---------------------------------------------------------------- materials


def _principled(name, color, rough, metal=0.0, coat=0.0, sheen=0.0, bump=None, aniso=0.0):
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
    if bump:  # fine grain (vinyl, rubber, powder texture): noise -> bump, scale in 1/m
        scale, strength = bump
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = strength; bp.inputs["Distance"].default_value = 0.0004
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
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


# ---------------------------------------------------------------- the kit

class Kit:
    def __init__(self, name, coll=None, look=None):
        self.name, self.groups = name, {}
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
    def sweep(self, mat, path, profile, bend=0.0, up=(0, 0, 1), caps=True, soft=0.0015, bend_seg=10, twist=0.0):
        """Sweep a closed profile along a polyline. bend > 0 rounds every corner with that centreline radius (bent tube).
        The profile's v axis starts on `up` projected off the first tangent (then parallel-transported)."""
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

    def tube(self, mat, p0, p1, r, seg=20, soft=0.0008, caps=True):
        self.sweep(mat, [p0, p1], circle(r, seg), soft=soft, caps=caps)

    def bar(self, mat, p0, p1, w, h=None, r=None, up=(0, 0, 1), soft=0.0015):
        """Straight rectangular tube between two points (h along `up`)."""
        h = w if h is None else h
        self.sweep(mat, [p0, p1], rect(w, h, w * 0.12 if r is None else r), up=up, soft=soft)

    # -- solids
    def box(self, mat, c, size, rx=0.0, ry=0.0, rz=0.0, soft=0.0015):
        b = self.bm(mat, soft)
        g = bmesh.ops.create_cube(b, size=1.0)["verts"]
        bmesh.ops.scale(b, vec=size, verts=g)
        R = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X")
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=R)
        bmesh.ops.translate(b, verts=g, vec=c)

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
            self.sweep("seam", pts, circle(0.0022, 6), caps=False, soft=0)

    def cyl(self, mat, c, r, h, axis="z", seg=32, soft=0.001, r2=None):
        b = self.bm(mat, soft)
        g = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)["verts"]
        if axis == "x":
            bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
        elif axis == "y":
            bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(b, verts=g, vec=c)

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

    def pulley(self, c, r, axis="x", w=0.025):
        """A cable pulley: grooved wheel in a plate housing hint (wheel only; housings are modelled by the piece)."""
        ax = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}[axis]
        cv = Vector(c)
        for s in (-1, 1):
            self.disc("plastic", cv + ax * s * w * 0.35, r, 0.012, w * 0.3, axis)
        self.disc("plastic", cv, r * 0.86, 0.012, w * 0.42, axis)
        self.cyl("chrome", cv, 0.008, w * 1.4, axis, seg=12)

    def cable(self, pts, r=0.0028):
        self.sweep("cable", pts, circle(r, 8), caps=False, soft=0)

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

    def text(self, mat, body, c, size, rz=0.0, rx=math.pi / 2, depth=0.001):
        """Raised lettering (labels on shrouds, weight numbers). Default faces -y (the user)."""
        cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.size = size; cu.extrude = depth / 2
        cu.align_x = "CENTER"; cu.align_y = "CENTER"
        try:
            cu.font = bpy.data.fonts.load("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", check_existing=True)
        except (RuntimeError, OSError):
            pass
        ob = bpy.data.objects.new("txt", cu); bpy.context.scene.collection.objects.link(ob)
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
        me.transform(Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(rx, 4, "X"))
        self.bm(mat, 0).from_mesh(me); bpy.data.meshes.remove(me)

    # -- output
    def finish(self):
        mats = {}
        obs = []
        for (role, soft), b in self.groups.items():
            if role not in mats:
                mats[role] = _principled(f"{self.name}_{role}", **self.looks.get(role, LOOK["frame"]))
            bmesh.ops.recalc_face_normals(b, faces=b.faces)
            me = bpy.data.meshes.new(f"{self.name}_{role}"); b.to_mesh(me); b.free()
            ob = bpy.data.objects.new(me.name, me); self.coll.objects.link(ob); me.materials.append(mats[role])
            if soft:
                bv = ob.modifiers.new("soft", "BEVEL"); bv.width = soft; bv.segments = 4 if soft > 0.004 else 2
                bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(35); bv.harden_normals = soft <= 0.004
            me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
            if soft > 0.004:  # soft pads: smooth shading without hardened normals
                ob.modifiers.new("ws", "WEIGHTED_NORMAL")
            obs.append(ob)
        self.groups = {}
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

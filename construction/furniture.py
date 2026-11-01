"""Furniture, fixtures and doors, designed for The Gym (every piece generated here; only textures are downloaded).

Language: Nordic mid-century, regional, minimal. Light oak with soft (bevelled) edges, tapered round legs, cream wool boucle,
cognac leather, sheepskin, light honed stone tops, dark bronze / blackened steel only for small hardware.
Local frame of every piece: origin on the floor, width along x, FRONT (where you sit / face from) towards +y.
Real sizes throughout (see tools/furnish.py). Pieces are built once per kind (+ size) and instanced.
"""
import math

from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import bl_common as bc

PROTO = {}
M = {}
PALETTE = {"lingon": (0.30, 0.06, 0.06), "cloud": (0.62, 0.40, 0.12), "moss": (0.20, 0.25, 0.11), "fjord": (0.11, 0.19, 0.30),
           "heather": (0.42, 0.25, 0.32), "oat": (0.62, 0.57, 0.48)}  # muted Nordic: lingonberry, cloudberry, moss, fjord, heather
COLOURS = ["lingon", "cloud", "moss", "fjord", "heather"]


def materials(MAT):
    """Furniture materials (scanned CC0 textures at real scale; light palette)."""
    if M:
        return M
    M["oak"] = MAT.get("oak_slat") or bc.pbr_material("oak_slat", "oak_veneer_01", 1.83, box=True, tint=(1.05, 1.0, 0.9), sat=0.65, val=1.7)
    M["stone"] = MAT.get("stone_light") or bc.pbr_material("stone_light", "smooth_concrete_floor", 2.0, box=True, sat=0.2, val=2.0)
    M["boucle"] = bc.pbr_material("wool_oat", "caban", 0.274, box=True, tint=(0.95, 0.93, 0.88), sat=0.12, val=1.55, piece_var=0.02)  # plain felted wool
    M["leather"] = bc.pbr_material("leather_cognac", "brown_leather", 0.4, box=True, tint=(1.15, 0.85, 0.6), sat=1.1, val=1.0, piece_var=0.03, rough_mul=0.7)
    M["sheepskin"] = bc.pbr_material("sheepskin", "curly_teddy_natural", 0.336, box=True, tint=(1.0, 0.98, 0.94), sat=0.4, val=1.5, piece_var=0.02)
    M["rug"] = bc.pbr_material("rug_wool", "poly_wool_herringbone", 0.27, tint=(1.0, 0.97, 0.92), sat=0.35, val=1.3, piece_var=0.0)
    M["linen"] = _emissive_fabric("linen_glow", "rough_linen", 0.27, (1.0, 0.86, 0.68), 2.5)
    M["opal"] = _opal("opal_glass", 9.0)
    M["walnut"] = bc.pbr_material("walnut_oiled", "natural_walnut_veneer", 1.0, box=True, tint=(1.15, 0.95, 0.75), sat=1.2, val=0.95, piece_var=0.06, rough_mul=0.8, rough_add=0.12)
    M["steel"] = bc.blackened_steel()           # primary metal (option D)
    M["bronze"] = M["steel"]                     # whole components are never brass/bronze (Roman): they take the primary metal
    M["brass"] = bc.brass_accent()               # brass only as small accents
    M["brushed"] = bc.metal_material("brushed_steel", (0.62, 0.62, 0.6), rough=(0.18, 0.32))
    M["felt"] = MAT.get("felt_black") or bc.material("felt_black", (0.012, 0.012, 0.013), 0.95)
    M["glass"] = MAT.get("glass") or bc.arch_glass("arch_glass")
    M["frame"] = MAT.get("frame") or bc.blackened_steel()
    M["rubber"] = bc.material("rubber_black", (0.02, 0.02, 0.02), 0.8)
    M["ceramic"] = bc.material("ceramic_white", (0.86, 0.85, 0.82), 0.05)
    for k_, rgb in PALETTE.items():  # daycare colour (VISION): wool felt and linoleum in a soft Nordic set, never on the walls
        M["felt_" + k_] = bc.material("felt_" + k_, tuple(c * 0.85 for c in rgb), 0.95)  # matte pressed wool felt
        M["lino_" + k_] = bc.material("lino_" + k_, rgb, 0.45)
    M["pad"] = bc.material("pad_oat", (0.62, 0.56, 0.46), 0.5)
    # garden (outdoors): tarred timber like the building, sod, sand, bark fall surface, granite
    M["tar"] = bc.stained_timber("tarred_timber")
    M["sod"] = bc.material("sod_roof", (0.07, 0.11, 0.035), 0.95)
    M["sand"] = bc.material("play_sand", (0.56, 0.47, 0.33), 0.95)
    M["bark"] = bc.material("bark_mulch", (0.16, 0.1, 0.06), 0.95)
    M["granite"] = bc.material("granite_field", (0.3, 0.29, 0.27), 0.85)
    M["ash"] = bc.material("fire_ash", (0.08, 0.075, 0.07), 0.95)
    M["log"] = bc.pbr_material("log_pine", "pine_bark", 1.2, box=True, piece_var=0.05)
    M["rope"] = bc.material("rope_hemp", (0.45, 0.36, 0.24), 0.9)
    M["trike"] = bc.material("rubber_path", (0.55, 0.46, 0.34), 0.9)  # sand-coloured poured rubber
    M["carpet"] = MAT.get("carpet_wool") or bc.material("carpet_oat", (0.66, 0.6, 0.5), 0.95)
    M["star"] = bc.material("star_dot", (1.0, 0.95, 0.85), 0.5, emit=((1.0, 0.9, 0.75), 25.0))
    M["mirror"] = bc.material("mirror", (0.92, 0.92, 0.9), 0.01, metal=1.0)
    M["mat_textile"] = bc.pbr_material("mat_textile", "caban", 0.274, box=True, tint=(0.2, 0.19, 0.18), sat=0.25, val=0.35, piece_var=0.0, rough_add=0.2)  # charcoal entrance textile
    return M


def _emissive_fabric(name, tid, size, rgb, strength):
    m = bc.pbr_material(name, tid, size, box=True, tint=(1.0, 0.95, 0.88), sat=0.4, val=1.3, piece_var=0.0)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = strength
    return m


def _opal(name, strength):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.95, 0.93, 0.9, 1); b.inputs["Roughness"].default_value = 0.3
    b.inputs["Emission Color"].default_value = (1.0, 0.82, 0.6, 1); b.inputs["Emission Strength"].default_value = strength  # ~2700 K
    return m


# ------------------------------------------------------------------ geometry helpers
class Part:
    """Collects bmesh geometry per material; build() makes one object per material with soft bevelled edges."""
    def __init__(self, name):
        self.name, self.bms = name, {}

    def bm(self, mat):
        return self.bms.setdefault(mat, bmesh.new())

    _CUBE = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
    _CUBE_F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]

    def box(self, mat, c, size, rz=0.0, rx=0.0, ry=0.0):
        """Same box as before (scaled unit cube, rotated Z @ Y @ X, moved to c), built directly: ~4x faster than four bmesh ops."""
        b = self.bm(mat)
        hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
        if rz == 0.0 and rx == 0.0 and ry == 0.0:
            vs = [b.verts.new((c[0] + sx * hx, c[1] + sy * hy, c[2] + sz * hz)) for sx, sy, sz in self._CUBE]
        else:
            R = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X"); cv = Vector(c)
            vs = [b.verts.new(R @ Vector((sx * hx, sy * hy, sz * hz)) + cv) for sx, sy, sz in self._CUBE]
        for f in self._CUBE_F:
            b.faces.new([vs[i] for i in f])

    def cyl(self, mat, c, r, h, seg=24, r2=None):
        b = self.bm(mat)
        g = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)["verts"]
        bmesh.ops.translate(b, verts=g, vec=(c[0], c[1], c[2] + h / 2))

    def blob(self, mat, c, radii, seg=24, z_cut=None):
        """Scaled sphere (ceramics: WC pans, urinal bowls); z_cut flattens it below a height (the wall side / a seat)."""
        b = self.bm(mat)
        g = bmesh.ops.create_uvsphere(b, u_segments=seg, v_segments=seg // 2, radius=1.0)["verts"]
        bmesh.ops.scale(b, vec=radii, verts=g)
        if z_cut is not None:
            for v in g:
                v.co.z = max(v.co.z, z_cut - c[2])
        bmesh.ops.translate(b, verts=g, vec=c)

    def text(self, mat, body, c, size, depth=0.0015, font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", flat=False, rz=0.0):
        """Real 3D lettering, centred on c, facing +y and reading left-to-right for someone looking at the front."""
        cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.size = size; cu.extrude = depth / 2
        cu.align_x = "CENTER"; cu.align_y = "CENTER"
        try:
            cu.font = bpy.data.fonts.load(font, check_existing=True)
        except (RuntimeError, OSError):
            pass
        ob = bpy.data.objects.new("txt", cu); bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
        if flat:  # lying on the floor, readable from -y, turned by rz
            me.transform(Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, "Z"))
        else:
            me.transform(Matrix.Translation(Vector(c)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X"))
        self.bm(mat).from_mesh(me); bpy.data.meshes.remove(me)

    def rod(self, mat, p0, p1, r0, r1=None, seg=16):
        """Tapered round member between two points (legs, spindles, cables)."""
        p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
        b = self.bm(mat)
        g = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=L)["verts"]
        bmesh.ops.translate(b, verts=g, vec=(0, 0, L / 2))
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=d.to_track_quat("Z", "Y").to_matrix())
        bmesh.ops.translate(b, verts=g, vec=p0)

    def rods(self, mat, P0, P1, r, seg=8):
        """Many round members at once (balustrade bars, rail segments): one numpy build, ~100x faster than rod() in a loop."""
        P0, P1 = np.asarray(P0, float), np.asarray(P1, float)
        if not len(P0):
            return
        d = P1 - P0; L = np.linalg.norm(d, axis=1, keepdims=True); d = d / np.maximum(L, 1e-9)
        h = np.where(np.abs(d[:, 2:3]) < 0.9, np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]))
        u = np.cross(d, h); u /= np.linalg.norm(u, axis=1, keepdims=True); v = np.cross(d, u)
        th = np.linspace(0, 2 * np.pi, seg, endpoint=False); ct, st_ = np.cos(th), np.sin(th)
        ring = r * (ct[None, :, None] * u[:, None, :] + st_[None, :, None] * v[:, None, :])        # n, seg, 3
        V = np.concatenate([P0[:, None, :] + ring, P1[:, None, :] + ring], axis=1).reshape(-1, 3)
        n = len(P0); base = (np.arange(n) * 2 * seg)[:, None]
        k = np.arange(seg); k1 = (k + 1) % seg
        sides = np.stack([base + k, base + k1, base + seg + k1, base + seg + k], -1).reshape(-1, 4)
        caps0 = (base + k[::-1][None, :]).tolist(); caps1 = (base + seg + k[None, :]).tolist()
        me = bpy.data.meshes.new("rods_tmp"); me.from_pydata(V.tolist(), [], sides.tolist() + caps0 + caps1)
        self.bm(mat).from_mesh(me); bpy.data.meshes.remove(me)

    def ring(self, mat, c, r_in, r_out, z0, z1, a0=0.0, a1=360.0, seg=128):
        """Annulus sector prism (round counters, ring lights)."""
        b = self.bm(mat)
        n = max(4, int(seg * (a1 - a0) / 360))
        full = abs(a1 - a0) >= 359.99
        vs = []
        for k in range(n + (0 if full else 1)):
            a = math.radians(a0 + (a1 - a0) * k / n)
            ca, sa = math.cos(a), math.sin(a)
            vs.append([b.verts.new((c[0] + r * ca, c[1] + r * sa, z)) for r, z in ((r_in, z0), (r_out, z0), (r_out, z1), (r_in, z1))])
        m_ = len(vs)
        for k in range(m_ if full else m_ - 1):
            A, B = vs[k], vs[(k + 1) % m_]
            for i in range(4):
                b.faces.new((A[i], A[(i + 1) % 4], B[(i + 1) % 4], B[i]))
        if not full:
            b.faces.new(vs[0][::-1]); b.faces.new(vs[-1])
        bmesh.ops.recalc_face_normals(b, faces=b.faces)

    def prism(self, mat, pts_xz, y0, y1):
        """A flat cut-out: polygon in the x-z plane (front view), extruded from y0 to y1 (relief layers, silhouettes)."""
        b = self.bm(mat)
        v0 = [b.verts.new((x, y0, z)) for x, z in pts_xz]; v1 = [b.verts.new((x, y1, z)) for x, z in pts_xz]
        b.faces.new(v0[::-1]); b.faces.new(v1)
        n = len(pts_xz)
        for i in range(n):
            j = (i + 1) % n
            b.faces.new((v0[i], v0[j], v1[j], v1[i]))
        bmesh.ops.recalc_face_normals(b, faces=b.faces[-(n + 2):])

    def build(self, coll, bevel=0.004):
        obs = []
        for mat, b in self.bms.items():
            if getattr(self, "vary", False):  # every separate piece (stave, slat, board) its own texture offset + tone
                lay = b.verts.layers.float.new("prand"); rng_ = np.random.default_rng(len(b.verts)); seen = set()
                for v0 in b.verts:
                    if v0.index in seen:
                        continue
                    val, stack = float(rng_.random()), [v0]
                    seen.add(v0.index)
                    while stack:
                        v = stack.pop(); v[lay] = val
                        for e in v.link_edges:
                            o = e.other_vert(v)
                            if o.index not in seen:
                                seen.add(o.index); stack.append(o)
            me = bpy.data.meshes.new(f"{self.name}_{mat.name}"); b.to_mesh(me); b.free()
            ob = bpy.data.objects.new(me.name, me); coll.objects.link(ob); ob.data.materials.append(mat)
            uv = me.uv_layers.new(name="UVMap")
            if bevel:
                bv = ob.modifiers.new("soft_edges", "BEVEL"); bv.width = bevel; bv.segments = 3; bv.limit_method = "ANGLE"
                bv.angle_limit = math.radians(40); bv.harden_normals = True
            me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
            obs.append(ob)
        return obs


def legs4(P, mat, w, d, h, inset=0.04, r0=0.022, r1=0.015, splay=0.025):
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = (sx * (w / 2 - inset), sy * (d / 2 - inset), h)
            bot = (sx * (w / 2 - inset + splay), sy * (d / 2 - inset + splay), 0.0)
            P.rod(mat, bot, top, r1, r0)


# ------------------------------------------------------------------ pieces
def lounge_chair(P, outdoor=False):
    """'Elverum' lounge chair: walnut frame with wide flat arms, deep oat wool cushions raked back 14°, a sheepskin over the back.
    0.78 x 0.82 x 0.76; seat at 0.40. outdoor=True: the deck version (oiled oak frame, solution-dyed canvas cushions)."""
    wd = M["oak"] if outdoor else M["walnut"]
    cu = _canvas() if outdoor else M["boucle"]
    W = 0.78
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.035)
        P.rod(wd, (x, 0.34, 0), (x, 0.31, 0.6), 0.022, 0.019)        # front leg runs up into the arm
        P.rod(wd, (x, -0.37, 0), (x, -0.33, 0.58), 0.022, 0.019)
        P.box(wd, (x, -0.01, 0.605), (0.075, 0.76, 0.028))           # wide flat arm
        P.box(wd, (x, -0.02, 0.2), (0.028, 0.66, 0.04))              # side rail carrying the seat
    P.box(wd, (0, 0.31, 0.2), (W - 0.07, 0.035, 0.05))
    P.box(wd, (0, -0.33, 0.2), (W - 0.07, 0.035, 0.05))
    P.box(cu, (0, 0.03, 0.33), (W - 0.13, 0.66, 0.15))      # seat cushion
    P.box(cu, (0, -0.27, 0.61), (W - 0.13, 0.15, 0.5), rx=math.radians(14))  # back cushion raked back
    P.box(M["sheepskin"], (0, -0.205, 0.66), (W - 0.24, 0.025, 0.44), rx=math.radians(14))


def sofa(P, L=2.2, outdoor=False):
    wd = M["oak"] if outdoor else M["walnut"]
    cu = _canvas() if outdoor else M["boucle"]
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.035)
        P.rod(wd, (x, 0.36, 0), (x, 0.33, 0.6), 0.024, 0.02); P.rod(wd, (x, -0.39, 0), (x, -0.35, 0.58), 0.024, 0.02)
        P.box(wd, (x, -0.01, 0.605), (0.08, 0.8, 0.028)); P.box(wd, (x, -0.02, 0.2), (0.028, 0.7, 0.04))
    P.box(wd, (0, 0.33, 0.2), (L - 0.07, 0.035, 0.05)); P.box(wd, (0, -0.35, 0.2), (L - 0.07, 0.035, 0.05))
    for x in (-L * 0.15, L * 0.15):  # extra centre legs
        P.rod(wd, (x, 0.33, 0), (x, 0.33, 0.18), 0.02); P.rod(wd, (x, -0.35, 0), (x, -0.35, 0.18), 0.02)
    cw = (L - 0.15) / 3
    for k in (-1, 0, 1):
        P.box(cu, (k * cw, 0.03, 0.33), (cw - 0.012, 0.7, 0.15))
        P.box(cu, (k * cw, -0.29, 0.61), (cw - 0.012, 0.15, 0.5), rx=math.radians(13))
    P.box(M["sheepskin"], (-cw, -0.225, 0.66), (0.52, 0.025, 0.44), rx=math.radians(13))
    if outdoor:  # a folded wool pledd over the right arm (Norwegian decks hand out blankets), a second sheepskin on the seat
        x = L / 2 - 0.035
        P.box(M["felt_fjord"], (x, 0.0, 0.625), (0.16, 0.42, 0.024))
        P.box(M["felt_fjord"], (x + 0.07, 0.0, 0.47), (0.024, 0.42, 0.3))
        P.box(M["sheepskin"], (cw * 0.9, 0.05, 0.415), (0.5, 0.55, 0.02))


def dining_chair(P):
    """Cafe chair: walnut, a curved steam-bent back band (100° arc) carried by the rear legs that run straight up into it,
    an upholstered cognac leather seat on a walnut frame at 0.45. Light, calm, mid-century."""
    wd = M["walnut"]
    lerp = lambda a, b, z: tuple(a[i] + (b[i] - a[i]) * z / b[2] for i in range(2)) + (z,)  # a leg's centre at height z
    zs, zc = 0.16, 0.2
    for sx in (-1, 1):
        fb, ft = (sx * 0.205, 0.205, 0), (sx * 0.185, 0.185, 0.43)
        rb, rt = (sx * 0.2, -0.235, 0), (sx * 0.175, -0.185, 0.8)
        P.rod(wd, fb, ft, 0.014, 0.019)                                                    # front legs, tapered
        P.rod(wd, rb, rt, 0.014, 0.018)                                                    # rear legs up into the back
        P.rod(wd, lerp(rb, rt, zs), lerp(fb, ft, zs), 0.009)                               # side stretcher, leg to leg
    # cross stretcher between the two side stretchers (their mid points), so it is carried, not floating
    mid = lambda sx: tuple((a + b) / 2 for a, b in zip(lerp((sx * 0.2, -0.235, 0), (sx * 0.175, -0.185, 0.8), zs),
                                                      lerp((sx * 0.205, 0.205, 0), (sx * 0.185, 0.185, 0.43), zs)))
    P.rod(wd, mid(-1), mid(1), 0.009)
    P.box(wd, (0, 0.0, 0.415), (0.42, 0.4, 0.035))                                         # seat frame
    P.box(M["leather"], (0, 0.005, 0.452), (0.41, 0.39, 0.04))                              # leather pad
    P.ring(wd, (0, 0.12), 0.333, 0.348, 0.64, 0.82, 230, 310, seg=96)                     # bent back band


def bar_stool(P, h=0.76):
    """Bar stool for a 1.05 bar: walnut legs splayed out of a walnut seat ring, a deep cognac leather cushion, bronze footring."""
    wd = M["walnut"]
    P.ring(wd, (0, 0), 0.13, 0.17, h - 0.06, h - 0.02, seg=64)
    P.cyl(M["leather"], (0, 0, h - 0.025), 0.185, 0.065, seg=64)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        P.rod(wd, (0.25 * math.cos(a), 0.25 * math.sin(a), 0), (0.15 * math.cos(a), 0.15 * math.sin(a), h - 0.05), 0.015, 0.021)
    r = 0.25 - 0.10 * 0.3 / (h - 0.05)  # the legs' radius at the footring height: the ring sits on them
    pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0.3) for a in range(0, 361, 15)]
    for p0, p1 in zip(pts, pts[1:]):
        P.rod(M["bronze"], p0, p1, 0.009, seg=10)


def cafe_table(P):
    oak = M["walnut"]
    P.cyl(oak, (0, 0, 0.71), 0.4, 0.03, seg=64)
    P.ring(oak, (0, 0), 0.24, 0.27, 0.66, 0.71, seg=48)  # apron ring
    for k in range(4):
        a = math.radians(45 + 90 * k)
        P.rod(oak, (0.33 * math.cos(a), 0.33 * math.sin(a), 0), (0.25 * math.cos(a), 0.25 * math.sin(a), 0.67), 0.016, 0.024)


def side_table(P):
    P.cyl(M["stone"], (0, 0, 0.5), 0.24, 0.025, seg=48)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        P.rod(M["walnut"], (0.22 * math.cos(a), 0.22 * math.sin(a), 0), (0.15 * math.cos(a), 0.15 * math.sin(a), 0.5), 0.012, 0.016)


def coffee_table(P):
    P.cyl(M["walnut"], (0, 0, 0.36), 0.5, 0.035, seg=64)
    P.cyl(M["walnut"], (0, 0, 0.1), 0.42, 0.018, seg=64)   # lower shelf
    for k in range(3):
        a = math.radians(90 + 120 * k)
        P.rod(M["walnut"], (0.44 * math.cos(a), 0.44 * math.sin(a), 0), (0.38 * math.cos(a), 0.38 * math.sin(a), 0.36), 0.016, 0.022)


def communal_table(P, L=4.0):
    """Long oak table, 50 mm solid top 1.0 deep, two A-trestles with a stretcher (Nordic farmhouse made minimal)."""
    oak = M["walnut"]
    P.box(oak, (0, 0, 0.715), (L, 1.0, 0.05))
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.45)
        for sy in (-1, 1):
            P.rod(oak, (x, sy * 0.42, 0), (x, sy * 0.18, 0.69), 0.03, 0.026)
        P.box(oak, (x, 0, 0.66), (0.07, 0.62, 0.06))
    P.rod(oak, (-(L / 2 - 0.45), 0, 0.3), ((L / 2 - 0.45), 0, 0.3), 0.025)


def bench(P, L=3.6):
    oak = M["walnut"]
    P.box(oak, (0, 0, 0.43), (L, 0.36, 0.04))
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.3)
        for sy in (-1, 1):
            P.rod(oak, (x, sy * 0.15, 0), (x, sy * 0.11, 0.41), 0.022, 0.02)
    P.box(M["sheepskin"], (-L / 4, 0, 0.462), (0.55, 0.34, 0.025))


def boot_bench(P, L=2.0):
    """Entrance boot bench: slatted oak seat, a slatted boot shelf below, two sheepskins."""
    oak = M["walnut"]
    for k in range(6):
        P.box(oak, (0, -0.16 + k * 0.064, 0.44), (L, 0.05, 0.03))
    for k in range(5):
        P.box(oak, (0, -0.15 + k * 0.075, 0.12), (L - 0.1, 0.05, 0.022))
    for sx in (-1, 0, 1):
        P.box(oak, (sx * (L / 2 - 0.04), 0, 0.22), (0.05, 0.4, 0.44))
    for sx in (-1, 1):
        P.box(M["sheepskin"], (sx * L / 4, 0, 0.47), (0.6, 0.38, 0.025))


def rug(P, size=(2.6, 3.0)):
    P.box(M["rug"], (0, 0, 0.006), (size[0], size[1], 0.012))


def reception_desk(P, L=4.6):
    """Reception desk, 0.8 deep: front of vertical oak staves (45 @ 65, the wall's language), 30 mm light stone ledge at 1.05
    with a soft overhang, staff worktop at 0.74, accessible low end (1.0 m at 0.76), black kick recess."""
    oak, stone = M["oak"], M["stone"]
    low = 1.0
    hi_L = L - low
    x0 = -L / 2
    # carcass
    P.box(oak, (x0 + low + hi_L / 2, 0.0, 0.53), (hi_L, 0.72, 0.9))
    P.box(oak, (x0 + low / 2, 0.0, 0.39), (low, 0.72, 0.62))
    P.box(M["felt"], (0, 0.0, 0.04), (L - 0.04, 0.64, 0.08))  # kick recess
    # staves on the front (+y) and the two ends
    for xs, ztop in ((np.arange(x0 + low + 0.035, L / 2, 0.065), 0.98), (np.arange(x0 + 0.035, x0 + low, 0.065), 0.70)):
        for x in xs:
            P.box(oak, (x, 0.38, 0.08 + (ztop - 0.08) / 2), (0.045, 0.03, ztop - 0.08))
    # stone ledges
    P.box(stone, (x0 + low + hi_L / 2, 0.11, 1.035), (hi_L + 0.04, 0.6, 0.03))
    P.box(stone, (x0 + low / 2, 0.11, 0.745), (low, 0.6, 0.03))
    # staff worktop on the back (-y)
    P.box(oak, (x0 + low + hi_L / 2, -0.43, 0.725), (hi_L, 0.5, 0.03))
    for x in (x0 + low + 0.05, L / 2 - 0.05):
        P.box(oak, (x, -0.43, 0.36), (0.04, 0.5, 0.72))
    # what a working desk carries: two slim monitors on blackened-steel arms facing the staff, keyboards + mice, a phone, two
    # lockable drawer pedestals; on the customer ledge a card terminal, a check-in tablet on a stand, a tray of member cards
    for x in (x0 + low + 0.9, x0 + low + 2.3):  # on the staff worktop, behind the desk's front: customers never see a screen's back
        P.box(M["steel"], (x, -0.42, 0.745), (0.2, 0.1, 0.012))
        P.rod(M["steel"], (x, -0.42, 0.75), (x, -0.41, 0.93), 0.012, seg=8)
        P.box(M["rubber"], (x, -0.4, 1.06), (0.6, 0.025, 0.34))
        P.box(M["felt"], (x, -0.414, 1.06), (0.58, 0.004, 0.32))
        P.box(M["rubber"], (x, -0.58, 0.745), (0.42, 0.13, 0.015))
        P.box(M["rubber"], (x + 0.3, -0.58, 0.745), (0.06, 0.1, 0.02))
        P.box(oak, (x, -0.53, 0.33), (0.42, 0.28, 0.6))            # drawer pedestal under the worktop
        for z in (0.2, 0.42):
            P.box(M["felt"], (x, -0.672, z), (0.4, 0.004, 0.004))
    P.box(M["rubber"], (x0 + low + 1.6, -0.55, 0.765), (0.18, 0.2, 0.05))  # desk phone
    P.box(M["rubber"], (x0 + low + 0.55, 0.25, 1.07), (0.08, 0.16, 0.035), rx=0.3)  # card terminal, angled to the customer
    P.box(M["steel"], (x0 + low + 3.0, 0.2, 1.06), (0.12, 0.1, 0.02))   # check-in tablet on a stand
    P.rod(M["steel"], (x0 + low + 3.0, 0.2, 1.06), (x0 + low + 3.0, 0.22, 1.18), 0.008, seg=8)
    P.box(M["rubber"], (x0 + low + 3.0, 0.24, 1.25), (0.26, 0.012, 0.18), rx=-0.35)
    P.box(oak, (x0 + low + 2.0, 0.22, 1.06), (0.2, 0.12, 0.025))        # member-card tray
    for k in range(4):
        P.box(M["lino_" + COLOURS[k]], (x0 + low + 1.94 + k * 0.04, 0.22, 1.08), (0.006, 0.054, 0.085), rz=0.1)


def cafe_island(P, r_out=3.5, gap_deg=225):
    """Round island bar, Ø7 m: outer bar (stone top at 1.05, 0.45 deep, staved oak front following the curve, steel footrail),
    0.9 m staff ring inside, inner back counter at 0.90 (stone top) with espresso machine, grinders, a pastry case."""
    oak, stone = M["oak"], M["stone"]
    g0, g1 = gap_deg - 8, gap_deg + 8  # service gap (staff hatch)
    a0, a1 = g1, g0 + 360
    r_in = r_out - 0.62
    P.ring(oak, (0, 0), r_in, r_out - 0.05, 0.08, 1.02, a0, a1)          # carcass
    P.ring(stone, (0, 0), r_in - 0.02, r_out + 0.03, 1.02, 1.05, a0, a1)  # bar top
    P.ring(M["felt"], (0, 0), r_in + 0.02, r_out - 0.1, 0.0, 0.08, a0, a1)
    n = int(2 * math.pi * r_out / 0.065)
    for k in range(n):  # staves
        a = 360 * k / n
        if g0 - 2 < a < g1 + 2 or g0 - 2 < a + 360 < g1 + 2:
            continue
        ar = math.radians(a)
        P.box(oak, ((r_out - 0.03) * math.cos(ar), (r_out - 0.03) * math.sin(ar), 0.55), (0.045, 0.03, 0.94), rz=ar + math.pi / 2)
    # footrail
    rr = r_out + 0.18; seg = 96
    for k in range(seg):
        aa, bb = a0 + (a1 - a0) * k / seg, a0 + (a1 - a0) * (k + 1) / seg
        A, B = math.radians(aa), math.radians(bb)
        P.rod(M["steel"], (rr * math.cos(A), rr * math.sin(A), 0.22), (rr * math.cos(B), rr * math.sin(B), 0.22), 0.016, seg=10)
    for k in range(12):
        A = math.radians(a0 + (a1 - a0) * (k + 0.5) / 12)
        P.rod(M["steel"], ((r_out - 0.02) * math.cos(A), (r_out - 0.02) * math.sin(A), 0.22), (rr * math.cos(A), rr * math.sin(A), 0.22), 0.012, seg=8)
    # back counter
    rb_out, rb_in = r_in - 0.9, r_in - 1.55
    P.ring(oak, (0, 0), rb_in, rb_out, 0.0, 0.87, 0, 360)
    P.ring(stone, (0, 0), rb_in - 0.02, rb_out + 0.02, 0.87, 0.9, 0, 360)
    # espresso machine (brushed steel, 3 groups), two grinders, cup rail
    ang = math.radians(45); cx_, cy_ = (rb_out - 0.3) * math.cos(ang), (rb_out - 0.3) * math.sin(ang)
    P.box(M["brushed"], (cx_, cy_, 0.9 + 0.22), (0.8, 0.5, 0.44), rz=ang + math.pi / 2)
    for k in (-1, 0, 1):
        ox, oy = math.cos(ang + math.pi / 2) * k * 0.24, math.sin(ang + math.pi / 2) * k * 0.24
        P.cyl(M["steel"], (cx_ + ox + 0.24 * math.cos(ang), cy_ + oy + 0.24 * math.sin(ang), 0.98), 0.035, 0.07, seg=16)
    for d in (0.62, -0.62):
        gx, gy = cx_ + math.cos(ang + math.pi / 2) * d, cy_ + math.sin(ang + math.pi / 2) * d
        P.cyl(M["steel"], (gx, gy, 0.9), 0.09, 0.42, seg=24)
        P.cyl(M["glass"], (gx, gy, 1.32), 0.08, 0.16, seg=24, r2=0.11)
    # cups warming on the machine, milk jugs, a cup shelf on the back counter; bag hooks under the bar at every stool; a card
    # terminal at the hatch side of the bar
    for k in range(-2, 3):
        for j in range(2):
            P.cyl(M["ceramic"], (cx_ + math.cos(ang + math.pi / 2) * k * 0.12, cy_ + math.sin(ang + math.pi / 2) * k * 0.12, 1.34 + j * 0.07), 0.04, 0.07, seg=16, r2=0.045)
    for d in (0.95, 1.1):
        jx, jy = cx_ + math.cos(ang + math.pi / 2) * d, cy_ + math.sin(ang + math.pi / 2) * d
        P.cyl(M["brushed"], (jx, jy, 0.9), 0.045, 0.12, seg=16, r2=0.038)
    for k in range(10):
        A = math.radians(80 + k * 8); rr_ = rb_out - 0.12
        P.cyl(M["ceramic"], (rr_ * math.cos(A), rr_ * math.sin(A), 0.9), 0.045, 0.09, seg=16, r2=0.05)
    nh = int(2 * math.pi * r_out / 0.66)
    for k in range(nh):
        a = 360 * k / nh + 4
        if abs(((a - gap_deg) + 180) % 360 - 180) < 16:
            continue
        A = math.radians(a); rh = r_out + 0.005
        P.rod(M["steel"], (rh * math.cos(A), rh * math.sin(A), 0.96), ((rh + 0.06) * math.cos(A), (rh + 0.06) * math.sin(A), 0.93), 0.006, seg=6)
    ta = math.radians(gap_deg - 16); tr_ = r_out - 0.2
    P.box(M["rubber"], (tr_ * math.cos(ta), tr_ * math.sin(ta), 1.07), (0.08, 0.16, 0.035), rz=ta, rx=0.3)
    # pastry case on the bar (glass box with an oak base), facing the reception path
    pa = math.radians(80); px_, py_ = (r_out - 0.28) * math.cos(pa), (r_out - 0.28) * math.sin(pa)
    P.box(oak, (px_, py_, 1.07), (1.2, 0.36, 0.04), rz=pa + math.pi / 2)
    P.box(M["glass"], (px_, py_, 1.24), (1.2, 0.36, 0.3), rz=pa + math.pi / 2)


def ring_pendant(P, r=3.15, hang=3.35, ceiling=5.42):
    """Ring light over the bar: a 60 x 120 mm oak hoop with a glowing linen band beneath, on 6 thin steel cables."""
    P.ring(M["oak"], (0, 0), r - 0.06, r, hang + 0.25, hang + 0.37, seg=192)
    P.ring(M["linen"], (0, 0), r - 0.055, r - 0.045, hang, hang + 0.25, seg=192)
    P.ring(M["linen"], (0, 0), r - 0.015, r - 0.005, hang, hang + 0.25, seg=192)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        P.rod(M["steel"], ((r - 0.03) * math.cos(a), (r - 0.03) * math.sin(a), hang + 0.37), ((r - 0.03) * math.cos(a), (r - 0.03) * math.sin(a), ceiling), 0.0015, seg=6)


def pendant_opal(P, hang=2.45, ceiling=5.42):
    """Opal glass cylinder (Ø220 x 420) with an oak cap and a cognac leather cord sleeve."""
    P.cyl(M["opal"], (0, 0, hang), 0.11, 0.42, seg=48)
    P.cyl(M["oak"], (0, 0, hang + 0.42), 0.115, 0.05, seg=48)
    P.rod(M["leather"], (0, 0, hang + 0.47), (0, 0, hang + 0.62), 0.008, seg=10)
    P.rod(M["steel"], (0, 0, hang + 0.62), (0, 0, ceiling), 0.0025, seg=6)


def glass_screen(P, width, height, door=0.0):
    """Framed glass screen (dark aluminium 50 x 120 frame); if door > 0 a pair of sliding leaves in the middle."""
    fr, gl = M["frame"], M["glass"]
    P.box(fr, (0, 0, height - 0.025), (width, 0.12, 0.05))
    P.box(fr, (0, 0, 0.01), (width, 0.12, 0.02))
    for x in (-width / 2 + 0.025, width / 2 - 0.025):
        P.box(fr, (x, 0, height / 2), (0.05, 0.12, height))
    if door > 0:
        leaf = door / 2
        P.box(fr, (0, 0, 2.32), (width, 0.12, 0.06))  # head over the doors
        for x in (-door / 2, door / 2):
            P.box(fr, (x, 0, 1.17), (0.05, 0.12, 2.3))
        for s in (-1, 1):
            cx = s * leaf / 2
            P.box(gl, (cx, 0.03, 1.15), (leaf - 0.06, 0.012, 2.2))
            for x in (cx - leaf / 2 + 0.03, cx + leaf / 2 - 0.03):
                P.box(fr, (x, 0.03, 1.15), (0.04, 0.05, 2.25))
            for z in (0.03, 2.26):
                P.box(fr, (cx, 0.03, z), (leaf, 0.05, 0.05))
        for s in (-1, 1):  # fixed glass either side
            w_ = (width - door) / 2
            if w_ > 0.1:
                P.box(gl, (s * (door / 2 + w_ / 2), 0, height / 2), (w_ - 0.08, 0.012, height - 0.08))
        P.box(gl, (0, 0, (2.35 + height) / 2), (door - 0.06, 0.012, height - 2.4))
    else:
        P.box(gl, (0, 0, height / 2), (width - 0.08, 0.012, height - 0.08))


def sliding_doors(P, width, height):
    glass_screen(P, width, height + 0.06, door=width - 0.1)


def vestibule_lid(P, size, height=3.0):
    """Oak slat lid over the vestibule (keeps the warm air pocket), black felt behind."""
    w, d = size
    P.box(M["felt"], (0, 0, height + 0.05), (w, d, 0.02))
    for y in np.arange(-d / 2 + 0.0325, d / 2, 0.065):
        P.box(M["oak"], (0, y, height + 0.02), (w, 0.045, 0.02))


def door_slatted(P, width=1.0, height=2.3):
    """Hidden stair door: a flush leaf carrying the wall's oak slats (45 @ 65), 3 mm shadow gap, slim bronze pull."""
    P.box(M["felt"], (0, -0.03, height / 2), (width - 0.006, 0.04, height - 0.006))
    for x in np.arange(-width / 2 + 0.0325, width / 2, 0.065):
        P.box(M["oak"], (x, 0.0, height / 2), (0.045, 0.02, height - 0.01))
    P.box(M["brass"], (width / 2 - 0.12, 0.022, 1.05), (0.02, 0.025, 0.42))  # brass pull: an accent


def lift_doors(P, width=1.2, height=2.3):
    """Lift: two blackened-steel centre-opening leaves in a 60 mm blackened-steel frame; brass only on the call plate and a thin head line."""
    br = M["bronze"]
    for s in (-1, 1):
        P.box(br, (s * width / 4, 0.0, height / 2), (width / 2 - 0.004, 0.03, height))
    P.box(br, (0, 0.02, height + 0.03), (width + 0.12, 0.04, 0.06))
    for x in (-width / 2 - 0.03, width / 2 + 0.03):
        P.box(br, (x, 0.02, height / 2), (0.06, 0.04, height + 0.06))
    P.box(M["brass"], (width / 2 + 0.25, 0.012, 1.1), (0.09, 0.012, 0.24))  # brass call plate: an accent
    P.box(M["brass"], (0, 0.017, height - 0.002), (width, 0.004, 0.004))   # a thin brass line at the head
    P.cyl(M["opal"], (width / 2 + 0.25, 0.02, 1.08), 0.015, 0.006, seg=16)


def glass_door(P, width=1.6, height=2.3, privacy=False):
    """Framed glass secure door (pair) with a long oak pull. privacy=True: switchable privacy glass (the training pods), shown
    frosted, as when the pod is booked and in use."""
    fr = M["frame"]
    gl = M.setdefault("glass_privacy", bc.arch_glass("glass_privacy", rough=0.35, frosted=True)) if privacy else M["glass"]
    for s in (-1, 1):
        cx = s * width / 4
        P.box(gl, (cx, 0, height / 2), (width / 2 - 0.08, 0.012, height - 0.08))
        for x in (cx - width / 4 + 0.025, cx + width / 4 - 0.025):
            P.box(fr, (x, 0, height / 2), (0.05, 0.06, height))
        for z in (0.03, height - 0.03):
            P.box(fr, (cx, 0, z), (width / 2, 0.06, 0.06))
        P.rod(M["oak"], (s * 0.06, 0.06, 0.8), (s * 0.06, 0.06, 1.5), 0.014)


def baffle_screen(P, width=2.6, height=2.4):
    """WC privacy baffle: oak slats 45 @ 65 on both faces of a black core (seen from the cafe and from inside alike)."""
    P.box(M["felt"], (0, -0.02, height / 2), (width, 0.03, height))
    for x in np.arange(-width / 2 + 0.0325, width / 2, 0.065):
        for y in (0.0, -0.04):
            P.box(M["oak"], (x, y, height / 2), (0.045, 0.02, height))


def porch_floor(P, size=(2.5, 4.1)):
    P.box(M["stone"], (0, 0, -0.03), (size[0], size[1], 0.06))
    P.box(bc.material("concrete", (0.48, 0.47, 0.44), 0.85), (0, 0, -0.35), (size[0], size[1], 0.58))


def entrance_mat(P, size=(2.15, 2.9), style="wiper"):
    """Entrance matting, flush with the floor (top at z 0). 'scraper': open blackened-steel bar grate (5 mm bars @ 15 mm,
    walking across them) over a dark drained pit. 'wiper': charcoal textile ribs 22 mm wide with every fourth a rubber
    scraper strip, in a 25 mm blackened-steel frame, 22 mm deep (the stone thickness)."""
    w, d = size
    fr = M["steel"]
    lift = 0.004 if style == "scraper" else 0.0  # the porch slab is one piece: the grate frame shows a 4 mm lip on it
    for sx in (-1, 1):
        P.box(fr, (sx * (w / 2 - 0.0125), 0, -0.011 + lift), (0.025, d, 0.022))
    for sy in (-1, 1):
        P.box(fr, (0, sy * (d / 2 - 0.0125), -0.011 + lift), (w - 0.05, 0.025, 0.022))
    if style == "scraper":
        P.box(M["rubber"], (0, 0, -0.08), (w - 0.05, d - 0.05, 0.02))
        for x in np.arange(-w / 2 + 0.035, w / 2 - 0.025, 0.015):  # bars run along the door (y), feet cross them
            P.box(fr, (x, 0, -0.016 + lift), (0.005, d - 0.05, 0.03))
        for y in np.arange(-d / 2 + 0.2, d / 2 - 0.1, 0.4):
            P.box(fr, (0, y, -0.027 + lift), (w - 0.05, 0.004, 0.008))
    else:
        tex, rub = M["mat_textile"], M["rubber"]
        P.box(rub, (0, 0, -0.02), (w - 0.05, d - 0.05, 0.004))
        for k, x in enumerate(np.arange(-w / 2 + 0.04, w / 2 - 0.03, 0.026)):
            if k % 4 == 3:
                P.box(rub, (x, 0, -0.0085), (0.012, d - 0.05, 0.017))
            else:
                P.box(tex, (x, 0, -0.009), (0.022, d - 0.05, 0.018))


# ------------------------------------------------------------------ wet rooms (VISION "Wet rooms", Roman 2026-10-12)
def _staved_front(P, x0, x1, h, y, doors):
    """Vertical oak staves 45 @ 65 across x0..x1 (the slat language) on a black core; doors = [(xa, xb, hd)] get a
    6 mm shadow gap round the leaf (staves straddling a door edge are left out = the vertical gap)."""
    P.box(M["felt"], ((x0 + x1) / 2, y - 0.025, h / 2), (x1 - x0, 0.02, h))
    for x in np.arange(x0 + 0.0325, x1 - 0.02, 0.065):
        a, b_ = x - 0.0225, x + 0.0225
        d_ = next((d for d in doors if a < d[1] and b_ > d[0]), None)
        if d_ and (a < d_[0] < b_ or a < d_[1] < b_):
            continue
        if d_:
            P.box(M["oak"], (x, y, d_[2] / 2), (0.045, 0.02, d_[2] - 0.006))
            P.box(M["oak"], (x, y, (d_[2] + h) / 2 + 0.003), (0.045, 0.02, h - d_[2] - 0.006))
        else:
            P.box(M["oak"], (x, y, h / 2), (0.045, 0.02, h))


# ------------------------------------------------------------------ sanitation (Roman: bins, soap, towels... that level of detail)
def _pedal_bin(P, c, h=0.42, r=0.12, lid=None):
    """Pedal bin: a blackened-steel drum with an oak lid and a steel foot pedal (sanitary 0.3, waste 0.42, nappy 0.6)."""
    x, y = c
    P.cyl(M["steel"], (x, y, 0.0), r, h - 0.02, seg=32)
    P.cyl(lid or M["oak"], (x, y, h - 0.02), r + 0.004, 0.02, seg=32)
    P.box(M["steel"], (x, y + r + 0.03, 0.02), (0.08, 0.07, 0.015))


def _brush(P, c):
    """Toilet brush in a blackened-steel holder."""
    x, y = c
    P.cyl(M["steel"], (x, y, 0.0), 0.05, 0.36, seg=20)
    P.rod(M["oak"], (x, y, 0.36), (x, y, 0.42), 0.012, seg=10)


def _soap(P, x, y, z):
    """Wall soap dispenser: a small blackened-steel box with a push plate, its nozzle over the basin."""
    P.box(M["steel"], (x, y + 0.05, z), (0.09, 0.1, 0.18))
    P.box(M["steel"], (x, y + 0.11, z - 0.07), (0.03, 0.03, 0.02))


def towel_station(P, h_disp=1.25):
    """Paper-towel dispenser recessed in an oak surround on the wall + a 60 l waste bin below (blackened steel, oak lid): beside
    every vanity. Origin = wall face, front +y."""
    P.box(M["oak"], (0, 0.03, h_disp), (0.36, 0.06, 0.42))
    P.box(M["steel"], (0, 0.065, h_disp), (0.3, 0.02, 0.36))
    P.box(M["felt"], (0, 0.076, h_disp - 0.17), (0.2, 0.004, 0.012))  # towel slot
    _pedal_bin(P, (0, 0.2), h=0.62, r=0.17)


def sanitiser(P):
    """Hand-sanitiser station: a slim oak post on a steel foot with a touch-free dispenser at 1.0 (0.8 for children's side) and a
    drip tray: by the entrances and the daycare doors."""
    P.cyl(M["steel"], (0, 0, 0), 0.16, 0.012, seg=32)
    P.box(M["oak"], (0, 0, 0.6), (0.08, 0.08, 1.2))
    P.box(M["steel"], (0, 0.07, 1.02), (0.1, 0.07, 0.2))
    P.box(M["steel"], (0, 0.08, 0.86), (0.12, 0.09, 0.012))


def recycling(P, L=1.2):
    """Kildesortering (Norwegian waste sorting): an oak cabinet with four lidded drop slots marked by coloured felt tags:
    restavfall, plast, papp/papir, matavfall (green), and glass/metall where it is a cafe."""
    d, h = 0.5, 0.9
    P.box(M["oak"], (0, d / 2, h / 2), (L, d, h))
    n = 4
    for k, c in enumerate(("oat", "fjord", "cloud", "moss")):
        x = -L / 2 + (k + 0.5) * L / n
        P.box(M["felt"], (x, d / 2, h + 0.002), (L / n - 0.12, 0.16, 0.004))
        P.box(M["felt_" + c], (x, d + 0.004, h - 0.12), (L / n - 0.16, 0.006, 0.06))
        P.box(M["felt"], (x - L / n / 2, d + 0.002, h / 2), (0.004, 0.004, h - 0.04))


def _cell_front(P, x0, x1, h, depth, doors, style="wc", number0=1, occupied=()):
    """Front of a row of WC cells (Roman: you must see where the doors are and if they are free): a continuous oak face with fine
    fluting (30 mm flutes, 3 mm grooves: the slat language without dark gaps), each door leaf framed by a 5 mm black shadow
    gap, a transom panel above it. On each door: a blackened-steel lever and an indicator thumb-turn (green 'ledig' / red
    'opptatt' segment). Over each door: a slim steel plate with the cell number in brass and a lit occupancy dot (green free,
    red occupied: the same signal as the turn), visible down the whole room. Accessible + cleaner's doors carry pictograms."""
    ok, sh = M["oak"], M["felt"]
    yf = depth + 0.01
    free = M.setdefault("led_free", bc.material("led_free", (0.02, 0.45, 0.1), 0.3, emit=((0.05, 1.0, 0.2), 0.5)))
    busy = M.setdefault("led_busy", bc.material("led_busy", (0.6, 0.02, 0.01), 0.3, emit=((1.0, 0.05, 0.02), 0.5)))
    P.box(ok, ((x0 + x1) / 2, yf - 0.012, h / 2), (x1 - x0, 0.024, h))          # the face (one plane, doors cut by shadow gaps)
    for x in np.arange(x0 + 0.015, x1, 0.03):                                   # fluting grooves, stopped at the door gaps
        P.box(sh, (x, yf + 0.0005, h / 2), (0.003, 0.002, h - 0.02))
    P.box(ok, ((x0 + x1) / 2, depth - 0.05, h / 2), (x1 - x0 - 0.03, 0.012, h))  # plain oak inside face
    for i, (xa, xb, hd) in enumerate(doors):
        for (cx, cz, sx, sz) in (((xa + xb) / 2, hd + 0.0025, xb - xa + 0.005, 0.005), (xa, hd / 2, 0.005, hd), (xb, hd / 2, 0.005, hd)):
            P.box(sh, (cx, yf + 0.001, cz), (sx, 0.004, sz))                     # shadow gap round the leaf
        lx = xb - 0.08
        P.box(M["steel"], (lx, yf + 0.008, 1.0), (0.05, 0.016, 0.05))            # lever rose + lever
        P.box(M["steel"], (lx - 0.06, yf + 0.03, 1.0), (0.13, 0.02, 0.018))
        busy_ = (number0 + i) in occupied
        b = P.bm(M["steel"]); g = bmesh.ops.create_cone(b, cap_ends=True, segments=24, radius1=0.028, radius2=0.028, depth=0.008)["verts"]
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X")); bmesh.ops.translate(b, verts=g, vec=(lx, yf + 0.004, 1.18))
        P.box(busy if busy_ else free, (lx, yf + 0.009, 1.195), (0.03, 0.002, 0.012))  # indicator window on the turn
        if style == "accessible":
            pictogram_on(P, "accessible", (xa + xb) / 2, yf + 0.004, 1.75, 0.16, plate=True)
        if style == "accessible":  # baby-changing on the accessible door too, at eye height
            pictogram_on(P, "baby", (xa + xb) / 2, yf + 0.004, 1.55, 0.16, plate=True)


def pictogram_on(P, figure, x, y, z, size, plate=False):
    """A pictogram placed in another piece's frame, facing +y (wraps pictogram())."""
    tmp = Part("tmp")
    pictogram(tmp, figure=figure, size=size if plate else size * 2.2, mount=0.0)
    for mat, b in tmp.bms.items():
        for v in b.verts:
            v.co = Vector((x + v.co.x, y + v.co.y - (0.0 if plate else 0.006), z + v.co.z))
        tgt = P.bm(mat)
        me = bpy.data.meshes.new("tmp"); b.to_mesh(me); b.free(); tgt.from_mesh(me); bpy.data.meshes.remove(me)


def _wc_pan(P, x, side_rail=0):
    """Wall-hung white WC (seat at 0.46) with a blackened-steel flush plate, roll holder and (accessible) fold-up rails."""
    P.box(M["ceramic"], (x, 0.06, 0.38), (0.34, 0.12, 0.2))                       # back, against the wall
    b = P.bm(M["ceramic"]); n = 40                                                # bowl: an egg-shaped shell tapering down
    rings = []
    for zz, sc in ((0.44, 1.0), (0.39, 0.97), (0.34, 0.86), (0.3, 0.62)):
        rings.append([b.verts.new((x + 0.18 * sc * math.cos(2 * math.pi * k / n), 0.32 + 0.25 * sc * math.sin(2 * math.pi * k / n) - 0.06 * (1 - sc), zz)) for k in range(n)])
    for A, B in zip(rings, rings[1:]):
        for k in range(n):
            b.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    b.faces.new(rings[-1][::-1])
    seat = P.bm(M["ceramic"])                                                     # oval seat ring + lid
    so = [seat.verts.new((x + 0.185 * math.cos(2 * math.pi * k / n), 0.31 + 0.24 * math.sin(2 * math.pi * k / n), 0.465)) for k in range(n)]
    sb = [seat.verts.new((x + 0.185 * math.cos(2 * math.pi * k / n), 0.31 + 0.24 * math.sin(2 * math.pi * k / n), 0.445)) for k in range(n)]
    seat.faces.new(so); seat.faces.new(sb[::-1])
    for k in range(n):
        seat.faces.new((sb[k], sb[(k + 1) % n], so[(k + 1) % n], so[k]))
    P.box(M["steel"], (x, 0.004, 1.05), (0.25, 0.008, 0.16))
    P.rod(M["steel"], (x + 0.38, 0.0, 0.75), (x + 0.38, 0.12, 0.75), 0.008, seg=8)
    P.rod(M["steel"], (x + 0.38, 0.12, 0.75), (x + 0.5, 0.12, 0.75), 0.008, seg=8)
    for s_ in ([-1, 1] if side_rail else []):  # fold-up grab rails either side, 0.35 off the pan centre, at 0.8
        xr = x + s_ * 0.35
        P.box(M["steel"], (xr, 0.03, 0.8), (0.07, 0.06, 0.16))
        P.rod(M["steel"], (xr, 0.05, 0.8), (xr, 0.85, 0.8), 0.016, seg=12)


def wc_cells(P, n=4, w=1.1, depth=1.65, h=2.73, style="wc", door_at=0.0, pan_at=0.0, number0=1, occupied=()):
    """A row of WC cells standing in the tall WC room: oak boxes, floor to 2.6 m and closed to the floor, with an oak lid,
    so each is private while the room above stays open to the clerestory light. Origin = the wall face at the row centre,
    cells along x, front towards +y. Panels 30 mm, front in vertical oak staves with flush doors (0.8 m; accessible 1.0).
    style 'wc' (a pan per cell), 'accessible' (one cell: pan with rails, basin, fold-down changing table), 'store' (cleaner)."""
    W = n * w
    for k in range(n + 1):
        P.box(M["oak"], (-W / 2 + k * w, depth / 2, h / 2), (0.03, depth, h))
    P.box(M["oak"], (0, depth / 2, h + 0.02), (W + 0.03, depth + 0.02, 0.04))  # lid
    dw = 1.0 if style == "accessible" else (0.9 if style == "store" else 0.8)
    doors = []
    for k in range(n):
        cx = -W / 2 + (k + 0.5) * w + (door_at if n == 1 else 0.0)
        doors.append((cx - dw / 2, cx + dw / 2, 2.1))
    _cell_front(P, -W / 2, W / 2, h, depth, doors, style=style, number0=number0, occupied=occupied)
    if style == "wc":
        for k in range(n):
            _wc_pan(P, -W / 2 + (k + 0.5) * w)
            _brush(P, (-W / 2 + (k + 0.5) * w - 0.36, 0.1))
            _pedal_bin(P, (-W / 2 + (k + 0.5) * w + 0.36, 0.14), h=0.3, r=0.09)  # sanitary bin
            P.rod(M["steel"], (-W / 2 + (k + 0.5) * w - 0.2, depth - 0.02, 1.7), (-W / 2 + (k + 0.5) * w - 0.2, depth - 0.08, 1.7), 0.01, seg=8)  # coat hook
    elif style == "accessible":
        _wc_pan(P, pan_at, side_rail=1)
        bx = -pan_at * 0.9 if abs(pan_at) > 0.3 else W / 2 - 0.45
        P.box(M["stone"], (bx, 0.24, 0.80), (0.5, 0.45, 0.06))  # small basin slab, knee space below (accessible)
        P.box(M["ceramic"], (bx, 0.24, 0.775), (0.38, 0.3, 0.02))
        P.rod(M["steel"], (bx, 0.0, 0.98), (bx, 0.16, 0.98), 0.012, seg=12)
        P.box(M["mirror"], (bx, 0.004, 1.45), (0.5, 0.006, 0.8))
        _soap(P, bx + 0.32, 0.0, 1.05)
        cx_ = pan_at + (0.6 if pan_at < 0 else -0.6)   # emergency pull cord (TEK17): red cord to 0.1 above the floor, reset button
        P.box(M["steel"], (cx_, depth / 2, h - 0.02), (0.06, 0.06, 0.03))
        P.rod(M["lino_lingon"], (cx_, depth / 2, h - 0.03), (cx_, depth / 2, 0.1), 0.003, seg=4)
        for z in (0.1, 0.8):
            P.blob(M["lino_lingon"], (cx_, depth / 2, z), (0.02, 0.02, 0.02))
        P.box(M["steel"], (cx_, 0.008, 0.9), (0.08, 0.016, 0.08))
        _brush(P, (pan_at + (0.55 if pan_at < 0 else -0.55), 0.1))
        _pedal_bin(P, (bx, 0.75), h=0.42, r=0.12)
        sx = W / 2 - 0.015 if bx < 0 else -W / 2 + 0.015  # fold-down changing table on the side panel away from the basin
        P.box(M["oak"], (sx - np.sign(sx) * 0.05, depth / 2, 0.9), (0.1, 0.8, 0.5))


def _leaf(P, hinge, L, hd, ang, occupied=False, inside=True):
    """A WC door leaf, 40 mm, fluted oak both faces, hinged at 'hinge' (x, y) on its -x edge, turned 'ang' (rad, outward = +):
    lever + rose on both faces, the indicator thumb-turn on the outside (green ledig / red opptatt), a turn knob inside, a
    concealed closer line at the head."""
    ca, sa = math.cos(ang), math.sin(ang)
    at = lambda u, v, z: (hinge[0] + u * ca - v * sa, hinge[1] + u * sa + v * ca, z)  # u along the leaf, v through it
    P.box(M["oak"], at(L / 2, 0.0, hd / 2), (L - 0.006, 0.04, hd - 0.006), rz=ang)
    for u in np.arange(0.015, L - 0.01, 0.03):
        for v in (0.0205, -0.0205):
            P.box(M["felt"], at(u, v, hd / 2), (0.003, 0.002, hd - 0.03), rz=ang)
    free = M["led_free"]; busy = M["led_busy"]
    for v, sgn in ((0.02, 1), (-0.02, -1)):
        P.box(M["steel"], at(L - 0.08, v + sgn * 0.006, 1.0), (0.05, 0.012, 0.05), rz=ang)
        P.box(M["steel"], at(L - 0.14, v + sgn * 0.026, 1.0), (0.13, 0.02, 0.018), rz=ang)
        P.box(M["steel"], at(L - 0.08, v + sgn * 0.005, 1.17), (0.05, 0.01, 0.05), rz=ang)
    P.box(busy if occupied else free, at(L - 0.08, 0.032, 1.185), (0.03, 0.003, 0.012), rz=ang)
    P.box(M["steel"], at(0.25, -0.03, hd - 0.04), (0.35, 0.02, 0.03), rz=ang)


def _accessible_basin(P, x, top=0.8):
    """Wall-hung accessible washbasin in white vitreous china (550 x 450, rim at 0.8, 120 mm thin body so a wheelchair rolls
    under it): a rounded front, a real bowl (a sunken oval with a drain), a tap ledge at the back with a long-lever single
    mixer (operable with a fist), the trap tucked against the wall."""
    w, d, t = 0.55, 0.45, 0.12
    b = P.bm(M["ceramic"]); n = 48
    def oval(rx, ry, cy, z):
        return [b.verts.new((x + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n), z)) for k in range(n)]
    outer_t = oval(w / 2, d / 2, d / 2, top); outer_b = oval(w / 2 - 0.02, d / 2 - 0.02, d / 2, top - t)
    inner_t = oval(0.2, 0.15, d / 2 + 0.03, top); inner_b = oval(0.15, 0.1, d / 2 + 0.03, top - 0.1)
    for A, B in ((outer_b, outer_t), (inner_t, inner_b)):
        for k in range(n):
            b.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    for k in range(n):  # the rim between the outer edge and the bowl
        b.faces.new((outer_t[k], outer_t[(k + 1) % n], inner_t[(k + 1) % n], inner_t[k]))
    b.faces.new(outer_b[::-1]); b.faces.new(inner_b[::-1])
    P.box(M["ceramic"], (x, 0.03, top - 0.06), (w - 0.1, 0.06, t))                 # back: fixes to the wall
    P.cyl(M["steel"], (x, d / 2 + 0.03, top - 0.099), 0.025, 0.002, seg=16)         # drain
    P.cyl(M["steel"], (x, 0.07, top), 0.022, 0.12, seg=20)                          # mixer body on the ledge
    P.rod(M["steel"], (x, 0.07, top + 0.11), (x, 0.17, top + 0.09), 0.01, seg=10)   # spout
    P.rod(M["steel"], (x + 0.02, 0.07, top + 0.12), (x + 0.17, 0.09, top + 0.13), 0.007, seg=8)  # long lever
    P.cyl(M["steel"], (x, 0.08, top - 0.32), 0.022, 0.2, seg=16)                    # trap, close to the wall


def wc_run(P, cells=((1.1, "wc"),), depth=1.8, h=2.73, open_=(), occupied=(), pan_side=-1):
    """One continuous run of WC cells against a wall (Roman: flush to each other and to the walls, no slivers, doors all on one
    face, opening OUTWARD). Origin = wall face at the run's centre, cells along x, front towards +y. 30 mm oak panels at every
    boundary incl. both ends, an oak lid at the ceiling, one front face of fluted oak with a shadow-gapped door per cell.
    cells: (width, style) with style 'wc' (0.8 door), 'accessible' (1.0 door, TEK17 kit), 'store' (cleaner's closet).
    open_: indices of cells whose door stands open (100 deg out), occupied: indices showing red. Every interior fully fitted."""
    W = sum(c[0] for c in cells)
    M.setdefault("led_free", bc.material("led_free", (0.02, 0.45, 0.1), 0.3, emit=((0.05, 1.0, 0.2), 0.5)))
    M.setdefault("led_busy", bc.material("led_busy", (0.6, 0.02, 0.01), 0.3, emit=((1.0, 0.05, 0.02), 0.5)))
    paper = M.setdefault("paper_white", bc.material("paper_white", (0.86, 0.85, 0.82), 0.8))
    bounds, x = [], -W / 2
    for c in cells:
        bounds.append((x, x + c[0])); x += c[0]
    for xb in [b[0] for b in bounds] + [W / 2]:
        P.box(M["oak"], (min(max(xb, -W / 2 + 0.015), W / 2 - 0.015), depth / 2, h / 2), (0.03, depth, h))
    P.box(M["oak"], (0, depth / 2, h + 0.01), (W, depth, 0.02))
    yf = depth - 0.02                                      # the front face plane (40 mm thick front)
    hd = 2.1
    for i, ((a, b), (w, style)) in enumerate(zip(bounds, cells)):
        dw = {"wc": 0.8, "accessible": 1.0, "store": w - 0.16}[style]
        if style == "accessible":
            edge, d = (a, 1) if pan_side < 0 else (b, -1)
            dc = edge + d * 1.8                            # door away from the WC, toward the far side
        else:
            dc = (a + b) / 2
        da, db = dc - dw / 2, dc + dw / 2
        for (u0, u1, z0, z1) in ((a + 0.015, da - 0.003, 0, h), (db + 0.003, b - 0.015, 0, h), (da - 0.003, db + 0.003, hd + 0.003, h)):
            if u1 - u0 > 0.005:
                P.box(M["oak"], ((u0 + u1) / 2, yf, (z0 + z1) / 2), (u1 - u0, 0.04, z1 - z0))
                for xg in np.arange(u0 + 0.015, u1, 0.03):
                    P.box(M["felt"], (xg, yf + 0.0205, (z0 + z1) / 2), (0.003, 0.002, z1 - z0 - 0.02))
        P.box(M["felt"], (dc, yf, hd + 0.0015), (dw + 0.006, 0.042, 0.003))       # shadow gap at the head
        P.box(M["oak"], (da - 0.004, yf, hd / 2), (0.005, 0.042, hd))           # frame lips (the gap reads dark between)
        P.box(M["oak"], (db + 0.004, yf, hd / 2), (0.005, 0.042, hd))
        _leaf(P, (da, yf), dw, hd, math.radians(100) if i in open_ else 0.0, occupied=i in occupied)
        if style == "accessible":  # pictograms on the transom face over the door: accessible + baby changing
            pictogram_on(P, "accessible", dc - 0.11, yf + 0.02, hd + 0.3, 0.18, plate=True)
            pictogram_on(P, "baby", dc + 0.11, yf + 0.02, hd + 0.3, 0.18, plate=True)
        cx = (a + b) / 2
        if style == "wc":
            _wc_pan(P, cx)
            P.rod(paper, (cx + 0.39, 0.12, 0.75), (cx + 0.5, 0.12, 0.75), 0.055, seg=20)           # the roll on its holder
            _brush(P, (cx - 0.36, 0.1))
            _pedal_bin(P, (cx + 0.36, 0.16), h=0.3, r=0.09)                                        # sanitary bin
            P.box(M["oak"], (b - 0.1, 0.7, 1.05), (0.15, 0.3, 0.02))                              # shelf on the panel (phone, bag)
            P.box(paper, (b - 0.1, 0.62, 1.1), (0.11, 0.11, 0.1))                                  # spare roll on it
            P.rod(M["steel"], (a + 0.015, 1.1, 1.7), (a + 0.08, 1.1, 1.72), 0.01, seg=8)          # coat hook
            P.box(M["steel"], (cx, 0.004, 1.42), (0.12, 0.008, 0.08))                              # small hygiene dispenser (seat cleaner)
        elif style == "accessible":
            px = edge + d * 0.5                                                                    # WC centre 0.5 from the side wall
            _wc_pan(P, px)
            P.rod(paper, (px + 0.39, 0.12, 0.75), (px + 0.5, 0.12, 0.75), 0.055, seg=20) if d > 0 else P.rod(paper, (px - 0.5, 0.12, 0.75), (px - 0.39, 0.12, 0.75), 0.055, seg=20)
            P.rod(M["steel"], (edge + d * 0.035, 0.25, 0.8), (edge + d * 0.035, 1.0, 0.8), 0.017, seg=12)   # fixed rail on the side wall
            P.rod(M["steel"], (edge + d * 0.035, 0.25, 0.8), (edge + d * 0.035, 0.25, 1.5), 0.017, seg=12)  # + vertical
            fx = px + d * 0.35                                                                     # fold-up rail on the open side
            P.box(M["steel"], (fx, 0.03, 0.8), (0.07, 0.06, 0.16)); P.rod(M["steel"], (fx, 0.05, 0.8), (fx, 0.85, 0.8), 0.017, seg=12)
            bx = edge + d * 1.95                                                                   # accessible washbasin, knee space under it
            _accessible_basin(P, bx)
            P.box(M["oak"], (bx, 0.012, 1.45), (0.54, 0.024, 0.84)); P.box(M["mirror"], (bx, 0.026, 1.45), (0.5, 0.004, 0.8))
            _soap(P, bx - d * 0.32, 0.0, 1.05)
            fp = edge + d * 2.385                                                                  # the far side panel's face
            P.box(M["oak"], (fp - d * 0.03, 0.4, 1.25), (0.06, 0.36, 0.42)); P.box(M["steel"], (fp - d * 0.065, 0.4, 1.25), (0.012, 0.3, 0.36))  # towels
            _pedal_bin(P, (fp - d * 0.2, 0.75), h=0.42, r=0.12)
            P.box(M["oak"], (fp - d * 0.06, 1.25, 0.95), (0.11, 0.8, 0.55))                        # fold-down changing table (folded)
            _brush(P, (edge + d * 0.15, 0.12))
            _pedal_bin(P, (edge + d * 1.05, 0.15), h=0.3, r=0.09)
            # emergency alarm (TEK17): a pull switch high on the side wall beside the WC, its red cord running down the wall face
            # (5 cm off it) with two red pull bangles, one within reach from the WC (0.9) and one near the floor (0.1) for a fall;
            # the red reset/acknowledge button + a small amber 'alarm' light by the door inside
            cxw, cyw = edge + d * 0.04, 1.2
            P.box(M["ceramic"], (cxw, cyw, 2.3), (0.03, 0.08, 0.08))
            P.rod(M["lino_lingon"], (cxw + d * 0.02, cyw, 2.26), (cxw + d * 0.02, cyw, 0.1), 0.0025, seg=6)
            for z in (0.1, 0.9):
                P.cyl(M["lino_lingon"], (cxw + d * 0.02, cyw, z - 0.02), 0.025, 0.04, seg=16)
            P.box(M["ceramic"], (edge + d * 2.0, depth - 0.07, 1.0), (0.08, 0.02, 0.08))
            b2 = P.bm(M["lino_lingon"]); g2 = bmesh.ops.create_cone(b2, cap_ends=True, segments=20, radius1=0.022, radius2=0.022, depth=0.01)["verts"]
            bmesh.ops.rotate(b2, verts=g2, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X")); bmesh.ops.translate(b2, verts=g2, vec=(edge + d * 2.0, depth - 0.085, 1.0))
            P.rod(M["steel"], (fp, 1.5, 1.7), (fp - d * 0.08, 1.5, 1.72), 0.01, seg=8)             # coat hook
        else:  # cleaner's closet: slop sink, shelves, mops, bottles, a cart
            P.box(M["brushed"], (a + 0.35, 0.22, 0.3), (0.5, 0.4, 0.3))
            P.rod(M["steel"], (a + 0.35, 0.0, 0.85), (a + 0.35, 0.18, 0.85), 0.012, seg=10)
            for z in (1.2, 1.55, 1.9):
                P.box(M["oak"], (b - 0.4, 0.15, z), (0.65, 0.28, 0.02))
                for k in range(4):
                    P.cyl(M["lino_" + COLOURS[(k + int(z * 10)) % 5]], (b - 0.65 + k * 0.15, 0.15, z + 0.01), 0.035, 0.2, seg=12)
            for k in range(3):
                P.rod(M["oak"], (a + 0.75 + k * 0.1, 0.06, 0.05), (a + 0.75 + k * 0.1, 0.06, 1.4), 0.012, seg=8)
                P.box(M["felt_oat"], (a + 0.75 + k * 0.1, 0.06, 0.08), (0.06, 0.04, 0.12))


def vanity(P, L=3.0, n=3, top=0.86):
    """Honed-stone trough vanity on the wall: 120 mm slab, top at 0.86, 0.5 deep, n basins sunk into it; wall-mounted
    blackened-steel spouts; a full-length mirror (1.0 tall) in a slim oak frame; a slim steel light channel above it."""
    d, t = 0.5, 0.12
    bw = 0.48
    xs = [-L / 2 + (k + 0.5) * L / n for k in range(n)]
    cuts = sorted([-L / 2, L / 2] + [v for x in xs for v in (x - bw / 2, x + bw / 2)])
    for a, b_ in zip(cuts[::2], cuts[1::2]):  # solid stone between the basins
        P.box(M["stone"], ((a + b_) / 2, d / 2, top - t / 2), (b_ - a, d, t))
    for x in xs:
        P.box(M["stone"], (x, 0.06, top - t / 2), (bw, 0.12, t))          # back strip
        P.box(M["stone"], (x, d - 0.04, top - t / 2), (bw, 0.08, t))      # front lip
        P.box(M["stone"], (x, 0.24, top - t - 0.03), (bw, 0.3, 0.06))     # basin floor, 150 mm below the top
        P.rod(M["steel"], (x, 0.0, top + 0.16), (x, 0.17, top + 0.16), 0.011, seg=12)        # spout
        P.rod(M["steel"], (x + 0.12, 0.0, top + 0.16), (x + 0.12, 0.05, top + 0.16), 0.009, seg=10)  # lever
        _soap(P, x - 0.17, 0.0, top + 0.18)
    P.box(M["oak"], (0, 0.012, top + 0.25 + 0.52), (L + 0.03, 0.022, 1.04))   # oak frame behind the mirror
    P.box(M["mirror"], (0, 0.025, top + 0.25 + 0.52), (L - 0.02, 0.006, 1.0))
    P.box(M["steel"], (0, 0.04, top + 1.37), (L, 0.06, 0.04))                 # light channel above the mirror
    P.box(M["opal"], (0, 0.04, top + 1.349), (L - 0.04, 0.05, 0.003))


def _nautilus(P, x, rim=0.62):
    """Splash-free urinal after the 'Nautilus' study (Pan, Thurairajah et al., U. Waterloo 2022; PNAS Nexus): a tall, slender
    vitreous-china shell whose inner back wall follows a nautilus (logarithmic) curve, so the stream meets it at under ~30 deg
    (the critical angle below which almost nothing splashes back) for any height or aim; a narrow front opening, the lip at
    'rim'. Built as a loft of U-shaped sections: depth and width follow the spiral from the floor trap up to the hood."""
    b = P.bm(M["ceramic"]); n = 40
    lip = rim - 0.06
    rings = []
    for j in range(17):
        u = j / 16
        z = 0.2 + (rim + 0.6 - 0.2) * u
        depth = 0.14 + 0.22 * math.sin(math.pi * min(1.0, u * 1.1)) ** 0.8   # the belly where the stream lands (shallow angle)
        half = 0.12 + 0.07 * math.sin(math.pi * u) ** 0.7
        ring = [b.verts.new((x + half * math.cos(2 * math.pi * k / n), 0.02 + depth / 2 + depth / 2 * math.sin(2 * math.pi * k / n), z)) for k in range(n)]
        rings.append((ring, z))
    for (A, za), (B, zb) in zip(rings, rings[1:]):
        for k in range(n):
            am = 2 * math.pi * (k + 0.5) / n
            front = abs(((am - math.pi / 2) + math.pi) % (2 * math.pi) - math.pi) < math.radians(55)
            if front and za >= lip:
                continue  # the narrow front opening above the lip
            b.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    b.faces.new(rings[0][0][::-1])
    P.box(M["ceramic"], (x, 0.03, 0.55), (0.32, 0.04, 0.95))                       # back plate on the wall
    P.cyl(M["steel"], (x, 0.12, 0.23), 0.025, 0.004, seg=16)                        # trap grate
    P.box(M["steel"], (x, 0.004, rim + 0.62), (0.08, 0.008, 0.12))                  # touch-free flush sensor


def urinals(P, n=3, pitch=0.85):
    """Splash-free 'Nautilus' urinals (one lower, rim 0.5, for children) with tall oak privacy screens on both sides of every one,
    the end ones included (Roman 2026-10-18) (0.45 deep, 0.4 to 1.6 m: you see a screen, never a neighbour) on blackened-steel brackets."""
    for k in range(n):
        x = -(n - 1) * pitch / 2 + k * pitch
        _nautilus(P, x, rim=0.5 if k == 0 else 0.62)
    for k in range(n + 1):
        x = -n * pitch / 2 + k * pitch
        P.box(M["oak"], (x, 0.28, 1.0), (0.025, 0.5, 1.2))
        for z in (0.55, 1.45):
            P.box(M["steel"], (x, 0.02, z), (0.04, 0.04, 0.04))


def cell_light(P, z_ceiling=2.6):
    """Small opal disc under a WC cell lid."""
    P.cyl(M["steel"], (0, 0, z_ceiling - 0.012), 0.06, 0.012, seg=24)
    P.cyl(M["opal"], (0, 0, z_ceiling - 0.014), 0.05, 0.003, seg=24)


# ------------------------------------------------------------------ daycare (VISION "Daycare: playful, still Nordic", Roman 2026-10-12)
def kid_wc_cells(P, n=4, w=0.85, depth=1.2):
    """Children's WCs: low oak screens (1.2 m, staff can see over) with half-height doors in coloured linoleum, oak-edged;
    small wall-hung pans (seat 0.33), a low flush plate. Origin = wall face at the row centre, front +y."""
    W, h = n * w, 1.2
    for k in range(n + 1):
        P.box(M["oak"], (-W / 2 + k * w, depth / 2, 0.15 + h / 2), (0.025, depth, h))
    for k in range(n):
        cx = -W / 2 + (k + 0.5) * w
        c = COLOURS[k % len(COLOURS)]
        P.box(M["lino_" + c], (cx, depth, 0.2 + 0.45), (w - 0.06, 0.02, 0.9))          # half-height door
        P.box(M["oak"], (cx, depth, 1.11), (w - 0.06, 0.025, 0.02))                    # oak top edge
        P.cyl(M["oak"], (cx + w / 2 - 0.12, depth + 0.012, 0.75), 0.03, 0.02, seg=20)  # round oak knob
        P.box(M["ceramic"], (cx, 0.08, 0.28), (0.3, 0.16, 0.16))
        P.blob(M["ceramic"], (cx, 0.26, 0.25), (0.14, 0.2, 0.09), z_cut=0.18)
        P.box(M["ceramic"], (cx, 0.26, 0.33), (0.3, 0.36, 0.018))
        P.box(M["steel"], (cx, 0.004, 0.75), (0.2, 0.008, 0.13))
        P.rod(M["steel"], (cx + 0.25, 0.0, 0.55), (cx + 0.25, 0.09, 0.55), 0.008, seg=8)  # low roll holder
        P.cyl(M["steel"], (cx - w / 2 + 0.06, 0.08, 0.95), 0.035, 0.3, seg=16)  # brush in a wall cup, out of reach


def changing_unit(P, L=1.8):
    """Nappy changing unit, 0.9 high x 0.8 deep in oak: a wipeable oat pad with a raised oak rim, a small sink with a hand
    shower at one end, and pull-out oak steps at the other so toddlers climb up themselves (saves the staff's backs)."""
    d = 0.8
    P.box(M["oak"], (0, d / 2, 0.45), (L, d, 0.9))
    P.box(M["pad"], (-0.15, d / 2, 0.93), (L - 0.65, d - 0.1, 0.06))
    for y in (0.04, d - 0.04):
        P.box(M["oak"], (-0.15, y, 0.98), (L - 0.65, 0.04, 0.1))
    P.box(M["stone"], (L / 2 - 0.25, d / 2, 0.91), (0.5, d, 0.03))
    P.box(M["ceramic"], (L / 2 - 0.25, d / 2, 0.895), (0.36, 0.4, 0.02))
    P.rod(M["steel"], (L / 2 - 0.25, 0.0, 1.2), (L / 2 - 0.25, 0.2, 1.2), 0.012, seg=10)
    P.rod(M["steel"], (L / 2 - 0.08, 0.02, 0.95), (L / 2 - 0.08, 0.02, 1.45), 0.01, seg=10)   # hand shower on its rail
    _pedal_bin(P, (L / 2 + 0.25, 0.3), h=0.62, r=0.16, lid=M["steel"])  # sealed nappy bin at the sink end
    P.box(M["oak"], (-0.1, 0.06, 1.55), (1.1, 0.12, 0.025))            # shelf above: wipes, creams
    for k, x in enumerate((-0.5, -0.25, 0.0)):
        P.box(M["lino_" + COLOURS[k]], (x, 0.07, 1.6), (0.2, 0.1, 0.07))
    for x, c in ((0.25, "oat"), (0.38, "fjord")):                      # glove boxes in a steel wall holder
        P.box(M["steel"], (x, 0.05, 1.3), (0.12, 0.1, 0.26))
        P.box(M["felt_" + c], (x, 0.101, 1.32), (0.1, 0.004, 0.06))
    P.rod(M["steel"], (-0.75, 0.05, 1.25), (-0.15, 0.05, 1.25), 0.012, seg=10)   # disposable liner roll on a rail
    b = P.bm(M["pad"]); g = bmesh.ops.create_cone(b, cap_ends=True, segments=24, radius1=0.05, radius2=0.05, depth=0.5)["verts"]
    bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y")); bmesh.ops.translate(b, verts=g, vec=(-0.45, 0.06, 1.25))
    _soap(P, L / 2 - 0.45, 0.0, 1.15)
    for k in range(3):  # steps out of the left end
        P.box(M["oak"], (-L / 2 - 0.15 - k * 0.0, d / 2 + 0.25 + k * 0.0, 0.11 + k * 0.25), (0.3, 0.6 - k * 0.12, 0.04))
        P.box(M["oak"], (-L / 2 - 0.15, d / 2 + 0.25 - (0.3 - k * 0.06) + 0.02, 0.06 + k * 0.125), (0.3, 0.03, 0.12 + k * 0.25))


def cubbies(P, L=3.4, n=8):
    """Wardrobe cubbies, one per child: an oak frame 1.75 high, 0.4 deep; a slatted bench at 0.3 with boot slots under it,
    a coloured felt back in each cubby (each child 'has a colour'), two steel pegs, a hat shelf at 1.45 and a box on top."""
    d, H = 0.4, 1.75
    w = L / n
    P.box(M["oak"], (0, d / 2, 0.02), (L, d, 0.04))
    for k in range(n + 1):
        P.box(M["oak"], (-L / 2 + k * w, d / 2, H / 2), (0.022, d, H))
    for z in (0.3, 1.45, H):
        P.box(M["oak"], (0, d / 2, z), (L, d, 0.022))
    for x in np.arange(-L / 2 + 0.03, L / 2 - 0.02, 0.06):   # bench slats over the boot slots
        P.box(M["oak"], (x, d / 2 + 0.02, 0.32), (0.045, d - 0.04, 0.025))
    for k in range(n):
        cx = -L / 2 + (k + 0.5) * w
        c = COLOURS[(k * 2) % len(COLOURS)]
        P.box(M["felt_" + c], (cx, 0.012, 0.88), (w - 0.03, 0.012, 1.13))
        for dx in (-0.09, 0.09):
            P.rod(M["steel"], (cx + dx, 0.02, 1.1), (cx + dx, 0.12, 1.14), 0.009, seg=8)
        P.box(M["felt_" + COLOURS[(k * 2 + 1) % len(COLOURS)]], (cx, d / 2, 1.58), (w - 0.06, d - 0.08, 0.24))  # a felt box on the hat shelf
        P.cyl(M["oak"], (cx, d + 0.001, 1.38), 0.035, 0.004, seg=16)  # a little round name tag


def drying_cabinet(P):
    """Drying cabinet for wet outdoor gear (tørkeskap): tall oak cabinet 0.6 x 0.6 x 1.9, vent slats at the top, steel pull."""
    P.box(M["oak"], (0, 0.3, 0.95), (0.6, 0.6, 1.9))
    for z in np.arange(1.72, 1.86, 0.03):
        P.box(M["felt"], (0, 0.601, z), (0.5, 0.004, 0.012))
    P.box(M["steel"], (0.24, 0.62, 1.0), (0.02, 0.03, 0.4))


def kid_table(P, colour="cloud", d=1.2, h=0.58):
    """Round table at child height: coloured linoleum top in a thick rounded oak edge, four splayed oak legs."""
    P.cyl(M["oak"], (0, 0, h - 0.035), d / 2, 0.035, seg=64)
    P.cyl(M["lino_" + colour], (0, 0, h), d / 2 - 0.03, 0.002, seg=64)
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        P.rod(M["oak"], (ca * 0.42, sa * 0.42, 0), (ca * 0.3, sa * 0.3, h - 0.035), 0.022, 0.03, seg=12)


def kid_chair(P, colour="fjord", seat=0.32):
    """Child's chair (seat 0.32; toddler size 0.22): oak frame, a round-ended oak back hoop, a coloured wool felt seat pad."""
    s, h = 0.3 * (0.85 if seat < 0.3 else 1.0), seat
    legs4(P, M["oak"], s, s, h, inset=0.03, r0=0.016, r1=0.012, splay=0.015)
    P.box(M["oak"], (0, 0, h), (s, s, 0.022))
    P.box(M["felt_" + colour], (0, 0.01, h + 0.02), (s - 0.03, s - 0.04, 0.025))
    for x in (-s / 2 + 0.03, s / 2 - 0.03):
        P.rod(M["oak"], (x, -s / 2 + 0.03, h), (x, -s / 2 + 0.01, h + 0.28), 0.012, seg=10)
    P.box(M["oak"], (0, -s / 2 + 0.01, h + 0.24), (s, 0.02, 0.08))


def play_loft(P, L=4.0, D=2.6, deck=1.6):
    """The 'tree house': an oak play loft against the forest glass. A deck at 1.6 m on four oak posts, oak slat guards 1.1 high
    (vertical, 80 mm gaps, nothing to climb), a gable 'house' frame of oak over it (the drawn-house silhouette every child knows)
    with a felt pennant line, a stair with a handrail up the right end, a slide down the left end, and a den underneath with
    cushions. Origin = front centre on the floor; the glass is behind (-y), the room in front (+y)."""
    y0, y1 = -D, 0.0
    for x in (-L / 2 + 0.06, L / 2 - 0.06):
        for y in (y0 + 0.06, y1 - 0.06):
            P.box(M["oak"], (x, y, (deck + 2.0) / 2), (0.1, 0.1, deck + 2.0))  # posts run up to carry the gable
    P.box(M["oak"], (0, (y0 + y1) / 2, deck - 0.05), (L, D, 0.1))
    for x in np.arange(-L / 2 + 0.06, L / 2, 0.11):  # guards front + back
        for y in (y0 + 0.03, y1 - 0.03):
            if y == y1 - 0.03 and (x > L / 2 - 0.85 or x < -L / 2 + 0.75):
                continue  # stair landing + slide openings
            P.box(M["oak"], (x, y, deck + 0.55), (0.03, 0.03, 1.1))
    for y in np.arange(y0 + 0.06, y1, 0.11):
        for x in (-L / 2 + 0.03, L / 2 - 0.03):
            P.box(M["oak"], (x, y, deck + 0.55), (0.03, 0.03, 1.1))
    for y in (y0 + 0.03, y1 - 0.03):
        P.box(M["oak"], (0, y, deck + 1.12), (L, 0.06, 0.04))
    # gable: two pitched rafters per end + a ridge (the house outline), 45 degrees
    eave, rise_ = deck + 2.0, 1.0  # gable top 4.6 m, under the wave ceiling (5.3)
    for y in (y0 + 0.06, y1 - 0.06):
        apex = (0, y, eave + rise_)
        for x in (-L / 2 + 0.06, L / 2 - 0.06):
            P.rod(M["oak"], (x, y, eave), apex, 0.05, seg=4)
        P.box(M["oak"], (0, y, eave), (L, 0.1, 0.1))
    P.box(M["oak"], (0, (y0 + y1) / 2, eave + rise_), (0.1, D, 0.1))
    for k in range(9):  # felt pennants on a cord under the front rafters
        x = -L / 2 + 0.5 + k * (L - 1.0) / 8
        z = eave + rise_ * (1 - abs(x) / (L / 2)) - 0.25
        P.box(M["felt_" + COLOURS[k % 5]], (x, y1 - 0.06, z), (0.18, 0.01, 0.2))
    # stair up the right end (9 risers 0.178, 0.25 going), towards +y, oak, with a low handrail
    n = 9
    for k in range(n):
        P.box(M["oak"], (L / 2 - 0.4, y1 + 0.25 * (n - k) - 0.125, (k + 1) * deck / n - 0.02), (0.7, 0.26, 0.04))
    for x in (L / 2 - 0.77, L / 2 - 0.03):
        P.rod(M["oak"], (x, y1 + 0.25 * n, 0.65), (x, y1, deck + 0.65), 0.022, seg=12)
        P.box(M["oak"], (x, y1 + 0.125 * n, deck / 2), (0.04, 0.25 * n * 1.0, 0.04), rx=-math.atan2(deck, 0.25 * n))
    # slide down the left end: a stainless chute in an oak cheek, out towards +y
    run = 2.6
    ang = math.atan2(deck - 0.25, run)
    # high end at the deck edge, falling away from it (rx < 0 tips the far end down), then a flat run-out at 0.25 to land on
    P.box(M["brushed"], (-L / 2 + 0.38, y1 + run / 2, (deck + 0.25) / 2), (0.5, run / math.cos(ang), 0.02), rx=-ang)
    for x in (-L / 2 + 0.1, -L / 2 + 0.66):
        P.box(M["oak"], (x, y1 + run / 2, (deck + 0.25) / 2 + 0.12), (0.03, run / math.cos(ang), 0.25), rx=-ang)
        P.box(M["oak"], (x, y1 + run + 0.2, 0.25 + 0.06), (0.03, 0.4, 0.25))
        P.box(M["oak"], (x, y1 + run + 0.38, 0.09), (0.05, 0.05, 0.18))  # a short leg under the run-out
    P.box(M["brushed"], (-L / 2 + 0.38, y1 + run + 0.2, 0.25), (0.5, 0.4, 0.02))
    # the den underneath: floor cushions + a felt curtain at the back
    for k, (x, c) in enumerate(zip((-1.1, -0.2, 0.7), ("moss", "heather", "fjord"))):
        P.blob(M["felt_" + c], (x, -D / 2, 0.11), (0.38, 0.34, 0.11), z_cut=0.0)
    P.box(M["felt_oat"], (0, y0 + 0.12, deck / 2 - 0.05), (L - 0.3, 0.02, deck - 0.2))


def stair_guard(P, r_in=0.92, r_out=2.55, rise=-6.13, risers=35, step_deg=15.0, a0=90.0, gap=(233.0, 262.0), h=1.2, gaps=None, gates=()):
    """Child-safe guards for the open round stair (daycare): a guard round the floor opening (oak staves 30 @ 90 = 60 mm gaps,
    1.2 m, an oak kerb ring hiding the floor edge, a steel top rail), the way on to the top tread left open; and an oak-staved
    balustrade up both edges of the helix (outer + round the open eye), with a handrail at 0.9 and a child rail at 0.6.
    Origin = stair centre at the upper floor; z goes down to the lower floor (rise)."""
    R = r_out + 0.07
    gaps = [tuple(g) for g in (gaps or [gap])]
    in_gap = lambda a: any(g0 <= a % 360 <= g1 for g0, g1 in gaps)
    P.ring(M["oak"], (0, 0), r_out - 0.005, r_out + 0.25, -0.02, 0.1, seg=192)
    na = int(2 * math.pi * R / 0.09)
    for k in range(na):
        a = 360 * k / na
        if in_gap(a):
            continue
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        P.box(M["oak"], (R * ca, R * sa, 0.1 + (h - 0.1) / 2), (0.03, 0.03, h - 0.1), rz=math.radians(a))
    gs = sorted(gaps)
    for (g0, g1), (n0, n1) in zip(gs, gs[1:] + [(gs[0][0] + 360, 0)]):  # top rail between the gaps
        P.ring(M["steel"], (0, 0), R - 0.025, R + 0.025, h, h + 0.04, a0=g1, a1=n0, seg=192)
    # helix balustrades: a stave every 90 mm along each edge, rails as short chords
    for rad in (r_out - 0.06, r_in + 0.06):
        prev = None
        steps = int(risers * step_deg * math.pi / 180 * rad / 0.09)
        for j in range(steps + 1):
            t = j / steps
            a = math.radians(a0 + step_deg * risers * t)
            k = min(risers - 1, int(t * risers))
            zt = rise + (-rise) * (k + 1) / risers  # tread top, counted up from the lower floor
            x, y = rad * math.cos(a), rad * math.sin(a)
            gate = rad < r_out - 0.5 and next((g for g in gates if abs(math.degrees(a) - g) * math.pi / 180 * rad < 0.3), None)
            if gate is not None and gate is not False:
                prev = None
                continue
            P.box(M["oak"], (x, y, zt + 0.45), (0.03, 0.03, 0.9), rz=a)
            top = (x, y, zt + 0.9)
            if prev is not None:
                P.rod(M["steel"], prev, top, 0.02, seg=8)
            prev = top
    for g in gates:  # rescue gates in the inner balustrade (hinged oak panels, a red latch an adult can reach, children can't)
        a = math.radians(g); rad = r_in + 0.06
        k = min(risers - 1, int((g - a0) / step_deg)); zt = rise + (-rise) * (k + 1) / risers
        ca, sa = math.cos(a), math.sin(a); tx, ty = -sa, ca
        for d in (-0.28, 0.28):
            P.box(M["oak"], (rad * ca + tx * d, rad * sa + ty * d, zt + 0.45), (0.04, 0.04, 0.9), rz=a)
        for dz in (0.05, 0.9):
            P.box(M["oak"], (rad * ca, rad * sa, zt + dz), (0.04, 0.6, 0.04), rz=a)
        for d in np.arange(-0.22, 0.25, 0.09):
            P.box(M["oak"], (rad * ca + tx * d, rad * sa + ty * d, zt + 0.47), (0.025, 0.025, 0.82), rz=a)
        P.box(M["lino_lingon"], (rad * ca + tx * 0.24 + ca * 0.03, rad * sa + ty * 0.24 + sa * 0.03, zt + 0.88), (0.04, 0.05, 0.06), rz=a)


def felt_cloud(P, colour="oat", s=1.0, hang=3.6, ceiling=5.3):
    """Acoustic cloud: three overlapping discs of 40 mm wool felt (a soft cloud outline) on thin steel cables."""
    for (dx, dy, r) in ((-0.45, 0.0, 0.55), (0.25, 0.12, 0.7), (0.85, -0.05, 0.45)):
        P.cyl(M["felt_" + colour], (dx * s, dy * s, hang), r * s, 0.04, seg=48)
    for dx in (-0.5, 0.3, 0.9):
        P.rod(M["steel"], (dx * s, 0, hang + 0.04), (dx * s, 0, ceiling), 0.0015, seg=4)


def soft_play(P):
    """Toddler soft-play landscape on a round oat mat: wool-felt covered foam steps (3 tiers), a ramp, a half-round hump
    and a low arch to crawl through, all with soft (30 mm) radii."""
    P.cyl(M["felt_oat"], (0, 0, 0.0), 1.9, 0.04, seg=96)
    P.box(M["felt_moss"], (-0.9, 0.5, 0.15), (0.9, 0.9, 0.3))
    P.box(M["felt_moss"], (-0.9, 0.85, 0.35), (0.9, 0.3, 0.1))  # the top tier
    P.box(M["felt_cloud"], (-0.9, -0.25, 0.1), (0.9, 0.6, 0.2))
    P.box(M["felt_fjord"], (0.25, 0.75, 0.2), (1.2, 0.45, 0.4), rx=0.0)
    P.box(M["felt_heather"], (0.3, 0.2, 0.08), (1.1, 0.6, 0.12), rx=0.25)  # ramp
    P.blob(M["felt_lingon"], (0.9, -0.7, 0.04), (0.5, 0.35, 0.28), z_cut=0.04)
    P.ring(M["felt_cloud"], (0, -0.8), 0.32, 0.55, -0.15, 0.15, seg=48)  # the arch, set on edge below
    for k in range(4):
        P.blob(M["felt_" + COLOURS[k]], (-1.3 + k * 0.6, -1.35, 0.12), (0.16, 0.16, 0.16))


def low_shelf(P, L=3.8, h=0.8, books=True):
    """Low oak shelving (0.8 m, 0.35 deep), open both sides, with face-out picture books on two ledges: the soft line
    between the kids' and the toddlers' zones. Books in palette colours."""
    d = 0.35
    for z in (0.04, 0.4, h):
        P.box(M["oak"], (0, 0, z), (L, d, 0.025))
    for x in np.arange(-L / 2, L / 2 + 0.01, L / max(1, round(L / 0.8))):
        P.box(M["oak"], (x, 0, h / 2), (0.025, d, h))
    if books:
        rng = np.random.default_rng(3)
        for k, x in enumerate(np.arange(-L / 2 + 0.2, L / 2 - 0.1, 0.32)):
            for z, side in ((0.06, 1), (0.42, -1)):
                c = COLOURS[int(rng.integers(0, 5))]
                P.box(M["lino_" + c], (x, side * 0.1, z + 0.12), (0.24, 0.02, 0.24), rx=side * 0.12)


def gate(P, w=0.9, h=0.8):
    """Low oak gate between the zones: vertical staves 60 mm apart, a toddler-proof latch high on the frame."""
    for x in np.arange(-w / 2 + 0.03, w / 2, 0.09):
        P.box(M["oak"], (x, 0, h / 2 + 0.03), (0.03, 0.03, h - 0.06))
    for z in (0.05, h):
        P.box(M["oak"], (0, 0, z), (w, 0.04, 0.05))
    P.box(M["steel"], (w / 2 - 0.05, 0.03, h - 0.06), (0.06, 0.02, 0.08))


def story_wall(P, L=4.4, h=2.6):
    """Freestanding 'story wall' at the edge of the kids' zone: a 120 mm oak-framed panel, the forest painting on the front
    (the canvas is its own piece), low face-out bookshelves and a felt pin board on the back (towards the toddlers)."""
    P.box(M["oak"], (0, 0.0, h / 2), (L, 0.12, h))
    for x in (-L / 2 + 0.3, L / 2 - 0.3):
        P.box(M["oak"], (x, 0, 0.03), (0.08, 0.6, 0.06))  # feet
    P.box(M["felt_oat"], (0, -0.065, 1.55), (L - 0.4, 0.01, 0.9))
    for z in (0.08, 0.5):
        P.box(M["oak"], (0, -0.2, z), (L - 0.2, 0.28, 0.025))
        P.box(M["oak"], (0, -0.33, z + 0.05), (L - 0.2, 0.02, 0.08))
        for k, x in enumerate(np.arange(-L / 2 + 0.3, L / 2 - 0.2, 0.34)):
            P.box(M["lino_" + COLOURS[(k + int(z * 10)) % 5]], (x, -0.12, z + 0.14), (0.26, 0.02, 0.26), rx=-0.15)


def floor_cushion(P, colour="moss", r=0.35):
    P.blob(M["felt_" + colour], (0, 0, 0.1), (r, r, 0.11), z_cut=0.0)


def rug_round(P, d=2.2, colour="oat"):
    P.cyl(M["felt_" + colour], (0, 0, 0.0), d / 2, 0.012, seg=96)


def kitchenette(P, L=2.4):
    """Staff kitchenette: oak base units 0.9 high, light stone top, a steel sink + tap, an oak tall unit (fridge) at one end,
    an open oak shelf above."""
    d = 0.6
    P.box(M["oak"], (-0.3, d / 2, 0.44), (L - 0.6, d - 0.02, 0.88))
    P.box(M["stone"], (-0.3, d / 2, 0.9), (L - 0.6, d, 0.03))
    P.box(M["brushed"], (0.0, d / 2, 0.905), (0.5, 0.38, 0.02))
    P.rod(M["steel"], (0.0, 0.08, 0.915), (0.0, 0.08, 1.2), 0.012, seg=10)
    P.rod(M["steel"], (0.0, 0.08, 1.2), (0.0, 0.25, 1.2), 0.012, seg=10)
    P.box(M["oak"], (L / 2 - 0.3, d / 2, 1.05), (0.6, d, 2.1))
    P.box(M["oak"], (-0.3, 0.13, 1.55), (L - 0.6, 0.26, 0.03))
    for k in range(int((L - 0.6) / 0.6)):  # base unit fronts: shadow gaps
        P.box(M["felt"], (-L / 2 + 0.6 * (k + 1), d, 0.44), (0.004, 0.004, 0.86))


# ------------------------------------------------------------------ daycare lower floor (E2): active play, sleep, prams
def climbing_wall(P, L=6.0, h=2.7):
    """Children's bouldering wall (max 2.7 m, no rope): birch-faced panels on the plaster, coloured holds in a few
    graded routes, a 300 mm crash mat in oat felt 1.8 m out from the wall."""
    P.box(M["oak"], (0, 0.02, h / 2 + 0.1), (L, 0.04, h))
    rng = np.random.default_rng(11)
    for k in range(int(L * h * 7)):
        x, z = rng.uniform(-L / 2 + 0.1, L / 2 - 0.1), rng.uniform(0.3, h)
        c = COLOURS[int(rng.integers(0, 5))]; r = rng.uniform(0.03, 0.07)
        P.blob(M["lino_" + c], (x, 0.05, z), (r * 1.3, r * 0.8, r), seg=12)
    P.box(M["felt_oat"], (0, 1.0, 0.15), (L, 1.8, 0.3))


def wall_bars(P, L=2.7, h=2.4):
    """Ribbevegg: oak wall bars, sections 0.9 wide, round rungs every 150 mm, 120 mm off the wall (every Norwegian gym hall)."""
    n = max(1, round(L / 0.9)); w = L / n
    for k in range(n + 1):
        P.box(M["oak"], (-L / 2 + k * w, 0.08, h / 2), (0.05, 0.1, h))
    for k in range(n):
        for z in np.arange(0.15, h, 0.15):
            P.rod(M["oak"], (-L / 2 + k * w + 0.03, 0.1, z), (-L / 2 + (k + 1) * w - 0.03, 0.1, z), 0.016, seg=10)


def nest_swing(P, top=5.13):
    """Indoor nest swing: a 1.0 m felt-padded ring with a hemp net, on four ropes up to the beam above, seat at 0.45."""
    P.ring(M["felt_fjord"], (0, 0), 0.42, 0.5, 0.41, 0.49, seg=48)
    for k in np.arange(-0.36, 0.37, 0.09):  # woven rope net
        w_ = math.sqrt(max(0.0, 0.43 ** 2 - k * k))
        P.rod(M["rope"], (-w_, k, 0.44), (w_, k, 0.44), 0.006, seg=6)
        P.rod(M["rope"], (k, -w_, 0.445), (k, w_, 0.445), 0.006, seg=6)
    for a in (45, 135, 225, 315):
        x, y = 0.46 * math.cos(math.radians(a)), 0.46 * math.sin(math.radians(a))
        P.rod(M["rope"], (x, y, 0.49), (0, 0, 1.6), 0.008, seg=6)
    P.rod(M["rope"], (0, 0, 1.6), (0, 0, top), 0.012, seg=8)
    P.box(M["steel"], (0, 0, top - 0.03), (0.12, 0.12, 0.06))


def balance_beam(P, L=3.0):
    """Low oak balance beam (100 mm wide, 0.3 high) on splayed feet."""
    P.box(M["oak"], (0, 0, 0.27), (L, 0.1, 0.06))
    for x in (-L / 2 + 0.2, 0.0, L / 2 - 0.2):
        P.box(M["oak"], (x, 0, 0.12), (0.08, 0.5, 0.24))


def sleep_mat(P, colour="fjord"):
    """A child's sleeping mat for the rest hour (Roman: a soft carpet, mats and blankets, sleep wherever): a 60 x 120 mat in an
    oat cover, a felt blanket half turned back, a small pillow."""
    P.box(M["pad"], (0, 0, 0.03), (0.6, 1.2, 0.06))
    P.box(M["felt_" + colour], (0, 0.18, 0.07), (0.62, 0.8, 0.025))
    P.box(M["felt_" + colour], (0, -0.2, 0.085), (0.62, 0.06, 0.03))
    P.blob(M["felt_oat"], (0, -0.42, 0.09), (0.2, 0.12, 0.05), z_cut=0.06)


def mat_shelf(P, L=1.6):
    """Low oak shelf where the mats and blankets live between naps: mats stacked, blankets folded on top."""
    d = 0.65
    for z in (0.03, 0.45, 0.8):
        P.box(M["oak"], (0, d / 2, z), (L, d, 0.025))
    for x in (-L / 2, 0, L / 2):
        P.box(M["oak"], (x, d / 2, 0.41), (0.025, d, 0.8))
    for k, x in enumerate((-L / 4, L / 4)):
        for j in range(5):
            P.box(M["pad"], (x, d / 2, 0.08 + j * 0.065), (0.6, 0.6, 0.06))
        for j in range(3):
            P.box(M["felt_" + COLOURS[(k * 3 + j) % 5]], (x, d / 2, 0.5 + j * 0.06), (0.5, 0.45, 0.05))


def star_ceiling(P, size=(4.6, 4.7), hang=3.2):
    """Sleep-room canopy: a dark fjord-blue felt plane with a few hundred tiny warm fibre-optic stars."""
    w, d = size
    z = hang
    P.box(M["felt_fjord"], (0, 0, z), (w, d, 0.03))
    rng = np.random.default_rng(5)
    for k in range(320):
        x, y = rng.uniform(-w / 2 + 0.05, w / 2 - 0.05), rng.uniform(-d / 2 + 0.05, d / 2 - 0.05)
        P.cyl(M["star"], (x, y, z - 0.017), 0.003 if k % 7 else 0.006, 0.002, seg=6)


def pram(P, colour="fjord"):
    """A Norwegian pram (barnevogn): big wheels for snow and gravel, a blackened-steel chassis, a deep felt bassinet with
    its hood up, a wool blanket, a leather-wrapped handle. Front = +y."""
    for x in (-0.27, 0.27):
        for y in (-0.35, 0.33):
            b = P.bm(M["rubber"])
            g = bmesh.ops.create_cone(b, cap_ends=True, segments=32, radius1=0.18, radius2=0.18, depth=0.045)["verts"]
            bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
            bmesh.ops.translate(b, verts=g, vec=(x, y, 0.18))
        P.rod(M["steel"], (x, -0.35, 0.18), (x * 0.6, 0.0, 0.48), 0.012, seg=8)
        P.rod(M["steel"], (x, 0.33, 0.18), (x * 0.6, 0.0, 0.48), 0.012, seg=8)
    P.box(M["felt_" + colour], (0, 0.0, 0.66), (0.42, 0.85, 0.34))
    P.box(M["felt_oat"], (0, 0.12, 0.835), (0.36, 0.5, 0.02))
    for k in range(6):  # hood: arcs of felt over the head end
        a = math.radians(15 * k)
        P.box(M["felt_" + colour], (0, -0.42 + 0.22 * (1 - math.cos(a)), 0.83 + 0.22 * math.sin(a)), (0.42, 0.06, 0.04), rx=-a)
    P.rod(M["steel"], (-0.18, -0.4, 0.75), (-0.18, -0.85, 1.05), 0.012, seg=8)
    P.rod(M["steel"], (0.18, -0.4, 0.75), (0.18, -0.85, 1.05), 0.012, seg=8)
    P.rod(M["leather"], (-0.2, -0.85, 1.05), (0.2, -0.85, 1.05), 0.016, seg=10)


def gear_rack(P, L=4.0):
    """Outdoor-gear wall for the pram store: an oak rail at 1.4 with steel pegs, a rain suit on every other peg (palette
    colours), a boot shelf below, a sled rack above."""
    P.box(M["oak"], (0, 0.03, 1.4), (L, 0.06, 0.1))
    P.box(M["oak"], (0, 0.18, 0.25), (L, 0.36, 0.025))
    rng = np.random.default_rng(9)
    for k, x in enumerate(np.arange(-L / 2 + 0.2, L / 2 - 0.1, 0.32)):
        P.rod(M["steel"], (x, 0.06, 1.38), (x, 0.16, 1.42), 0.008, seg=8)
        if k % 2 == 0:
            c = COLOURS[int(rng.integers(0, 5))]
            P.box(M["lino_" + c], (x, 0.12, 1.05), (0.28, 0.08, 0.55))
            P.box(M["lino_" + c], (x, 0.12, 0.66), (0.22, 0.06, 0.3))
        P.box(M["rubber"], (x, 0.2, 0.33), (0.08, 0.16, 0.14))
    P.box(M["oak"], (0, 0.15, 2.05), (L, 0.3, 0.025))
    for x in (-L / 4, L / 4):
        P.box(M["lino_lingon"], (x, 0.15, 2.1), (0.9, 0.35, 0.06))


# ------------------------------------------------------------------ the sunken garden (outdoors; Norwegian barnehage practice)
def gapahuk(P, L=3.6, D=2.2):
    """Gapahuk: the open lean-to every barnehage has, by the fire. Tarred posts and plank walls on three sides, a mono-pitch
    sod roof falling to the back, a raised plank floor + a bench along the back. Open front = +y, towards the fire pit."""
    hf, hb = 2.3, 1.5
    for x in (-L / 2, L / 2):
        for y, hh in ((D / 2, hf), (-D / 2, hb)):
            P.box(M["tar"], (x, y, hh / 2), (0.12, 0.12, hh))
    ang = math.atan2(hf - hb, D)
    P.box(M["tar"], (0, 0, (hf + hb) / 2 + 0.08), (L + 0.6, D / math.cos(ang) + 0.5, 0.12), rx=ang)
    P.box(M["sod"], (0, 0, (hf + hb) / 2 + 0.22), (L + 0.6, D / math.cos(ang) + 0.5, 0.16), rx=ang)
    for z in np.arange(0.35, hb, 0.2):  # back wall planks
        P.box(M["tar"], (0, -D / 2, z), (L, 0.04, 0.19))
    for x in (-L / 2, L / 2):
        for z in np.arange(0.35, hb, 0.2):
            P.box(M["tar"], (x, 0, z), (0.04, D, 0.19))
    P.box(M["oak"], (0, 0, 0.25), (L, D, 0.05))
    P.box(M["oak"], (0, -D / 2 + 0.3, 0.5), (L - 0.2, 0.4, 0.05))
    for x in (-L / 2 + 0.2, L / 2 - 0.2):
        P.box(M["tar"], (x, 0, 0.12), (0.15, D, 0.24))


def fire_pit(P, r=0.6):
    """Bålplass: a ring of split granite blocks round a bed of ash with a few charred logs, a steel tripod for the kettle."""
    for k in range(14):
        a = 2 * math.pi * k / 14
        P.box(M["granite"], (r * math.cos(a), r * math.sin(a), 0.1), (0.28, 0.2, 0.2), rz=a)
    P.cyl(M["ash"], (0, 0, 0.0), r - 0.1, 0.04, seg=32)
    for a in (0.3, 1.9, 3.8):
        P.rod(M["log"], (0.05 * math.cos(a), 0.05 * math.sin(a), 0.08), (0.4 * math.cos(a), 0.4 * math.sin(a), 0.06), 0.045, seg=10)
    for a in (90, 210, 330):
        P.rod(M["steel"], (0.75 * math.cos(math.radians(a)), 0.75 * math.sin(math.radians(a)), 0), (0, 0, 1.2), 0.012, seg=6)


def log_bench(P, L=2.0):
    """A split pine log on two short log blocks: the fire-pit seat."""
    P.box(M["oak"], (0, 0, 0.4), (L, 0.3, 0.06))
    P.rod(M["log"], (-L / 2, 0, 0.3), (L / 2, 0, 0.3), 0.15, seg=16)
    for x in (-L / 2 + 0.3, L / 2 - 0.3):
        P.cyl(M["log"], (x, 0, 0), 0.16, 0.2, seg=16)


def sandbox(P, w=3.0, d=2.4):
    """Sandbox with a wide larch-oak edge to sit on (0.3 high, 0.25 wide), deep play sand, buckets and a spade."""
    for (x, y, sx, sy) in ((0, d / 2, w, 0.25), (0, -d / 2, w, 0.25), (w / 2, 0, 0.25, d), (-w / 2, 0, 0.25, d)):
        P.box(M["oak"], (x, y, 0.15), (sx, sy, 0.3))
    P.box(M["sand"], (0, 0, 0.11), (w - 0.2, d - 0.2, 0.22))
    for k, (x, y) in enumerate(((-0.6, 0.3), (0.5, -0.4), (0.9, 0.5))):
        P.cyl(M["lino_" + COLOURS[k]], (x, y, 0.22), 0.08, 0.12, seg=16, r2=0.1)
    P.blob(M["sand"], (-0.2, -0.3, 0.22), (0.4, 0.3, 0.15))


def swing_frame(P, L=3.2, h=2.4):
    """Swings in tarred timber: A-frames at both ends, a beam, a nest swing + a seat swing on chains, bark fall surface."""
    for x in (-L / 2, L / 2):
        for s_ in (-1, 1):
            P.rod(M["tar"], (x, s_ * 0.9, 0), (x, 0, h), 0.06, seg=8)
    P.box(M["tar"], (0, 0, h), (L + 0.3, 0.14, 0.14))
    P.box(M["bark"], (0, 0, 0.01), (L + 1.0, 4.0, 0.03))
    xs = (-0.7, 0.85)
    P.ring(M["felt_moss"], (xs[0], 0), 0.42, 0.5, 0.43, 0.51, seg=48)
    P.cyl(M["rope"], (xs[0], 0, 0.46), 0.42, 0.01, seg=32)
    for a in (0, 120, 240):
        P.rod(M["steel"], (xs[0] + 0.46 * math.cos(math.radians(a)), 0.46 * math.sin(math.radians(a)), 0.5), (xs[0], 0, h - 0.07), 0.006, seg=4)
    P.box(M["rubber"], (xs[1], 0, 0.42), (0.45, 0.18, 0.03))
    for x in (xs[1] - 0.2, xs[1] + 0.2):
        P.rod(M["steel"], (x, 0, 0.43), (x, 0, h - 0.07), 0.006, seg=4)


def playhouse(P, w=2.0, d=1.6):
    """Lekehus: the building in miniature: tarred vertical boards, a sod roof, a door hole and a divided window in black
    frames, a little oak porch step. Front (door) = +y."""
    hw = 1.3
    P.box(M["tar"], (0, d / 2 - 0.03, hw / 2), (w, 0.06, hw))
    P.box(M["tar"], (0, -d / 2 + 0.03, hw / 2), (w, 0.06, hw))
    for x in (-w / 2 + 0.03, w / 2 - 0.03):
        P.box(M["tar"], (x, 0, hw / 2), (0.06, d, hw))
    for sx in (-1, 1):  # gable ends
        b = P.bm(M["tar"])
        v0 = [b.verts.new((sx * (w / 2 - 0.03) - 0.03, y, z)) for y, z in ((-d / 2, hw), (d / 2, hw), (0, hw + 0.7))]
        v1 = [b.verts.new((sx * (w / 2 - 0.03) + 0.03, y, z)) for y, z in ((-d / 2, hw), (d / 2, hw), (0, hw + 0.7))]
        b.faces.new(v0[::-1]); b.faces.new(v1)
        for i in range(3):
            j = (i + 1) % 3; b.faces.new((v0[i], v0[j], v1[j], v1[i]))
    ang = math.atan2(0.7, d / 2)
    for s_ in (-1, 1):
        P.box(M["sod"], (0, s_ * d / 4, hw + 0.35 + 0.06), (w + 0.4, d / 2 / math.cos(ang) + 0.3, 0.12), rx=-s_ * ang)
    P.box(M["felt"], (-0.4, d / 2, 0.55), (0.6, 0.065, 1.05))  # door hole (dark)
    P.box(M["glass"], (0.45, d / 2, 0.85), (0.6, 0.065, 0.45))
    P.box(M["frame"], (0.45, d / 2 + 0.035, 0.85), (0.03, 0.01, 0.45))
    P.box(M["frame"], (0.45, d / 2 + 0.035, 0.85), (0.6, 0.01, 0.03))
    P.box(M["oak"], (-0.4, d / 2 + 0.2, 0.05), (0.8, 0.4, 0.1))


def mud_kitchen(P, L=1.6):
    """Gjørmekjøkken: an oak bench with a stone top, two sunk steel bowls, a hand pump, pots and pans on pegs. Front = +y."""
    P.box(M["oak"], (0, 0.25, 0.3), (L, 0.5, 0.6))
    P.box(M["stone"], (0, 0.25, 0.62), (L, 0.52, 0.04))
    for x in (-0.4, 0.35):
        P.cyl(M["brushed"], (x, 0.27, 0.6), 0.16, 0.05, seg=24)
    P.rod(M["steel"], (0.75, 0.05, 0.6), (0.75, 0.05, 1.0), 0.02, seg=8)
    P.rod(M["steel"], (0.75, 0.05, 1.0), (0.75, 0.25, 0.95), 0.012, seg=8)
    P.box(M["oak"], (0, 0.02, 1.3), (L, 0.04, 0.7))
    for x in (-0.5, -0.1, 0.3):
        P.cyl(M["brushed"], (x, 0.12, 1.15), 0.1, 0.12, seg=20)


def trike_loop(P, rx=2.6, ry=2.3, w=0.9):
    """Tricycle loop: an elliptical ring of sand-coloured poured rubber, 0.9 wide, flush with the garden floor."""
    b = P.bm(M["trike"]); n = 96
    vs = []
    for k in range(n):
        a = 2 * math.pi * k / n
        ring = []
        for (dx, z) in ((-w / 2, 0.0), (w / 2, 0.0), (w / 2, 0.03), (-w / 2, 0.03)):
            ring.append(b.verts.new(((rx + dx) * math.cos(a), (ry + dx) * math.sin(a), z)))
        vs.append(ring)
    for k in range(n):
        A, B = vs[k], vs[(k + 1) % n]
        for i in range(4):
            b.faces.new((A[i], A[(i + 1) % 4], B[(i + 1) % 4], B[i]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces)


def terrace_slide(P, drop=2.75, deg=35.0):
    """Slide off the terrace: the banks are too steep to lay a slide on, so it stands free. A wide stainless trough at 35
    degrees from an oak start deck on the terrace edge (local origin, terrace level) down to the garden floor, carried on
    tarred posts, ending in a flat run-out; a timber stair with handrails beside it (+x) climbs back up. Down = +y."""
    run = drop / math.tan(math.radians(deg)); ang = math.radians(deg); Ls = drop / math.sin(ang)
    P.box(M["oak"], (0.45, -0.45, -0.05), (2.0, 0.9, 0.1))  # start deck over the edge
    for x in (-0.55, 1.45):
        P.rod(M["tar"], (x, -0.85, -0.6), (x, -0.85, 1.0), 0.04, seg=8)
    P.rod(M["tar"], (-0.55, -0.85, 1.0), (1.45, -0.85, 1.0), 0.03, seg=8)
    P.box(M["brushed"], (0, run / 2, -drop / 2 + 0.06), (0.6, Ls, 0.02), rx=-ang)
    for x in (-0.32, 0.32):
        P.box(M["brushed"], (x, run / 2, -drop / 2 + 0.19), (0.03, Ls, 0.26), rx=-ang)
        P.box(M["brushed"], (x, run + 0.3, -drop + 0.38), (0.03, 0.6, 0.26))
    P.box(M["brushed"], (0, run + 0.3, -drop + 0.25), (0.6, 0.6, 0.02))
    for t in (0.25, 0.5, 0.75):  # posts under the trough
        y, z = run * t, -drop * t
        for x in (-0.25, 0.25):
            P.rod(M["tar"], (x, y, -drop), (x, y, z + 0.02), 0.035, seg=8)
    for x in (-0.25, 0.25):
        P.rod(M["tar"], (x, run + 0.5, -drop), (x, run + 0.5, -drop + 0.24), 0.035, seg=8)
    # the stair beside it: 14 risers, oak treads between tarred stringers, handrails at 0.9
    n = 14; sx0, sx1 = 0.75, 1.55
    for k in range(n):
        y = run - (k + 1) * run / n; z = -drop + (k + 1) * drop / n
        P.box(M["oak"], ((sx0 + sx1) / 2, y + run / n / 2, z - 0.02), (sx1 - sx0, run / n + 0.03, 0.04))
    for x in (sx0, sx1):
        P.box(M["tar"], (x, run / 2, -drop / 2 - 0.12), (0.05, Ls, 0.22), rx=-ang)
        P.rod(M["oak"], (x, run, -drop + 0.9), (x, 0.0, 0.9), 0.022, seg=10)
        for t in (0.0, 0.5, 1.0):
            P.rod(M["tar"], (x, run * t, -drop * t), (x, run * t, -drop * t + 0.9), 0.025, seg=8)


def pram_shelter(P, L=3.4, D=2.0):
    """Vognskur: the uninsulated open shelter where the youngest nap outdoors in their prams (Norwegian practice).
    Tarred timber, a sod roof, slatted back + sides for air, open front = +y."""
    h = 2.2
    for x in (-L / 2, L / 2):
        for y in (-D / 2, D / 2):
            P.box(M["tar"], (x, y, h / 2), (0.1, 0.1, h))
    P.box(M["tar"], (0, 0, h + 0.06), (L + 0.6, D + 0.6, 0.12))
    P.box(M["sod"], (0, 0, h + 0.2), (L + 0.6, D + 0.6, 0.16))
    for x in np.arange(-L / 2, L / 2, 0.12):
        P.box(M["tar"], (x, -D / 2, h / 2 + 0.1), (0.07, 0.025, h - 0.2))
    for y in np.arange(-D / 2, D / 2, 0.12):
        for x in (-L / 2, L / 2):
            P.box(M["tar"], (x, y, h / 2 + 0.1), (0.025, 0.07, h - 0.2))
    P.box(M["oak"], (0, 0, 0.04), (L, D, 0.08))


def stump(P, r=0.18, h=0.35):
    P.cyl(M["log"], (0, 0, 0), r, h, seg=20)
    P.cyl(M["oak"], (0, 0, h), r - 0.01, 0.003, seg=20)


def tube_slide(P, rt=1.08, rr=0.33, a_top=300.0, turns_deg=690.0, z_top=0.36, z_bot=-5.39, run=3.0, hatches=(), bridge=(2.62, 1.3), stair_a0=90.0):
    """Tube slide spiralling down inside the eye of the round stair (Roman): a 660 mm tube on a 1.08 m centreline radius, going
    round the same way the stair does, from the upper floor to a straight run-out and an open chute on the lower floor.
    Lower half brushed stainless, upper half clear polycarbonate (children are seen all the way down); steel flanges every
    1.5 m; side rescue hatches facing the stair where an adult on the treads can reach them (opposite gates in the stair's
    inner balustrade); slim steel brackets to the inner stringer. At the top an oak bridge crosses from the floor guard to the
    entry hood. Origin = stair centre on the upper floor; angles in degrees like the stair."""
    poly = M.setdefault("polycarb", bc.arch_glass("polycarbonate", tint=(0.94, 0.97, 0.98), rough=0.02))
    n_ring = 28
    def frame_at(t):  # t in [0, 1] down the helix -> centre, tangent, outward normal
        a = math.radians(a_top + turns_deg * t)
        c = Vector((rt * math.cos(a), rt * math.sin(a), z_top + (z_bot - z_top) * t))
        L = math.radians(turns_deg) * rt; dz = z_bot - z_top
        tng = Vector((-math.sin(a) * L, math.cos(a) * L, dz)).normalized()
        out = Vector((math.cos(a), math.sin(a), 0))
        return c, tng, out
    pts = []
    N = int(turns_deg / 2.5)
    for i in range(N + 1):
        pts.append(frame_at(i / N))
    c_end, t_end, o_end = pts[-1]
    t_flat = Vector((t_end.x, t_end.y, 0)).normalized()
    z_exit = -6.13 + 0.42 - 0.0
    for j in range(1, 13):  # run-out: straight, easing down to the exit height
        u = j / 12
        c = c_end + t_flat * run * u; c.z = c_end.z + (z_exit - c_end.z) * (1 - (1 - u) ** 2)
        pts.append((c, t_flat, Vector((-t_flat.y, t_flat.x, 0))))
    lo, hi = P.bm(M["brushed"]), P.bm(poly)
    rings_lo, rings_hi = [], []
    for k_, (c, tng, out) in enumerate(pts):
        side = tng.cross(Vector((0, 0, 1))).normalized(); up = side.cross(tng).normalized()
        chute = k_ > len(pts) - 5  # the last 0.8 m is an open chute (no lid)
        rl, rh = [], []
        for i in range(n_ring + 1):
            ph = math.pi + math.pi * i / n_ring  # lower half: 180..360 deg round the tube
            rl.append(lo.verts.new(c + (side * math.cos(ph) + up * math.sin(ph)) * rr))
            if not chute:
                ph2 = math.pi * i / n_ring
                rh.append(hi.verts.new(c + (side * math.cos(ph2) + up * math.sin(ph2)) * rr))
        rings_lo.append(rl); rings_hi.append(rh)
    for A, B in zip(rings_lo, rings_lo[1:]):
        for i in range(n_ring):
            lo.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
    for A, B in zip(rings_hi, rings_hi[1:]):
        if A and B:
            for i in range(n_ring):
                hi.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
    step = max(1, int(1.5 / (math.radians(2.5) * rt)))
    for k_ in range(0, N, step):  # flanges; a hanger from each up to the stair's inner stringer on the turn above
        c, tng, out = pts[k_]
        P.rod(M["steel"], c - tng * 0.012, c + tng * 0.012, rr + 0.02, seg=32)
        ang = (a_top + turns_deg * k_ / N) % 360
        above = [-6.13 + (int((al - stair_a0) / 15) + 1) * 6.13 / 35 - 0.36 for al in (ang + 360 * j for j in range(-1, 4))
                 if stair_a0 <= al <= stair_a0 + 525]
        above = [z for z in above if z > c.z + rr + 0.1]
        if above:
            P.rod(M["steel"], c + Vector((0, 0, rr + 0.02)), Vector((c.x * 1.45 / rt, c.y * 1.45 / rt, min(above))), 0.008, seg=6)
    for th in hatches:  # rescue hatch: a framed 480 x 420 door on the stair side, hinged at the top, red pull
        t = (th - a_top) / turns_deg
        c, tng, out = frame_at(t)
        hc = c + out * (rr + 0.012)
        for dz, dt, sx, sz in ((0.21, 0, 0.5, 0.03), (-0.21, 0, 0.5, 0.03), (0, 0.24, 0.03, 0.45), (0, -0.24, 0.03, 0.45)):
            P.box(M["steel"], hc + Vector((0, 0, dz)) + tng * dt, (sx, 0.02, sz), rz=math.atan2(tng.y, tng.x))
        P.cyl(M["steel"], hc + Vector((0, 0, 0.22)) - tng * 0.2, 0.012, 0.0, seg=8)
        P.box(M["lino_lingon"], hc + Vector((0, 0, -0.14)) + out * 0.02, (0.12, 0.03, 0.04), rz=math.atan2(tng.y, tng.x))
    # the oak bridge from the floor guard to the entry hood, guards both sides, an oak hood with a grab bar over the start
    a = math.radians(a_top); ca, sa = math.cos(a), math.sin(a); tx, ty = -sa, ca
    r0, r1 = bridge; rm = (r0 + r1) / 2
    P.box(M["oak"], (rm * ca, rm * sa, -0.05), (r0 - r1 + 0.3, 0.95, 0.1), rz=a)
    for d in (-0.47, 0.47):
        for r_ in np.arange(r1, r0, 0.09):
            P.box(M["oak"], (r_ * ca + tx * d, r_ * sa + ty * d, 0.6), (0.03, 0.03, 1.2), rz=a)
        P.box(M["steel"], (rm * ca + tx * d, rm * sa + ty * d, 1.22), (r0 - r1, 0.04, 0.04), rz=a)
    c, tng, out = frame_at(0.0)
    for d in (-0.42, 0.42):
        P.box(M["oak"], (c.x + out.x * d, c.y + out.y * d, 0.55), (0.08, 0.08, 1.1), rz=a)
    P.box(M["oak"], (c.x, c.y, 1.12), (0.08, 0.95, 0.08), rz=a)
    P.rod(M["steel"], (c.x - out.x * 0.35, c.y - out.y * 0.35, 0.95), (c.x + out.x * 0.35, c.y + out.y * 0.35, 0.95), 0.016, seg=10)
    # a soft landing mat at the exit
    ce = pts[-1][0]
    P.box(M["felt_oat"], (ce.x + t_flat.x * 0.7, ce.y + t_flat.y * 0.7, -6.13 + 0.05), (1.2, 1.2, 0.1), rz=math.atan2(t_flat.y, t_flat.x))


def foam_fortress(P):
    """Foam fortress (Roman): big lightweight foam blocks in wool-felt covers, stacked into a little fort they can knock down and
    rebuild: walls two courses high with a gateway, two round towers, a half-round arch, and a scatter of thrown blocks."""
    rng = np.random.default_rng(21)
    bx, by, bz = 0.6, 0.3, 0.3
    c_ = lambda k: M["felt_" + COLOURS[k % 5]]
    k = 0
    for course in range(2):
        z = bz / 2 + course * bz
        off = (bx / 2) * (course % 2)
        j_ = lambda: (rng.uniform(-0.012, 0.012), rng.uniform(-0.03, 0.03))  # hand-stacked: a little off, a little turned
        for x in np.arange(-1.2 + off, 1.21, bx):  # back wall
            d, r_ = j_(); P.box(c_(k), (x + d, -1.0 + d, z), (bx - 0.015, by, bz - 0.005), rz=r_); k += 1
        for y in np.arange(-0.7 + off, 0.95, bx):  # side walls
            for sx in (-1.35, 1.35):
                d, r_ = j_(); P.box(c_(k), (sx + d, y + d, z), (by, bx - 0.015, bz - 0.005), rz=r_); k += 1
        for x in (-1.0, 1.0):  # front wall either side of the gate
            d, r_ = j_(); P.box(c_(k), (x + d, 1.0 + d, z), (bx - 0.015, by, bz - 0.005), rz=r_); k += 1
    for sx in (-1.35, 1.35):  # towers
        P.cyl(c_(k), (sx, 1.0, 0), 0.3, 0.9, seg=32); k += 1
        P.cyl(M["felt_oat"], (sx, 1.0, 0.9), 0.32, 0.08, seg=32)
    P.ring(M["felt_cloud"], (0, 1.0), 0.32, 0.5, -0.15, 0.15, seg=48)  # on edge as the gateway arch
    for j in range(9):  # thrown blocks
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(2.0, 2.9)
        P.box(c_(j + 3), (d * math.cos(a), d * math.sin(a) + 0.3, bz / 2), (bx, by, bz), rz=rng.uniform(0, math.pi),
              rx=(math.pi / 2 if j % 3 == 0 else 0.0))
    P.box(M["felt_oat"], (0, 0, 0.01), (3.4, 2.8, 0.02))


def ripstick(P, colour="lingon"):
    """Caster board (RipStik): two shaped decks on a torsion bar, a 76 mm inline caster under each, 0.86 long. Long axis = x."""
    for x in (-0.25, 0.25):
        P.cyl(M["lino_" + colour], (x, 0, 0.1), 0.13, 0.02, seg=32)
        P.rod(M["steel"], (x, 0, 0.1), (x, 0, 0.04), 0.012, seg=8)
        b = P.bm(M["rubber"])
        g = bmesh.ops.create_cone(b, cap_ends=True, segments=24, radius1=0.038, radius2=0.038, depth=0.025)["verts"]
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(b, verts=g, vec=(x, 0, 0.038))
    P.rod(M["steel"], (-0.25, 0, 0.09), (0.25, 0, 0.09), 0.018, seg=12)


def _wheel(P, c, r, w, mat=None):
    b = P.bm(mat or M["rubber"])
    g = bmesh.ops.create_cone(b, cap_ends=True, segments=28, radius1=r, radius2=r, depth=w)["verts"]
    bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
    bmesh.ops.translate(b, verts=g, vec=c)


def tricycle(P, colour="fjord"):
    """Child's tricycle: a bent steel frame in a palette colour, a big front wheel with pedals, two rear wheels on an axle, an oak
    seat, a handlebar with rubber grips. Front = +y."""
    fr = M["lino_" + colour]
    _wheel(P, (0, 0.38, 0.17), 0.17, 0.04)
    for x in (-0.22, 0.22):
        _wheel(P, (x, -0.22, 0.12), 0.12, 0.04)
    P.rod(M["steel"], (-0.22, -0.22, 0.12), (0.22, -0.22, 0.12), 0.01, seg=8)
    P.rod(fr, (0, -0.2, 0.14), (0, 0.15, 0.36), 0.022, seg=12)
    P.rod(fr, (0, 0.15, 0.36), (0, 0.38, 0.17), 0.018, seg=12)
    P.rod(fr, (0, 0.33, 0.28), (0, 0.3, 0.6), 0.016, seg=12)
    P.rod(M["steel"], (-0.2, 0.3, 0.6), (0.2, 0.3, 0.6), 0.012, seg=10)
    for x in (-0.2, 0.2):
        P.rod(M["rubber"], (x * 0.9, 0.3, 0.6), (x * 1.15, 0.3, 0.6), 0.016, seg=10)
    P.box(M["oak"], (0, -0.02, 0.42), (0.16, 0.2, 0.03))
    for s_ in (-1, 1):
        P.box(M["rubber"], (s_ * 0.07, 0.38, 0.17 + s_ * 0.08), (0.06, 0.03, 0.02))


def strider(P, colour="moss"):
    """Balance bike (Strider type, no pedals): 12-inch wheels, a slim frame in a palette colour, oak saddle, low handlebar."""
    fr = M["lino_" + colour]
    for y in (-0.3, 0.32):
        _wheel(P, (0, y, 0.15), 0.15, 0.05)
    P.rod(fr, (0, -0.3, 0.15), (0, -0.08, 0.38), 0.016, seg=10)
    P.rod(fr, (0, -0.08, 0.38), (0, 0.24, 0.42), 0.02, seg=10)
    P.rod(fr, (0, 0.24, 0.42), (0, 0.32, 0.15), 0.015, seg=10)
    P.rod(fr, (0, 0.24, 0.42), (0, 0.22, 0.58), 0.014, seg=10)
    P.rod(M["steel"], (-0.18, 0.22, 0.58), (0.18, 0.22, 0.58), 0.011, seg=10)
    P.box(M["oak"], (0, -0.1, 0.42), (0.1, 0.2, 0.025))


def wheel_rack(P, L=2.3):
    """Low oak rack on the wall for the kids' wheels: slotted front rail for balance-bike wheels, a shelf above for caster boards
    and helmets (felt-lined hooks)."""
    P.box(M["oak"], (0, 0.2, 0.1), (L, 0.4, 0.04))
    for x in np.arange(-L / 2 + 0.1, L / 2, 0.38):
        P.box(M["oak"], (x, 0.3, 0.2), (0.03, 0.2, 0.2))
    P.box(M["oak"], (0, 0.15, 1.1), (L, 0.3, 0.03))
    P.box(M["oak"], (0, 0.01, 0.65), (L, 0.02, 1.1))
    for k, x in enumerate(np.arange(-L / 2 + 0.25, L / 2, 0.45)):
        P.blob(M["lino_" + COLOURS[k % 5]], (x, 0.15, 1.125), (0.1, 0.125, 0.12), z_cut=1.125)  # kids' helmets: domes on the shelf
        P.box(M["rubber"], (x, 0.03, 1.13), (0.06, 0.02, 0.01))


def rolling_hill(P, L=3.2, D=2.4, h=0.8):
    """'Lekebakke', the indoor rolling hill (my pick): a soft rounded ridge (3.2 across, 2.4 long, 0.8 high) on an oak frame to
    run over, roll down and sit on, with an arched crawl tunnel (0.62 wide, 0.66 high) running straight through it, open at
    both flat ends. Upholstered in wool felt in contour bands of the palette (a little mountain on a map); the tunnel is lined
    in dark fjord felt. Tunnel axis = y."""
    zt = lambda x: h * max(0.0, 1 - (2 * x / L) ** 2) ** 0.7     # the ridge's cross-section
    ar = 0.31; ac = 0.35                                            # tunnel arch radius, arch centre height
    za = lambda x: ac + math.sqrt(max(0.0, ar * ar - x * x))        # tunnel roof
    bands = ["felt_oat", "felt_moss", "felt_oat", "felt_cloud", "felt_oat", "felt_heather", "felt_oat", "felt_fjord"]
    n = 64
    xs = sorted(set([round(-L / 2 + L * i / n, 5) for i in range(n + 1)] + [-ar, ar] + [ar * math.cos(math.pi * k / 24) for k in range(1, 24)]))
    for x0, x1 in zip(xs, xs[1:]):  # top surface, in bands by height (straight stripes along the ridge)
        zc = zt((x0 + x1) / 2)
        b = P.bm(M[bands[min(len(bands) - 1, int(zc / 0.1))]])
        v = [b.verts.new(p) for p in ((x0, -D / 2, zt(x0)), (x1, -D / 2, zt(x1)), (x1, D / 2, zt(x1)), (x0, D / 2, zt(x0)))]
        b.faces.new(v)
        inside = abs((x0 + x1) / 2) < ar  # over the tunnel the end face starts at the arch, elsewhere at the floor
        zb = lambda x: za(x) if inside else 0.0
        for y, flip in ((-D / 2, False), (D / 2, True)):  # flat end faces, cut round the arch
            e = P.bm(M["felt_oat"])
            q = [e.verts.new(p) for p in ((x0, y, zb(x0)), (x1, y, zb(x1)), (x1, y, zt(x1)), (x0, y, zt(x0)))]
            e.faces.new(q[::-1] if flip else q)
    lin = P.bm(M["felt_fjord"])  # the tunnel: two low walls + the arched roof, the whole length
    m = 24
    for side in (-1, 1):
        lin.faces.new([lin.verts.new(p) for p in ((side * ar, -D / 2, 0.0), (side * ar, D / 2, 0.0), (side * ar, D / 2, ac), (side * ar, -D / 2, ac))])
    for k in range(m):
        a0, a1 = math.pi * k / m, math.pi * (k + 1) / m
        p0 = (ar * math.cos(a0), ac + ar * math.sin(a0)); p1 = (ar * math.cos(a1), ac + ar * math.sin(a1))
        lin.faces.new([lin.verts.new(p) for p in ((p0[0], -D / 2, p0[1]), (p1[0], -D / 2, p1[1]), (p1[0], D / 2, p1[1]), (p0[0], D / 2, p0[1]))])
    P.box(M["felt_moss"], (0, 0, 0.01), (2 * ar, D, 0.02))  # soft floor in the tunnel
    for (x, y, sx, sy) in ((0, D / 2 + 0.03, L, 0.06), (0, -D / 2 - 0.03, L, 0.06), (L / 2, 0, 0.06, D + 0.12), (-L / 2, 0, 0.06, D + 0.12)):
        P.box(M["oak"], (x, y, 0.04), (sx, sy, 0.08))


def _flat_quad(P, mat, pts, z=0.002):
    b = P.bm(mat)
    b.faces.new([b.verts.new((x, y, z)) for x, y in pts])


def floor_track(P, straight=5.2, r=2.55, w=0.9):
    """Race track inlaid in the oak floor (Roman: make the bottom floor fun): a stadium loop of muted fjord-blue linoleum, 0.9
    wide, oat edge lines, a dashed white centre line, a checkered start/finish line on the south straight and chevrons
    showing the way round (anticlockwise). Flush inlay (2 mm proud only so it renders). Origin = loop centre."""
    white = M.setdefault("line_white", bc.material("line_white", (0.84, 0.82, 0.77), 0.45))
    per = 2 * straight + 2 * math.pi * r
    def at(s_):  # centreline point + outward normal, s_ from the middle of the south straight, anticlockwise
        s_ = s_ % per
        if s_ < straight / 2:
            return (s_, -r), (0, -1)
        s_ -= straight / 2
        if s_ < math.pi * r:
            a = -math.pi / 2 + s_ / r
            return (straight / 2 + r * math.cos(a), r * math.sin(a)), (math.cos(a), math.sin(a))
        s_ -= math.pi * r
        if s_ < straight:
            return (straight / 2 - s_, r), (0, 1)
        s_ -= straight
        if s_ < math.pi * r:
            a = math.pi / 2 + s_ / r
            return (-straight / 2 + r * math.cos(a), r * math.sin(a)), (math.cos(a), math.sin(a))
        s_ -= math.pi * r
        return (-straight / 2 + s_, -r), (0, -1)
    def ribbon(mat, d0, d1, s0, s1, z, step=0.08):
        n = max(1, int((s1 - s0) / step))
        for k in range(n):
            sa, sb = s0 + (s1 - s0) * k / n, s0 + (s1 - s0) * (k + 1) / n
            (pa, na), (pb, nb) = at(sa), at(sb)
            _flat_quad(P, mat, [(pa[0] + na[0] * d0, pa[1] + na[1] * d0), (pb[0] + nb[0] * d0, pb[1] + nb[1] * d0),
                                (pb[0] + nb[0] * d1, pb[1] + nb[1] * d1), (pa[0] + na[0] * d1, pa[1] + na[1] * d1)], z)
    ribbon(M["lino_fjord"], -w / 2, w / 2, 0, per, 0.002)
    for d in (-w / 2, w / 2 - 0.05):
        ribbon(M["lino_oat"], d, d + 0.05, 0, per, 0.0025)
    s_ = 0.6
    while s_ < per - 0.3:  # dashed centre line
        ribbon(white, -0.025, 0.025, s_, s_ + 0.3, 0.0028); s_ += 0.6
    for i in range(9):  # checkered start/finish across the south straight
        for j in range(2):
            x0, y0 = -0.2 + j * 0.1, -r - w / 2 + i * w / 9
            _flat_quad(P, white if (i + j) % 2 else M["lino_lingon"], [(x0, y0), (x0 + 0.1, y0), (x0 + 0.1, y0 + w / 9), (x0, y0 + w / 9)], 0.003)
    for s_ in (straight / 2 + math.pi * r / 2, straight * 1.5 + math.pi * r * 1.5 - straight / 2 + straight / 2):  # chevrons on the bends
        for k in range(3):
            (p0, n0) = at(s_ + k * 0.35); t = (-n0[1], n0[0])
            tip = (p0[0] + t[0] * 0.12, p0[1] + t[1] * 0.12)
            for sgn in (-1, 1):
                q = (p0[0] - t[0] * 0.08 + n0[0] * sgn * 0.25, p0[1] - t[1] * 0.08 + n0[1] * sgn * 0.25)
                _flat_quad(P, M["lino_cloud"], [q, tip, (tip[0] - t[0] * 0.07, tip[1] - t[1] * 0.07), (q[0] - t[0] * 0.07, q[1] - t[1] * 0.07)], 0.0029)


def hopscotch(P):
    """Hopscotch inlaid in linoleum along +x: 1-2-3 single, 4|5, 6, 7|8, a half-round 'home', numbers burnt into the squares."""
    burnt = bc.material("burnt_text", (0.035, 0.022, 0.014), 0.75)
    a = 0.42; cells = [(0, 0, 1), (1, 0, 2), (2, 0, 3), (3, -0.5, 4), (3, 0.5, 5), (4, 0, 6), (5, -0.5, 7), (5, 0.5, 8)]
    for k, (i, j, num) in enumerate(cells):
        x0, y0 = i * a, j * a - a / 2
        _flat_quad(P, M["lino_" + COLOURS[k % 5]], [(x0 + 0.02, y0 + 0.02), (x0 + a - 0.02, y0 + 0.02), (x0 + a - 0.02, y0 + a - 0.02), (x0 + 0.02, y0 + a - 0.02)], 0.002)
        P.text(burnt, str(num), (x0 + a / 2, y0 + a / 2, 0.0025), 0.2, depth=0.0005, flat=True, rz=math.pi / 2)
    b = P.bm(M["lino_oat"]); n = 16; cx = 6 * a
    vs = [b.verts.new((cx, 0, 0.002))] + [b.verts.new((cx + 0.4 * math.sin(math.pi * t / n), -0.4 * math.cos(math.pi * t / n), 0.002)) for t in range(n + 1)]
    for t in range(n):
        b.faces.new((vs[0], vs[t + 1], vs[t + 2]))


def music_wall(P, L=1.9):
    """Music wall at child height on an oak panel: a xylophone of 8 tuned oak bars (palette-tipped) with two mallets on a cord,
    a row of hanging brass-free steel chime tubes, two felt-rimmed hand drums and a rain stick. Origin = wall face, centre."""
    P.box(M["oak"], (0, 0.015, 0.95), (L, 0.03, 1.3))
    for k in range(8):  # xylophone: bars getting shorter to the right, on a felt rail
        x = -L / 2 + 0.25 + k * 0.1; ln = 0.42 - k * 0.03
        P.box(M["oak"], (x, 0.06, 0.62), (0.07, 0.03, ln))
        P.box(M["lino_" + COLOURS[k % 5]], (x, 0.076, 0.62 + ln / 2 - 0.03), (0.07, 0.002, 0.05))
    P.box(M["felt"], (-L / 2 + 0.6, 0.04, 0.62), (0.85, 0.01, 0.03))
    for x in (-L / 2 + 0.15, -L / 2 + 1.05):
        P.rod(M["oak"], (x, 0.05, 0.85), (x, 0.08, 0.6), 0.008, seg=8)
        P.blob(M["felt_lingon"], (x, 0.08, 0.6), (0.025, 0.025, 0.025))
    P.box(M["oak"], (0.35, 0.08, 1.55), (0.7, 0.1, 0.04))  # chime rail
    for k in range(7):
        x = 0.05 + k * 0.1
        P.cyl(M["brushed"], (x, 0.1, 1.55 - 0.15 - (0.45 - k * 0.04)), 0.013, 0.45 - k * 0.04, seg=16)
    for (x, z, r) in ((0.25, 0.75, 0.16), (0.6, 0.72, 0.12)):  # hand drums mounted face-out
        b = P.bm(M["felt_moss"] if r > 0.14 else M["felt_cloud"])
        g = bmesh.ops.create_cone(b, cap_ends=True, segments=32, radius1=r, radius2=r, depth=0.1)["verts"]
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(b, verts=g, vec=(x, 0.08, z))
        b2 = P.bm(M["pad"])
        g2 = bmesh.ops.create_cone(b2, cap_ends=True, segments=32, radius1=r - 0.01, radius2=r - 0.01, depth=0.004)["verts"]
        bmesh.ops.rotate(b2, verts=g2, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(b2, verts=g2, vec=(x, 0.132, z))
    P.rod(M["log"], (L / 2 - 0.15, 0.08, 0.35), (L / 2 - 0.15, 0.08, 1.45), 0.035, seg=12)  # rain stick on two clips


def dance_mirror(P, L=1.8, h=1.3, barre=0.55):
    """Low wide safety mirror (shatterproof acrylic mirror in a slim oak frame, from 0.15 to 1.45) with an oak barre at 0.55 on
    blackened-steel brackets: for dancing, pulling faces, and watching yourself on the balance trail."""
    P.box(M["oak"], (0, 0.012, 0.15 + h / 2), (L + 0.04, 0.024, h + 0.04))
    P.box(M["mirror"], (0, 0.026, 0.15 + h / 2), (L, 0.006, h))
    for x in (-L / 2 + 0.15, 0.0, L / 2 - 0.15):
        P.box(M["steel"], (x, 0.1, barre), (0.025, 0.17, 0.025))
    P.rod(M["oak"], (-L / 2 + 0.05, 0.18, barre), (L / 2 - 0.05, 0.18, barre), 0.02, seg=16)


def balance_trail(P):
    """Balance trail (more fun than one beam): three oak beams in a zig-zag at 0.2 / 0.3 / 0.25 high (100, 80 and a wavy 120 mm
    one), felt-topped stepping pods of different heights between them, and a rocking wobble board at the end."""
    beams = [((-2.0, -0.6), (-0.9, 0.2), 0.2, 0.1), ((-0.5, 0.35), (0.7, -0.35), 0.3, 0.08), ((1.1, -0.2), (2.0, 0.45), 0.25, 0.12)]
    for (a, b, h, w) in beams:
        L_ = math.hypot(b[0] - a[0], b[1] - a[1]); ang = math.atan2(b[1] - a[1], b[0] - a[0]); c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        P.box(M["oak"], (c[0], c[1], h - 0.03), (L_, w, 0.06), rz=ang)
        for t in (0.15, 0.85):
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            P.box(M["oak"], (x, y, (h - 0.06) / 2), (0.08, 0.4, h - 0.06), rz=ang)
    for k, (x, y, h) in enumerate(((-0.72, 0.38, 0.16), (-0.65, -0.15, 0.24), (0.9, -0.55, 0.2), (0.95, 0.05, 0.3), (2.3, 0.6, 0.12))):
        P.cyl(M["oak"], (x, y, 0), 0.15, h - 0.03, seg=24)
        P.cyl(M["felt_" + COLOURS[k % 5]], (x, y, h - 0.03), 0.15, 0.03, seg=24)
    b = P.bm(M["oak"])  # wobble board: a curved rocker under a flat oak board
    n = 16
    for k in range(n):
        a0, a1 = math.pi * (1 + k / n), math.pi * (1 + (k + 1) / n)
        p0 = (0.35 * math.cos(a0), 0.12 + 0.12 * math.sin(a0)); p1 = (0.35 * math.cos(a1), 0.12 + 0.12 * math.sin(a1))
        b.faces.new([b.verts.new((2.55 + p0[0], -0.35 - 0.15, p0[1])), b.verts.new((2.55 + p1[0], -0.35 - 0.15, p1[1])),
                     b.verts.new((2.55 + p1[0], -0.35 + 0.15, p1[1])), b.verts.new((2.55 + p0[0], -0.35 + 0.15, p0[1]))])
    P.box(M["oak"], (2.55, -0.35, 0.135), (0.75, 0.32, 0.03))
    P.box(M["felt_lingon"], (2.55, -0.35, 0.152), (0.7, 0.28, 0.004))


def felt_banner(P, motif="sun", colour="fjord", w=0.8, h=1.9, top=4.75):
    """A tall wool-felt wall banner (fanevegg) with a swallowtail hem, hung on an oak rod with round end knobs and two cords to a
    wall hook; a simple appliqué motif in contrasting felt: sun, mountains, spruce, waves or moon + star. Front = +y, on a wall."""
    y0, y1 = 0.03, 0.036
    bot = top - h
    P.prism(M["felt_" + colour], [(-w / 2, top), (w / 2, top), (w / 2, bot), (0, bot + 0.18), (-w / 2, bot)], y0, y1)
    P.rod(M["oak"], (-w / 2 - 0.08, 0.04, top + 0.02), (w / 2 + 0.08, 0.04, top + 0.02), 0.016, seg=12)
    for x in (-w / 2 - 0.08, w / 2 + 0.08):
        P.blob(M["oak"], (x, 0.04, top + 0.02), (0.025, 0.025, 0.025))
        P.rod(M["rope"], (x * 0.9, 0.04, top + 0.02), (0, 0.01, top + 0.32), 0.003, seg=4)
    a, b_ = y1, y1 + 0.006
    cz = bot + h * 0.58
    other = [c for c in ("oat", "cloud", "lingon", "moss", "heather", "fjord") if c != colour]
    m1, m2 = M["felt_" + other[0]], M["felt_" + other[1]]
    if motif == "sun":
        pts = [(0.2 * math.cos(2 * math.pi * k / 24), cz + 0.2 * math.sin(2 * math.pi * k / 24)) for k in range(24)]
        P.prism(m2, pts, a, b_)
        for k in range(12):
            t = 2 * math.pi * k / 12
            P.prism(m2, [(0.25 * math.cos(t - 0.08), cz + 0.25 * math.sin(t - 0.08)), (0.33 * math.cos(t), cz + 0.33 * math.sin(t)),
                         (0.25 * math.cos(t + 0.08), cz + 0.25 * math.sin(t + 0.08))], a, b_)
    elif motif == "mountains":
        P.prism(m1, [(-0.36, cz - 0.3), (-0.08, cz + 0.22), (0.12, cz - 0.05), (0.2, cz + 0.08), (0.36, cz - 0.3)], a, b_)
        P.prism(m2, [(-0.15, cz + 0.09), (-0.08, cz + 0.22), (-0.01, cz + 0.09)], b_, b_ + 0.004)
    elif motif == "spruce":
        for k, s_ in enumerate((0.34, 0.27, 0.2, 0.13)):
            z0_ = cz - 0.35 + k * 0.16
            P.prism(m1 if colour != "moss" else M["felt_oat"], [(-s_, z0_), (s_, z0_), (0, z0_ + 0.26)], a, b_)
        P.prism(M["felt_oat"], [(-0.04, cz - 0.48), (0.04, cz - 0.48), (0.04, cz - 0.35), (-0.04, cz - 0.35)], a, b_)
    elif motif == "waves":
        for k in range(3):
            zc = cz + 0.25 - k * 0.22
            pts = [(-0.36 + 0.72 * i / 24, zc + 0.05 * math.sin(i / 24 * 4 * math.pi)) for i in range(25)]
            P.prism(m1 if k % 2 == 0 else m2, pts + [(x, z - 0.07) for x, z in reversed(pts)], a, b_)
    else:  # moon + star
        pts = [(0.22 * math.cos(t), cz + 0.22 * math.sin(t)) for t in np.linspace(math.pi * 0.35, math.pi * 1.65, 20)]
        inner = [(0.07 + 0.17 * math.cos(t), cz + 0.17 * math.sin(t)) for t in np.linspace(math.pi * 1.62, math.pi * 0.38, 20)]
        P.prism(m2, pts + inner, a, b_)
        P.prism(m1, [(0.2 + 0.07 * math.cos(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45),
                      cz + 0.22 + 0.07 * math.sin(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45)) for k in range(10)], a, b_)


def bunting(P, L=17.0, sag=0.6):
    """A string of felt pennant bunting swagged between two walls (origin = one end, string runs along +x), a pennant every 0.32 m
    in the palette colours, hanging on a hemp cord that sags 0.6 m in the middle."""
    length = L
    n = int(length / 0.08)
    zc = lambda x: -4 * sag * (x / length) * (1 - x / length)
    prev = None
    for i in range(n + 1):
        x = length * i / n; p_ = (x, 0, zc(x))
        if prev:
            P.rod(M["rope"], prev, p_, 0.004, seg=4)
        prev = p_
    k = 0
    x = 0.3
    while x < length - 0.3:
        z = zc(x)
        P.prism(M["felt_" + COLOURS[k % 5]], [(x - 0.12, z), (x + 0.12, z), (x, z - 0.3)], -0.003, 0.003)
        x += 0.32; k += 1


def staff_wc_fit(P):
    """Fittings of the staff toilet (a small walled, tiled room): a wall-hung WC with a blackened-steel flush plate and roll
    holder on the back wall, and a small stone basin with a spout, mirror and hook on the side wall. Origin = back wall face."""
    _wc_pan(P, 0.0)
    P.rod(M["steel"], (-0.45, 0.1, 1.65), (-0.45, 0.18, 1.65), 0.01, seg=8)
    _brush(P, (-0.4, 0.1))
    _pedal_bin(P, (0.45, 0.16), h=0.3, r=0.09)


def staff_lockers(P, n=6, w=0.38, h=1.9, d=0.5):
    """Staff lockers: tall oak doors in a run, each with a blackened-steel pull and a small oak name tag, a plinth and a top."""
    W = n * w
    P.box(M["oak"], (0, d / 2, h / 2 + 0.05), (W, d - 0.02, h))
    P.box(M["felt"], (0, d / 2, 0.025), (W, d - 0.06, 0.05))
    for k in range(n):
        x = -W / 2 + (k + 0.5) * w
        P.box(M["felt"], (x - w / 2, d - 0.005, h / 2 + 0.05), (0.004, 0.004, h))
        P.box(M["steel"], (x + w / 2 - 0.06, d + 0.012, 1.1), (0.016, 0.02, 0.22))
        P.box(M["oak"], (x, d + 0.004, h - 0.15), (0.12, 0.006, 0.04))


# ------------------------------------------------------------------ the toddler zone (0-3): Kronen + the nest (Roman: high effort)
def canopy_crown(P, rx=3.0, ry=2.3, z=2.75, ceiling=5.3, n=72):
    """'Kronen', the crown: the toddler zone's own low sky. An oval sunburst canopy hung at 2.75 m from the roof on six steel rods:
    an oak ring beam, 72 radial oak fins (30 mm) running in to a glowing linen oculus, each fin deepest at the rim (420 mm)
    and thinning to the centre, so from below it reads as a wooden flower over the nest and brings the 5.5 m room down to a
    toddler's scale. Light comes from the oculus drum and from behind the fins onto the ceiling."""
    for k in range(n):
        a = 2 * math.pi * k / n
        steps = 10
        for j in range(steps):
            t0, t1 = 0.22 + 0.78 * j / steps, 0.22 + 0.78 * (j + 1) / steps
            x0, y0 = rx * t0 * math.cos(a), ry * t0 * math.sin(a)
            x1, y1 = rx * t1 * math.cos(a), ry * t1 * math.sin(a)
            dep = 0.1 + 0.32 * ((t0 + t1) / 2 - 0.22) / 0.78
            L_ = math.hypot(x1 - x0, y1 - y0)
            P.box(M["oak"], ((x0 + x1) / 2, (y0 + y1) / 2, z + 0.42 - dep / 2), (L_ + 0.005, 0.03, dep), rz=math.atan2(y1 - y0, x1 - x0))
    b = P.bm(M["oak"]); m_ = 96  # the oval ring beam round the rim
    for k in range(m_):
        a0, a1 = 2 * math.pi * k / m_, 2 * math.pi * (k + 1) / m_
        q = [(rx * math.cos(a0), ry * math.sin(a0)), (rx * math.cos(a1), ry * math.sin(a1)),
             (rx * 1.03 * math.cos(a1), ry * 1.03 * math.sin(a1)), (rx * 1.03 * math.cos(a0), ry * 1.03 * math.sin(a0))]
        lo = [b.verts.new((x, y, z)) for x, y in q]; hi = [b.verts.new((x, y, z + 0.44)) for x, y in q]
        b.faces.new(lo[::-1]); b.faces.new(hi)
        for i in range(4):
            b.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]))
    # the oculus: a linen drum glowing warm, an oak lip
    ox, oy = rx * 0.22, ry * 0.22
    P.cyl(M["linen"], (0, 0, z + 0.12), ox, 0.3, seg=48)
    P.cyl(M["oak"], (0, 0, z + 0.1), ox + 0.03, 0.03, seg=48)
    for k in range(6):  # hangers to the roof
        a = 2 * math.pi * k / 6 + 0.3
        P.rod(M["steel"], (rx * 0.9 * math.cos(a), ry * 0.9 * math.sin(a), z + 0.44), (rx * 0.9 * math.cos(a), ry * 0.9 * math.sin(a), ceiling), 0.005, seg=6)


def nest(P, rx=2.6, ry=2.1):
    """The nest: an oval oak amphitheatre for crawlers and new walkers. From the floor two 150 mm steps (oak treads, wool-felt
    tops) climb to an upholstered rim, then two steps go down again into a soft pit of thick wool felt (top 0.08) full of
    cushions; a gentle oak ramp runs in from the south (-y) for crawlers. Low edges everywhere: nothing to fall from."""
    def ring(f0, f1, ztop, mat, gap=None, n=96):
        b = P.bm(mat)
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            am = (a0 + a1) / 2
            if gap and abs(((am - gap[0]) + math.pi) % (2 * math.pi) - math.pi) < gap[1]:
                continue
            q = [(rx * f0 * math.cos(a0), ry * f0 * math.sin(a0)), (rx * f0 * math.cos(a1), ry * f0 * math.sin(a1)),
                 (rx * f1 * math.cos(a1), ry * f1 * math.sin(a1)), (rx * f1 * math.cos(a0), ry * f1 * math.sin(a0))]
            lo = [b.verts.new((x, y, 0.0)) for x, y in q]; hi = [b.verts.new((x, y, ztop)) for x, y in q]
            b.faces.new(lo[::-1]); b.faces.new(hi)
            for i in range(4):
                b.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]))
    gap = (-math.pi / 2, 0.22)  # the ramp into the pit, from the south
    tiers = [(1.0, 0.86, 0.15, "felt_oat"), (0.86, 0.72, 0.30, "felt_moss"), (0.72, 0.6, 0.22, "felt_cloud"), (0.6, 0.48, 0.15, "felt_heather")]
    for f0, f1, zt, c in tiers:
        ring(f1, f0, zt - 0.02, M["oak"], gap)
        ring(f1 + 0.005, f0 - 0.005, zt, M[c], gap)
    b = P.bm(M["felt_fjord"]); n = 64  # the pit: thick wool felt
    vs = [b.verts.new((0, 0, 0.08))] + [b.verts.new((rx * 0.48 * math.cos(2 * math.pi * k / n), ry * 0.48 * math.sin(2 * math.pi * k / n), 0.08)) for k in range(n)]
    for k in range(n):
        b.faces.new((vs[0], vs[k + 1], vs[(k + 1) % n + 1]))
    P.box(M["oak"], (0, -ry * 0.78, 0.04), (0.9, ry * 0.6, 0.08))  # the ramp in (a gentle 80 mm)
    for k, (x, y, c) in enumerate(((-0.5, 0.2, "heather"), (0.45, 0.35, "cloud"), (0.0, -0.25, "moss"), (0.6, -0.3, "lingon"))):
        P.blob(M["felt_" + c], (x, y, 0.16), (0.3, 0.26, 0.09), z_cut=0.08)
    P.blob(M["felt_oat"], (-0.35, -0.35, 0.2), (0.12, 0.12, 0.12))  # a soft ball


def pikler_arch(P):
    """Pikler climbing arch in oak (for 1-3): a wide, low A-frame with round rungs 150 mm apart, and a slatted ramp hooked onto
    one side (climb up, slide or walk down). Wide feet, rounded everywhere."""
    w, h = 1.0, 0.85
    for s_ in (-1, 1):
        for x in (-0.45, 0.45):
            P.rod(M["oak"], (x, s_ * 0.55, 0.0), (x, s_ * 0.03, h), 0.022, seg=10)
    for k in range(1, 6):
        z = k * h / 6; yy = 0.55 * (1 - z / h)
        for s_ in (-1, 1):
            P.rod(M["oak"], (-0.45, s_ * yy, z), (0.45, s_ * yy, z), 0.014, seg=10)
    P.rod(M["oak"], (-0.45, 0, h), (0.45, 0, h), 0.02, seg=10)
    ang = math.atan2(h - 0.05, 1.2)
    P.box(M["oak"], (0, 0.55 + 0.6, (h - 0.05) / 2), (0.55, math.hypot(1.2, h - 0.05), 0.03), rx=-ang)
    for t in np.linspace(0.1, 0.9, 6):
        P.box(M["oak"], (0, 0.55 + 1.2 * t, (h - 0.05) * (1 - t) + 0.025), (0.5, 0.02, 0.012), rx=-ang)


def window_nest(P, L=7.0):
    """Window nest along the forest glass: a low oak platform (0.2 high, 0.85 deep) with a long wool cushion and bolsters, and a
    low oak rail 0.45 above it a hand's width off the glass, so toddlers can kneel and watch birds and trees; slatted kick
    face. Origin = glass line, front +y."""
    P.box(M["oak"], (0, 0.45, 0.1), (L, 0.85, 0.2))
    for x in np.arange(-L / 2 + 0.03, L / 2, 0.065):
        P.box(M["oak"], (x, 0.88, 0.1), (0.045, 0.02, 0.18))
    P.box(M["felt_oat"], (0, 0.47, 0.25), (L - 0.1, 0.78, 0.1))
    for x in np.arange(-L / 2 + 0.5, L / 2, 1.4):
        P.rod(M["felt_" + COLOURS[int((x + L) * 3) % 5]], (x - 0.3, 0.12, 0.38), (x + 0.3, 0.12, 0.38), 0.1, seg=16)
    for x in np.arange(-L / 2 + 0.2, L / 2, 1.1):
        P.rod(M["oak"], (x, 0.1, 0.2), (x, 0.1, 0.68), 0.016, seg=8)
    P.rod(M["oak"], (-L / 2 + 0.2, 0.1, 0.68), (L / 2 - 0.2, 0.1, 0.68), 0.02, seg=12)


def sensory_panel(P, w=1.2, h=1.0, z0=0.2, style="maze"):
    """Sensory wall panel at toddler height in an oak frame: 'maze' = a bead maze of bent steel wires with oak beads, spinning oak
    discs and a row of textured felt squares; 'peek' = felt peekaboo flaps over little mirrors, pockets and a soft felt tree."""
    P.box(M["oak"], (0, 0.015, z0 + h / 2), (w, 0.03, h))
    if style == "maze":
        for k, c in enumerate(("lingon", "fjord", "cloud")):
            pts = [(-w / 2 + 0.12 + (w - 0.24) * i / 12, z0 + 0.25 + 0.18 * k + 0.08 * math.sin(i * 0.9 + k)) for i in range(13)]
            for (x0, z0_), (x1, z1_) in zip(pts, pts[1:]):
                P.rod(M["steel"], (x0, 0.08, z0_), (x1, 0.08, z1_), 0.004, seg=6)
            for i in (2, 5, 9):
                P.blob(M["lino_" + c], (pts[i][0], 0.08, pts[i][1]), (0.03, 0.03, 0.03))
        for k in range(3):
            P.box(M["oak"], (-w / 2 + 0.2 + k * 0.35, 0.04, z0 + 0.12), (0.2, 0.02, 0.2), ry=0.3 * k)
        for k in range(5):
            P.box(M["felt_" + COLOURS[k]], (-w / 2 + 0.15 + k * 0.22, 0.035, z0 + h - 0.12), (0.18, 0.012, 0.15))
    else:
        for k in range(3):
            x = -w / 2 + 0.22 + k * 0.38
            P.box(M["mirror"], (x, 0.033, z0 + 0.65), (0.22, 0.004, 0.2))
            P.box(M["felt_" + COLOURS[k + 1]], (x, 0.04, z0 + 0.72), (0.26, 0.008, 0.18), rx=-0.25)
        for k in range(4):
            P.box(M["felt_" + COLOURS[(k + 3) % 5]], (-w / 2 + 0.18 + k * 0.28, 0.04, z0 + 0.22), (0.2, 0.015, 0.2))
        P.prism(M["felt_moss"], [(0.42, z0 + 0.9), (0.55, z0 + 0.45), (0.29, z0 + 0.45)], 0.03, 0.04)


def toddler_table(P, L=1.6, d=0.8, h=0.42):
    """Low oval oak table for snacks and play at toddler height (0.42), a rounded edge all round."""
    b = P.bm(M["oak"]); n = 48
    top = [b.verts.new((L / 2 * math.cos(2 * math.pi * k / n), d / 2 * math.sin(2 * math.pi * k / n), h)) for k in range(n)]
    bot = [b.verts.new((L / 2 * math.cos(2 * math.pi * k / n), d / 2 * math.sin(2 * math.pi * k / n), h - 0.03)) for k in range(n)]
    b.faces.new(top); b.faces.new(bot[::-1])
    for k in range(n):
        b.faces.new((bot[k], bot[(k + 1) % n], top[(k + 1) % n], top[k]))
    for x in (-L / 2 + 0.25, L / 2 - 0.25):
        for y in (-0.2, 0.2):
            P.rod(M["oak"], (x * 1.05, y * 1.2, 0), (x, y, h - 0.03), 0.025, 0.03, seg=12)


# ------------------------------------------------------------------ detail pass: reception, public WCs, cafe, building services
def _sign_text(P, mat, txt, c, size):
    for i, line in enumerate(txt.split("|")):
        P.text(mat, line, (c[0], c[1], c[2] - i * size * 1.5), size)


def wall_sign(P, text="WC", w=0.6, h=0.2, mount=2.2, size=0.05, blade=False):
    """Wayfinding sign: a white-oiled oak plate (20 mm) with the words burnt in, Norwegian + English on two lines ('|' splits).
    blade=True projects it off the wall on a blackened-steel bracket, read from both sides."""
    z = mount
    burnt = bc.material("burnt_text", (0.035, 0.022, 0.014), 0.75)
    if blade:
        P.box(M["steel"], (0, 0.04, z + h / 2 + 0.03), (0.02, 0.08, 0.02))
        P.box(M["oak"], (0, 0.08 + w / 2, z), (0.02, w, h))
        return
    P.box(M["oak"], (0, 0.01, z), (w, 0.02, h))
    lines = text.split("|")
    _sign_text(P, burnt, text, (0, 0.0215, z + (len(lines) - 1) * size * 0.75), size)


def exit_sign(P, mount=2.45, hang_to=None):
    """Emergency exit sign (lit, battery-backed): the green running-man panel in a slim blackened-steel frame, over every exit.
    hang_to = a ceiling / beam height: hung on two steel rods, lit both faces (where no wall carries it, e.g. the bridge)."""
    z = mount
    if hang_to:
        for x in (-0.14, 0.14):
            P.rod(M["steel"], (x, 0.02, z + 0.08), (x, 0.02, hang_to), 0.002, seg=6)
        exit_sign(P, mount)
        P.box(M["exit_green"], (0, -0.001, z), (0.33, 0.004, 0.13))
        P.box(M["exit_white"], (0.06, -0.004, z), (0.03, 0.002, 0.08)); P.box(M["exit_white"], (-0.06, -0.004, z), (0.1, 0.002, 0.02))
        return
    g = M.setdefault("exit_green", bc.material("exit_green", (0.05, 0.5, 0.2), 0.4, emit=((0.1, 0.9, 0.35), 4.0)))
    P.box(M["steel"], (0, 0.02, z), (0.36, 0.04, 0.16))
    P.box(g, (0, 0.041, z), (0.33, 0.004, 0.13))
    w_ = M.setdefault("exit_white", bc.material("exit_white", (0.9, 0.95, 0.9), 0.4, emit=((1, 1, 1), 3.0)))
    P.box(w_, (-0.06, 0.044, z), (0.03, 0.002, 0.08))
    P.box(w_, (0.06, 0.044, z), (0.1, 0.002, 0.02))


def safety_point(P, aed=True):
    """Safety point on a wall: a hjertestarter (AED) in a wall cabinet with its green sign, and a 6 kg extinguisher in an oak-door
    cabinet with a small red sign; a first-aid kit beside them."""
    burnt = M.setdefault("sign_white", bc.material("sign_white", (0.92, 0.92, 0.9), 0.5))
    red = M.setdefault("sign_red", bc.material("sign_red", (0.55, 0.05, 0.04), 0.5))
    green = M.setdefault("sign_green", bc.material("sign_green", (0.04, 0.4, 0.18), 0.5))
    if aed:
        P.box(M["steel"], (-0.35, 0.09, 1.3), (0.42, 0.18, 0.42))
        P.box(M["glass"], (-0.35, 0.181, 1.3), (0.38, 0.004, 0.38))
        P.box(green, (-0.35, 0.12, 1.4), (0.24, 0.1, 0.24))
        P.box(green, (-0.35, 0.01, 1.68), (0.3, 0.02, 0.16))
        P.text(burnt, "AED", (-0.35, 0.022, 1.67), 0.07)
    P.box(M["oak"], (0.2, 0.09, 0.75), (0.4, 0.18, 0.75))
    P.box(red, (0.2, 0.01, 1.3), (0.2, 0.02, 0.2))
    P.text(burnt, "BRANN", (0.2, 0.022, 1.29), 0.04)
    P.box(M["felt_moss"], (0.2, 0.09, 1.55), (0.3, 0.16, 0.2))      # first-aid kit
    P.box(burnt, (0.2, 0.171, 1.55), (0.06, 0.004, 0.02)); P.box(burnt, (0.2, 0.171, 1.55), (0.02, 0.004, 0.06))


def ceiling_services(P, z_local=4.93, ceiling=5.5, device="sprinkler"):
    """Ceiling services, as a real building needs (TEK17): a pendent sprinkler (chrome head + deflector on a drop pipe) or an optical
    smoke detector (white disc with a red pilot light), dropped to just below the wave fins."""
    z = z_local
    P.rod(M["brushed"], (0, 0, z + 0.04), (0, 0, ceiling), 0.012, seg=8)
    if device == "sprinkler":
        P.cyl(M["brushed"], (0, 0, z), 0.02, 0.04, seg=12)
        P.cyl(M["brushed"], (0, 0, z - 0.012), 0.03, 0.004, seg=16)
    else:
        P.cyl(M["ceramic"], (0, 0, z - 0.03), 0.055, 0.045, seg=24, r2=0.05)
        P.cyl(M["lino_lingon"], (0.03, 0, z - 0.032), 0.004, 0.002, seg=8)


def floor_drain(P, w=0.15):
    """Floor drain in a wet floor: a square blackened-steel grate with slots, flush with the stone."""
    P.box(M["steel"], (0, 0, 0.001), (w, w, 0.002))
    for k in range(5):
        P.box(M["felt"], (-w / 2 + (k + 1) * w / 6, 0, 0.0022), (0.006, w - 0.03, 0.0005))


def amenity_tray(P, products=False):
    """Vanity tray: an oak tray with a hand-cream and a hand-wash bottle in amber glass; with products=True a small felt basket of
    complimentary period products."""
    amber = M.setdefault("amber_glass", bc.arch_glass("amber_glass", tint=(0.75, 0.45, 0.15)))
    P.box(M["oak"], (0, 0.25, 0.006), (0.32, 0.14, 0.012))
    for x in (-0.07, 0.07):
        P.cyl(amber, (x, 0.25, 0.012), 0.03, 0.14, seg=16)
        P.cyl(M["steel"], (x, 0.25, 0.152), 0.012, 0.03, seg=10)
    if products:
        P.box(M["felt_oat"], (0.3, 0.25, 0.05), (0.18, 0.12, 0.1))
        for k in range(3):
            P.box(M["lino_" + COLOURS[k + 2]], (0.26 + k * 0.04, 0.25, 0.11), (0.03, 0.08, 0.05))


def table_setting(P, carafe=True):
    """What sits on a cafe table: a tealight in a smoked-glass holder (a real small flame: hygge), a water carafe with two glasses,
    and a small oak card stand with the menu."""
    flame = M.setdefault("tealight", bc.material("tealight", (1.0, 0.8, 0.5), 0.5, emit=((1.0, 0.7, 0.35), 18.0)))
    P.cyl(M["glass"], (0, 0, 0.0), 0.035, 0.07, seg=16)
    P.cyl(M["ceramic"], (0, 0, 0.005), 0.019, 0.015, seg=12)
    P.cyl(flame, (0, 0, 0.022), 0.003, 0.012, seg=6, r2=0.0)
    if carafe:
        P.cyl(M["glass"], (0.14, 0.05, 0.0), 0.045, 0.2, seg=20, r2=0.03)
        for dx in (-0.12, -0.2):
            P.cyl(M["glass"], (dx, 0.08, 0.0), 0.032, 0.09, seg=16)
    P.box(M["oak"], (0.05, -0.1, 0.01), (0.1, 0.04, 0.02))
    P.box(M["pad"], (0.05, -0.1, 0.075), (0.1, 0.004, 0.13), rx=-0.15)


def water_station(P, L=1.6):
    """Self-service station: an oak cabinet with a light stone top (0.9), a still/sparkling water tap over a steel drip tray, glass
    carafes, glasses upside down on an oak tray, an oak caddy of cutlery and napkins, a stack of trays; waste sorting in the base."""
    d = 0.55
    P.box(M["oak"], (0, d / 2, 0.44), (L, d, 0.88))
    P.box(M["stone"], (0, d / 2, 0.895), (L + 0.02, d + 0.02, 0.03))
    P.box(M["steel"], (-0.5, 0.06, 1.2), (0.2, 0.12, 0.5))
    P.rod(M["steel"], (-0.5, 0.12, 1.15), (-0.5, 0.25, 1.15), 0.01, seg=8)
    P.box(M["brushed"], (-0.5, 0.28, 0.915), (0.3, 0.2, 0.01))
    for k in range(3):
        P.cyl(M["glass"], (-0.15 + k * 0.1, 0.3, 0.91), 0.045, 0.22, seg=20, r2=0.03)
    P.box(M["oak"], (0.32, 0.3, 0.915), (0.36, 0.26, 0.012))
    for i in range(3):
        for j in range(2):
            P.cyl(M["glass"], (0.22 + i * 0.1, 0.24 + j * 0.12, 0.92), 0.032, 0.09, seg=14)
    P.box(M["oak"], (0.65, 0.3, 0.97), (0.22, 0.14, 0.12))
    for k in range(3):
        P.rod(M["brushed"], (0.59 + k * 0.06, 0.3, 0.96), (0.59 + k * 0.06, 0.3, 1.1), 0.006, seg=6)
    for k in range(4):
        P.box(M["oak"], (0.0, 0.3, 0.92 + k * 0.022), (0.46, 0.34, 0.012))
    for k, c in enumerate(("oat", "fjord", "cloud", "moss")):  # waste sorting doors in the base
        P.box(M["felt_" + c], (-L / 2 + (k + 0.5) * L / 4, d + 0.004, 0.7), (0.12, 0.004, 0.05))
        P.box(M["felt"], (-L / 2 + k * L / 4, d + 0.002, 0.44), (0.004, 0.004, 0.84))


def menu_board(P):
    """Menu on the bar: an oak board on a blackened-steel stand, the drinks and prices burnt in (NOK)."""
    burnt = bc.material("burnt_text", (0.035, 0.022, 0.014), 0.75)
    P.box(M["steel"], (0, 0, 0.005), (0.3, 0.12, 0.01))
    P.rod(M["steel"], (0, 0, 0.01), (0, 0.02, 0.3), 0.008, seg=8)
    P.box(M["oak"], (0, 0.03, 0.42), (0.5, 0.02, 0.5))
    lines = ["KAFFE", "Espresso  38", "Cortado  45", "Cappuccino  52", "Filter  39", "Te  42", "Kanelbolle  49"]
    for i, t in enumerate(lines):
        P.text(burnt, t, (0, 0.0415, 0.63 - i * 0.065), 0.04 if i == 0 else 0.03)


def high_chair(P):
    """Oak high chair for the youngest at the cafe tables: seat at 0.55, splayed legs, footrest, a removable oak tray, a felt pad."""
    s_ = 0.36
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.rod(M["oak"], (sx * 0.26, sy * 0.26, 0), (sx * 0.15, sy * 0.15, 0.55), 0.018, seg=10)
    P.box(M["oak"], (0, 0, 0.55), (s_, s_, 0.025))
    P.box(M["felt_oat"], (0, 0, 0.575), (s_ - 0.04, s_ - 0.04, 0.025))
    P.box(M["oak"], (0, -0.17, 0.82), (s_, 0.02, 0.5))
    for sx in (-1, 1):
        P.box(M["oak"], (sx * 0.17, 0.0, 0.72), (0.02, s_, 0.3))
    P.box(M["oak"], (0, 0.24, 0.75), (s_ + 0.06, 0.2, 0.02))
    lx = 0.26 - 0.11 * 0.3 / 0.55  # the front legs' centre at the footrest height: it is let into them
    P.box(M["oak"], (0, lx, 0.3), (2 * lx + 0.03, 0.12, 0.02))


def coat_rack(P):
    """Coat stand by the waiting nook: an oak post on a blackened-steel foot with oak pegs at two heights; beside it a steel
    umbrella stand with two umbrellas."""
    P.cyl(M["steel"], (0, 0, 0), 0.22, 0.015, seg=32)
    P.rod(M["oak"], (0, 0, 0.0), (0, 0, 1.8), 0.025, seg=12)
    for k in range(6):
        a = 2 * math.pi * k / 6; z = 1.7 if k % 2 else 1.45
        P.rod(M["oak"], (0, 0, z), (0.16 * math.cos(a), 0.16 * math.sin(a), z + 0.06), 0.012, seg=8)
    P.cyl(M["steel"], (0.45, 0, 0), 0.12, 0.55, seg=24)
    for dx, c in ((0.42, "fjord"), (0.49, "oat")):
        P.rod(M["lino_" + c], (dx, 0, 0.1), (dx, 0, 0.85), 0.03, 0.008, seg=8)
        P.rod(M["oak"], (dx, 0, 0.85), (dx, 0, 0.95), 0.012, seg=8)


def floor_lamp(P):
    """Reading lamp by the lounge chairs: blackened-steel stem and base, an oat linen drum shade, warm light."""
    P.cyl(M["steel"], (0, 0, 0), 0.16, 0.02, seg=32)
    P.rod(M["steel"], (0, 0, 0.02), (0, 0, 1.45), 0.01, seg=8)
    P.cyl(M["linen"], (0, 0, 1.3), 0.2, 0.28, seg=32, r2=0.18)


def magazines(P):
    """A stack of magazines and two books on a side table."""
    for k in range(4):
        P.box(M["lino_" + COLOURS[k % 5]] if k % 2 else M["pad"], (0, 0, 0.005 + k * 0.006), (0.22, 0.29, 0.005), rz=0.08 * k)
    P.box(M["lino_moss"], (0.05, 0.02, 0.035), (0.15, 0.22, 0.03), rz=-0.2)


# ------------------------------------------------------------------ cafe rethink (Roman, 2026-10-12): pictograms, a lounge, a centrepiece
def _circle(cx, cz, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * k / n), cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def pictogram(P, figure="woman", size=0.3, mount=1.6):
    """Pictogram sign: a blackened-steel square plate (size, 6 mm) with the figure raised 3 mm in brass (the brass accent).
    Kinds: woman, man, accessible, baby (changing), gym (dumbbell + arrow pointing local +x), child (daycare: a small figure
    holding a big one's hand), lift (car with up/down arrows). Origin = wall face, plate centre at 'mount'."""
    br = M["brass"]; s_ = size / 0.3; z = mount; kind = figure
    P.box(M["steel"], (0, 0.003, z), (size, 0.006, size))
    y0, y1 = 0.006, 0.009
    f = lambda pts: P.prism(br, [(x * s_, z + zz * s_) for x, zz in pts], y0, y1)
    def person(cx, sc=1.0, dress=False):
        f(_circle(cx, 0.075 * sc, 0.022 * sc))
        if dress:
            f([(cx - 0.042 * sc, -0.035 * sc), (cx + 0.042 * sc, -0.035 * sc), (cx + 0.022 * sc, 0.045 * sc), (cx - 0.022 * sc, 0.045 * sc)])
        else:
            f(_rect(cx - 0.025 * sc, -0.02 * sc, cx + 0.025 * sc, 0.045 * sc))
        for dx in (-0.012, 0.012):
            f(_rect(cx + dx * sc - 0.008 * sc, -0.1 * sc, cx + dx * sc + 0.008 * sc, -0.02 * sc))
    if kind == "woman":
        person(0.0, 1.0, dress=True)
    elif kind == "man":
        person(0.0)
    elif kind == "accessible":
        f(_circle(-0.005, 0.085, 0.02))
        f(_rect(-0.02, -0.01, 0.0, 0.06))                       # torso
        f(_rect(-0.02, -0.01, 0.045, 0.008))                    # thigh
        f(_rect(0.03, -0.075, 0.045, 0.008))                    # shin
        for k in range(20):                                     # the wheel: an arc of small segments
            a0, a1 = math.radians(60 + k * 12), math.radians(60 + (k + 1) * 12)
            r0, r1 = 0.05, 0.062
            f([(-0.01 + r0 * math.cos(a0), -0.04 + r0 * math.sin(a0)), (-0.01 + r1 * math.cos(a0), -0.04 + r1 * math.sin(a0)),
               (-0.01 + r1 * math.cos(a1), -0.04 + r1 * math.sin(a1)), (-0.01 + r0 * math.cos(a1), -0.04 + r0 * math.sin(a1))])
    elif kind == "baby":
        f(_rect(-0.09, -0.06, 0.09, -0.045))                    # changing table
        f(_circle(-0.06, -0.025, 0.018)); f(_rect(-0.04, -0.04, 0.06, -0.012))
        person(0.03, 0.75)
    elif kind == "gym":
        f(_rect(-0.07, 0.035, 0.07, 0.045))
        for x in (-0.06, 0.06):
            f(_rect(x - 0.012, 0.01, x + 0.012, 0.07))
        f(_rect(-0.06, -0.06, 0.04, -0.045))
        f([(0.04, -0.08), (0.09, -0.0525), (0.04, -0.025)])
    elif kind == "child":
        person(-0.03, 1.0); person(0.045, 0.6)
        f(_rect(-0.01, 0.0, 0.035, 0.008))
    elif kind == "lift":
        f(_rect(-0.05, -0.09, 0.05, 0.09)); P.box(M["steel"], (0, 0.0095, z), (0.07 * s_, 0.001, 0.15 * s_))
        f([(-0.025, 0.01), (0.025, 0.01), (0.0, 0.05)]); f([(-0.025, -0.01), (0.025, -0.01), (0.0, -0.05)])


def portal_frame(P, width=1.6, height=2.4, depth=0.25):
    """Blackened-steel portal lining an opening: jambs + head as 10 mm plates the full wall depth, with a 40 mm face flange on the
    front (+y) side, so the entrance reads as a crafted frame in the slat wall."""
    st = M["steel"]
    for x in (-width / 2, width / 2):
        P.box(st, (x, -depth / 2, height / 2), (0.01, depth, height))
        P.box(st, (x + (0.02 if x > 0 else -0.02), 0.004, height / 2), (0.05, 0.008, height + 0.05))
    P.box(st, (0, -depth / 2, height), (width, depth, 0.01))
    P.box(st, (0, 0.004, height + 0.02), (width + 0.09, 0.008, 0.05))


def conversation_ring(P, r=2.0, gaps=((30.0, 32.0), (210.0, 32.0))):
    """'Steinringen': a built-in curved banquette round the boulder, the cafe's centrepiece for meeting people. An oak plinth ring
    (seat 0.42, 0.6 deep), oat wool seat cushions in segments, a raked oak backrest with wool back cushions, outward-facing
    oak back skin with the slat language; open in two places (gaps = (angle, width deg))."""
    seat_in, seat_out = r - 0.68, r - 0.08
    def arcs():
        cuts = sorted([(a - w / 2, a + w / 2) for a, w in gaps])
        for (a0, a1), (b0, b1) in zip(cuts, cuts[1:] + [(cuts[0][0] + 360, 0)]):
            yield a1, b0
    for a0, a1 in arcs():
        P.ring(M["oak"], (0, 0), seat_in, seat_out, 0.0, 0.32, a0, a1, seg=160)
        P.ring(M["felt"], (0, 0), seat_in + 0.04, seat_out - 0.04, 0.0, 0.06, a0, a1, seg=160)
        n = max(1, int((a1 - a0) / 18))
        for k in range(n):  # cushion segments with 8 mm gaps
            c0, c1 = a0 + (a1 - a0) * k / n + 0.3, a0 + (a1 - a0) * (k + 1) / n - 0.3
            P.ring(M["boucle"], (0, 0), seat_in + 0.02, seat_out - 0.02, 0.32, 0.43, c0, c1, seg=48)
            P.ring(M["boucle"], (0, 0), seat_out - 0.14, seat_out - 0.02, 0.45, 0.82, c0, c1, seg=48)  # back cushion
        P.ring(M["oak"], (0, 0), seat_out, r, 0.0, 0.86, a0, a1, seg=160)  # backrest wall
        P.ring(M["oak"], (0, 0), seat_out - 0.02, r + 0.02, 0.86, 0.9, a0, a1, seg=160)  # oak cap
        ns = int(math.radians(a1 - a0) * (r + 0.01) / 0.065)
        for k in range(ns):  # slats on the outside
            a = math.radians(a0 + (a1 - a0) * (k + 0.5) / ns)
            P.box(M["oak"], ((r + 0.012) * math.cos(a), (r + 0.012) * math.sin(a), 0.43), (0.022, 0.045, 0.82), rz=a)


def _honed_granite(name="granite_honed"):
    """Sawn + honed grey granite: a flat face (no bump), a fine salt-and-pepper of quartz, feldspar and mica crystals from two
    Voronoi scales over a soft cloudy grey, a satin sheen."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; tc = N.new("ShaderNodeTexCoord")
    cloud = N.new("ShaderNodeTexNoise"); cloud.inputs["Scale"].default_value = 3.0; L.new(tc.outputs["Object"], cloud.inputs["Vector"])
    v1 = N.new("ShaderNodeTexVoronoi"); v1.inputs["Scale"].default_value = 180.0; L.new(tc.outputs["Object"], v1.inputs["Vector"])
    v2 = N.new("ShaderNodeTexVoronoi"); v2.inputs["Scale"].default_value = 520.0; L.new(tc.outputs["Object"], v2.inputs["Vector"])
    r1 = N.new("ShaderNodeValToRGB"); L.new(v1.outputs["Color"], r1.inputs["Fac"])
    e = r1.color_ramp.elements; e[0].position = 0.35; e[0].color = (0.05, 0.05, 0.055, 1); e[1].position = 0.55; e[1].color = (0.42, 0.41, 0.4, 1)
    r2 = N.new("ShaderNodeValToRGB"); L.new(v2.outputs["Color"], r2.inputs["Fac"])
    e = r2.color_ramp.elements; e[0].position = 0.6; e[0].color = (0.2, 0.2, 0.2, 1); e[1].position = 0.7; e[1].color = (0.75, 0.73, 0.7, 1)
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["Factor"].default_value = 0.35
    L.new(r1.outputs["Color"], mx.inputs["A"]); L.new(r2.outputs["Color"], mx.inputs["B"])
    mc = N.new("ShaderNodeMix"); mc.data_type = "RGBA"; mc.blend_type = "MULTIPLY"; mc.inputs["Factor"].default_value = 0.3
    L.new(mx.outputs["Result"], mc.inputs["A"]); L.new(cloud.outputs["Color"], mc.inputs["B"])
    L.new(mc.outputs["Result"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.28
    return m


def boulder_table(P, L=1.6, D=1.15, h=0.42, seed=7):
    """'Flyttblokk': a glacial granite erratic as the table in the ring: a rounded, weathered boulder with its top sawn flat and
    honed (a dark polished granite plane showing the crystals), the rest left raw. Mesh: a subdivided sphere scaled to the
    boulder, displaced by low-frequency noise, cut flat at h (top) and 0 (floor)."""
    rng = np.random.default_rng(seed)
    b = P.bm(M.setdefault("granite_raw", bc.pbr_material("granite_raw", "dark_rock", 1.4, box=True, tint=(0.82, 0.8, 0.78), rough_add=0.25, piece_var=0.0, sat=0.45, val=1.9)))
    g = bmesh.ops.create_icosphere(b, subdivisions=4, radius=1.0)["verts"]
    waves = [(rng.normal(size=3), rng.uniform(0, 6.28), rng.uniform(0.03, 0.07)) for _ in range(7)]
    for v in g:
        p = Vector(v.co)
        d = 1.0 + sum(a * math.sin(k_.dot(p) * 2.2 + ph) for k_, ph, a in waves)
        p = p * d
        v.co = (p.x * L / 2, p.y * D / 2, (p.z * 0.5 + 0.38) * h * 1.15)
        v.co.z = min(max(v.co.z, 0.0), h)
    bmesh.ops.remove_doubles(b, verts=g, dist=0.0005)
    top = P.bm(M.setdefault("granite_tiled", bc.pbr_material("granite_tiled", "granite_tile", 0.6, box=True, tint=(0.75, 0.73, 0.72),
                                                                rough_mul=0.35, rough_add=0.02, piece_var=0.0, sat=0.6, val=0.9)))  # Roman preferred the gridded top
    # the sawn top: the outline of the boulder at h, as a flat honed face just proud of the raw mesh
    pts = []
    for k in range(64):
        a = 2 * math.pi * k / 64; p = Vector((math.cos(a), math.sin(a), 0.62))
        d = 1.0 + sum(am * math.sin(k_.dot(p) * 2.2 + ph) for k_, ph, am in waves)
        pts.append((p.x * d * L / 2 * 0.86, p.y * d * D / 2 * 0.86))
    vs = [top.verts.new((x, y, h + 0.001)) for x, y in pts]
    top.faces.new(vs)


def elva(P, pts=((0, 0), (2.2, -3.0), (5.6, -5.4), (9.8, -6.2), (13.0, -5.9)), n=230, base=2.75, ceiling=5.45):
    """'Elva' (the river): a suspended sculpture tracing the Glomma through the room, seen from above. ~230 thin fins (14 x 140 mm,
    0.6-1.0 m tall) hung on fine steel wires along a winding line, each turned to follow the current, lower edges rippling
    between 2.75 and 3.2 m. Colour (Roman): the river's middle runs in lacquered glacier teal and deep fjord blue, the banks are
    white-oiled oak; every fin has a polished brass edge at its tip (the accent catching the light) and nine mirror-polished steel
    fish (trout + grayling) swim upstream through it. Origin = the first point of the line, at the floor."""
    glacier = M.setdefault("lacquer_glacier", bc.material("lacquer_glacier", (0.33, 0.52, 0.55), 0.22))
    fjord = M.setdefault("lacquer_fjord", bc.material("lacquer_fjord", (0.07, 0.15, 0.26), 0.22))
    mist = M.setdefault("lacquer_mist", bc.material("lacquer_mist", (0.62, 0.72, 0.72), 0.25))
    fishm = M.setdefault("polished_steel", bc.metal_material("polished_steel", (0.92, 0.92, 0.9), rough=(0.02, 0.06), brushed=False))
    rng = np.random.default_rng(12)
    P_ = [Vector((x, y, 0)) for x, y in pts]
    def at(t):  # Catmull-Rom through the points, t in [0, 1]
        segs = len(P_) - 1; u = min(t * segs, segs - 1e-6); i = int(u); f = u - i
        p0, p1, p2, p3 = P_[max(i - 1, 0)], P_[i], P_[i + 1], P_[min(i + 2, segs)]
        return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)
    def frame(t):
        c = at(t); tg = (at(min(1.0, t + 0.002)) - at(max(0.0, t - 0.002))).normalized()
        return c, tg, Vector((-tg.y, tg.x, 0))
    def water(t):  # the colour down the river: mist at the source, glacier teal, deep fjord blue in the pools, back to teal
        g = 0.5 + 0.5 * math.sin(t * math.pi * 3.0 - 1.0) + rng.normal(0, 0.12)
        return fjord if g > 0.72 else (glacier if g > 0.3 else mist)
    for k in range(n):
        t = k / (n - 1)
        c, tg, nrm = frame(t)
        width = 0.3 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 3.0))  # the river widens + narrows
        lanes = (-width / 2, 0.0, width / 2) if width > 0.45 else (-width / 2, width / 2)
        for j, off in enumerate(lanes):
            p = c + nrm * off
            mat = M["oak"] if (j == len(lanes) - 1 and len(lanes) == 3 and k % 2) else water(t)  # coloured water, oak glints at the bank
            hgt = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 17.0 + 2 * j))
            z0 = base + 0.45 * (0.5 + 0.5 * math.sin(t * 9.0 + 1.3 * j))
            rz = math.atan2(tg.y, tg.x) + math.pi / 2 + 0.3 * math.sin(t * 23 + j)  # fins stand ACROSS the current, like ripples
            P.box(mat, (p.x, p.y, z0 + hgt / 2), (0.16, 0.014, hgt), rz=rz)
            P.box(M["brass"], (p.x, p.y, z0 + 0.004), (0.162, 0.016, 0.008), rz=rz)   # brass tip
            if k % 3 == 0:
                P.rod(M["steel"], (p.x, p.y, z0 + hgt), (p.x, p.y, ceiling), 0.0012, seg=4)
    for i in range(9):  # fish swimming upstream (against the line's direction), just under the fins
        t = 0.08 + 0.1 * i + rng.uniform(-0.02, 0.02)
        c, tg, nrm = frame(t)
        p = c + nrm * rng.uniform(-0.15, 0.15)
        z = base - 0.18 - rng.uniform(0.0, 0.25)
        L = 0.42 if i % 3 == 0 else 0.3  # trout bigger, grayling smaller
        body = [(L / 2 * math.cos(a), 0.11 * L * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        tail = [(-L / 2 + 0.02, 0.0), (-L / 2 - 0.12 * L / 0.3, 0.06), (-L / 2 - 0.1 * L / 0.3, 0.0), (-L / 2 - 0.12 * L / 0.3, -0.06)]
        ang = math.atan2(-tg.y, -tg.x)  # facing upstream
        for shape in (body, tail):
            b = P.bm(fishm)
            v0 = [b.verts.new((p.x + x * math.cos(ang), p.y + x * math.sin(ang), z + zz)) for x, zz in shape]
            off = Vector((-math.sin(ang), math.cos(ang), 0)) * 0.006
            v1 = [b.verts.new(v.co + off) for v in v0]
            b.faces.new(v0[::-1]); b.faces.new(v1)
            for q in range(len(v0)):
                r = (q + 1) % len(v0); b.faces.new((v0[q], v0[r], v1[r], v1[q]))
        P.rod(M["steel"], (p.x, p.y, z + 0.03), (p.x, p.y, ceiling), 0.0008, seg=4)


def light_only(P):
    """A light whose fitting belongs to another piece (e.g. the vanity's light channel): no geometry."""


def window_counter(P, L=11.0):
    """Window counter at 1.05: 40 mm oak top 0.45 deep on blackened steel brackets, facing the forest."""
    P.box(M["oak"], (0, 0, 1.03), (L, 0.45, 0.04))
    for x in np.arange(-L / 2 + 0.3, L / 2, 1.2):
        P.rod(M["steel"], (x, 0.12, 0), (x, 0.12, 1.01), 0.02, seg=12)
        P.box(M["steel"], (x, 0.0, 1.0), (0.04, 0.4, 0.02))


def _paint(name, rgb, rough=0.85):
    return bc.material(name, rgb, rough)


def _moss():
    """Preserved reindeer / cushion moss: deep greens with lighter tips, very rough, bumpy."""
    m = bpy.data.materials.get("preserved_moss")
    if m:
        return m
    m = bpy.data.materials.new("preserved_moss"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 1.0
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 8; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    big = N.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 4; L.new(tc.outputs["Object"], big.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.09, 0.02, 1); ramp.color_ramp.elements[1].color = (0.32, 0.45, 0.12, 1)
    mx = N.new("ShaderNodeMath"); mx.operation = "MULTIPLY_ADD"; mx.inputs[1].default_value = 0.6; L.new(nz.outputs["Fac"], mx.inputs[0]); L.new(big.outputs["Fac"], mx.inputs[2])
    mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.5; mr.inputs[2].default_value = 1.3; L.new(mx.outputs[0], mr.inputs[0])
    L.new(mr.outputs[0], ramp.inputs[0]); L.new(ramp.outputs[0], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 1.0; bp.inputs["Distance"].default_value = 0.01; L.new(nz.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs[0], b.inputs["Normal"])
    return m


def relief_art(P, width=6.0, height=2.9, z0=1.45):
    """'Glomma' relief, an artwork for the wall behind the reception desk: the valley's ridges cut from layered timber, receding
    from pale mist at the back to preserved green moss in front, with a band of spruce silhouettes along the foreground.
    7 layers, each 18 mm thick and 28 mm proud of the one behind (0.2 m deep in all); frameless, on a black backing board."""
    rng = np.random.default_rng(1957)
    W, H = width, height
    P.box(M["felt"], (0, -0.012, z0 + H / 2), (W, 0.02, H))
    layers = [  # (ridge base as share of height, amplitude, colour)
        (0.86, 0.10, _paint("relief_sky", (0.78, 0.80, 0.76), 0.9)),
        (0.74, 0.16, _paint("relief_mist", (0.62, 0.68, 0.64), 0.9)),
        (0.62, 0.18, _paint("relief_far", (0.42, 0.52, 0.45), 0.9)),
        (0.50, 0.16, _paint("relief_sage", (0.30, 0.42, 0.30), 0.9)),
        (0.38, 0.13, _moss()),
        (0.26, 0.10, _paint("relief_forest", (0.07, 0.17, 0.08), 0.9)),
        (0.12, 0.07, _moss()),
    ]
    xs = np.linspace(-W / 2, W / 2, 140)
    for k, (base, amp, mat) in enumerate(layers):
        ph = rng.uniform(0, 10, 4)
        ridge = base + amp * (0.55 * np.sin(xs * 1.1 + ph[0]) + 0.3 * np.sin(xs * 2.7 + ph[1]) + 0.15 * np.sin(xs * 6.3 + ph[2]))
        if k <= 2:  # the far fells get sharper peaks
            ridge += amp * 0.6 * np.maximum(0, np.sin(xs * 0.9 + ph[3])) ** 6
        ridge = np.clip(ridge, 0.03, 0.98)
        pts = [(-W / 2, z0)] + [(x, z0 + r * H) for x, r in zip(xs, ridge)] + [(W / 2, z0)]
        y0 = k * 0.028
        P.prism(mat, pts, y0, y0 + 0.018)
        if k in (3, 5):  # spruce silhouettes standing on the ridge
            dark = _paint("relief_spruce", (0.03, 0.09, 0.04), 0.9)
            for x in rng.uniform(-W / 2 + 0.1, W / 2 - 0.1, 26 if k == 5 else 14):
                zr = z0 + np.interp(x, xs, ridge) * H
                h = rng.uniform(0.18, 0.42) * (1.0 if k == 5 else 0.6)
                w = h * 0.36
                tri = [(x - w / 2, zr - 0.03), (x + w / 2, zr - 0.03), (x + w * 0.18, zr + h * 0.45), (x + w * 0.34, zr + h * 0.42),
                       (x, zr + h), (x - w * 0.34, zr + h * 0.42), (x - w * 0.18, zr + h * 0.45)]
                P.prism(dark, tri, y0 + 0.018, y0 + 0.03)
    # a brass-toned sun disc low over the fells
    sun = [(W * 0.25 + 0.22 * math.cos(a), z0 + H * 0.9 + 0.22 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    P.prism(_paint("relief_sun", (0.85, 0.66, 0.36), 0.5), sun, 0.03, 0.045)


def _canvas_mat(path):
    """Oil on linen: the painting + a procedural linen weave (warp and weft threads ~0.6 mm, each thread slightly uneven in
    thickness and tone, gaps where paint pools), impasto from the painting's own brushwork (luminance as height), a little
    sheen variation where the paint is thicker. Built after the usual Blender canvas recipe: two banded waves at 90°, distorted."""
    name = "canvas_" + path.split("/")[-1]
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path, check_existing=True); t.interpolation = "Cubic"
    L.new(tc.outputs["UV"], t.inputs["Vector"])
    def thread(rot, seed):
        mp = N.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, rot, 0); mp.inputs["Location"].default_value = (seed, 0, seed)  # canvas plane = local x-z
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        w = N.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "X"; w.wave_profile = "SIN"
        w.inputs["Scale"].default_value = 1000.0  # ~1 mm threads (medium linen)   # object metres -> ~1600 threads / m (0.6 mm linen)
        w.inputs["Distortion"].default_value = 1.2; w.inputs["Detail"].default_value = 2.0; w.inputs["Detail Scale"].default_value = 2.0
        L.new(mp.outputs[0], w.inputs["Vector"])
        return w.outputs["Fac"]
    warp, weft = thread(0.0, 0.0), thread(1.5708, 3.7)
    weave = N.new("ShaderNodeMath"); weave.operation = "ADD"; L.new(warp, weave.inputs[0]); L.new(weft, weave.inputs[1])  # plain weave
    slub = N.new("ShaderNodeTexNoise"); slub.inputs["Scale"].default_value = 120.0; slub.inputs["Detail"].default_value = 4; L.new(tc.outputs["Object"], slub.inputs["Vector"])
    th = N.new("ShaderNodeMath"); th.operation = "MULTIPLY_ADD"; L.new(weave.outputs[0], th.inputs[0]); th.inputs[1].default_value = 0.45; L.new(slub.outputs["Fac"], th.inputs[2])
    # impasto: the painting's brushwork as height
    gray = N.new("ShaderNodeRGBToBW"); L.new(t.outputs["Color"], gray.inputs[0])
    b1 = N.new("ShaderNodeBump"); b1.inputs["Strength"].default_value = 0.35; b1.inputs["Distance"].default_value = 0.0006; L.new(th.outputs[0], b1.inputs["Height"])
    b2 = N.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = 0.25; b2.inputs["Distance"].default_value = 0.002; L.new(gray.outputs[0], b2.inputs["Height"])
    L.new(b1.outputs[0], b2.inputs["Normal"]); L.new(b2.outputs[0], b.inputs["Normal"])
    # colour: paint settles darker in the weave gaps
    gap = N.new("ShaderNodeMapRange"); gap.inputs[1].default_value = 0.2; gap.inputs[2].default_value = 0.9; gap.inputs[3].default_value = 0.86; gap.inputs[4].default_value = 1.03
    L.new(th.outputs[0], gap.inputs[0])
    col = N.new("ShaderNodeMix"); col.data_type = "RGBA"; col.blend_type = "MULTIPLY"; col.inputs["Factor"].default_value = 1.0
    L.new(t.outputs["Color"], col.inputs["A"])
    cc = N.new("ShaderNodeCombineColor"); L.new(gap.outputs[0], cc.inputs[0]); L.new(gap.outputs[0], cc.inputs[1]); L.new(gap.outputs[0], cc.inputs[2])
    L.new(cc.outputs[0], col.inputs["B"]); L.new(col.outputs["Result"], b.inputs["Base Color"])
    # oil sheen: thicker (brighter) paint a touch glossier, varnish overall satin
    rg = N.new("ShaderNodeMapRange"); rg.inputs[3].default_value = 0.62; rg.inputs[4].default_value = 0.42; L.new(gray.outputs[0], rg.inputs[0])
    L.new(rg.outputs[0], b.inputs["Roughness"])
    return m


def canvas_art(P, width=6.0, height=2.9, z0=1.45, image=""):
    """Stretched canvas (40 mm deep) in an oak float frame with a 10 mm shadow gap. The painting is generated (gpt-image-2)
    and lives in docs/art/. The front face carries the image (UV 0..1), the canvas wraps the edges in its own paint."""
    import bmesh as _bm
    mat = _canvas_mat(image)
    b = P.bm(mat)
    W, H, D = width, height, 0.04
    v = [b.verts.new(c) for c in ((-W / 2, D, z0), (W / 2, D, z0), (W / 2, D, z0 + H), (-W / 2, D, z0 + H))]
    f = b.faces.new(v)
    uv = b.loops.layers.uv.verify()
    for loop, (u_, w_) in zip(f.loops, ((1, 0), (0, 0), (0, 1), (1, 1))):  # viewed from the front (+y) x runs right-to-left
        loop[uv].uv = (u_, w_)
    P.box(M["felt"], (0, D / 2 - 0.001, z0 + H / 2), (W - 0.002, D - 0.004, H - 0.002))   # stretcher body behind the face
    fr = 0.012; g = 0.01
    for x in (-W / 2 - g - fr / 2, W / 2 + g + fr / 2):
        P.box(M["oak"], (x, 0.03, z0 + H / 2), (fr, 0.06, H + 2 * (g + fr)))
    for z in (z0 - g - fr / 2, z0 + H + g + fr / 2):
        P.box(M["oak"], (0, 0.03, z), (W + 2 * (g + fr), 0.06, fr))
    P.box(M["felt"], (0, 0.002, z0 + H / 2), (W + 2 * g, 0.004, H + 2 * g))  # dark tray behind the gap


def art_labels(P, width=4.0, height=2.0, z0=0.45, labels=(), size=0.034):
    """Educational name plaques on a painting (Roman: English names under each animal): small white-oiled oak tablets, 8 mm,
    set on the canvas, the name burnt in dark. labels = [(u, v, name)] in image fractions (u from the left, v from the top);
    same local frame as canvas_art (canvas face at y 0.04, seen from +y, image left at +x)."""
    burnt = bc.material("burnt_text", (0.035, 0.022, 0.014), 0.75)
    for u, v, name in labels:
        x, z = width / 2 - u * width, z0 + (1 - v) * height
        w = 0.06 + 0.9 * size * len(name)
        P.box(M["oak"], (x, 0.044, z), (w, 0.008, size * 2.1))
        P.text(burnt, name, (x, 0.0485, z - size * 0.08), size * 1.5)


def wall_light(P):
    """Slim vertical wall light: a 60 x 40 blackened-steel channel, 0.9 m tall, centred at 2.75, an opal diffuser on its face."""
    P.box(M["steel"], (0, 0.02, 2.75), (0.06, 0.04, 0.9))
    P.box(M["opal"], (0, 0.042, 2.75), (0.036, 0.006, 0.84))
    P.box(M["brass"], (0, 0.02, 2.75 - 0.46), (0.062, 0.042, 0.012))  # thin brass collar: the accent


def downlight(P, z_ceiling=5.02):
    """Downlight dropped just below the wave fins: Ø90 blackened-steel can, 160 long, opal lens glowing at the bottom."""
    P.cyl(M["steel"], (0, 0, z_ceiling - 0.16), 0.045, 0.16, seg=32)
    P.cyl(M["opal"], (0, 0, z_ceiling - 0.165), 0.032, 0.006, seg=32)
    P.rod(M["steel"], (0, 0, z_ceiling), (0, 0, 5.62), 0.004, seg=6)


def gallery_spot(P, z_ceiling=5.02):
    """Adjustable gallery spot: a blackened-steel cylinder on a yoke, tilted towards the painting."""
    P.rod(M["steel"], (0, 0, z_ceiling), (0, 0, 5.62), 0.004, seg=6)
    P.box(M["steel"], (0, 0, z_ceiling - 0.02), (0.06, 0.06, 0.04))
    P.rod(M["steel"], (0, 0, z_ceiling - 0.06), (-0.12, 0, z_ceiling - 0.2), 0.04, 0.04, seg=32)
    P.cyl(M["opal"], (-0.125, 0, z_ceiling - 0.205), 0.03, 0.004, seg=24)


# ------------------------------------------------------------------ lounge bridge + decks (Roman, 2026-10-12: minimal pass-through
# to the gym, a flowing ladder of light down the middle, glass in the floor each side, standing tables + outdoor sofas on the decks)
def _canvas():
    """Outdoor upholstery: solution-dyed acrylic canvas in the cafe's oat, a close linen-like weave (dries fast, keeps its colour)."""
    if "canvas" not in M:
        M["canvas"] = bc.pbr_material("canvas_oat", "rough_linen", 0.27, box=True, tint=(0.97, 0.94, 0.88), sat=0.15, val=1.5, piece_var=0.02)
    return M["canvas"]


def _led(name, rgb, strength):
    return M.setdefault(name, bc.material(name, tuple(c * 0.5 for c in rgb), 0.4, emit=(rgb, strength)))


def _tube(P, mat, pts, r, seg=16, caps=True):
    """A smooth round member swept along a polyline (bent-laminated rails): rings of verts on parallel-transported frames."""
    b = P.bm(mat)
    pts = [Vector(p) for p in pts]
    tg = [(pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(len(pts))]
    n = Vector((0, 0, 1)) if abs(tg[0].z) < 0.9 else Vector((1, 0, 0))
    n = (n - tg[0] * n.dot(tg[0])).normalized()
    rings = []
    for i, p in enumerate(pts):
        if i:
            n = (n - tg[i] * n.dot(tg[i])).normalized()
        bn = tg[i].cross(n)
        rings.append([b.verts.new(p + (n * math.cos(a) + bn * math.sin(a)) * r) for a in np.linspace(0, 2 * math.pi, seg, endpoint=False)])
    for A, B in zip(rings, rings[1:]):
        for k in range(seg):
            b.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))
    if caps:
        b.faces.new(rings[0][::-1]); b.faces.new(rings[-1])


def _fish(P, mat, p, ang, L, pitch=0.0):
    """A mirror-polished steel trout (as in Elva), 6 mm plate, head towards ang; pitch tilts it nose-up (leaping)."""
    body = [(L / 2 * math.cos(a), 0.11 * L * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
    tail = [(-L / 2 + 0.02, 0.0), (-L / 2 - 0.12 * L / 0.3, 0.06), (-L / 2 - 0.1 * L / 0.3, 0.0), (-L / 2 - 0.12 * L / 0.3, -0.06)]
    for shape in (body, tail):
        b = P.bm(mat)
        v0 = [b.verts.new((p[0] + x * math.cos(pitch) * math.cos(ang), p[1] + x * math.cos(pitch) * math.sin(ang), p[2] + x * math.sin(pitch) + z * math.cos(pitch)))
              for x, z in shape]
        off = Vector((-math.sin(ang), math.cos(ang), 0)) * 0.006
        v1 = [b.verts.new(v.co + off) for v in v0]
        b.faces.new(v0[::-1]); b.faces.new(v1)
        for q in range(len(v0)):
            r = (q + 1) % len(v0); b.faces.new((v0[q], v0[r], v1[r], v1[q]))


def laksetrappa(P, rails=(), rungs=(), cables=(), fish=()):
    """'Laksetrappa' (the salmon ladder): the bridge's light, a flowing ladder hung down its middle. Two rails of steam-bent,
    white-oiled solid oak (Ø64) sway in plan, dip and rise, and roll round each other as they go; they grow out of the slat ceiling at
    both ends. Between them ~50 rungs of opal light (Ø36 opal acrylic tubes with 2700 K LED inside, tenoned into the rails, a thin
    brass collar at each joint). Hung on 1.5 mm steel wires from the glulam beams and through the slats to the CLT. Three
    mirror-steel trout leap up it towards the gym: Elva's fish swim upstream to the bridge, the ladder carries them on.
    Geometry (local, origin on the bridge axis at F1) comes from tools/furnish.py: rails, rungs, cable points, fish."""
    for rail in rails:
        _tube(P, M["oak"], rail, 0.032, seg=20)
        for end in (rail[0], rail[-1]):  # blackened-steel ceiling rose where the rail meets the slats
            if end[2] > 5.0:
                P.cyl(M["steel"], (end[0], end[1], end[2] - 0.01), 0.07, 0.012, seg=32)
    for a, b_ in rungs:
        a, b_ = Vector(a), Vector(b_); d = (b_ - a).normalized()
        P.rod(M["opal"], a + d * 0.026, b_ - d * 0.026, 0.018, seg=20)
        for c, s_ in ((a, 1), (b_, -1)):
            P.rod(M["brass"], c + d * s_ * 0.024, c + d * s_ * 0.034, 0.021, seg=20)
    for (x, y, z0, z1) in cables:
        P.rod(M["steel"], (x, y, z0), (x, y, z1), 0.0012, seg=5)
    fm = M.setdefault("polished_steel", bc.metal_material("polished_steel", (0.92, 0.92, 0.9), rough=(0.02, 0.06), brushed=False))
    for (x, y, z, ang, L, pitch, ztop) in fish:
        _fish(P, fm, (x, y, z), ang, L, pitch)
        P.rod(M["steel"], (x, y, z + 0.03), (x, y, ztop), 0.0008, seg=4)


def _ar_glass():
    """Low-iron glass with an anti-reflective coating (the walk-on panels): ~1 % reflection instead of ~8 %, so the dark gorge below
    shows through instead of the bright ceiling mirrored in it; a Fresnel-weighted gloss, clear for everything else."""
    m = bpy.data.materials.get("glass_lowiron_ar")
    if m:
        return m
    m = bpy.data.materials.new("glass_lowiron_ar"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tr = N.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = (0.97, 0.99, 0.98, 1)
    gl = N.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.02
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.15
    f = N.new("ShaderNodeMath"); f.operation = "MULTIPLY"; f.inputs[1].default_value = 0.25; L.new(lw.outputs["Fresnel"], f.inputs[0])
    mx = N.new("ShaderNodeMixShader"); L.new(f.outputs[0], mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(gl.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    return m


def glass_floor(P, depth=0.42):
    """Walk-on glass panel, 1.0 m square (origin = its centre on the finished floor): a 20 mm blackened-steel rim flush with the
    oak, the glass bedded on EPDM on a steel angle ledge; laminated low-iron 3 x 12 mm heat-strengthened + an 8 mm top ply, fully
    clear, anti-reflective coated (Roman: see the river, no frit) (SentryGlas interlayers, 5 kN/m2); below it a blackened-steel sleeve lines the cast opening
    down through the screed and the 300 mm deck to the soffit, a framed window straight down to the river."""
    st = M["steel"]
    G, F, ledge = 1.0, 1.04, 0.02
    for sx, sy, w, d in ((0, 1, F, (F - G) / 2), (0, -1, F, (F - G) / 2), (1, 0, (F - G) / 2, G), (-1, 0, (F - G) / 2, G)):
        c = (sx * (G + F) / 4, sy * (G + F) / 4)
        P.box(st, (c[0], c[1], -0.0225), (w, d, 0.045))                               # rim: the angle's upstand, flush
    for sx, sy, w, d in ((0, 1, G, ledge), (0, -1, G, ledge), (1, 0, ledge, G - 2 * ledge), (-1, 0, ledge, G - 2 * ledge)):
        P.box(st, (sx * (G / 2 - ledge / 2), sy * (G / 2 - ledge / 2), -0.051), (w, d, 0.008))  # the ledge the glass sits on
    P.box(_ar_glass(), (0, 0, -0.024), (G - 0.004, G - 0.004, 0.042))                  # laminated glass, low-iron, anti-reflective
    S = 1.06
    for sx, sy, w, d in ((0, 1, S + 0.016, 0.008), (0, -1, S + 0.016, 0.008), (1, 0, 0.008, S), (-1, 0, 0.008, S)):
        P.box(st, (sx * (S / 2 + 0.004), sy * (S / 2 + 0.004), -0.055 - (depth - 0.055) / 2), (w, d, depth - 0.055))  # sleeve


def speed_gates(P, cabs=(), lanes=(), open_=(), Lc=1.5, hc=0.98, wing=1.2):
    """Members' speed gates (Roman: automatic, the phone is the key): slim blackened-steel cabinets with white-oiled oak tops (Roman
    preferred the metal to an all-oak version), the tap point for the phone (NFC / BLE) in each top in a brass ring with a soft
    light, glass swing wings to 1.2 m. Local x runs
    across the lanes, +y faces the cafe. Entry readers sit on the walker's right at the cafe end, exit readers at the gym end.
    Lane lights in the cabinet faces glow green while a lane is open. Wings fail safe: they swing open on a fire alarm (TEK17 escape
    route) and from the release by the gates. cabs = [[x, width]], lanes = [[x0, x1]], open_ = lane indices shown open."""
    st, oak = M["steel"], M["oak"]
    green, white = _led("led_green", (0.2, 1.0, 0.4), 6.0), M["opal"]
    sensor = M.setdefault("sensor_glass", bc.material("sensor_glass", (0.01, 0.01, 0.012), 0.08))
    for x, w in cabs:  # blackened-steel cabinets with white-oiled oak tops (Roman: back to the metal, he liked it)
        P.box(st, (x, 0, 0.04 + (hc - 0.07) / 2), (w, Lc, hc - 0.07))
        P.box(M["rubber"], (x, 0, 0.02), (w - 0.02, Lc - 0.02, 0.04))                  # shadow plinth
        P.box(oak, (x, 0, hc - 0.015), (w + 0.01, Lc + 0.01, 0.03))                    # oak top
    def reader(x, y):
        P.ring(M["brass"], (x, y), 0.04, 0.046, hc, hc + 0.002, seg=48)
        P.cyl(white, (x, y, hc), 0.038, 0.0015, seg=48)
        P.box(M["brass"], (x, y - 0.075 if y > 0 else y + 0.075, hc + 0.001), (0.014, 0.024, 0.0015))  # a little phone in brass: tap here
    for i, (x0, x1) in enumerate(lanes):
        is_open = i in open_
        left = next((c for c in cabs if abs(c[0] + c[1] / 2 - x0) < 0.02), None)
        right = next((c for c in cabs if abs(c[0] - c[1] / 2 - x1) < 0.02), None)
        if left:
            reader(left[0], Lc / 2 - 0.16)          # entry (walking from the cafe): reader on the walker's right
        if right:
            reader(right[0], -Lc / 2 + 0.16)        # exit (walking from the gym)
        for xf, sg in ((x0, 1), (x1, -1)):           # lane light + safety sensors in both faces
            P.box(st, (xf + sg * 0.002, 0, 0.84), (0.006, Lc - 0.3, 0.03))
            P.box(green if is_open else white, (xf + sg * 0.005, 0, 0.84), (0.003, Lc - 0.36, 0.012))
            for yy in (-0.45, 0.45):
                for zz in (0.35, 0.62):
                    P.box(sensor, (xf + sg * 0.004, yy, zz), (0.004, 0.05, 0.03))
        wl = (x1 - x0) / 2 - 0.008
        for xp, sg in ((x0, 1), (x1, -1)):           # two glass wings, hubs on polished pivots in the cabinets
            P.cyl(M["brushed"], (xp + sg * 0.012, 0, 0.22), 0.016, wing - 0.2, seg=20)
            if is_open:                              # swung 90 deg towards the gym
                P.box(M["glass"], (xp + sg * 0.03, -wl / 2 - 0.02, (0.25 + wing) / 2), (0.012, wl, wing - 0.25))
            else:
                P.box(M["glass"], (xp + sg * (wl / 2 + 0.012), 0, (0.25 + wing) / 2), (wl, 0.012, wing - 0.25))


def glass_fence(P, L=4.0, h=1.2):
    """Frameless 12 mm toughened laminated glass, 1.2 m, clamped in a channel set into the floor (only a 35 mm steel cover shows):
    closes the line either side of the gates without closing the view."""
    n = max(1, math.ceil(L / 2.0)); w = L / n
    for k in range(n):
        P.box(M["glass"], (-L / 2 + w * (k + 0.5), 0, h / 2), (w - 0.006, 0.012, h))
    P.box(M["steel"], (0, 0, 0.0015), (L, 0.035, 0.003))


def floor_strip(P, L=2.0, w=0.03, style="plain"):
    """Flush floor strips: 'plain' = a blackened-steel threshold / track line; 'grate' = a slot drain (blackened-steel grating
    over a channel) at the deck thresholds, so the deck can sit 15 mm lower and water never reaches the oak."""
    if style == "grate":
        P.box(M["felt"], (0, 0, -0.03), (L, w - 0.01, 0.06))
        for y in (-w / 2 + 0.004, w / 2 - 0.004):
            P.box(M["steel"], (0, y, -0.006), (L, 0.008, 0.012))
        for x in np.arange(-L / 2 + 0.0125, L / 2, 0.025):
            P.box(M["steel"], (x, 0, -0.008), (0.006, w - 0.012, 0.016))
    else:
        P.box(M["steel"], (0, 0, -0.001), (L, w, 0.003))


def bridge_bench(P, L=3.2):
    """Bridge bench: one solid walnut plank (480 x 60) on two blackened-steel sled frames (60 x 12 flat bar), backless so you can
    sit facing the view or the room; a sheepskin. Seat at 0.45."""
    P.box(M["walnut"], (0, 0, 0.42), (L, 0.48, 0.06))
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.42)
        P.box(M["steel"], (x, 0, 0.384), (0.012, 0.42, 0.012))                         # under the plank
        P.box(M["steel"], (x, 0, 0.006), (0.012, 0.46, 0.012))                         # runner
        for sy in (-1, 1):
            P.box(M["steel"], (x, sy * 0.204, 0.195), (0.012, 0.012, 0.37))
    P.box(M["sheepskin"], (L / 2 - 0.55, 0.0, 0.462), (0.6, 0.44, 0.025))


def standing_table(P, d=0.7, h=1.08):
    """Standing table for the decks: a round oiled-oak top (40 mm, glued staves), a blackened-steel column on a heavy steel disc
    (it stays put in the wind over the gorge), a footrest ring at 0.28 and a small brass bag hook under the top."""
    P.cyl(M["oak"], (0, 0, h - 0.04), d / 2, 0.04, seg=64)
    P.cyl(M["steel"], (0, 0, h - 0.06), 0.09, 0.02, seg=32)                              # top plate
    P.cyl(M["steel"], (0, 0, 0.025), 0.038, h - 0.085, seg=24)
    P.cyl(M["steel"], (0, 0, 0.0), 0.26, 0.025, seg=64)
    pts = [(0.2 * math.cos(math.radians(a)), 0.2 * math.sin(math.radians(a)), 0.28) for a in range(0, 361, 15)]
    for p0, p1 in zip(pts, pts[1:]):
        P.rod(M["steel"], p0, p1, 0.009, seg=10)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        P.rod(M["steel"], (0.036 * math.cos(a), 0.036 * math.sin(a), 0.28), (0.2 * math.cos(a), 0.2 * math.sin(a), 0.28), 0.008, seg=8)
    P.rod(M["brass"], (0, -0.09, h - 0.06), (0, -0.13, h - 0.11), 0.004, seg=8)
    P.rod(M["brass"], (0, -0.13, h - 0.11), (0, -0.13, h - 0.085), 0.004, seg=8)


def deck_sofa(P, L=2.2):
    """The cafe sofa made for the decks: same form, oiled oak frame, solution-dyed canvas in the cafe's oat, a wool pledd."""
    sofa(P, L, outdoor=True)


def deck_chair(P):
    """The 'Elverum' lounge chair for the decks: oiled oak frame, outdoor canvas cushions, sheepskin."""
    lounge_chair(P, outdoor=True)


def deck_table(P, d=0.9, h=0.38):
    """Deck table: a honed granite top (40 mm, the same stone as the cafe's boulder) on a blackened-steel pedestal and cross base."""
    P.cyl(_honed_granite(), (0, 0, h - 0.04), d / 2, 0.04, seg=64)
    P.cyl(M["steel"], (0, 0, 0.03), 0.035, h - 0.07, seg=24)
    for a in (0, 90):
        P.box(M["steel"], (0, 0, 0.015), (d * 0.6, 0.05, 0.03), rz=math.radians(a + 45))


def blanket_basket(P, colours=("moss", "oat", "lingon")):
    """A woven willow basket (Ø0.46) of rolled wool blankets by each deck sofa."""
    P.ring(M["rope"], (0, 0), 0.215, 0.23, 0.0, 0.4, seg=48)
    P.cyl(M["rope"], (0, 0, 0.0), 0.215, 0.015, seg=48)
    for k, c in enumerate(colours):
        a = math.radians(40 + 120 * k)
        P.cyl(M["felt_" + c], (0.1 * math.cos(a), 0.1 * math.sin(a), 0.015), 0.085, 0.45 + 0.04 * k, seg=24)


def ir_heater(P, z_top=5.615, L=1.4):
    """Infrared heater under the eave soffit: a slim blackened-steel body with a dark ceramic-glass emitter, on two short drops.
    Off by day; warms the people, not the air, on cold evenings."""
    z = z_top - 0.15
    P.box(M["steel"], (0, 0, z), (L, 0.13, 0.06))
    P.box(M.setdefault("sensor_glass", bc.material("sensor_glass", (0.01, 0.01, 0.012), 0.08)), (0, 0, z - 0.031), (L - 0.06, 0.1, 0.002))
    for x in (-L / 2 + 0.15, L / 2 - 0.15):
        P.rod(M["steel"], (x, 0, z + 0.03), (x, 0, z_top), 0.008, seg=8)


def gate_release(P):
    """Green emergency release (nødåpning) for the gates: a break-glass call point on the column, at 1.2 m."""
    g = M.setdefault("sign_green", bc.material("sign_green", (0.04, 0.4, 0.18), 0.5))
    P.box(g, (0, 0.025, 1.2), (0.09, 0.05, 0.09))
    P.box(M.setdefault("sign_white", bc.material("sign_white", (0.92, 0.92, 0.9), 0.5)), (0, 0.0505, 1.2), (0.05, 0.002, 0.05))
    P.box(M["glass"], (0, 0.053, 1.2), (0.07, 0.003, 0.07))


def slide_wall(P, L=18.3, rise=0.12, n=20, state="closed", head=3.07):
    """The bridge's glass walls, made to open fully: a frameless slide-and-turn system (as Sunflex SF25 / Solarlux SL 25):
    20 panels of 10 mm toughened low-iron glass, ~0.91 x 2.72 m (~65 kg), each on two stainless rollers in a drained floor track
    recessed flush in the oak and guided at the top in a blackened-steel guide beam. The bridge's slim posts stand in the old glass
    line, so the track runs just inside them and the panels pass them. The floor rises 1:150 (gym -> cafe): track and guide both
    follow it, parallel, so every panel is the same; the guide beam is level on top under the fixed clerestory and tapers with the
    floor below (that is all the slope shows). Downhill pull on a panel ~8 N against ~25 N to break it away: it stays where it is
    left, and floor bolts lock each one shut. To open, each panel slides to its end of the bridge, its leading roller drops out of
    the guide at the turning point and it swings 90 degrees inward about the other, parking beside the last: two stacks of ten,
    ~0.45 m along the wall, 0.91 m into the room, in the corners. The first panel at each end is hinged to its jamb: the everyday
    door when the wall is shut. Local frame: x along the track from its start (floor height there = 0), +y = outside (the deck),
    rise = floor rise over L; head = top of the guide beam (level). state 'closed' | 'open' (parked)."""
    st, gl = M["steel"], M["glass"]
    zf = lambda x: rise * x / L
    P.prism(M["brushed"], [(0, -0.02), (L, rise - 0.02), (L, rise + 0.0005), (0, 0.0005)], -0.016, 0.016)       # floor track (stainless)
    P.prism(M["felt"], [(0, -0.0005), (L, rise - 0.0005), (L, rise + 0.001), (0, 0.001)], -0.004, 0.004)          # its running slot
    gb = 2.74                                                                                                     # guide beam underside above the floor
    P.prism(st, [(0, gb), (L, rise + gb), (L, head), (0, head)], -0.05, 0.05)
    P.prism(M["felt"], [(0, gb - 0.001), (L, rise + gb - 0.001), (L, rise + gb + 0.002), (0, gb + 0.002)], -0.008, 0.008)  # the guide slot
    jw = 0.05
    for x in (jw / 2, L - jw / 2):                                                                               # wall jambs (seal + door hinge side)
        P.box(st, (x, 0, (zf(x) + head) / 2), (jw, 0.09, head - zf(x)))
    pw = (L - 2 * jw) / n
    hp = gb - 0.02 - 0.012                                                                                        # panel height (12 mm off the floor, 20 mm into the guide)
    def panel(c, rz_, z0, door=False):
        """one panel: glass + bottom roller profile + top guide profile, centred on c (its hinge-free centre), turned rz_"""
        cx, cy = c
        for zc, h_, mat, t in ((z0 + 0.02, 0.04, st, 0.03), (z0 + hp - 0.0175, 0.035, st, 0.03), (z0 + hp / 2, hp - 0.06, gl, 0.010)):
            P.box(mat, (cx, cy, zc), (pw - 0.004, t, h_) if abs(rz_) < 1e-6 else (t, pw - 0.004, h_))
        # a slim blackened-steel pull on the inside face, at the leading edge
        if abs(rz_) < 1e-6:
            P.box(st, (cx + pw / 2 - 0.08, -0.02, z0 + 1.05), (0.015, 0.02, 0.32))
        else:
            P.box(st, (cx - 0.02, cy - pw / 2 + 0.08, z0 + 1.05), (0.02, 0.015, 0.32))
    half = n // 2
    for k in range(n):
        if state == "closed":
            x0 = jw + k * pw
            panel((x0 + pw / 2, 0.0), 0.0, max(zf(x0), zf(x0 + pw)) + 0.012)
        else:  # parked: west half at the start, east half at the far end, each swung 90 deg inward about its end roller
            j = k if k < half else n - 1 - k
            xp = jw + 0.03 + j * 0.045 if k < half else L - jw - 0.03 - j * 0.045
            panel((xp, -pw / 2), 90.0, zf(xp) + 0.012)
    for k in range(n):  # floor bolt sockets (each panel locks shut here)
        x = jw + (k + 0.85) * pw
        P.cyl(M["brushed"], (x, -0.03, zf(x) - 0.002), 0.008, 0.0025, seg=12)


def _rough_block(P, mat, c, size, amp=0.006, seed=0, cuts=4, rz=0.0, rx=0.0, flat_top=False, front_amp=None):
    """A piece of natural stone: a box subdivided and pushed in and out along its faces by noise (split, cleft, hand-hewn faces,
    never machine-flat); flat_top keeps the upper face true (a basin rim), front_amp sets a quieter +y face (for an inscription)."""
    from mathutils import noise
    b = bmesh.new()  # each stone in its own mesh, then merged into the piece
    bmesh.ops.create_cube(b, size=1.0)
    bmesh.ops.subdivide_edges(b, edges=list(b.edges), cuts=cuts, use_grid_fill=True)
    vs = list(b.verts)
    sx, sy, sz = size
    for v in vs:
        x, y, z = v.co  # -0.5..0.5
        ax = max(range(3), key=lambda i: abs(v.co[i]))  # the face this vertex belongs to most
        n_ = noise.noise(Vector((x * sx * 9 + seed, y * sy * 9 + seed * 1.7, z * sz * 9 - seed))) + 0.5 * noise.noise(Vector((x * sx * 31, y * sy * 31 + seed, z * sz * 31)))
        a_ = amp if not (front_amp is not None and ax == 1 and y > 0) else front_amp
        if flat_top and ax == 2 and z > 0:
            a_ = 0.0
        d = [0.0, 0.0, 0.0]; d[ax] = (1 if v.co[ax] > 0 else -1) * a_ * n_
        v.co = Vector((x * sx + d[0], y * sy + d[1], z * sz + d[2]))
    R = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(rx, 3, "X")
    bmesh.ops.rotate(b, verts=vs, cent=(0, 0, 0), matrix=R)
    bmesh.ops.translate(b, verts=vs, vec=c)
    me = bpy.data.meshes.new("stone"); b.to_mesh(me); b.free()
    P.bm(mat).from_mesh(me); bpy.data.meshes.remove(me)


def kilden(P):
    """'Kilden' (the spring): where the gym begins, on the bridge axis between the two locker entries. Natural stone, rough
    (Roman: natural, not synthetic): a 1.6 m niche whose back and sides are dry-stacked riven slate (Norwegian tørrmur: thin
    cleft slabs, each a little proud or shy of the next, joints dark and open), under a split granite lintel. The water comes
    out from under one projecting stone at 2.2 m and runs down the face of the slabs, course by course, into a hewn granite
    trough: one block, split faces outside, only its basin honed. A sensor bottle filler on the left over a blackened-steel grate,
    a drinking spout on the right, 'KILDEN' inlaid in brass. A hidden light under the lintel grazes the wet stone. Elva (the river)
    runs through the cafe, the salmon ladder climbs the bridge; the spring is where they come from. Origin = niche centre on the
    gallery face of the oak slats, +y = the gallery; the stud box behind houses pump, filter + chiller."""
    sl = M.setdefault("riven_slate_v2", bc.pbr_material("riven_slate_v2", "slate_floor_03", 0.7, box=True, tint=(0.72, 0.78, 0.84), sat=0.45, val=0.34,
                                                   rough_add=0.12, piece_var=0.0))  # Otta-like: dark blue-grey
    hg = M.setdefault("hewn_granite", bc.pbr_material("hewn_granite", "quarry_wall", 1.4, box=True, tint=(0.95, 0.94, 0.92), sat=0.35, val=0.85,
                                                    rough_add=0.1, piece_var=0.0))
    film = M.get("water_running")
    if film is None:  # running water over stone: almost clear, its sheen in rivulets (long distorted vertical streaks)
        film = bc.material("water_running", (0.05, 0.06, 0.06), 0.01, alpha=0.12)
        N_, L_ = film.node_tree.nodes, film.node_tree.links
        tc_ = N_.new("ShaderNodeTexCoord"); wv = N_.new("ShaderNodeTexWave"); wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 60.0
        wv.inputs["Distortion"].default_value = 14.0; wv.inputs["Detail"].default_value = 8.0; L_.new(tc_.outputs["Object"], wv.inputs["Vector"])
        bp_ = N_.new("ShaderNodeBump"); bp_.inputs["Strength"].default_value = 1.0; bp_.inputs["Distance"].default_value = 0.004
        L_.new(wv.outputs["Fac"], bp_.inputs["Height"]); L_.new(bp_.outputs[0], N_["Principled BSDF"].inputs["Normal"])
        M["water_running"] = film
    W, D, H = 1.6, 0.6, 2.5
    rng = np.random.default_rng(31)
    BACK = -D
    P.box(M["felt"], (0, BACK + 0.01, H / 2), (W, 0.02, H))                       # dark behind the open joints
    for sx in (-1, 1):
        P.box(M["felt"], (sx * (W / 2 - 0.01), -D / 2, H / 2), (0.02, D, H))
    # the back: courses of riven slate across the full width
    z, k, src = 0.0, 0, None
    water = []
    LIN = 0.1                                                                    # the lintel's depth at the top
    while z < H - LIN - 0.02:
        h = float(rng.uniform(0.035, 0.085)); h = min(h, H - LIN - z)
        x = -W / 2 + 0.02
        while x < W / 2 - 0.03:
            Ls = float(min(rng.uniform(0.22, 0.55), W / 2 - 0.02 - x))
            if Ls < 0.06:
                break
            d = float(rng.uniform(0.07, 0.12))
            spill = abs(z - 2.2) < h and x < 0 < x + Ls                          # the source: one stone stands out over the water
            if spill:
                d = 0.17; src = (z + h, BACK + d)
            _rough_block(P, sl, (x + Ls / 2, BACK + 0.02 + d / 2, z + h / 2), (Ls - 0.006, d, h - 0.005), amp=0.004, seed=k * 1.3,
                         cuts=3, rz=float(rng.uniform(-0.012, 0.012)))
            if 0.95 < z + h and z < 2.2 and not spill:                            # the water runs down over this stone's face
                xa, xb = max(x, -0.3), min(x + Ls, 0.3)
                if xb - xa > 0.03:
                    water.append(((xa + xb) / 2, BACK + 0.02 + d + 0.006, max(z, 0.95), min(z + h, 2.2), xb - xa))
            x += Ls; k += 1
        z += h
    for (xc, yc, za, zb, w) in water:
        P.box(film, (xc, yc, (za + zb) / 2), (w, 0.003, zb - za))
    # the sides: the same slate, along the depth
    for sx in (-1, 1):
        z = 0.0
        while z < H - LIN - 0.02:
            h = float(rng.uniform(0.035, 0.085)); h = min(h, H - LIN - z); y = BACK + 0.02
            while y < -0.02:
                Ls = float(min(rng.uniform(0.2, 0.4), -0.02 - y))
                if Ls < 0.05:
                    break
                d = float(rng.uniform(0.06, 0.1))
                _rough_block(P, sl, (sx * (W / 2 - 0.02 - d / 2), y + Ls / 2, z + h / 2), (d, Ls - 0.006, h - 0.005), amp=0.004, seed=k * 0.7, cuts=3)
                y += Ls; k += 1
            z += h
    # the lintel: one split granite slab across the top
    _rough_block(P, hg, (0, -D / 2, H - LIN / 2), (W, D, LIN), amp=0.008, seed=5.5, cuts=5)
    P.box(M["opal"], (0, -0.08, H - LIN - 0.004), (W - 0.3, 0.025, 0.006))       # hidden light under the lintel's front
    # the trough: one hewn granite block to the floor, its basin honed
    _rough_block(P, hg, (0, -0.3, 0.475), (1.42, 0.46, 0.95), amp=0.012, seed=2.0, cuts=6, flat_top=True, front_amp=0.004)
    P.box(_honed_granite(), (0, -0.31, 0.951), (1.3, 0.36, 0.004))               # the honed basin rim + bed
    P.box(film, (0.12, -0.31, 0.948), (1.0, 0.3, 0.004))                          # water standing in the basin
    if src:
        P.box(film, (-0.05, src[1] + 0.004, src[0] - 0.05), (0.5, 0.004, 0.1))    # the water appearing from under the source stone
    # bottle filler (left): a blackened-steel spout out of the slate, over a grate
    P.box(M["steel"], (-0.42, BACK + 0.16, 1.32), (0.15, 0.1, 0.2))
    P.box(M.setdefault("sensor_glass", bc.material("sensor_glass", (0.01, 0.01, 0.012), 0.08)), (-0.42, BACK + 0.211, 1.36), (0.05, 0.002, 0.03))
    P.cyl(M["brushed"], (-0.42, BACK + 0.19, 1.2), 0.012, 0.025, seg=16)
    for k_ in range(8):
        P.box(M["steel"], (-0.6 + k_ * 0.05, -0.31, 0.958), (0.008, 0.34, 0.012))
    # drinking spout (right): a gooseneck from the rim
    P.rod(M["steel"], (0.5, -0.42, 0.95), (0.5, -0.42, 1.12), 0.012, seg=14)
    P.rod(M["steel"], (0.5, -0.42, 1.12), (0.5, -0.33, 1.16), 0.012, seg=14)
    P.box(M["steel"], (0.6, -0.063, 0.88), (0.06, 0.012, 0.03))                   # push button on the trough front
    P.text(M["brass"], "KILDEN", (-0.1, -0.062, 0.86), 0.035, depth=0.002)
    # the stud box behind (pump, filter, chiller), painted gypsum, from the wall's back face (y -0.215) into the men's room
    box = M.setdefault("painted_gypsum_box", bc.material("painted_gypsum_box", (0.82, 0.8, 0.76), 0.85))
    for x0_, x1_ in ((-0.9, -W / 2), (W / 2, 1.05)):                            # solid either side of the niche (the pier)
        P.box(box, ((x0_ + x1_) / 2, -0.55, H / 2 + 0.25), (x1_ - x0_, 0.67, H + 0.5))
    P.box(box, (0.075, -0.935, (H + 0.5) / 2), (1.95, 0.1, H + 0.5))
    P.box(box, (0.075, -0.6, H + 0.5 - 0.05), (1.95, 0.77, 0.1))


def linear_light(P, L=4.0, z_ceiling=5.58):
    """Recessed linear light for the gym (3500 K, crisper than the lounge's 2700 K): a 50 mm blackened-aluminium channel set flush
    into the wood-wool ceiling, a 35 mm opal diffuser."""
    P.box(M["steel"], (0, 0, z_ceiling - 0.03), (L, 0.05, 0.06))
    P.box(_led("opal_cool", (1.0, 0.92, 0.82), 8.0), (L / 2 * 0, 0, z_ceiling - 0.061), (L - 0.02, 0.035, 0.004))


def floor_grazer(P, L=4.0):
    """Floor-recessed linear grazer (VISION: light recessed in floors): a 50 mm slot along the foot of the oak wall, frosted glass
    flush with the rubber, washing the slats from below."""
    P.box(M["steel"], (0, 0, -0.03), (L, 0.06, 0.06))
    P.box(_led("opal_warm_floor", (1.0, 0.85, 0.68), 5.0), (0, 0, -0.002), (L - 0.02, 0.04, 0.003))


# ------------------------------------------------------------------ locker rooms (Roman, 2026-10-13): shell pieces first
def oculus(P, r=1.0, h=0.7, z_ceiling=3.2):
    """The oculus over a round locker room: a light well r 1.0 through the slat ceiling, lined in warm plaster, an opal disc at its
    top glowing (a soft round sky over the room); a thin oak ring at the ceiling edge."""
    pl = M.setdefault("plaster_warm", bc.material("plaster_warm", (0.8, 0.77, 0.71), 0.9))
    P.ring(pl, (0, 0), r, r + 0.03, z_ceiling, z_ceiling + h, seg=96)
    P.cyl(M.setdefault("opal_oculus", _opal("opal_oculus", 1.3)), (0, 0, z_ceiling + h - 0.01), r, 0.01, seg=96)  # a soft glow, not a skylight (Roman: the round rooms too bright)
    P.ring(M["oak"], (0, 0), r - 0.005, r + 0.06, z_ceiling - 0.03, z_ceiling, seg=96)



# ------------------------------------------------------------------ locker rooms, phase 2: the changing rooms (Roman, 2026-10-13)
DRUM_GLASS = (("multe", (0.92, 0.36, 0.03)), ("mose", (0.16, 0.4, 0.06)), ("fjord", (0.04, 0.17, 0.55)))  # cloudberry, moss, fjord


def _drum_glass(rank):
    """Each round locker room has its own colour (Roman: no numbers; colour, stained glass): three tints of it, light to deep."""
    name, c = DRUM_GLASS[rank % 3]; out = []
    for k, f in enumerate((1.0, 0.72, 0.5)):
        cc = tuple(min(1.0, v * f) for v in c)
        out.append(M.setdefault(f"stained2_{name}_{k}", bc.material(f"stained2_{name}_{k}", cc, 0.2, emit=(cc, 0.55 - 0.12 * k))))
    return out


def _stained_transom(P, glass, x, y, w, H, h=0.34, seed=0):
    """A band of stained glass across the top of a drum's mouth: hand-cut pieces of the room's three tints in blackened-steel cames,
    glowing softly (lit from the light well behind); seen down the aisle, the colour tells you which room is yours."""
    st = M["steel"]; z0 = H - h
    P.box(st, (x, y, z0 - 0.015), (w, 0.04, 0.03))                                         # the head of the opening
    rng = np.random.default_rng(seed * 31 + 5)
    for row, (za, zb) in enumerate(((z0, z0 + h * 0.45), (z0 + h * 0.45, H))):
        xa = x - w / 2
        while xa < x + w / 2 - 0.02:
            pw = float(min(rng.uniform(0.07, 0.19), x + w / 2 - xa))
            P.box(glass[int(rng.integers(0, 3))], (xa + pw / 2, y, (za + zb) / 2), (pw - 0.008, 0.012, zb - za - 0.008))
            P.box(st, (xa + pw, y, (za + zb) / 2), (0.008, 0.02, zb - za))                  # a came
            xa += pw
        P.box(st, (x, y, zb), (w, 0.02, 0.008))
    for sx in (-1, 1):
        P.box(st, (x + sx * w / 2, y, z0 + h / 2), (0.012, 0.02, h))


def _locker_inside(P, dx, r_in, a1, a2, depth=0.52, in_use=False, lit=False):
    """The inside of one round-room locker (a wedge, wider at the back): an oak shell, a wool-felt back with a vent slot at the top,
    a hat shelf at 1.72 with a warm LED strip under its front edge (on when the door opens), a front-to-back hanging rail with oak
    hangers, a slatted oak shoe shelf at 0.32, two hooks on the back, a charging pad (Qi) on the shelf. in_use: a shirt on a hanger,
    a folded towel on the shelf, a bag on the floor, trainers on the shoe shelf."""
    oak, st = M["oak"], M["steel"]
    wool = M.setdefault("locker_wool", bc.material("locker_wool", (0.36, 0.33, 0.3), 0.95))
    am = (a1 + a2) / 2; c, s_ = math.cos(am), math.sin(am); rz = am + math.pi / 2; da = a2 - a1
    def at(rho, z):
        return (dx + rho * c, rho * s_, z)
    def wid(rho):
        return 2 * rho * math.sin(da / 2) - 0.02
    rb = r_in + depth; rm = r_in + depth / 2
    P.box(wool, at(rb, 1.075), (wid(rb), 0.012, 1.95), rz=rz)                                   # the back
    P.box(M["felt"], at(rb - 0.008, 1.98), (wid(rb) - 0.06, 0.004, 0.025), rz=rz)                # its vent slot
    for z in (0.11, 2.04):                                                                        # floor + top
        P.box(oak, at(rm, z), (wid(rm), depth, 0.018), rz=rz)
    P.box(oak, at(r_in + 0.24, 1.72), (wid(r_in + 0.24), 0.4, 0.018), rz=rz)                    # the hat shelf
    if lit:
        P.box(_led("locker_led", (1.0, 0.74, 0.46), 3.0), at(r_in + 0.06, 1.706), (wid(r_in + 0.06) - 0.03, 0.012, 0.004), rz=rz)
    P.box(M["felt"], at(r_in + 0.3, 1.731), (0.1, 0.1, 0.004), rz=rz)                            # charging pad
    P.box(M["brass"], at(r_in + 0.3, 1.734), (0.02, 0.004, 0.002), rz=rz)
    P.rod(st, at(r_in + 0.04, 1.64), at(rb - 0.02, 1.64), 0.008, seg=8)                          # the rail, front to back
    tx_, ty_ = math.cos(rz), math.sin(rz)
    def att(rho, t, z):  # a point at radius rho, t along the door's width
        x, y, _ = at(rho, z); return (x + tx_ * t, y + ty_ * t, z)
    def hanger(rho):  # a slim oak hanger: two sloping arms + a bar, a steel hook over the rail
        for sg in (-1, 1):
            P.rod(oak, att(rho, 0, 1.6), att(rho, sg * 0.16, 1.53), 0.009, seg=8)
        P.rod(oak, att(rho, -0.15, 1.535), att(rho, 0.15, 1.535), 0.004, seg=6)
        P.rod(st, att(rho, 0, 1.6), att(rho, 0, 1.655), 0.0025, seg=6)
    for f in ((0.3, 0.5, 0.7) if not in_use else (0.55, 0.75)):
        hanger(r_in + depth * f)
    for k in range(4):                                                                            # the slatted shoe shelf
        rr = r_in + 0.08 + k * 0.12
        P.box(oak, at(rr, 0.32), (wid(rr), 0.08, 0.018), rz=rz)
    for sx in (-0.08, 0.08):                                                                      # hooks on the back
        hx = dx + (rb - 0.01) * c + math.cos(rz) * sx; hy = (rb - 0.01) * s_ + math.sin(rz) * sx
        P.rod(st, (hx, hy, 1.35), (hx - c * 0.05, hy - s_ * 0.05, 1.38), 0.006, seg=6)
    if in_use:
        shirt = M.setdefault("shirt_merino", bc.material("shirt_merino", (0.1, 0.12, 0.14), 0.9))
        rs = r_in + depth * 0.3; hanger(rs)                                                       # a merino top on its hanger
        P.rod(shirt, att(rs, 0, 1.56), att(rs, 0, 0.98), 0.11, seg=16)                            # the body, falling from the shoulders
        for sg in (-1, 1):
            P.rod(shirt, att(rs, sg * 0.14, 1.53), att(rs, sg * 0.16, 1.1), 0.035, seg=10)        # the sleeves
        P.box(M.setdefault("towel_oat", bc.material("towel_oat", (0.82, 0.78, 0.7), 0.95)), at(r_in + 0.2, 1.77), (0.26, 0.2, 0.08), rz=rz)
        bag = M.setdefault("bag_canvas", bc.material("bag_canvas", (0.16, 0.17, 0.14), 0.85))         # a duffel on the shoe shelf's slats
        P.rod(bag, at(r_in + 0.06, 0.48), at(r_in + 0.46, 0.48), 0.14, seg=20)
        P.rod(M["rubber"], att(r_in + 0.26, -0.03, 0.62), att(r_in + 0.26, 0.03, 0.62), 0.012, seg=8)
        for sx in (-0.06, 0.06):                                                                  # trainers on the floor, under the shelf
            tx = dx + (r_in + 0.26) * c + math.cos(rz) * sx; ty = (r_in + 0.26) * s_ + math.sin(rz) * sx
            P.box(M["rubber"], (tx, ty, 0.135), (0.09, 0.27, 0.03), rz=rz)
            P.box(M.setdefault("shoe_knit", bc.material("shoe_knit", (0.7, 0.7, 0.68), 0.8)), (tx, ty, 0.185), (0.085, 0.24, 0.07), rz=rz)


def locker_hall(P, L=12.5, D=3.85, H=3.18, drums=(), r_in=1.35, r_out=1.9, mouth=1.2, n=18, slots=(), open_=((1, 4, False), (1, 12, True))):
    """The oak block of a changing room with three round locker rooms carved out of it. Outside: white-oiled oak flutes (35 @ 60) on
    black felt, a shadow plinth, floor to the ceiling. Each drum opens to the aisle through a full-height mouth with oak reveals; inside,
    18 full-height oak lockers on the curve (400 at the face), each with a finger-pull groove, a phone reader (the phone is the key,
    as at the gates) and a small brass number; an oak band above the lockers to the ceiling, the oculus overhead. Towel-return slots in
    the aisle face. Local: origin = the block's centre on the floor, +y = the aisle side, drums = their x along the block."""
    oak, felt = M["oak"], M["felt"]
    sensor = M.setdefault("sensor_glass", bc.material("sensor_glass", (0.01, 0.01, 0.012), 0.08))
    half = mouth / 2
    def flutes_x(x0, x1, y, sgn):  # a fluted face along x at y (sgn = which way it faces)
        x = x0 + 0.03
        while x < x1 - 0.02:
            P.box(oak, (x, y + sgn * 0.0125, 0.1 + (H - 0.1) / 2), (0.035, 0.025, H - 0.1))
            x += 0.06
        P.box(felt, ((x0 + x1) / 2, y - sgn * 0.005, H / 2), (x1 - x0, 0.01, H))
        P.box(M["rubber"], ((x0 + x1) / 2, y - sgn * 0.02, 0.05), (x1 - x0, 0.03, 0.1))
    # the aisle face, cut at each mouth
    cuts = sorted([(dx - half - 0.02, dx + half + 0.02) for dx in drums]); xa = -L / 2
    for a_, b_ in cuts + [(L / 2, L / 2)]:
        if a_ - xa > 0.05:
            flutes_x(xa, a_, D / 2, 1)
        xa = b_
    # the end faces
    for sx in (-1, 1):
        y = -D / 2 + 0.03
        while y < D / 2 - 0.02:
            P.box(oak, (sx * (L / 2 + 0.0125), y, 0.1 + (H - 0.1) / 2), (0.025, 0.035, H - 0.1))
            y += 0.06
        P.box(felt, (sx * (L / 2 - 0.005), 0, H / 2), (0.01, D, H))
    for sx_ in slots:  # towel returns: a slot in the aisle face, a black chute behind
        P.box(felt, (sx_, D / 2 + 0.03, 0.95), (0.6, 0.012, 0.16))
        P.box(M["brass"], (sx_, D / 2 + 0.032, 1.06), (0.12, 0.004, 0.012))
    for di, dx in enumerate(drums):
        glass = _drum_glass(len(drums) - 1 - di)  # the drum nearest the entry is listed last in both rooms: it is Multe
        _stained_transom(P, glass, dx, D / 2 - 0.01, mouth + 0.04, H, seed=di)
        ym = math.sqrt(r_in * r_in - half * half)  # where the mouth meets the inner circle
        for sx in (-1, 1):  # the mouth's reveals
            P.box(oak, (dx + sx * (half + 0.01), (ym + D / 2) / 2, H / 2), (0.02, D / 2 - ym, H))
        a_m = mouth / r_in; a0 = math.pi / 2 + a_m / 2; span = 2 * math.pi - a_m
        da = span / n
        opened = {k: use for (d_, k, use) in open_ if d_ == di}
        for k in range(n + 1):  # the dividers between the lockers (radial oak boards)
            ab = a0 + k * da; cb, sb = math.cos(ab), math.sin(ab); rr = r_in + 0.27
            P.box(oak, (dx + rr * cb, rr * sb, 1.075), (0.018, 0.54, 1.95), rz=ab + math.pi / 2)
        for k in range(n):
            a1, a2 = a0 + k * da + 0.002, a0 + (k + 1) * da - 0.002
            am = (a1 + a2) / 2; c = math.cos(am); s_ = math.sin(am)
            w = 2 * r_in * math.sin((a2 - a1) / 2)
            cx, cy = dx + r_in * c, r_in * s_
            rz = am + math.pi / 2
            _locker_inside(P, dx, r_in, a0 + k * da + 0.009, a0 + (k + 1) * da - 0.009, in_use=opened.get(k, False), lit=k in opened)
            P.box(M["rubber"], (cx + c * 0.02, cy + s_ * 0.02, 0.05), (w + 0.004, 0.02, 0.1), rz=rz)          # shadow plinth
            if k in opened:  # swung open 100 deg into the room on its hinge (the a2 edge); a mirror + a hook on its inside face
                hx, hy = dx + (r_in - 0.01) * math.cos(a2), (r_in - 0.01) * math.sin(a2)
                tx, ty = math.cos(a1) - math.cos(a2), math.sin(a1) - math.sin(a2); tl = math.hypot(tx, ty); tx, ty = tx / tl, ty / tl
                for sg in (1, -1):
                    th = sg * math.radians(100); ux, uy = tx * math.cos(th) - ty * math.sin(th), tx * math.sin(th) + ty * math.cos(th)
                    if ux * -c + uy * -s_ > 0:
                        break
                drz = math.atan2(uy, ux); nx, ny = c * math.cos(th) - s_ * math.sin(th), c * math.sin(th) + s_ * math.cos(th)  # the inside face's normal
                ox, oy = hx + ux * w / 2, hy + uy * w / 2
                P.box(oak, (ox, oy, 0.1 + 1.9 / 2), (w, 0.02, 1.9), rz=drz)
                P.box(M["mirror"], (ox + nx * 0.012, oy + ny * 0.012, 1.45), (0.22, 0.004, 0.42), rz=drz)
                P.rod(M["steel"], (ox + nx * 0.011, oy + ny * 0.011, 1.15), (ox + nx * 0.05, oy + ny * 0.05, 1.18), 0.006, seg=6)
                fx, fy = ox - nx * 0.011, oy - ny * 0.011
                P.box(felt, (fx - ux * (w / 2 - 0.035), fy - uy * (w / 2 - 0.035), 1.1), (0.014, 0.004, 0.32), rz=drz)
                P.box(sensor, (fx, fy, 1.42), (0.05, 0.004, 0.05), rz=drz)
                P.box(glass[1], (fx, fy, 1.6), (0.03, 0.005, 0.03), rz=drz)
                continue
            P.box(oak, (cx - c * 0.01, cy - s_ * 0.01, 0.1 + 1.9 / 2), (w, 0.02, 1.9), rz=rz)                 # the door
            fx, fy = cx - c * 0.021, cy - s_ * 0.021                                                           # the door's room-side face
            P.box(felt, (fx + math.cos(rz) * (w / 2 - 0.035), fy + math.sin(rz) * (w / 2 - 0.035), 1.1), (0.014, 0.004, 0.32), rz=rz)  # pull groove
            P.box(sensor, (fx, fy, 1.42), (0.05, 0.004, 0.05), rz=rz)                                          # the phone reader
            P.box(glass[1], (fx, fy, 1.6), (0.03, 0.005, 0.03), rz=rz)                                        # a chip of the room's glass
        P.ring(oak, (dx, 0), r_in - 0.02, r_in + 0.01, 2.02, H, a0=math.degrees(a0), a1=math.degrees(a0 + span), seg=120)
        P.ring(_led("plinth_glow", (1.0, 0.72, 0.42), 2.5), (dx, 0), r_in - 0.006, r_in + 0.004, 0.004, 0.012, a0=math.degrees(a0), a1=math.degrees(a0 + span), seg=120)


def round_seat(P, d=0.6):
    """The round seat in a locker room: a turned walnut drum on a shadow plinth, a thick oat wool cushion with a soft bevelled edge,
    stitched in eight segments to a leather button, seat height 0.45; a warm glow under the plinth (it floats like the lockers)."""
    wool = M.setdefault("wool_oat_seat", bc.material("wool_oat_seat", (0.5, 0.43, 0.35), 0.95))
    leather = M.setdefault("leather_cognac", bc.material("leather_cognac", (0.32, 0.15, 0.07), 0.45))
    P.cyl(M["rubber"], (0, 0, 0.0), d / 2 - 0.08, 0.03, seg=48)
    P.ring(_led("plinth_glow", (1.0, 0.72, 0.42), 2.5), (0, 0), d / 2 - 0.085, d / 2 - 0.075, 0.0, 0.004, seg=64)
    P.cyl(M["walnut"], (0, 0, 0.03), d / 2 - 0.04, 0.32, seg=64)
    P.ring(M["brass"], (0, 0), d / 2 - 0.042, d / 2 - 0.036, 0.345, 0.35, seg=64)            # a brass ring where wood meets wool
    P.cyl(wool, (0, 0, 0.35), d / 2, 0.075, seg=64)
    P.cyl(wool, (0, 0, 0.425), d / 2 - 0.018, 0.02, seg=64)                                 # the bevel
    for k in range(8):                                                                       # stitched segments
        a_ = k * math.pi / 4
        P.box(leather, (math.cos(a_) * d / 4.4, math.sin(a_) * d / 4.4, 0.446), (d / 2.4, 0.004, 0.002), rz=a_)
    P.cyl(leather, (0, 0, 0.443), 0.022, 0.008, seg=24)


def wall_waterfall(P, L=1.6, d=0.3, h=3.18):
    """A wall waterfall (Roman: water flowing over the face of the wall from the ceiling, plants at the bottom; static for now): a
    face of cleft dark slate in a blackened-steel frame, a sheet of water running down it from a slot in a steel head at the ceiling
    into a catch channel at the foot; in front of the channel an empty planter trough of honed granite with its soil, waiting for the
    plants (they come at the very end). Origin = the unit's centre on the floor, -y = the wall."""
    sl = M.setdefault("slate_riven_wf", bc.pbr_material("slate_riven_wf", "slate_floor_03", 0.7, box=True, tint=(0.7, 0.76, 0.82), sat=0.4, val=0.3, rough_add=0.08, piece_var=0.0))
    film = M.get("water_running")
    if film is None:
        film = bc.material("water_running", (0.05, 0.06, 0.06), 0.01, alpha=0.12)
        N_, L_ = film.node_tree.nodes, film.node_tree.links
        tc_ = N_.new("ShaderNodeTexCoord"); wv = N_.new("ShaderNodeTexWave"); wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 60.0
        wv.inputs["Distortion"].default_value = 14.0; wv.inputs["Detail"].default_value = 8.0; L_.new(tc_.outputs["Object"], wv.inputs["Vector"])
        bp_ = N_.new("ShaderNodeBump"); bp_.inputs["Strength"].default_value = 1.0; bp_.inputs["Distance"].default_value = 0.004
        L_.new(wv.outputs["Fac"], bp_.inputs["Height"]); L_.new(bp_.outputs[0], N_["Principled BSDF"].inputs["Normal"])
        M["water_running"] = film
    st = M["steel"]; yb = -d / 2
    # the cleft slate face: vertical slabs, each a little proud or shy, full height
    rng = np.random.default_rng(int(L * 1000))
    x = -L / 2 + 0.04
    while x < L / 2 - 0.05:
        w = float(min(rng.uniform(0.16, 0.32), L / 2 - 0.04 - x))
        dd = float(rng.uniform(0.03, 0.05))
        _rough_block(P, sl, (x + w / 2, yb + 0.01 + dd / 2, 0.2 + (h - 0.3) / 2), (w - 0.004, dd, h - 0.3), amp=0.004, seed=x * 7, cuts=4)
        x += w
    P.box(film, (0, yb + 0.07, 0.2 + (h - 0.3) / 2), (L - 0.1, 0.003, h - 0.3))           # the water sheet over the stone
    for sx in (-1, 1):
        P.box(st, (sx * (L / 2 - 0.02), yb + 0.05, h / 2), (0.04, 0.1, h))                    # the frame
    P.box(st, (0, yb + 0.06, h - 0.05), (L, 0.12, 0.1))                                     # the head, its slot at the ceiling
    P.box(M["felt"], (0, yb + 0.115, h - 0.105), (L - 0.12, 0.012, 0.01))
    P.box(st, (0, yb + 0.085, 0.09), (L - 0.08, 0.06, 0.18))                                # the catch channel
    P.box(film, (0, yb + 0.085, 0.181), (L - 0.12, 0.04, 0.002))
    gr = _honed_granite(); pd = d - 0.12                                                    # the planter (empty: plants later)
    P.box(gr, (0, yb + 0.12 + pd / 2, 0.21), (L - 0.04, pd, 0.42))
    soil = M.setdefault("planter_soil", bc.material("planter_soil", (0.05, 0.035, 0.025), 0.95))
    P.box(soil, (0, yb + 0.12 + pd / 2, 0.405), (L - 0.1, pd - 0.05, 0.02))
    P.box(M["opal"], (0, yb + 0.12, h - 0.115), (L - 0.12, 0.012, 0.006))                 # a light under the head grazing the water


def grooming_bar(P, L=2.4):
    """The grooming bar on the dry side, three places: a 40 mm oak counter at 0.86 on blackened-steel brackets with a warm light
    under its front edge; a full-width mirror floating 30 mm off the wall with a halo of warm light behind it; per place a slate tray
    (amber-glass bottles with brass pumps: face wash, moisturiser, hair tonic; an oak comb; a stone cup of cotton pads), a hair dryer
    standing in its steel wall holster with its cord to a recessed socket; a tissue box in oak; a walnut + leather stool per place;
    a steel bin under the counter."""
    oak, st = M["oak"], M["steel"]
    amber = M.setdefault("glass_amber", bc.material("glass_amber", (0.35, 0.12, 0.02), 0.08))
    sl = M.setdefault("slate_riven_wf", bc.pbr_material("slate_riven_wf", "slate_floor_03", 0.7, box=True, tint=(0.7, 0.76, 0.82), sat=0.4, val=0.3, rough_add=0.08, piece_var=0.0))
    P.box(oak, (0, 0.25, 0.84), (L, 0.5, 0.04))
    P.box(_led("counter_glow", (1.0, 0.74, 0.46), 2.0), (0, 0.48, 0.817), (L - 0.1, 0.01, 0.004))
    for x in (-L / 2 + 0.2, 0.0, L / 2 - 0.2):
        P.box(st, (x, 0.2, 0.7), (0.03, 0.4, 0.24))
    P.box(_led("halo_warm", (1.0, 0.76, 0.5), 3.0), (0, 0.01, 1.55), (L - 0.02, 0.004, 1.14))  # the halo behind the mirror
    P.box(st, (0, 0.025, 1.55), (L - 0.12, 0.03, 1.08))                                       # the mirror's standoff
    P.box(M["mirror"], (0, 0.042, 1.55), (L - 0.06, 0.006, 1.14))
    for k, x in enumerate((-L / 3, 0.0, L / 3)):
        P.box(sl, (x - 0.12, 0.13, 0.866), (0.3, 0.13, 0.012))                               # the tray
        for j, h_ in enumerate((0.15, 0.12, 0.13)):
            bx = x - 0.22 + j * 0.07
            P.cyl(amber, (bx, 0.13, 0.872), 0.025, h_, seg=16)
            P.rod(M["brass"], (bx, 0.13, 0.872 + h_), (bx, 0.13, 0.872 + h_ + 0.03), 0.006, seg=8)
            P.rod(M["brass"], (bx, 0.13, 0.872 + h_ + 0.03), (bx, 0.16, 0.872 + h_ + 0.03), 0.004, seg=6)
        P.box(oak, (x + 0.02, 0.15, 0.876), (0.16, 0.035, 0.005))                            # comb
        P.cyl(M["ceramic"], (x + 0.12, 0.3, 0.86), 0.04, 0.07, seg=20)                       # a stone cup of cotton pads
        P.cyl(M.setdefault("cotton", bc.material("cotton", (0.92, 0.92, 0.9), 0.95)), (x + 0.12, 0.3, 0.925), 0.033, 0.01, seg=16)
        hx = x + 0.3                                                                          # the dryer in its holster
        P.ring(st, (hx, 0.09), 0.03, 0.038, 0.98, 1.08, seg=20)
        P.box(st, (hx, 0.05, 1.03), (0.03, 0.05, 0.06))
        dry = M.setdefault("dryer_matte", bc.material("dryer_matte", (0.08, 0.08, 0.085), 0.4))
        P.rod(dry, (hx, 0.09, 0.95), (hx, 0.09, 1.2), 0.022, seg=16)                         # handle
        P.rod(dry, (hx, 0.04, 1.24), (hx, 0.19, 1.24), 0.045, seg=24)                        # the head (a ring, air through it)
        P.rod(M["rubber"], (hx, 0.09, 0.95), (hx + 0.06, 0.06, 0.9), 0.004, seg=6)            # its cord to the socket
        P.box(st, (hx + 0.06, 0.012, 0.95), (0.06, 0.01, 0.06))
        P.cyl(M["walnut"], (x, 0.78, 0.0), 0.17, 0.62, seg=32, r2=0.15)                     # stool
        P.cyl(M.setdefault("leather_cognac", bc.material("leather_cognac", (0.32, 0.15, 0.07), 0.45)), (x, 0.78, 0.62), 0.17, 0.035, seg=32)
    P.box(oak, (L / 2 - 0.2, 0.33, 0.9), (0.24, 0.12, 0.09))                                 # tissues in an oak box
    P.box(M["felt"], (L / 2 - 0.2, 0.33, 0.946), (0.1, 0.02, 0.002))
    P.cyl(st, (-L / 2 + 0.3, 0.25, 0.0), 0.13, 0.42, seg=24)                                 # bin


def shoe_cubbies(P, L=2.0, h=1.6, d=0.35):
    """Shoe cubbies at the shoes-off line: an open oak grid, cells 330 x 250, a few pairs of shoes in them."""
    oak = M["oak"]
    nc = max(1, int(L / 0.33)); cw = L / nc; nr = int(h / 0.25)
    for i in range(nc + 1):
        P.box(oak, (-L / 2 + i * cw, d / 2, h / 2), (0.018, d, h))
    for j in range(nr + 1):
        P.box(oak, (0, d / 2, j * h / nr), (L, d, 0.018))
    P.box(oak, (0, 0.009, h / 2), (L, 0.018, h))
    rng = np.random.default_rng(3)
    for i in range(nc):
        for j in range(nr):
            if rng.random() < 0.6:  # a pair: sole + upper + a heel counter
                x0 = -L / 2 + (i + 0.5) * cw; z0 = j * h / nr + 0.01
                c = M["felt_" + COLOURS[int(rng.integers(0, 5))]]
                for sx in (-0.055, 0.055):
                    P.box(M["rubber"], (x0 + sx, d / 2 + 0.02, z0 + 0.012), (0.09, 0.27, 0.022))
                    P.box(c, (x0 + sx, d / 2 + 0.04, z0 + 0.05), (0.085, 0.2, 0.06))
                    P.box(c, (x0 + sx, d / 2 - 0.08, z0 + 0.06), (0.08, 0.06, 0.08))
    P.rod(M["brass"], (L / 2 + 0.01, d - 0.05, 1.3), (L / 2 + 0.04, d - 0.05, 1.32), 0.005, seg=6)   # a long oak shoe horn on a hook
    P.box(M["walnut"], (L / 2 + 0.045, d - 0.05, 0.92), (0.012, 0.05, 0.75))


def towel_shelf(P, L=1.0, h=1.8):
    """Fresh towels: an open oak shelf, stacks of folded white towels."""
    oak = M["oak"]; d = 0.42
    for x in (-L / 2, L / 2):
        P.box(oak, (x, d / 2, h / 2), (0.022, d, h))
    towel = M.setdefault("towel_white", bc.material("towel_white", (0.85, 0.84, 0.8), 0.95))
    for k in range(5):
        z = 0.12 + k * 0.38
        P.box(oak, (0, d / 2, z), (L, d, 0.022))
        if k < 4:
            for sx in (-0.25, 0.0, 0.25):
                if abs(sx) < L / 2 - 0.1:
                    P.box(towel, (sx, d / 2, z + 0.012 + 0.11), (0.24, 0.32, 0.22))


def uvc_plate(P, L=1.5, D=0.9):
    """UV-C sole plate: walk over it and your soles are sanitised; a blackened-steel frame flush with the floor, ribbed dark glass,
    a faint violet glow (UV-C itself is invisible)."""
    P.box(M["steel"], (0, 0, -0.004), (L, D, 0.008))
    glow = M.setdefault("uvc_glow", bc.material("uvc_glow", (0.02, 0.01, 0.04), 0.1, emit=((0.4, 0.25, 1.0), 0.6)))
    P.box(glow, (0, 0, 0.0005), (L - 0.06, D - 0.06, 0.002))
    for k in range(int((L - 0.1) / 0.06)):
        P.box(M["sensor_glass"] if "sensor_glass" in M else M["felt"], (-L / 2 + 0.06 + k * 0.06, 0, 0.0018), (0.012, D - 0.08, 0.001))


def auto_door(P, w=1.0, h=2.1):
    """The WC room's door: hands-free (hygiene), a 40 mm fluted oak leaf sliding in front of the wall on a concealed track, a
    blackened-steel head box with the motion sensor; shut here."""
    oak = M["oak"]
    P.box(M["felt"], (0, 0.03, h / 2), (w + 0.06, 0.01, h))
    x = -w / 2 - 0.03 + 0.03
    while x < w / 2 + 0.03:
        P.box(oak, (x, 0.05, h / 2), (0.035, 0.03, h - 0.01))
        x += 0.05
    P.box(M["steel"], (0, 0.06, h + 0.06), (w * 2 + 0.2, 0.08, 0.12))
    P.box(M.setdefault("sensor_glass", bc.material("sensor_glass", (0.01, 0.01, 0.012), 0.08)), (0, 0.101, h + 0.05), (0.08, 0.003, 0.03))
    P.box(M["brass"], (w / 2 - 0.08, 0.068, 1.05), (0.02, 0.008, 0.3))



# ------------------------------------------------------------------ locker rooms, phase 2: wash zones, WC rooms, robots, sauna lobby
def _tile_mat():
    return M.setdefault("tile_chalk_f", bc.glazed_tile("tile_chalk"))


def _water_film():
    film = M.get("water_running")
    if film is None:
        film = bc.material("water_running", (0.05, 0.06, 0.06), 0.01, alpha=0.12)
        N_, L_ = film.node_tree.nodes, film.node_tree.links
        tc_ = N_.new("ShaderNodeTexCoord"); wv = N_.new("ShaderNodeTexWave"); wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 60.0
        wv.inputs["Distortion"].default_value = 14.0; wv.inputs["Detail"].default_value = 8.0; L_.new(tc_.outputs["Object"], wv.inputs["Vector"])
        bp_ = N_.new("ShaderNodeBump"); bp_.inputs["Strength"].default_value = 1.0; bp_.inputs["Distance"].default_value = 0.004
        L_.new(wv.outputs["Fac"], bp_.inputs["Height"]); L_.new(bp_.outputs[0], N_["Principled BSDF"].inputs["Normal"])
        M["water_running"] = film
    return film


def shower_cell(P, w=1.1, d=2.1, h=2.6, open_door=False, accessible=False):
    """A private shower (VISION wet rooms: oak boxes in the tall room, with a lid): the shower at the back (1.2 deep), a frosted glass
    screen, the dry part at the front with an oak bench, hooks and a towel ring; side walls tiled both faces, an oak lid at 2.6 with
    its light, a fluted oak door with a shadow gap and a green/red thumb-turn (open: swung out). Rain head 300 + hand shower on a
    rail, a blackened-steel thermostatic mixer, a niche for soap, a linear drain. Accessible: 1.8 wide, no screen, a fold-down seat,
    grab rails, a wider (1.0) door. Origin = the back wall at the cell's centre, the front towards +y."""
    oak, st, tile = M["oak"], M["steel"], _tile_mat()
    for sx in (-1, 1):  # the side walls (shared with the neighbours: here each cell draws its own half)
        P.box(tile, (sx * (w / 2 - 0.015), d / 2, h / 2), (0.03, d, h))
    P.box(oak, (0, d / 2, h + 0.015), (w, d, 0.03))                                   # the lid
    P.cyl(M["opal"], (0, d * 0.45, h - 0.012), 0.06, 0.008, seg=24)                     # its light
    ws = 1.2
    if not accessible:  # frosted screen between the shower and the dry part, an opening at one side
        P.box(M.setdefault("glass_satin_s", bc.arch_glass("glass_satin_s", rough=0.35)), (-0.12, ws, 1.05), (w - 0.3, 0.01, 2.0))
        P.box(st, (-0.12, ws, 2.06), (w - 0.3, 0.02, 0.02))                              # its top rail
    P.box(st, (0, 0.04, 2.25), (0.3, 0.3, 0.012))                                       # rain head
    P.rod(st, (0, 0.02, 2.4), (0, 0.04, 2.25), 0.012, seg=10)
    P.box(st, (w / 2 - 0.2, 0.012, 1.05), (0.16, 0.024, 0.1))                           # mixer
    P.rod(st, (w / 2 - 0.35, 0.02, 0.9), (w / 2 - 0.35, 0.02, 1.8), 0.01, seg=10)       # rail
    P.rod(st, (w / 2 - 0.35, 0.05, 1.5), (w / 2 - 0.35, 0.06, 1.72), 0.018, seg=12)     # hand shower
    P.box(M["felt"], (-w / 2 + 0.3, 0.004, 1.2), (0.3, 0.008, 0.25))                    # soap niche
    P.box(st, (0, 0.12, 0.002), (w - 0.2, 0.05, 0.004))                                 # linear drain
    yb = (ws + d) / 2
    if accessible:
        P.box(oak, (-w / 2 + 0.25, 0.5, 0.48), (0.45, 0.45, 0.04))                       # fold-down seat
        P.rod(st, (w / 2 - 0.04, 0.3, 0.85), (w / 2 - 0.04, 1.6, 0.85), 0.016, seg=12)  # grab rails
        P.rod(st, (-w / 2 + 0.04, 0.2, 0.85), (-w / 2 + 0.04, 0.2, 1.6), 0.016, seg=12)
    else:
        P.box(oak, (-w / 2 + 0.2, yb, 0.44), (0.35, d - ws - 0.15, 0.04))                # the bench in the dry part
        for sy in (-1, 1):
            P.rod(st, (-w / 2 + 0.2, yb + sy * 0.25, 0), (-w / 2 + 0.2, yb + sy * 0.25, 0.42), 0.015, seg=8)
    for k in range(2):
        P.rod(st, (w / 2 - 0.035, yb - 0.15 + k * 0.3, 1.65), (w / 2 - 0.09, yb - 0.15 + k * 0.3, 1.65), 0.008, seg=8)  # hooks
    dw = 1.0 if accessible else 0.75
    fz = d - 0.02
    P.box(_led("plinth_glow", (1.0, 0.72, 0.42), 2.5), (0, fz + 0.03, 0.004), (w - 0.06, 0.012, 0.008))  # a warm line at the foot
    for xa_, xb_ in ((-w / 2 + 0.03, -dw / 2 - 0.003), (dw / 2 + 0.003, w / 2 - 0.03)):  # the oak front beside the door
        if xb_ - xa_ > 0.02:
            x = xa_ + 0.015
            while x < xb_:
                P.box(oak, (x, fz, h / 2), (0.028, 0.035, h)); x += 0.03
    if open_door:
        hx = -dw / 2
        P.box(oak, (hx - 0.02, fz + dw / 2, h * 0.45), (0.04, dw, h * 0.9))
    else:
        x = -dw / 2 + 0.015
        while x < dw / 2:
            P.box(oak, (x, fz, h * 0.45), (0.028, 0.04, h * 0.9)); x += 0.03
        P.box(M["felt"], (0, fz + 0.005, h * 0.9 + (h * 0.1) / 2), (dw, 0.03, h * 0.1))    # transom shadow
        P.cyl(_led("led_green", (0.2, 1.0, 0.4), 6.0), (dw / 2 - 0.08, fz + 0.022, 1.05), 0.012, 0.004, seg=16)


def _stone_courses(P, mat, x0, x1, y, z0, z1, seed=0, d=(0.05, 0.064)):
    """Stacked courses of rough stone on a face along x at y (front +y), from z0 to z1: each course 70-150 high, stones 180-460
    long, each a little proud or shy."""
    rng = np.random.default_rng(seed); z = z0
    while z < z1 - 0.02:
        ch = float(min(rng.uniform(0.07, 0.15), z1 - z)); x = x0
        while x < x1 - 0.02:
            pl = float(min(rng.uniform(0.18, 0.46), x1 - x)); dd = float(rng.uniform(*d))
            _rough_block(P, mat, (x + pl / 2, y + dd / 2 - 0.03, z + ch / 2), (pl - 0.006, dd, ch - 0.006), amp=0.006, seed=seed * 1000 + x * 10 + z * 7, cuts=2)
            x += pl
        z += ch


def stone_lining(P, L=3.6, H=3.05):
    """The wash zone's west end wall in the earthy stone of Fossen, stacked in rough courses to the canopy line, so the grotto is
    part of the room, not a box put into it. Origin = the wall face at the centre, front +y."""
    earth = M.setdefault("stone_earth", bc.pbr_material("stone_earth", "slate_floor_03", 0.6, box=True, tint=(0.82, 0.7, 0.58), sat=0.45, val=0.24, rough_add=0.1, piece_var=0.12))
    _stone_courses(P, earth, -L / 2, L / 2, 0.03, 0.0, H, seed=int(L * 100))


def fossen(P, w=2.4, d=2.1, h=2.6, H=3.05):
    """Fossen (the falls): the walk-in experience shower at the west end, a grotto (Roman: more stylised, zen, darker, earthier).
    Back: cleft dark slate, set vertical, the falling water's face. Sides: dark earthy stone stacked in rough horizontal courses,
    full height. Overhead: a low lid of walnut slats at 2.6, the 600 rain head set into it. Underfoot: dark honed slate with a band
    of wet river pebbles set flush where the water lands (nothing cut into the floor). A broad steel lip at 2.3 pours a sheet of
    real water; a cold oak bucket on a steel arm (after the sauna); a hewn stone block to sit on. No frame (Roman: it looked stuck
    in, an asset): the sides rise to the canopy line with a stone lintel over the lid, and the same stone wraps the wash zone's west
    end wall, so Fossen is a niche carved into a stone end of the room. Light only where the water is. Origin = back wall centre, open to the aisle at +y (2.1 deep)."""
    sl = M.setdefault("slate_riven_wf", bc.pbr_material("slate_riven_wf", "slate_floor_03", 0.7, box=True, tint=(0.7, 0.76, 0.82), sat=0.4, val=0.3, rough_add=0.08, piece_var=0.0))
    earth = M.setdefault("stone_earth", bc.pbr_material("stone_earth", "slate_floor_03", 0.6, box=True, tint=(0.82, 0.7, 0.58), sat=0.45, val=0.24, rough_add=0.1, piece_var=0.12))
    st, film = M["steel"], _water_film(); D = d  # the full depth: a short stone passage in, covering the first shower's side wall
    rng = np.random.default_rng(9); x = -w / 2 + 0.06
    while x < w / 2 - 0.08:  # the back: vertical cleft slate
        ww = float(min(rng.uniform(0.18, 0.34), w / 2 - 0.06 - x))
        _rough_block(P, sl, (x + ww / 2, 0.035, h / 2), (ww - 0.004, 0.05, h), amp=0.005, seed=x * 3, cuts=4)
        x += ww
    for sx in (-1, 1):  # the sides: stacked courses of earthy stone up to the canopy line (the west end wall carries on in it)
        z = 0.0
        while z < H - 0.02:
            ch = float(min(rng.uniform(0.07, 0.15), H - z)); y = 0.0
            while y < D - 0.02:
                pl = float(min(rng.uniform(0.18, 0.46), D - y)); dd = float(rng.uniform(0.05, 0.064))
                _rough_block(P, earth, (sx * (w / 2 - dd / 2), y + pl / 2, z + ch / 2), (dd, pl - 0.006, ch - 0.006), amp=0.006, seed=sx * 100 + y * 10 + z * 7, cuts=2)
                y += pl
            z += ch
    _stone_courses(P, earth, -w / 2, w / 2, D - 0.03, h, H, seed=5)  # the lintel over the mouth: one mass of stone, cut open
    for x in np.arange(-w / 2 + 0.035, w / 2, 0.07):  # the walnut lid, black felt behind the gaps
        P.box(M["walnut"], (x, D / 2, h - 0.03), (0.05, D, 0.06))
    P.box(M["felt"], (0, D / 2, h + 0.005), (w, D, 0.01))
    slate_floor = M.setdefault("slate_honed_dark2", bc.material("slate_honed_dark2", (0.035, 0.034, 0.032), 0.6))
    P.box(slate_floor, (0, D / 2, 0.003), (w - 0.1, D, 0.006))                          # dark honed slate underfoot
    peb = M.setdefault("pebble_wet2", bc.material("pebble_wet2", (0.05, 0.047, 0.042), 0.4))
    for px in np.arange(-0.85, 0.16, 0.075):                                              # wet river pebbles, set flush
        for py in np.arange(0.17, 0.46, 0.065):
            r_ = float(rng.uniform(0.026, 0.036))
            P.blob(peb, (float(px + rng.uniform(-0.012, 0.012)), float(py + rng.uniform(-0.01, 0.01)), 0.006), (r_ * 1.25, r_, 0.012), seg=12, z_cut=0.006)
    P.box(st, (-0.35, 0.09, 2.3), (1.0, 0.12, 0.03))                                     # the pouring lip
    fall = M.get("water_fall2")
    if fall is None:  # real water: transmissive, IOR 1.33, streaked; it bends the slate behind it and catches the light
        fall = bc.material("water_fall2", (0.95, 0.97, 0.98), 0.03)
        bsdf = fall.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Transmission Weight"].default_value = 1.0; bsdf.inputs["IOR"].default_value = 1.33
        M["water_fall2"] = fall
    N_, L_ = fall.node_tree.nodes, fall.node_tree.links
    if not any(n.type == "TEX_WAVE" for n in N_):  # streaks running down the sheet
        tc_ = N_.new("ShaderNodeTexCoord"); wv = N_.new("ShaderNodeTexWave"); wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 40.0
        wv.inputs["Distortion"].default_value = 6.0; L_.new(tc_.outputs["Object"], wv.inputs["Vector"])
        bp_ = N_.new("ShaderNodeBump"); bp_.inputs["Strength"].default_value = 0.8
        L_.new(wv.outputs["Fac"], bp_.inputs["Height"]); L_.new(bp_.outputs[0], N_["Principled BSDF"].inputs["Normal"])
    P.box(fall, (-0.35, 0.16, 1.15), (0.95, 0.006, 2.3))                                 # the sheet of water falling from it
    P.box(film, (-0.35, 0.3, 0.008), (1.0, 0.3, 0.002))                                  # the pebbles are wet where it lands
    P.box(st, (0.55, 0.9, 2.5), (0.6, 0.6, 0.02))                                       # rain head, set into the lid
    P.rod(st, (w / 2 - 0.08, 0.6, 2.35), (w / 2 - 0.45, 0.6, 2.35), 0.012, seg=10)        # the cold bucket's arm
    P.cyl(M["oak"], (w / 2 - 0.45, 0.6, 2.1), 0.17, 0.22, seg=24, r2=0.19)              # the pail
    P.ring(M["steel"], (w / 2 - 0.45, 0.6), 0.185, 0.195, 2.17, 2.2, seg=40)
    P.rod(st, (w / 2 - 0.3, 0.6, 2.1), (w / 2 - 0.3, 0.6, 1.7), 0.004, seg=6)             # its pull
    P.ring(M["brass"], (w / 2 - 0.3, 0.6), 0.025, 0.035, 1.68, 1.7, seg=24)
    _rough_block(P, earth, (-w / 2 + 0.33, 0.72, 0.22), (0.42, 1.05, 0.44), amp=0.012, seed=77, cuts=4, flat_top=True)  # a hewn stone to sit on
    P.box(st, (0, 0.25, 0.007), (w - 0.3, 0.05, 0.004))                                 # linear drain
    P.box(_led("niche_glow", (1.0, 0.74, 0.46), 2.0), (-0.35, 0.2, 2.284), (0.9, 0.02, 0.004))  # a low glow under the lip on the water


def wash_place(P, w=0.9, d=1.0):
    """Onsen wash place, made Nordic: seated washing on a low oak stool, a slate shelf at 0.62 with soap + shampoo, a small round
    mirror, a hand shower on a hose with its holder, a blackened-steel mixer, an oak bucket; low oak screens between the places; a
    floor drain. Origin = the wall at the place's centre, front +y."""
    sl = M.setdefault("slate_riven_wf", bc.pbr_material("slate_riven_wf", "slate_floor_03", 0.7, box=True, tint=(0.7, 0.76, 0.82), sat=0.4, val=0.3, rough_add=0.08, piece_var=0.0))
    oak, st = M["oak"], M["steel"]
    P.box(sl, (0, 0.11, 0.62), (w - 0.06, 0.22, 0.04))
    P.box(M["mirror"], (0, 0.006, 1.15), (0.36, 0.004, 0.42))
    P.box(st, (0.25, 0.015, 0.82), (0.12, 0.03, 0.08))
    P.rod(st, (-0.25, 0.02, 0.85), (-0.25, 0.05, 1.0), 0.018, seg=12)
    for k, c in enumerate(((0.5, 0.42, 0.3), (0.85, 0.83, 0.78))):
        P.cyl(bc.material(f"bottle_{k}", c, 0.3), (-0.12 + k * 0.08, 0.12, 0.64), 0.025, 0.16, seg=12)
    P.cyl(oak, (0.05, 0.45, 0.0), 0.16, 0.34, seg=24, r2=0.15)                          # the stool
    P.cyl(oak, (-0.25, 0.4, 0.0), 0.13, 0.2, seg=24, r2=0.15)                           # the bucket
    P.ring(st, (-0.25, 0.4), 0.145, 0.152, 0.17, 0.19, seg=32)
    for sx in (-1, 1):  # a low slatted oak screen between places (seated privacy; light and air pass)
        for k in range(7):
            P.box(oak, (sx * (w / 2 - 0.01), 0.04 + k * 0.065, 0.55), (0.022, 0.035, 1.1))
        P.box(oak, (sx * (w / 2 - 0.01), 0.235, 1.11), (0.03, 0.46, 0.025))
    P.box(sl, (0, 0.012, 1.0), (w - 0.1, 0.02, 1.0))                                           # slate splashback
    P.box(_led("niche_glow", (1.0, 0.74, 0.46), 2.0), (0, 0.2, 0.597), (w - 0.14, 0.01, 0.004))  # warm light under the shelf
    P.box(st, (0, 0.55, 0.002), (0.15, 0.15, 0.004))


def stone_bench(P, L=1.3):
    """A stone bench: one honed granite slab on two granite blocks (onsen-style rest, sit and wait)."""
    gr = _honed_granite()
    P.box(gr, (0, 0, 0.42), (L, 0.42, 0.07))
    for sx in (-1, 1):
        P.box(gr, (sx * (L / 2 - 0.2), 0, 0.19), (0.2, 0.36, 0.38))


def vaskebjorn(P, ring="fjord"):
    """Vaskebjørn (the raccoon, 'wash bear'): the little cleaning robot. A 420 cube on four hidden wheels: oiled oak side panels, a
    blackened-steel chassis + top, a grey rubber bumper skirt, a smoked-glass face band with two soft round LED eyes, a thin zone
    ring (lingon = WC rooms, fjord = wash zones), a scrub pad + squeegee underneath."""
    a = 0.42
    P.box(M["rubber"], (0, 0, 0.03), (a + 0.02, a + 0.02, 0.06))
    P.box(M["steel"], (0, 0, 0.07), (a, a, 0.02))
    for sx, sy, rz in ((1, 0, 0), (-1, 0, 0), (0, 1, 1), (0, -1, 1)):
        P.box(M["oak"], (sx * (a / 2 - 0.01), sy * (a / 2 - 0.01), 0.24), (0.02 if not rz else a - 0.04, a - 0.04 if not rz else 0.02, 0.32))
    P.box(M["steel"], (0, 0, 0.41), (a, a, 0.02))
    face = M.setdefault("robot_face", bc.material("robot_face", (0.01, 0.012, 0.014), 0.05))
    P.box(face, (0, a / 2 + 0.002, 0.3), (a - 0.08, 0.006, 0.12))
    eye = _led("robot_eye", (0.75, 0.9, 1.0), 6.0)
    for sx in (-0.07, 0.07):
        P.box(eye, (sx, a / 2 + 0.006, 0.3), (0.04, 0.003, 0.04))
    P.box(M["lino_" + ring] if "lino_" + ring in M else M["felt"], (0, 0, 0.083), (a + 0.004, a + 0.004, 0.006))


def robot_dock(P, w=0.5):
    """A robot's dock: a 500 x 500 arch-topped recess at floor level with a blackened-steel frame, charging contacts, its own drain."""
    st = M["steel"]
    P.box(M["felt"], (0, 0.01, 0.25), (w - 0.04, 0.02, 0.5))
    for sx in (-1, 1):
        P.box(st, (sx * (w / 2 - 0.015), 0.02, 0.26), (0.03, 0.04, 0.52))
    P.box(st, (0, 0.02, 0.51), (w, 0.04, 0.03))
    for sx in (-0.08, 0.08):
        P.box(M["brass"], (sx, 0.03, 0.1), (0.04, 0.01, 0.02))


def slipper_cabinet(P, L=1.0):
    """Toilet slippers in a UV-C cabinet (the onsen habit; sanitised between users): an oak cabinet with a glass front, a violet glow
    inside, pairs of felt slippers on two shelves; a used-slippers drop slot beside it."""
    oak = M["oak"]; d = 0.35; h = 0.9
    P.box(oak, (0, d / 2, 0.02), (L, d, 0.04)); P.box(oak, (0, d / 2, h), (L, d, 0.03))
    for sx in (-1, 1):
        P.box(oak, (sx * (L / 2 - 0.01), d / 2, h / 2), (0.02, d, h))
    P.box(oak, (0, 0.01, h / 2), (L, 0.02, h))
    P.box(oak, (0, d / 2, 0.45), (L - 0.04, d - 0.02, 0.02))
    P.box(M["glass"], (0, d - 0.005, h / 2), (L - 0.04, 0.008, h - 0.06))
    P.box(M.setdefault("uvc_glow", bc.material("uvc_glow", (0.02, 0.01, 0.04), 0.1, emit=((0.4, 0.25, 1.0), 0.6))), (0, 0.03, h - 0.05), (L - 0.06, 0.02, 0.01))
    for z in (0.05, 0.48):
        for k in range(int(L / 0.24)):
            x = -L / 2 + 0.14 + k * 0.24
            for sx in (-0.04, 0.04):
                P.box(M["felt_oat"] if "felt_oat" in M else M["felt"], (x + sx, d / 2, z + 0.02), (0.07, 0.24, 0.03))


def far_uvc(P, z_ceiling=2.73):
    """A far-UVC lamp (222 nm, safe with people present) recessed in the WC ceiling: a small blackened-steel square with a filter window."""
    P.box(M["steel"], (0, 0, z_ceiling - 0.01), (0.22, 0.22, 0.02))
    P.box(M.setdefault("uvc_glow", bc.material("uvc_glow", (0.02, 0.01, 0.04), 0.1, emit=((0.4, 0.25, 1.0), 0.6))), (0, 0, z_ceiling - 0.021), (0.14, 0.14, 0.002))


def robe_wall(P, L=4.2):
    """The sauna lobby's robe wall: an oak rail of steel hooks at 1.8 (for your robe while you are in), an oak shelf of fresh robes
    rolled with their ends out and a linen band, an oak sandal rack below."""
    oak, st = M["oak"], M["steel"]
    P.box(oak, (0, 0.02, 1.8), (L, 0.04, 0.12))
    robe = M.setdefault("robe_linen", bc.pbr_material("robe_linen", "rough_linen", 0.27, box=True, tint=(0.95, 0.93, 0.88), sat=0.2, val=1.4, piece_var=0.03))
    for k in range(int(L / 0.35)):                                                            # hooks, free for your own robe
        x = -L / 2 + 0.2 + k * 0.35
        P.rod(st, (x, 0.04, 1.8), (x, 0.12, 1.84), 0.008, seg=8)
    P.box(oak, (0, 0.17, 1.15), (L, 0.32, 0.03))                                              # the robe shelf
    for sx in (-1, 0, 1):
        P.box(st, (sx * (L / 2 - 0.3), 0.12, 1.08), (0.025, 0.22, 0.12))
    _kulpen_mats(); rng = np.random.default_rng(31)
    band = M.setdefault("robe_band", bc.material("robe_band", (0.55, 0.47, 0.37), 0.9))
    x = -L / 2 + 0.13
    while x < L / 2 - 0.1:                                                                    # fresh robes, rolled, ends out
        r = float(rng.uniform(0.078, 0.09)); sag = float(rng.uniform(0.82, 0.9)); y0 = 0.03 + float(rng.uniform(0, 0.025))
        _robe_roll(P, M["robe_terry"], x, 1.165 + r * sag, y0, y0 + 0.27, r, sag)
        P.prism(band, [(x + (r + 0.002) * math.cos(a), 1.165 + r * sag + (r + 0.002) * math.sin(a) * sag) for a in np.linspace(0, 2 * math.pi, 25)[:-1]], 0.15, 0.18)  # a linen band
        x += 2 * r + 0.025
    for z in (0.08, 0.3):
        P.box(oak, (0, 0.17, z), (L, 0.3, 0.025))
    for k in range(int(L / 0.3)):                                                             # sandals: a footbed + a felt strap
        x = -L / 2 + 0.18 + k * 0.3
        for sx in (-0.05, 0.05):
            P.blob(M["rubber"], (x + sx, 0.17, 0.11), (0.042, 0.13, 0.014), seg=20)
            P.box(M["felt"], (x + sx, 0.12, 0.126), (0.085, 0.045, 0.012))


def towel_warmer(P, L=1.2):
    """A towel warmer: a blackened-steel cabinet with an oak door + a glass window, warm towels inside, a soft glow."""
    st = M["steel"]; d = 0.45; h = 1.6
    P.box(st, (0, d / 2, h / 2), (L, d, h))
    P.box(M["oak"], (0, d + 0.01, h / 2), (L - 0.04, 0.02, h - 0.04))
    P.box(M["glass"], (0, d + 0.022, h * 0.62), (L - 0.3, 0.004, 0.6))
    P.box(_led("warm_glow", (1.0, 0.7, 0.45), 1.5), (0, d - 0.03, h * 0.62), (L - 0.34, 0.01, 0.56))



def tap_station(P):
    """A water station (drink before, during, after): a recessed panel of cleft slate in a blackened-steel frame, a steel spout
    with a push plate (still, chilled, from the house filter), a slotted drain under it, no lettering. Members bring their own bottle
    (Roman 2026-10-18: the cups on top were low-brow; only the cafe's water station keeps glasses). Origin = the wall at the centre, front +y."""
    st = M["steel"]
    sl = M.setdefault("slate_riven_wf", bc.pbr_material("slate_riven_wf", "slate_floor_03", 0.7, box=True, tint=(0.7, 0.76, 0.82), sat=0.4, val=0.3, rough_add=0.08, piece_var=0.0))
    P.box(st, (0, 0.02, 1.15), (0.66, 0.04, 1.06))
    P.box(sl, (0, 0.035, 1.15), (0.6, 0.02, 1.0))
    P.box(st, (0, 0.11, 1.32), (0.05, 0.16, 0.04)); P.rod(st, (0, 0.17, 1.32), (0, 0.17, 1.28), 0.008, seg=8)
    P.box(M["brass"], (0.12, 0.048, 1.35), (0.07, 0.006, 0.07))                                # push plate
    P.box(st, (0, 0.11, 0.92), (0.36, 0.16, 0.02))
    for k in range(9):
        P.box(M["felt"], (-0.16 + k * 0.04, 0.11, 0.931), (0.012, 0.13, 0.002))                 # the drain slots


def log_store(P, L=1.2, h=2.0, d=0.35):
    """A birch log store for the sauna stove: an oak frame filled with split birch, ends out, white bark showing; a kindling basket
    of felt on top, a steel ladle and a birch bucket (kjøkle + bøtte) on the shelf. Origin = the wall at the centre, front +y."""
    oak, st = M["oak"], M["steel"]
    for sx in (-1, 1):
        P.box(oak, (sx * (L / 2 - 0.015), d / 2, h / 2), (0.03, d, h))
    for z in (0.0, h - 0.4, h):
        P.box(oak, (0, d / 2, z + 0.015), (L, d, 0.03))
    bark = M.setdefault("birch_bark", bc.material("birch_bark", (0.86, 0.83, 0.77), 0.8))
    end = M.setdefault("birch_end", bc.material("birch_end", (0.78, 0.62, 0.43), 0.85))
    rng = np.random.default_rng(11); z = 0.09
    while z < h - 0.45:
        x = -L / 2 + 0.08
        while x < L / 2 - 0.07:
            r = float(rng.uniform(0.045, 0.065))
            P.rod(bark, (x, 0.02, z), (x, d - 0.02, z), r, seg=10)
            P.rod(end, (x, d - 0.021, z), (x, d - 0.017, z), r - 0.008, seg=10)                       # the cut end
            x += 2 * r + 0.005
        z += 0.11
    P.cyl(oak, (-0.25, d / 2, h - 0.37), 0.12, 0.2, seg=24, r2=0.13)                           # the bucket
    P.ring(st, (-0.25, d / 2), 0.125, 0.132, h - 0.3, h - 0.28, seg=32)
    P.rod(oak, (0.15, d / 2, h - 0.36), (0.45, d / 2, h - 0.2), 0.012, seg=8)                  # the ladle
    P.cyl(oak, (0.12, d / 2, h - 0.37), 0.04, 0.03, seg=16)


def duckboard(P, w=1.2, d=0.8):
    """An oak duckboard at the sauna door: slats on two battens, wet feet off the stone."""
    for k in range(int(d / 0.06)):
        P.box(M["oak"], (0, -d / 2 + 0.03 + k * 0.06, 0.03), (w, 0.045, 0.022))
    for sx in (-1, 1):
        P.box(M["rubber"], (sx * (w / 2 - 0.1), 0, 0.009), (0.05, d, 0.018))


def slat_canopy(P, L=9.7, W=4.9, z=3.05, pitch=0.12, hang=1.4):
    """An open oak slat canopy over a wash zone: 40 x 60 white-oiled oak slats at 120 along the room, two-thirds open, on blackened-
    steel cross bearers hung from the soffit. The clerestory daylight still comes in, but filtered and dappled (light through
    trees), and the tall wet room gets an intimate height over the bathers. Origin = the room's centre on the floor."""
    oak, st = M["oak"], M["steel"]
    y = -W / 2 + pitch / 2
    while y < W / 2:
        P.box(oak, (0, y, z + 0.03), (L - 0.04, 0.04, 0.06)); y += pitch
    nb = max(2, int(L / 1.8)) + 1
    for k in range(nb):
        x = -L / 2 + 0.3 + k * (L - 0.6) / (nb - 1)
        P.box(st, (x, 0, z + 0.075), (0.04, W - 0.04, 0.03))
        for sy in (-1, 1):
            P.rod(st, (x, sy * (W / 2 - 0.4), z + 0.09), (x, sy * (W / 2 - 0.4), z + 0.09 + hang), 0.005, seg=6)


def eyelid_sconce(P, z=1.95):
    """A small blackened-steel 'eyelid' sconce over a wash place: a hooded half-cylinder on a wall plate at 1.95, its warm light
    falling in a pool on the shelf and the stool; nothing glares at a seated bather."""
    st = M["steel"]
    P.box(st, (0, 0.006, z), (0.12, 0.012, 0.16))
    P.rod(st, (-0.07, 0.07, z + 0.03), (0.07, 0.07, z + 0.03), 0.06, seg=16)
    P.box(M["felt"], (0, 0.07, z - 0.01), (0.13, 0.11, 0.06))
    P.box(_led("niche_glow", (1.0, 0.74, 0.46), 2.0), (0, 0.075, z - 0.041), (0.11, 0.07, 0.002))



# ------------------------------------------------------------------ Kulpen, the outdoor sauna (VISION "Kulpen", Roman 2026-10-14)
def _kulpen_mats():
    """Thermo-aspen (heat-treated: honey-brown all through, no resin, cool to sit on), light aspen, soapstone (kleberstein), split
    granite, birch bark, the fire, the bathing water."""
    M.setdefault("aspen_thermo", bc.pbr_material("aspen_thermo", "ash_veneer", 1.0, box=True, tint=(1.0, 0.74, 0.5), sat=0.95, val=0.78, piece_var=0.08, rough_add=0.1))
    M.setdefault("aspen", bc.pbr_material("aspen_light", "ash_veneer", 1.0, box=True, tint=(1.05, 1.0, 0.9), sat=0.4, val=1.55, piece_var=0.06))
    M.setdefault("soapstone", bc.pbr_material("soapstone", "dark_rock", 1.6, box=True, tint=(0.78, 0.86, 0.82), sat=0.35, val=0.72, rough_mul=0.55, rough_add=0.15, piece_var=0.05))
    M.setdefault("granite_split", bc.pbr_material("granite_split", "quarry_wall", 1.4, box=True, tint=(0.95, 0.95, 0.95), sat=0.25, val=0.8, piece_var=0.12))
    M.setdefault("slate_floor", bc.pbr_material("slate_floor", "slate_floor_03", 1.0, box=True, tint=(0.75, 0.78, 0.8), sat=0.4, val=0.42, rough_add=0.05, piece_var=0.1))
    M.setdefault("birch_bark", bc.material("birch_bark", (0.86, 0.83, 0.77), 0.8))
    M.setdefault("birch_end", bc.material("birch_end", (0.78, 0.62, 0.43), 0.85))
    if "birch_bark_real" not in M:
        M["birch_bark_real"] = _birch_bark()
        M["birch_split"] = bc.pbr_material("birch_split", "ash_veneer", 0.5, box=True, tint=(1.02, 0.93, 0.76), sat=0.7, val=1.05, piece_var=0.12, rough_add=0.25)
        M["birch_endgrain"] = bc.pbr_material("birch_endgrain", "ash_veneer", 0.25, box=True, rotate=1.2, tint=(1.0, 0.88, 0.68), sat=0.7, val=1.0, piece_var=0.15, rough_add=0.3)
        M["robe_terry"] = _terry()
    M.setdefault("fire", bc.material("fire_glow", (1.0, 0.45, 0.12), 0.6, emit=((1.0, 0.42, 0.1), 18.0)))
    M.setdefault("water_bath", bc.arch_glass("water_bath", tint=(0.8, 0.9, 0.86)))
    M.setdefault("towel_white", bc.material("towel_white", (0.85, 0.84, 0.8), 0.95))
    return M


def _birch_bark():
    """Birch bark: chalk white with a faint warm cast, thin dark lenticel streaks running round the trunk (across the log), a few
    dark rough patches; matte."""
    m = bpy.data.materials.new("birch_bark_real"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.0, 45.0, 2.0); L.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 2.0; L.new(mp.outputs[0], nz.inputs["Vector"])
    lent = N.new("ShaderNodeMapRange"); lent.inputs[1].default_value = 0.6; lent.inputs[2].default_value = 0.68; L.new(nz.outputs["Fac"], lent.inputs[0])
    pz = N.new("ShaderNodeTexNoise"); pz.inputs["Scale"].default_value = 7.0; pz.inputs["Detail"].default_value = 4.0; L.new(tc.outputs["Object"], pz.inputs["Vector"])
    pat = N.new("ShaderNodeMapRange"); pat.inputs[1].default_value = 0.62; pat.inputs[2].default_value = 0.7; L.new(pz.outputs["Fac"], pat.inputs[0])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; L.new(lent.outputs[0], mx.inputs[0]); L.new(pat.outputs[0], mx.inputs[1])
    tone = N.new("ShaderNodeTexNoise"); tone.inputs["Scale"].default_value = 3.0; L.new(tc.outputs["Object"], tone.inputs["Vector"])
    base = N.new("ShaderNodeValToRGB"); base.color_ramp.elements[0].color = (0.62, 0.6, 0.55, 1); base.color_ramp.elements[1].color = (0.8, 0.78, 0.72, 1)
    L.new(tone.outputs["Fac"], base.inputs[0])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; L.new(mx.outputs[0], mix.inputs["Factor"]); L.new(base.outputs[0], mix.inputs["A"])
    mix.inputs["B"].default_value = (0.05, 0.045, 0.04, 1)
    L.new(mix.outputs["Result"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.75
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; L.new(mx.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


def _terry():
    """Cotton terry towelling: warm off-white, matte, a fine looped pile (bump), a faint unevenness of tone."""
    m = bpy.data.materials.new("robe_terry"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    tone = N.new("ShaderNodeTexNoise"); tone.inputs["Scale"].default_value = 12.0; L.new(tc.outputs["Object"], tone.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = (0.7, 0.68, 0.63, 1); rp.color_ramp.elements[1].color = (0.8, 0.78, 0.73, 1)
    L.new(tone.outputs["Fac"], rp.inputs[0]); L.new(rp.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.97
    try:
        b.inputs["Sheen Weight"].default_value = 0.4
    except KeyError:
        pass
    pile = N.new("ShaderNodeTexVoronoi"); pile.inputs["Scale"].default_value = 450.0; L.new(tc.outputs["Object"], pile.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.002
    L.new(pile.outputs["Distance"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m


def _split_piece(P, x, z, y0, y1, r, kind, rot):
    """One piece of split birch lying along y: a half, a third, a quarter or a whole round; split faces pale, the bark only on the
    outer arc, the front end a separate cut face (end grain)."""
    span = {"half": math.pi, "third": 2 * math.pi / 3, "quarter": math.pi / 2, "round": 2 * math.pi}[kind]
    n = 14 if kind == "round" else 9
    arc = [rot + span * k / n for k in range(n + (0 if kind == "round" else 1))]
    ri = r - 0.007
    body = [(x + ri * math.cos(a), z + ri * math.sin(a)) for a in arc] + ([] if kind == "round" else [(x, z)])
    P.prism(M["birch_split"], body, y0, y1 - 0.004)
    P.prism(M["birch_endgrain"], body, y1 - 0.004, y1)
    shell = [(x + r * math.cos(a), z + r * math.sin(a)) for a in arc] + [(x + ri * math.cos(a), z + ri * math.sin(a)) for a in reversed(arc)]
    if kind == "round":
        for a0, a1 in ((0, n // 2), (n // 2, n)):
            seg = arc[a0:a1 + 1] if a1 < n else arc[a0:] + [arc[0] + 2 * math.pi]
            P.prism(M["birch_bark_real"], [(x + r * math.cos(a), z + r * math.sin(a)) for a in seg] + [(x + ri * math.cos(a), z + ri * math.sin(a)) for a in reversed(seg)], y0, y1 - 0.004)
    else:
        P.prism(M["birch_bark_real"], shell, y0, y1 - 0.004)


def _robe_roll(P, mat, x, z, y0, y1, r=0.085, sag=0.86):
    """A robe rolled for the shelf: the towelling wound in a spiral you can see at the end, slightly flattened by its own weight."""
    t, turns = 0.011, max(2.5, (r - 0.012) / 0.0135)
    pts_o, pts_i = [], []
    nseg = int(turns * 28)
    for k in range(nseg + 1):
        th = 2 * math.pi * turns * k / nseg; rr = 0.012 + (r - 0.012) * k / nseg
        pts_o.append((x + rr * math.cos(th), z + rr * math.sin(th) * sag)); pts_i.append((x + (rr - t) * math.cos(th), z + (rr - t) * math.sin(th) * sag))
    P.prism(mat, pts_o + pts_i[::-1], y0, y1)


def _xprism(P, mat, pts_yz, x0, x1):
    """A profile in the y-z plane extruded along x (half logs, sloped stringers)."""
    b = P.bm(mat)
    v0 = [b.verts.new((x0, y, z)) for y, z in pts_yz]; v1 = [b.verts.new((x1, y, z)) for y, z in pts_yz]
    b.faces.new(v0[::-1]); b.faces.new(v1)
    n = len(pts_yz)
    for i in range(n):
        j = (i + 1) % n
        b.faces.new((v0[i], v0[j], v1[j], v1[i]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces[-(n + 2):])


def sauna_tier(P, L=3.0, d=0.6, seat=1.0, back=False):
    """A tier of Kulpen's benches in thermo-aspen: seat slats 28 thick along the run with 12 mm gaps, on bearers at <= 600, a wall
    cleat and front legs; under the front edge a warm LED line that lights the slatted skirt below (the only light in the hot
    room besides the fire and the window). back=True: a raked three-slat backrest on brackets against the wall.
    Origin = the bench's centre on the floor, front +y."""
    _kulpen_mats(); a = M["aspen_thermo"]
    n = max(3, int(round(d / 0.1))); p = d / n
    for k in range(n):
        P.box(a, (0, -d / 2 + p * (k + 0.5), seat - 0.014), (L - 0.004, p - 0.012, 0.028))
    nb = max(2, math.ceil(L / 0.6) + 1)
    for k in range(nb):
        u = -L / 2 + 0.03 + k * (L - 0.06) / (nb - 1)
        P.box(a, (u, 0, seat - 0.063), (0.045, d - 0.02, 0.07))
    P.box(a, (0, -d / 2 + 0.0225, seat - 0.063), (L, 0.045, 0.07))                       # wall cleat
    P.box(a, (0, d / 2 - 0.0425, seat - 0.063), (L, 0.045, 0.07))                        # front rail
    nl = max(2, math.ceil(L / 1.2) + 1)
    for k in range(nl):
        u = -L / 2 + 0.05 + k * (L - 0.1) / (nl - 1)
        P.box(a, (u, d / 2 - 0.09, (seat - 0.098) / 2), (0.068, 0.068, seat - 0.098))
    z0 = 0.6 if seat > 0.8 else 0.07                                                       # the skirt: above the lower tier's seat / off the floor
    u = -L / 2 + 0.04
    while u < L / 2 - 0.03:
        P.box(a, (u, d / 2 - 0.13, (z0 + seat - 0.1) / 2), (0.07, 0.02, seat - 0.1 - z0)); u += 0.085
    P.box(_led("bench_line", (1.0, 0.7, 0.42), 0.8), (0, d / 2 - 0.075, seat - 0.1), (L - 0.1, 0.012, 0.005))
    if back:
        for k, z in enumerate((0.25, 0.42, 0.59)):
            P.box(a, (0, -d / 2 + 0.06 + 0.035 * k, seat + z), (L - 0.02, 0.022, 0.09), rx=math.radians(-12))
        for k in range(nb):
            uu = -L / 2 + 0.03 + k * (L - 0.06) / (nb - 1)
            P.box(a, (uu, -d / 2 + 0.03, seat + 0.42), (0.04, 0.05, 0.5))


def sauna_heater(P):
    """Kulpen's heater: a soapstone (kleberstein) mass heater, hybrid. Four courses of 300 mm soapstone on a slate plinth hold the
    heat for hours; a steel basket of stones on top for the löyly; a small fire window into the hot room; electric elements in the
    same mass keep it hot in the unstaffed hours. It is fired from the changing room: a neck through the wall, a soapstone face
    there with a cast door, an ash door, a slate hearth in front. A blackened-steel guard rail round the hot-room sides; the flue
    rises to the granite chimney. Origin = the body's centre on the floor (hot room side), front +y (into the hot room)."""
    _kulpen_mats(); ss, st, sl = M["soapstone"], M["steel"], M["slate_floor"]
    W, D = 0.9, 0.75
    P.box(sl, (0, 0, 0.025), (W + 0.06, D + 0.06, 0.05))
    for k, (z0, z1) in enumerate(((0.05, 0.36), (0.36, 0.67), (0.67, 0.98), (0.98, 1.25))):
        i = 0.02 if k == 3 else 0.0
        P.box(ss, (0, 0, (z0 + z1) / 2), (W - 2 * i, D - 2 * i, z1 - z0 - 0.004))
    for sx in (-1, 1):                                                                     # the stone basket
        P.box(st, (sx * 0.42, 0, 1.36), (0.008, 0.69, 0.22)); P.box(st, (0, sx * 0.345, 1.36), (0.84, 0.008, 0.22))
    rng = np.random.default_rng(7)
    stone = M.setdefault("sauna_stones", bc.pbr_material("sauna_stones", "dark_rock", 0.6, box=True, tint=(0.75, 0.75, 0.75), sat=0.3, val=0.6, piece_var=0.15))
    for z in (1.29, 1.36, 1.43):
        for _ in range(26):
            r = float(rng.uniform(0.045, 0.07))
            P.blob(stone, (float(rng.uniform(-0.36, 0.36)), float(rng.uniform(-0.28, 0.28)), z), (r, r * float(rng.uniform(0.8, 1.1)), r * 0.7), seg=12)
    P.box(st, (0, D / 2 + 0.006, 0.55), (0.4, 0.012, 0.32))                                # the fire window (hot room)
    P.box(M["fire"], (0, D / 2 + 0.008, 0.55), (0.3, 0.012, 0.22))
    P.box(M["glass"], (0, D / 2 + 0.016, 0.55), (0.32, 0.006, 0.24))
    P.box(ss, (0, -D / 2 - 0.1, 0.525), (0.5, 0.2, 0.45))                                  # the neck through the wall
    yF = -D / 2 - 0.2 - 0.06                                                               # the face in the changing room
    P.box(ss, (0, yF, 0.5), (0.9, 0.12, 0.9))
    P.box(st, (0, yF - 0.07, 0.5), (0.38, 0.02, 0.32)); P.box(M["fire"], (0, yF - 0.075, 0.5), (0.24, 0.012, 0.18))
    P.box(M["glass"], (0, yF - 0.083, 0.5), (0.26, 0.006, 0.2))
    P.rod(st, (0.15, yF - 0.08, 0.5), (0.15, yF - 0.14, 0.5), 0.01, seg=8); P.rod(st, (0.15, yF - 0.14, 0.44), (0.15, yF - 0.14, 0.56), 0.012, seg=8)
    P.box(st, (0, yF - 0.07, 0.17), (0.3, 0.02, 0.09))                                     # ash door
    P.box(sl, (0, yF - 0.06 - 0.3, 0.01), (0.9, 0.6, 0.02))                                # slate hearth
    P.cyl(st, (0, -0.18, 1.25), 0.08, 1.1, seg=24)                                          # flue to the chimney
    for sx in (-1, 1):                                                                     # guard
        for yy in (-0.3, 0.5):
            P.rod(st, (sx * 0.58, yy, 0.0), (sx * 0.58, yy, 0.9), 0.012, seg=10)
        for z in (0.45, 0.88):
            P.rod(st, (sx * 0.58, -0.3, z), (sx * 0.58, 0.5, z), 0.01, seg=10)
    for z in (0.45, 0.88):
        P.rod(st, (-0.58, 0.5, z), (0.58, 0.5, z), 0.01, seg=10)


def sauna_bucket(P):
    """An oak löyly bucket with brass hoops and a long-handled oak ladle across it (the brass is the accent). Origin = floor, front +y."""
    _kulpen_mats(); oak = M["oak"]
    P.cyl(oak, (0, 0, 0.0), 0.13, 0.03, seg=28)
    P.ring(oak, (0, 0), 0.125, 0.145, 0.0, 0.26, seg=48)
    for z in (0.05, 0.2):
        P.ring(M["brass"], (0, 0), 0.145, 0.151, z, z + 0.015, seg=48)
    P.cyl(M["water_bath"], (0, 0, 0.17), 0.126, 0.005, seg=28)
    P.rod(oak, (-0.1, 0.0, 0.27), (0.42, 0.04, 0.33), 0.011, seg=8)
    P.cyl(oak, (-0.06, 0.0, 0.2), 0.045, 0.06, seg=18)


def kindling_basket(P):
    """A birch-bark basket of kindling by the firebox. Origin = floor, front +y."""
    _kulpen_mats(); bark = M["birch_bark"]
    P.ring(bark, (0, 0), 0.15, 0.165, 0.0, 0.32, seg=40); P.cyl(bark, (0, 0, 0.0), 0.16, 0.02, seg=28)
    rng = np.random.default_rng(5)
    for _ in range(14):
        x, y = rng.uniform(-0.1, 0.1, 2)
        P.rod(M["birch_end"], (float(x), float(y), 0.03), (float(x) + float(rng.uniform(-0.04, 0.04)), float(y), 0.42), 0.012, seg=6)


def firewood_stack(P, L=1.2, h=1.8, d=0.42):
    """Birch for the heater and the tub, stacked under the porch eave against the granite wall the way it is done: split halves,
    thirds and quarters (some small rounds), 30-40 cm long, ends out and ragged, bark white with dark lenticels, the split faces
    pale, the cut ends warmer; on two oak sleepers. Origin = the wall at the centre, front +y."""
    _kulpen_mats()
    for sx in (-1, 1):
        P.box(M["oak"], (sx * (L / 2 - 0.1), d / 2, 0.03), (0.08, d, 0.06))
    rng = np.random.default_rng(23); z = 0.06
    kinds = ["half", "half", "third", "quarter", "quarter", "round"]
    while z < h - 0.05:
        x = -L / 2 + 0.02; row_h = 0.0
        while x < L / 2 - 0.06:
            kind = kinds[int(rng.integers(len(kinds)))]
            r = float(rng.uniform(0.05, 0.075)) if kind != "round" else float(rng.uniform(0.03, 0.045))
            w = 2 * r if kind in ("half", "round") else 1.6 * r
            ln = float(rng.uniform(0.3, 0.4)); yf = d - 0.01 - float(rng.uniform(0, 0.05))
            span = {"half": math.pi, "third": 2 * math.pi / 3, "quarter": math.pi / 2, "round": 2 * math.pi}[kind]
            if kind == "half":   # flat face down or up
                rot = float(rng.choice([0.0, math.pi])) + float(rng.uniform(-0.12, 0.12))
            else:                # wedges point down, the bark arc on top (they nest into the row below)
                rot = math.pi / 2 - span / 2 + float(rng.uniform(-0.25, 0.25))
            arc = [rot + span * k / 12 for k in range(13)]
            zs = [r * math.sin(a) for a in arc] + ([] if kind == "round" else [0.0])
            xs_ = [r * math.cos(a) for a in arc] + ([] if kind == "round" else [0.0])
            w = max(xs_) - min(xs_)
            cz = z - min(zs) + float(rng.uniform(0, 0.006))
            _split_piece(P, x - min(xs_), cz, yf - ln, yf, r, kind, rot)
            x += w + float(rng.uniform(0.002, 0.012)); row_h = max(row_h, max(zs) - min(zs))
        z += row_h * 0.88


def peg_rail(P, L=2.0):
    """Changing-room pegs: an oak rail at 1.65 with oak pegs at 200, two towels hanging. Origin = the wall, front +y."""
    _kulpen_mats(); oak = M["oak"]
    P.box(oak, (0, 0.012, 1.65), (L, 0.024, 0.1))
    n = int(L / 0.2)
    for k in range(n):
        x = -L / 2 + 0.1 + k * 0.2
        P.rod(oak, (x, 0.02, 1.65), (x, 0.1, 1.68), 0.012, seg=10)
    for x in (-L / 2 + 0.3, -L / 2 + 0.9):
        P.box(M["towel_white"], (x, 0.085, 1.4), (0.3, 0.025, 0.5))


def sauna_gauges(P):
    """A thermometer + hygrometer (brass rims) and a sand timer on an aspen board at eye height. Origin = the wall, front +y."""
    _kulpen_mats()
    P.box(M["aspen_thermo"], (0, 0.01, 1.7), (0.32, 0.02, 0.18))
    for x in (-0.08, 0.04):
        P.cyl(M["brass"], (x, 0.03, 1.7), 0.045, 0.012, seg=28); P.cyl(M["ceramic"], (x, 0.037, 1.7), 0.04, 0.006, seg=28)
    P.box(M["aspen_thermo"], (0.12, 0.05, 1.63), (0.06, 0.05, 0.012)); P.box(M["aspen_thermo"], (0.12, 0.05, 1.77), (0.06, 0.05, 0.012))
    P.cyl(M["glass"], (0.12, 0.05, 1.64), 0.022, 0.12, seg=16)


def split_log_bench(P, L=1.4):
    """The porch bench: a half pine log, flat side up, on two split granite blocks. Origin = floor, front +y."""
    _kulpen_mats()
    for sx in (-1, 1):
        P.box(M["granite_split"], (sx * (L / 2 - 0.25), 0, 0.15), (0.34, 0.3, 0.3))
    r = 0.17
    prof = [(r * math.cos(a), 0.47 - r * math.sin(a)) for a in np.linspace(0, math.pi, 13)]
    _xprism(P, M["log"], [(y, z) for y, z in prof], -L / 2, L / 2)
    P.box(M["oak"], (0, 0, 0.475), (L, 2 * r - 0.01, 0.01))


def porch_lantern(P, z=2.0):
    """A blackened-steel porch lantern: an open frame round an opal cylinder, a cap, a wall arm. Origin = the wall, front +y."""
    st = M["steel"]
    P.box(st, (0, 0.006, z + 0.1), (0.1, 0.012, 0.16)); P.box(st, (0, 0.08, z + 0.15), (0.03, 0.15, 0.02))
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.box(st, (sx * 0.07, 0.16 + sy * 0.07, z), (0.012, 0.012, 0.26))
    P.box(st, (0, 0.16, z + 0.14), (0.18, 0.18, 0.02)); P.box(st, (0, 0.16, z - 0.13), (0.16, 0.16, 0.012))
    P.cyl(M["opal"], (0, 0.16, z - 0.11), 0.045, 0.2, seg=20)


def plank_door(P, width=0.9, height=2.05):
    """Kulpen's front door: tarred vertical planks (120, V-jointed) on ledges and a brace, a hand-forged steel latch and a brass
    ring pull (the accent), in a tarred casing. Origin = the opening's centre on the floor, front +y (the porch)."""
    _kulpen_mats(); tar, st = M["tar"], M["steel"]
    n = int(width / 0.12)
    for k in range(n):
        x = -width / 2 + (k + 0.5) * width / n
        P.box(tar, (x, 0.0, height / 2), (width / n - 0.006, 0.04, height - 0.01))
    for z in (0.25, height - 0.25):
        P.box(tar, (0, -0.035, z), (width - 0.06, 0.03, 0.12))
    for sx in (-1, 1):
        P.box(tar, (sx * (width / 2 + 0.04), 0.03, height / 2 + 0.04), (0.08, 0.025, height + 0.08))
    P.box(tar, (0, 0.03, height + 0.04), (width + 0.16, 0.025, 0.08))
    P.box(st, (width / 2 - 0.13, 0.025, 1.05), (0.06, 0.01, 0.16))
    P.ring(M["brass"], (width / 2 - 0.13, 0.03), 0.032, 0.04, 0.95, 0.958, seg=24)
    for z in (0.3, height - 0.3):
        P.box(st, (-width / 2 + 0.2, 0.024, z), (0.38, 0.006, 0.04))                        # strap hinges


def sauna_glass_door(P, width=0.75, height=1.9):
    """The hot-room door: one leaf of 8 mm bronze-tinted toughened glass in a thermo-aspen frame, aspen pull bars both sides,
    opens out (no lock, never). Origin = the opening's centre on the floor, front +y."""
    _kulpen_mats(); a = M["aspen_thermo"]
    for sx in (-1, 1):
        P.box(a, (sx * (width / 2 - 0.03), 0, height / 2), (0.06, 0.07, height))
    for z in (0.04, height - 0.04):
        P.box(a, (0, 0, z), (width, 0.07, 0.08))
    tint = M.setdefault("glass_bronze", bc.arch_glass("glass_bronze", tint=(0.86, 0.74, 0.58)))
    P.box(tint, (0, 0, height / 2), (width - 0.12, 0.008, height - 0.16))
    for sy in (-1, 1):
        P.box(a, (width / 2 - 0.12, sy * 0.06, 1.0), (0.035, 0.03, 0.42))
        for z in (0.82, 1.18):
            P.box(a, (width / 2 - 0.12, sy * 0.04, z), (0.03, 0.03, 0.03))


def deck_door(P, width=0.9, height=2.05):
    """The door out to the deck: a blackened-steel framed glass leaf (like the windows), an oak kick plate and a brass lever.
    Origin = the opening's centre on the floor, front +y (outside)."""
    fr = M["frame"]
    for sx in (-1, 1):
        P.box(fr, (sx * (width / 2 - 0.03), 0, height / 2), (0.06, 0.06, height))
    for z in (0.03, 0.3, height - 0.03):
        P.box(fr, (0, 0, z), (width, 0.06, 0.06))
    P.box(M["glass"], (0, 0, (0.33 + height - 0.06) / 2), (width - 0.12, 0.024, height - 0.39))
    P.box(M["oak"], (0, 0, 0.165), (width - 0.12, 0.03, 0.24))
    for sy in (-1, 1):
        P.rod(M["brass"], (width / 2 - 0.09, sy * 0.03, 1.05), (width / 2 - 0.09, sy * 0.08, 1.05), 0.009, seg=10)
        P.rod(M["brass"], (width / 2 - 0.09, sy * 0.08, 1.05), (width / 2 - 0.22, sy * 0.08, 1.05), 0.009, seg=10)


def _stamp_wood(top=1.08):
    """The tub's thermo-spruce, weathered: every stave its own grain + tone; outside the wood greys in soft vertical streaks, the
    top 20 cm stays dark and a little glossy where it is always wet, a damp darkening at the foot."""
    if "stamp_wood" in M:
        return M["stamp_wood"]
    m = bc.pbr_material("stamp_wood", "coated_pine_02", 0.9, box=True, tint=(0.86, 0.74, 0.6), sat=0.55, val=0.7, piece_var=0.25, rough_add=0.12)
    N, L = m.node_tree.nodes, m.node_tree.links; b = N["Principled BSDF"]
    src = b.inputs["Base Color"].links[0].from_socket; rsrc = b.inputs["Roughness"].links[0].from_socket
    tc = next(n for n in N if n.bl_idname == "ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (9.0, 9.0, 1.1); L.new(tc.outputs["Object"], mp.inputs["Vector"])
    st = N.new("ShaderNodeTexNoise"); st.inputs["Scale"].default_value = 2.5; st.inputs["Detail"].default_value = 5.0; L.new(mp.outputs[0], st.inputs["Vector"])
    wf = N.new("ShaderNodeMapRange"); wf.inputs[1].default_value = 0.35; wf.inputs[2].default_value = 0.75; wf.inputs[4].default_value = 0.75; L.new(st.outputs["Fac"], wf.inputs[0])
    grey = N.new("ShaderNodeMix"); grey.data_type = "RGBA"; L.new(wf.outputs[0], grey.inputs["Factor"]); L.new(src, grey.inputs["A"]); grey.inputs["B"].default_value = (0.3, 0.28, 0.25, 1)
    wet = N.new("ShaderNodeMapRange"); wet.inputs[1].default_value = top - 0.24; wet.inputs[2].default_value = top - 0.06; L.new(sep.outputs["Z"], wet.inputs[0])
    foot = N.new("ShaderNodeMapRange"); foot.inputs[1].default_value = 0.25; foot.inputs[2].default_value = 0.05; foot.inputs[4].default_value = 0.6; L.new(sep.outputs["Z"], foot.inputs[0])
    dmp = N.new("ShaderNodeMath"); dmp.operation = "MAXIMUM"; L.new(wet.outputs[0], dmp.inputs[0]); L.new(foot.outputs[0], dmp.inputs[1])
    dark = N.new("ShaderNodeMix"); dark.data_type = "RGBA"; dark.blend_type = "MULTIPLY"; L.new(dmp.outputs[0], dark.inputs["Factor"])
    L.new(grey.outputs["Result"], dark.inputs["A"]); dark.inputs["B"].default_value = (0.45, 0.4, 0.36, 1)
    L.new(dark.outputs["Result"], b.inputs["Base Color"])
    rr = N.new("ShaderNodeMix"); rr.data_type = "FLOAT"; L.new(wet.outputs[0], rr.inputs["Factor"]); L.new(rsrc, rr.inputs["A"]); rr.inputs["B"].default_value = 0.35
    L.new(rr.outputs["Result"], b.inputs["Roughness"])
    M["stamp_wood"] = m
    return m


def _tub_water():
    if "tub_water" in M:
        return M["tub_water"]
    m = bpy.data.materials.new("tub_water"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.62, 0.72, 0.62, 1); b.inputs["Roughness"].default_value = 0.03; b.inputs["IOR"].default_value = 1.33
    b.inputs["Transmission Weight"].default_value = 1.0
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6.0; nz.inputs["Detail"].default_value = 3.0
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    M["tub_water"] = m
    return m


def badestamp(P, d=2.0, h=1.0):
    """Kulpen's badestamp: a wood-fired hot tub for eight. 40 thermo-spruce staves (45 thick), each a little different in width,
    height and tone, weathered grey outside, dark where it is always wet; two blackened-steel hoops drawn tight by a bolted lug;
    a slatted bench ring inside at 0.45, a board floor, the water 0.15 under the rim with a couple of birch leaves on it, a towel
    over the rim by the steps; three bearers under it on the deck. Heated by its own stove (hybrid: the stove + an electric
    heater that keeps it warm in between). Origin = the tub's centre on the deck."""
    _kulpen_mats(); P.vary = True
    a, st, z0 = _stamp_wood(0.08 + h), M["steel"], 0.08
    r = d / 2; n = 40; rng = np.random.default_rng(41)
    w = rng.uniform(0.88, 1.12, n); w = w / w.sum() * 2 * math.pi
    t0 = 0.0
    for k in range(n):
        t = t0 + w[k] / 2; t0 += w[k]
        rr = r - 0.0225 + float(rng.uniform(-0.0015, 0.0015)); hh = h + float(rng.uniform(-0.007, 0.004))
        P.box(a, (rr * math.cos(t), rr * math.sin(t), z0 + hh / 2), (0.045, 2 * r * math.sin(w[k] / 2) - 0.003, hh), rz=t)
    lug = -math.pi / 2 + 0.6
    for z in (0.25, h - 0.14):
        P.ring(st, (0, 0), r + 0.001, r + 0.009, z0 + z, z0 + z + 0.05, seg=120)
        cx, cy = (r + 0.03) * math.cos(lug), (r + 0.03) * math.sin(lug)
        for s_ in (-1, 1):
            P.box(st, (cx + s_ * 0.03 * -math.sin(lug), cy + s_ * 0.03 * math.cos(lug), z0 + z + 0.025), (0.04, 0.02, 0.06), rz=lug)
        P.rod(st, (cx - 0.06 * -math.sin(lug), cy - 0.06 * math.cos(lug), z0 + z + 0.025), (cx + 0.06 * -math.sin(lug), cy + 0.06 * math.cos(lug), z0 + z + 0.025), 0.007, seg=8)
    for k in range(int((2 * r - 0.12) / 0.11)):                                              # board floor
        x = -r + 0.1 + k * 0.11; half = math.sqrt(max(0.0, (r - 0.045) ** 2 - x * x))
        P.box(a, (x, 0, z0 + 0.025), (0.1, 2 * half, 0.05))
    nb = 30                                                                                   # slatted bench ring
    for k in range(nb):
        t = 2 * math.pi * k / nb
        P.box(a, ((r - 0.22) * math.cos(t), (r - 0.22) * math.sin(t), z0 + 0.44), (0.32, 2 * (r - 0.22) * math.sin(math.pi / nb) - 0.02, 0.03), rz=t)
    for t in np.linspace(0, 2 * math.pi, 9)[:-1]:
        P.box(a, ((r - 0.22) * math.cos(t), (r - 0.22) * math.sin(t), z0 + 0.21), (0.3, 0.05, 0.42), rz=float(t))
    P.cyl(_tub_water(), (0, 0, z0 + h - 0.16), r - 0.046, 0.008, seg=96)
    leaf = M.setdefault("birch_leaf", bc.material("birch_leaf", (0.72, 0.52, 0.1), 0.6))
    for (lx, ly, lr) in ((0.3, 0.25, 0.4), (-0.42, -0.1, 2.1), (0.05, -0.5, 1.2)):
        P.blob(leaf, (lx, ly, z0 + h - 0.15), (0.028, 0.02, 0.002), seg=10)
    ta = -math.pi / 2                                                                         # a towel over the rim, towards the steps
    ux, uy = math.cos(ta), math.sin(ta)
    tw = M["robe_terry"] if "robe_terry" in M else M["towel_white"]
    td = Path(__file__).resolve().parent / "data" / "towel_badestamp.npz"     # the towel, draped by a cloth sim (construction/towel_sim.py)
    if td.exists():
        tdat = np.load(td); tb = bmesh.new()
        tv = [tb.verts.new(tuple(map(float, v))) for v in tdat["verts"]]
        for f in tdat["faces"]:
            tb.faces.new([tv[i] for i in f])
        bmesh.ops.solidify(tb, geom=tb.faces[:], thickness=0.005)
        tme = bpy.data.meshes.new("towel_tmp"); tb.to_mesh(tme); tb.free()
        P.bm(tw).from_mesh(tme); bpy.data.meshes.remove(tme)
    for x in (-0.6, 0.0, 0.6):
        P.box(a, (x, 0, 0.04), (0.1, d - 0.3, 0.08))


def stamp_stove(P):
    """The tub's stove: a blackened-steel firebox on legs beside the tub, two pipes into the staves (the water circulates through
    it), a glowing door on its side, a 120 chimney with a rain cap. Origin = floor, front +y (towards the tub)."""
    _kulpen_mats(); st = M["steel"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.box(st, (sx * 0.2, sy * 0.2, 0.1), (0.03, 0.03, 0.2))
    P.box(st, (0, 0, 0.55), (0.5, 0.5, 0.7))
    P.box(st, (0.255, 0, 0.45), (0.012, 0.26, 0.22)); P.box(M["fire"], (0.262, 0, 0.45), (0.004, 0.18, 0.14))
    for z in (0.35, 0.75):
        P.rod(st, (0, 0.25, z), (0, 0.55, z), 0.035, seg=12)
    P.cyl(st, (-0.1, -0.1, 0.9), 0.06, 1.9, seg=16)
    P.cyl(st, (-0.1, -0.1, 2.85), 0.12, 0.08, seg=16, r2=0.02)
    P.box(M["birch_bark"], (0, -0.36, 0.06), (0.4, 0.2, 0.12))


def stamp_steps(P, w=0.8):
    """Steps up to the tub rim in the tub's weathered wood: two treads at 0.33 and 0.66 on cut stringers. Origin = floor centre,
    front +y (away from the tub)."""
    _kulpen_mats(); P.vary = True; oak = _stamp_wood()
    for k, (y, z) in enumerate(((0.12, 0.33), (-0.14, 0.66))):
        P.box(oak, (0, y, z - 0.02), (w, 0.28, 0.04))
    for sx in (-1, 1):
        _xprism(P, oak, [(0.26, 0.0), (0.26, 0.31), (-0.02, 0.31), (-0.02, 0.64), (-0.28, 0.64), (-0.28, 0.0)], sx * (w / 2 - 0.03) - 0.02, sx * (w / 2 - 0.03) + 0.02)


def tip_bucket(P):
    """The cold shower: a tipping oak bucket (300 l a minute of pool water, pumped up the flume) on a steel axle between two peeled
    pine posts, a rope pull with an oak toggle. Origin = the deck under it, front +y."""
    _kulpen_mats(); lg, st, oak = M["log"], M["steel"], M["oak"]
    for sx in (-1, 1):
        P.rod(lg, (sx * 0.5, 0, 0), (sx * 0.5, 0, 2.62), 0.07, 0.065, seg=14)
    P.rod(lg, (-0.58, 0, 2.55), (0.58, 0, 2.55), 0.06, seg=14)
    P.rod(st, (-0.45, 0, 2.15), (0.45, 0, 2.15), 0.012, seg=10)
    tl = math.radians(14)
    c = Vector((0, 0.02, 2.05)); ax = Vector((0, math.sin(tl), math.cos(tl)))
    P.rod(oak, tuple(c - ax * 0.18), tuple(c + ax * 0.2), 0.21, 0.23, seg=28)
    for t in (-0.1, 0.12):
        P.rod(st, tuple(c + ax * (t - 0.012)), tuple(c + ax * (t + 0.012)), 0.237, seg=28)
    P.rod(M["rope"], (0.2, 0.2, 2.2), (0.2, 0.25, 1.45), 0.008, seg=6)
    P.rod(oak, (0.2, 0.25, 1.46), (0.2, 0.25, 1.36), 0.016, seg=8)


# ------------------------------------------------------------------ the gym floors' light (Roman 2026-10-14: serious gyms, not commercial)
GYM_LED = {"4000": (1.0, 0.96, 0.9), "3500": (1.0, 0.92, 0.82), "3000": (1.0, 0.86, 0.7), "2700": (1.0, 0.81, 0.62)}


def gym_line(P, L=6.0, z_ceiling=4.56, temp="4000"):
    """The training floors' light: a continuous 130 x 90 blackened-aluminium profile on the soffit between the beams with a broad,
    soft opal (2026-10-30, Roman: "less surgical": a soft glow, not a hard bright line; the 1.1 m beams shield it from a lifter on a
    bench across the bay). CRI 90+: 3500 K on F2, 3000 K in the F1 hall, 2700 K in the den. Origin = under its centre on the floor."""
    st = M["steel"]
    P.box(st, (0, 0, z_ceiling - 0.045), (L, 0.13, 0.09))
    P.box(_led(f"gym_line_soft_{temp}", GYM_LED[temp], 4.0), (0, 0, z_ceiling - 0.0905), (L - 0.02, 0.11, 0.003))  # a broad, soft opal (2026-10-30: less surgical)


def wall_washer(P, L=6.0, z_ceiling=4.56, temp="4000"):
    """A recessed wall-washer line 0.6 m off a wall: an asymmetric reflector throws an even sheet of light down the mirror / back
    wall, so the room reads lit and deep (vertical brightness: the premium look, not flat commercial light). Origin = under it
    on the floor, front +y = towards the wall."""
    st = M["steel"]
    P.box(st, (0, 0, z_ceiling - 0.04), (L, 0.09, 0.08))
    P.box(_led(f"gym_line_{temp}", GYM_LED[temp], 6.0), (0, 0.02, z_ceiling - 0.075), (L - 0.02, 0.03, 0.003), rx=-0.5)



def ring_guard(P, r=3.5, gap_a=135.0, gap_b=160.0, h=1.1, band=0.39):
    """The edge of a round stair opening, cleaned up: a blackened-steel fascia band wrapping the slab edge (it hides the cut floor
    layers + the raw concrete, and reads as one clean ring from below), and a frameless glass guard on the slab in a steel base
    shoe with an oak cap rail, open only where you step on and off the stair (gap_a..gap_b, degrees). Origin = the opening's centre
    at floor level."""
    st, oak = M["steel"], M["oak"]
    P.ring(st, (0, 0), r - 0.012, r, -band, 0.012, seg=180)
    a0, a1 = gap_b, gap_a + 360.0
    P.ring(st, (0, 0), r + 0.005, r + 0.075, 0.0, 0.11, a0=a0, a1=a1, seg=180)
    P.ring(M["glass"], (0, 0), r + 0.034, r + 0.046, 0.09, h - 0.045, a0=a0, a1=a1, seg=180)
    P.ring(oak, (0, 0), r + 0.005, r + 0.075, h - 0.05, h, a0=a0, a1=a1, seg=180)
    P.ring(st, (0, 0), r + 0.036, r + 0.044, h - 0.065, h - 0.05, a0=a0, a1=a1, seg=180)
    for a in (a0, a1):  # end posts at the opening
        t = math.radians(a)
        P.box(st, ((r + 0.04) * math.cos(t), (r + 0.04) * math.sin(t), h / 2), (0.05, 0.05, h), rz=t)


def spiral_planter(P, ri=1.26, ro=3.4, rise=9.77, risers=56, step_deg=15.0, a0=90.0, head=2.1):
    """The space under the spiral's low first turn as a planted bed (Roman 2026-10-31 on F3: "someone could hit their head";
    a glass ring round it read as clipping, then bars down from the stringers "like a jail prison cell ... think of a much
    better solution"): a raised bed under the stair wherever its underside is under `head` (TEK17 2.1 m), its sides smoked oak
    staves (the den's partitions) 0.45 high (ADA 307.4: a barrier's leading edge 0.685 m max where the headroom is under
    2.03 m, so a cane finds it), a blackened-steel cap, moss with a few river stones, upright greenery growing to under
    the treads. Nothing stands outside the stair's own footprint. Origin = the stair's centre at its foot."""
    st, oak = M["steel"], M.setdefault("smoked_oak", bc.pbr_material("oak_slat_smoked", "oak_veneer_01", 1.83, box=True, tint=(0.55, 0.42, 0.32),
                                                                       sat=0.7, val=0.45, piece_var=0.08, rough_add=0.1))
    soil = M.setdefault("planter_soil", bc.material("planter_soil", (0.05, 0.035, 0.025), 0.95))
    moss, lf = _moss(), _foliage()
    stone = M.get("stone_nero_honed") or bc.interior_materials()["stone_nero_honed"]
    rr = rise / risers
    zb = lambda th: rr * (1 + th / step_deg) - 0.06 - 0.36    # the stringers' underside, th degrees round from the foot
    tha = ((0.08 + 0.42) / rr - 1) * step_deg                 # where it is 0.08 m up
    th1 = ((head + 0.42) / rr - 1) * step_deg                 # where it reaches the headroom
    H, T = 0.45, 0.03                                         # the bed's sides, the staves' depth
    r0, r1 = ri - 0.1, ro + 0.1                               # just inside the eye, just outside the outer stringer
    hw = lambda th: max(0.05, min(H, zb(th) - 0.03))
    def pt(r, th, z=0.0):
        t = math.radians(a0 + th); return (r * math.cos(t), r * math.sin(t), z)
    for r, sg in ((r1, 1), (r0, -1)):                         # the curved sides: staves 45 mm at 65 mm, the cap on them
        n = math.ceil(math.radians(th1 - tha) * r / 0.065)
        for i in range(n + 1):
            th = tha + (th1 - tha) * i / n; h = hw(th)
            x, y, _ = pt(r - sg * T / 2, th)
            P.box(oak, (x, y, h / 2), (T, 0.045, h - 0.004), rz=math.radians(a0 + th))
        k = 24
        for j in range(k):                                    # the cap in short lengths, stepping down with the low end
            ta, tb = tha + (th1 - tha) * j / k, tha + (th1 - tha) * (j + 1) / k
            h = hw((ta + tb) / 2)
            P.ring(st, (0, 0), r - T - 0.008, r + 0.008, h, h + 0.012, a0=a0 + ta, a1=a0 + tb, seg=360)
    for th in (tha, th1):                                     # the radial ends
        h = hw(th); n = math.ceil((r1 - r0) / 0.065)
        for i in range(n):
            r = r0 + (r1 - r0) * (i + 0.5) / n
            x, y, _ = pt(r, th + math.degrees(T / 2 / r) * (1 if th == tha else -1))   # just inside the bed
            P.box(oak, (x, y, h / 2), (0.045, T, h - 0.004), rz=math.radians(a0 + th))
        x, y, _ = pt((r0 + r1) / 2, th)
        P.box(st, (x, y, h + 0.006), (r1 - r0, T + 0.016, 0.012), rz=math.radians(a0 + th) + math.pi / 2)
    k = 36
    for j in range(k):                                        # the soil + moss, a sector at a time (the low end steps down)
        ta, tb = tha + (th1 - tha) * j / k, tha + (th1 - tha) * (j + 1) / k
        h = hw((ta + tb) / 2)
        P.ring(soil, (0, 0), r0 + T, r1 - T, 0.0, h - 0.06, a0=a0 + ta, a1=a0 + tb, seg=360)
        P.ring(moss, (0, 0), r0 + T, r1 - T, h - 0.06, h - 0.035, a0=a0 + ta, a1=a0 + tb, seg=360)
    rng = np.random.default_rng(7)
    for q in range(9):                                        # river stones on the moss
        th = rng.uniform(tha + 20, th1 - 8); r = rng.uniform(r0 + 0.3, r1 - 0.3); h = hw(th)
        s_ = rng.uniform(0.12, 0.26)
        x, y, _ = pt(r, th)
        _rough_block(P, stone, (x, y, h - 0.04 + s_ * 0.22), (s_, s_ * 0.8, s_ * 0.5), amp=0.02, seed=q * 1.7, cuts=3, rz=rng.uniform(0, 3.1))
    for q in range(60):                                       # upright greenery (sansevieria-like blades) where it has room
        th = rng.uniform(tha + 25, th1 - 5); r = rng.uniform(r0 + 0.2, r1 - 0.2); h = hw(th)
        room = zb(th) - h - 0.18
        if room < 0.25:
            continue
        x, y, _ = pt(r, th)
        for b_ in range(int(rng.integers(5, 10))):
            a = rng.uniform(0, 2 * math.pi); d_ = rng.uniform(0, 0.07); L = rng.uniform(0.45, 1.0) * min(room, 1.3); tilt = rng.uniform(0.02, 0.2)
            cx, cy = x + d_ * math.cos(a), y + d_ * math.sin(a)
            P.box(lf, (cx + math.cos(a) * tilt * L / 2, cy + math.sin(a) * tilt * L / 2, h - 0.04 + L / 2), (0.05, 0.008, L),
                  rz=rng.uniform(0, math.pi), rx=-math.sin(a) * tilt, ry=math.cos(a) * tilt)


def spiral_balustrade(P, ri=1.26, ro=3.4, rise=9.77, risers=56, step_deg=15.0, a0=90.0, gaps=((26.33, 28.67),)):
    """The spiral's guards, side-mounted on the stringers (nothing stands on a tread): 14 mm blackened-steel bars at <= 110 mm
    (child-safe), each held off the stringer's face by a small steel shoe, carried at the top by a 40 x 12 steel flat rail; on the
    outside a 50 mm oiled-oak handrail sits on it, on the well side a 40 mm steel one. 0.95 over the nosing line. The outer guard
    opens over each gap (in treads from the foot: where a floor's guard opens, so the two always line up), closed by heavier end
    bars.
    Origin = the stair's centre at its foot."""
    st, oak = M["steel"], M["oak"]
    rr = rise / risers; H = 0.95
    span_k = lambda a: (a - a0) / step_deg                     # treads from the foot at angle a
    zn = lambda a: rr * (span_k(a) + 0.5)                       # the nosing line
    def pt(r, a, z):
        t = math.radians(a); return (r * math.cos(t), r * math.sin(t), z)
    gap = lambda a: any(g0 <= span_k(a) <= g1 for g0, g1 in gaps)
    B = {"bar": ([], []), "shoe": ([], []), "top": ([], []), "oak": ([], []), "inner": ([], [])}
    def add(key, a_, b_):
        B[key][0].append(a_); B[key][1].append(b_)
    for r_bar, r_face, outer in ((ro + 0.03, ro + 0.0125, True), (ri - 0.03, ri - 0.0125, False)):
        arc_tread = math.radians(step_deg) * r_bar
        nb = max(2, math.ceil(arc_tread / 0.11))
        for k in range(risers):
            for i in range(nb):
                a = a0 + step_deg * (k + (i + 0.5) / nb)
                if outer and gap(a):
                    continue
                zb = zn(a) - 0.28
                Pt0, Pt1 = pt(r_bar, a, zb), pt(r_bar, a, zn(a) + H - 0.05)
                add("bar", Pt0, Pt1)
                add("shoe", pt(r_face, a, zb + 0.04), pt(r_bar, a, zb + 0.04))                  # the shoe off the stringer
        n = risers * 6
        for j in range(n):
            aa, ab = a0 + step_deg * risers * j / n, a0 + step_deg * risers * (j + 1) / n
            if outer and (gap(aa) or gap(ab)):
                continue
            add("top", pt(r_bar, aa, zn(aa) + H - 0.05), pt(r_bar, ab, zn(ab) + H - 0.05))       # the top rail
            if outer:
                add("oak", pt(r_bar, aa, zn(aa) + H - 0.008), pt(r_bar, ab, zn(ab) + H - 0.008))  # oak handrail
            else:
                add("inner", pt(r_bar, aa, zn(aa) + H - 0.015), pt(r_bar, ab, zn(ab) + H - 0.015))
    for key, mat_, rad, sg in (("bar", st, 0.007, 8), ("shoe", st, 0.009, 8), ("top", st, 0.011, 8), ("oak", oak, 0.025, 14), ("inner", st, 0.02, 12)):
        P.rods(mat_, B[key][0], B[key][1], rad, seg=sg)
    for kk in [v for g in gaps for v in g if v < risers - 0.01]:      # heavier end bars at the openings
        a = a0 + step_deg * kk
        P.rod(st, pt(ro + 0.03, a, zn(a) - 0.3), pt(ro + 0.03, a, zn(a) + H + 0.02), 0.014, seg=12)


def wipe_station(P):
    """Wipes + bin for the training floors (Roman's reference: a round brushed-stainless stand): a 320 mm drum, 920 tall, brushed
    stainless; the satin lid with a grommet and a wipe pulled up through it (the roll inside); a soft-cornered opening at 0.45-0.62
    for used wipes into a black liner; a slim oiled-oak band under the lid (the flair) and a black rubber foot. Origin = floor, front +y."""
    if "stainless_satin" not in M:  # bright satin stainless, brushed up and down the drum (the reference's look)
        ms = bc.metal_material("stainless_satin", (0.86, 0.86, 0.84), rough=(0.1, 0.18))
        for n_ in ms.node_tree.nodes:
            if n_.bl_idname == "ShaderNodeMapping" and tuple(n_.inputs["Scale"].default_value) == (400.0, 4.0, 400.0):
                n_.inputs["Scale"].default_value = (400.0, 400.0, 4.0)
        M["stainless_satin"] = ms
    bs, oak = M["stainless_satin"], M["oak"]
    r, h = 0.16, 0.92
    P.cyl(M["rubber"], (0, 0, 0.0), r + 0.002, 0.012, seg=48)
    # the drum: ONE continuous shell (outer + inner skin, 1.2 mm) with the opening cut in it, so no seams anywhere
    b_ = P.bm(bs); n_ = 72; zs_ = [0.012, 0.45, 0.62, h - 0.06]; t_ = 0.0012
    open_ = lambda k: abs(((360.0 * (k + 0.5) / n_) - 90 + 180) % 360 - 180) < 38      # segment k inside the opening's arc (front +y)
    ring_v = [[[b_.verts.new(((r - t_ * j) * math.cos(2 * math.pi * k / n_), (r - t_ * j) * math.sin(2 * math.pi * k / n_), z)) for k in range(n_)]
               for z in zs_] for j in (0, 1)]
    for j in (0, 1):
        for zi in range(3):
            for k in range(n_):
                if zi == 1 and open_(k):
                    continue
                q_ = (ring_v[j][zi][k], ring_v[j][zi][(k + 1) % n_], ring_v[j][zi + 1][(k + 1) % n_], ring_v[j][zi + 1][k])
                b_.faces.new(q_ if j == 0 else q_[::-1])
    for zi in (0, 3):                                                                # top + bottom edges of the shell
        for k in range(n_):
            b_.faces.new((ring_v[0][zi][k], ring_v[1][zi][k], ring_v[1][zi][(k + 1) % n_], ring_v[0][zi][(k + 1) % n_]))
    for k in range(n_):                                                              # the opening's edges, skin to skin
        if open_(k):
            for zi in (1, 2):
                b_.faces.new((ring_v[0][zi][k], ring_v[0][zi][(k + 1) % n_], ring_v[1][zi][(k + 1) % n_], ring_v[1][zi][k]))
        elif open_((k + 1) % n_) or open_((k - 1) % n_):
            kk = (k + 1) % n_ if open_((k + 1) % n_) else k
            try:
                b_.faces.new((ring_v[0][1][kk], ring_v[0][2][kk], ring_v[1][2][kk], ring_v[1][1][kk]))
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(b_, faces=b_.faces[:])
    P.ring(oak, (0, 0), r - 0.004, r + 0.001, h - 0.06, h - 0.025, seg=64)
    P.cyl(bs, (0, 0, h - 0.025), r + 0.004, 0.02, seg=64)                       # the lid with a rolled rim
    P.cyl(bs, (0, 0, h - 0.005), r - 0.01, 0.004, seg=64)
    P.cyl(M["rubber"], (0, 0, h - 0.002), 0.022, 0.004, seg=24)                    # the grommet
    P.blob(M.setdefault("wipe", bc.material("wipe_sheet", (0.92, 0.92, 0.9), 0.85)), (0.004, 0.0, h + 0.035), (0.03, 0.02, 0.045), seg=12)
    P.ring(M["felt"], (0, 0), r - 0.012, r - 0.004, 0.02, 0.86, seg=48)           # the liner, seen through the opening
    P.cyl(M["felt"], (0, 0, 0.02), r - 0.01, 0.4, seg=48)                         # used wipes sit on the bag's floor (inside: dark)



def stair_landing(P, r_in=1.26, r_out=3.5, a_from=52.5, a_to=97.5, h=1.1, t=0.25):
    """The spiral's top landing (Roman: a death drop to the right of the top step): the top tread carried on round as a platform
    level with the floor, so nothing is open beside you as you step on. Oiled oak on a steel plate (like the treads), a blackened-
    steel fascia on its inner + far edges (as the ring), and the ring's glass guard (steel shoe, oak cap) along both edges, meeting
    the stair's inner guard and the floor ring guard. Origin = the stair's centre at floor level; angles in degrees."""
    st, oak = M["steel"], M["oak"]
    n = max(8, int((a_to - a_from) / 2.5))
    P.ring(oak, (0, 0), r_in, r_out, -0.045, 0.0, a0=a_from, a1=a_to, seg=int(n * 360 / (a_to - a_from)))
    P.ring(st, (0, 0), r_in, r_out, -t, -0.045, a0=a_from, a1=a_to, seg=int(n * 360 / (a_to - a_from)))
    P.ring(st, (0, 0), r_in - 0.012, r_in, -t - 0.02, 0.012, a0=a_from, a1=a_to, seg=int(n * 360 / (a_to - a_from)))  # inner fascia
    te = math.radians(a_to); ux, uy = math.cos(te), math.sin(te)
    rm = (r_in + r_out) / 2; L = r_out - r_in
    P.box(st, (rm * ux - 0.006 * -uy, rm * uy - 0.006 * ux, -t / 2 + 0.006), (L, 0.012, t + 0.012), rz=te)                # far-edge fascia
    # guards: along the inner arc (the well) and across the far edge
    a0_, a1_ = a_from - 2.0, a_to
    P.ring(st, (0, 0), r_in + 0.005, r_in + 0.075, 0.0, 0.11, a0=a0_, a1=a1_, seg=96)
    P.ring(M["glass"], (0, 0), r_in + 0.034, r_in + 0.046, 0.09, h - 0.045, a0=a0_, a1=a1_, seg=96)
    P.ring(oak, (0, 0), r_in + 0.005, r_in + 0.075, h - 0.05, h, a0=a0_, a1=a1_, seg=96)
    off = 0.04; cx_, cy_ = rm * ux + off * uy, rm * uy - off * ux                           # just inside the landing's far edge
    P.box(st, (cx_, cy_, 0.055), (L, 0.07, 0.11), rz=te)
    P.box(M["glass"], (cx_, cy_, (0.09 + h - 0.045) / 2), (L - 0.02, 0.012, h - 0.135), rz=te)
    P.box(oak, (cx_, cy_, h - 0.025), (L + 0.02, 0.07, 0.05), rz=te)
    for r_ in (r_in + 0.04, r_out + 0.04):                                                 # posts where the guards meet
        P.box(st, (r_ * ux - off * -uy, r_ * uy - off * ux, h / 2), (0.05, 0.05, h), rz=te)



def core_door(P, width=1.2, height=2.3, finish="oak", exit_=False):
    """A flush door for the gym floors in a slim (40 mm) blackened-steel frame, its leaf faced to match the wall it sits in:
    'mirror' on the mirror walls (it disappears into them), 'oak' on oak walls, 'smoked' in the den, 'steel'. Exit doors (the stair
    cores) carry a blackened-steel push bar; the others a slim pull with a brass collar (the accent). A concealed closer line at the
    head. Origin = the opening's centre on the floor, front +y (the room side)."""
    st = M["steel"]
    face = {"mirror": M["mirror"], "oak": M["oak"], "steel": st,
            "smoked": M.setdefault("smoked_oak", bc.pbr_material("oak_slat_smoked", "oak_veneer_01", 1.83, box=True, tint=(0.55, 0.42, 0.32),
                                                                 sat=0.7, val=0.45, piece_var=0.08, rough_add=0.1))}[finish]
    for sx in (-1, 1):
        P.box(st, (sx * (width / 2 + 0.02), 0.0, height / 2 + 0.02), (0.04, 0.07, height + 0.04))
    P.box(st, (0, 0.0, height + 0.02), (width + 0.08, 0.07, 0.04))
    P.box(st if finish == "mirror" else face, (0, -0.005, height / 2), (width - 0.006, 0.05, height - 0.006))   # the leaf
    if finish == "mirror":
        P.box(face, (0, 0.0215, height / 2), (width - 0.03, 0.002, height - 0.03))
    P.box(st, (0, 0.022, height - 0.05), (width - 0.1, 0.004, 0.02))                                             # closer line
    if exit_:
        P.box(st, (0, 0.07, 1.0), (width - 0.2, 0.03, 0.05))
        for sx in (-1, 1):
            P.box(st, (sx * (width / 2 - 0.12), 0.045, 1.0), (0.04, 0.05, 0.08))
    else:
        P.box(st, (width / 2 - 0.1, 0.05, 1.05), (0.022, 0.022, 0.42))
        for z in (0.9, 1.2):
            P.box(st, (width / 2 - 0.1, 0.035, z), (0.016, 0.03, 0.016))
        P.box(M["brass"], (width / 2 - 0.1, 0.05, 1.26), (0.024, 0.024, 0.012))



# ------------------------------------------------------------------ Bekken i hulen, the den's river (VISION, Roman 2026-10-14/17)
DEN = {"xg": -6.665, "xs": -6.715, "xr": -8.13, "cope": 0.12, "y_n": 11.78, "y_s": -32.95, "y_w": -33.78, "zw_n": -0.035, "zw_s": -0.055,
       "z_bot": -0.30, "slit": (-32.1, 10.1), "z_slit": 0.95, "courses": (0.2, 0.17, 0.12, 0.18, 0.14, 0.11, 0.16, 0.17), "step": 0.05, "top_d": 0.1}


def _pebbles(P, mats, pts, radii, rng, seg=8):
    """Many small stones at once: flattened, turned ellipsoids built in one numpy pass per material (a riverbed of thousands)."""
    u = np.linspace(0, 2 * np.pi, seg, endpoint=False); v = np.linspace(-np.pi / 2, np.pi / 2, seg // 2 + 1)[1:-1]
    ring = np.array([(np.cos(a) * np.cos(b), np.sin(a) * np.cos(b), np.sin(b)) for b in v for a in u] + [(0, 0, -1), (0, 0, 1)])
    nr = len(v); faces = []
    for j in range(nr - 1):
        for i in range(seg):
            i1 = (i + 1) % seg
            faces.append((j * seg + i, j * seg + i1, (j + 1) * seg + i1, (j + 1) * seg + i))
    bot, top = nr * seg, nr * seg + 1
    for i in range(seg):
        i1 = (i + 1) % seg
        faces.append((bot, i1, i)); faces.append(((nr - 1) * seg + i, (nr - 1) * seg + i1, top))
    faces = np.array(faces, dtype=object)
    which = rng.integers(0, len(mats), len(pts))
    for k, mat in enumerate(mats):
        idx = np.where(which == k)[0]
        if not len(idx):
            continue
        V, F = [], []
        for n, i in enumerate(idx):
            a = float(rng.uniform(0, 2 * np.pi)); ca, sa = math.cos(a), math.sin(a)
            r = ring * radii[i]
            r = np.stack([r[:, 0] * ca - r[:, 1] * sa, r[:, 0] * sa + r[:, 1] * ca, r[:, 2]], 1) + pts[i]
            V.append(r); off = n * len(ring)
            F.extend([tuple(x + off for x in f) for f in faces])
        me = bpy.data.meshes.new("pebbles"); me.from_pydata(np.concatenate(V).tolist(), [], F)
        P.bm(mat).from_mesh(me); bpy.data.meshes.remove(me)


def den_stream(P):
    """The den's river (Roman 2026-10-17: minimal; the rocks form the base right under the glass, a slit the whole width at the
    water level, a super long slow waterfall; little stones on the bottom; clean edges + finishes). The river glass stands on a
    base of split dark granite laid in five long courses, wall to wall, each set back a hand's width from the one below, so the base
    leans out from the glass like the ravine's sheeted cliffs. Between the glass and the top course a dark slit runs the length of
    the window, exactly at the river's surface outside, in front of the pilasters; the river skims in over the top course and steps
    down the ledges in long thin sheets, a bead of water on every lip, into a pool sunk flush along the foot (1.42 m of water,
    40-60 mm under a flush dark granite coping) over black sand covered in near-black river stones. It drifts south and slides over a
    steel lip into a slit across the floor. Built in the den's own coordinates (origin, z = F3)."""
    st = M["steel"]; d = DEN
    gr = M.setdefault("granite_honed_dark", bc.pbr_material("granite_honed_dark", "granite_tile", 1.2, box=True, tint=(0.55, 0.55, 0.57), sat=0.3,
                                                          val=0.34, rough_mul=0.45, rough_add=0.05, piece_var=0.08))
    split = _split_granite()
    stones = [M.setdefault(f"river_pebble_{k}", bc.pbr_material(f"river_pebble_{k}", "dark_rock", 0.35, box=True, tint=t, sat=0.15, val=v_, rough_add=0.0,
                                                                rough_mul=0.3, piece_var=0.2))
              for k, (t, v_) in enumerate((((0.8, 0.8, 0.82), 0.06), ((0.82, 0.82, 0.8), 0.1), ((0.78, 0.8, 0.82), 0.035), ((0.8, 0.8, 0.8), 0.15)))]
    if "black_sand" not in M:  # black sand beach: near black, a fine grain
        bs = bc.material("black_sand", (0.012, 0.012, 0.013), 0.7)
        N_, L_ = bs.node_tree.nodes, bs.node_tree.links
        nz_ = N_.new("ShaderNodeTexNoise"); nz_.inputs["Scale"].default_value = 900.0; nz_.inputs["Detail"].default_value = 2.0
        bp_ = N_.new("ShaderNodeBump"); bp_.inputs["Strength"].default_value = 0.6; bp_.inputs["Distance"].default_value = 0.001
        L_.new(nz_.outputs["Fac"], bp_.inputs["Height"]); L_.new(bp_.outputs[0], N_["Principled BSDF"].inputs["Normal"])
        M["black_sand"] = bs
    bed = M["black_sand"]
    if "water_den" not in M:  # clear and neutral, so the black stones stay black
        M["water_den"] = bc.arch_glass("water_den", tint=(0.93, 0.94, 0.94))
    wat = M["water_den"]
    if "water_sheet" not in M:  # the thin running sheet: clear, a silver sheen, faint streaks down the fall
        ws = bc.material("water_sheet", (0.9, 0.92, 0.9), 0.02)
        N_, L_ = ws.node_tree.nodes, ws.node_tree.links
        b_ = N_["Principled BSDF"]; b_.inputs["Transmission Weight"].default_value = 1.0; b_.inputs["IOR"].default_value = 1.33
        tc_ = N_.new("ShaderNodeTexCoord"); mp_ = N_.new("ShaderNodeMapping"); mp_.inputs["Scale"].default_value = (20.0, 20.0, 2.0)
        L_.new(tc_.outputs["Object"], mp_.inputs["Vector"])
        nz_ = N_.new("ShaderNodeTexNoise"); nz_.inputs["Scale"].default_value = 3.0; nz_.inputs["Detail"].default_value = 8.0; L_.new(mp_.outputs[0], nz_.inputs["Vector"])
        bp_ = N_.new("ShaderNodeBump"); bp_.inputs["Strength"].default_value = 0.9; bp_.inputs["Distance"].default_value = 0.004
        L_.new(nz_.outputs["Fac"], bp_.inputs["Height"]); L_.new(bp_.outputs[0], N_["Principled BSDF"].inputs["Normal"])
        M["water_sheet"] = ws
    sheet = M["water_sheet"]
    P.vary = True
    xg, xs, xr, c = d["xg"], d["xs"], d["xr"], d["cope"]
    yn, ys_, yw = d["y_n"], d["y_s"], d["y_w"]
    rng = np.random.default_rng(17)

    # ---- the rock base: five courses of split dark granite, wall to wall, each stone its own length, tight joints, true ledges
    H = d["courses"]; n = len(H); z0s = [d["z_bot"] + sum(H[:k]) for k in range(n)]
    front = [xs - d["top_d"] - d["step"] * (n - 1 - k) for k in range(n)]
    for k in range(n):
        y = yw; seed = 40 * k
        while y < yn - 0.01:
            L_ = float(min(rng.uniform(1.4, 3.2), yn - y))
            if yn - y - L_ < 0.6:
                L_ = yn - y
            dx = float(rng.uniform(-0.014, 0.014))
            _rough_block(P, split, ((front[k] + dx + xs) / 2, y + L_ / 2, z0s[k] + H[k] / 2), (xs - front[k] - dx, L_ - 0.005, H[k] - 0.004),
                         amp=0.005, seed=seed + y, cuts=6, flat_top=True)
            y += L_
    P.box(M["felt"], ((xg + xs) / 2, (yw + yn) / 2, d["z_slit"] - 0.06), (xs - xg, yn - yw, 0.12))      # the slit's dark recess, wall to wall

    # ---- the water: over the top course from the slit, then down every riser and over every ledge, a bead on each lip
    s0, s1 = d["slit"]; sl = s1 - s0; sy = (s0 + s1) / 2
    for k in range(n):
        ztop = z0s[k] + H[k]
        back = xs if k == n - 1 else front[k + 1]
        P.box(sheet, ((back + front[k]) / 2 - 0.004, sy, ztop + 0.003), (back - front[k] + 0.008, sl, 0.004))   # on the ledge
        P.box(sheet, (front[k] - 0.008, sy, (ztop + max(z0s[k], d["zw_s"])) / 2), (0.004, sl, ztop - max(z0s[k], d["zw_s"])))  # down the riser
    P.rods(sheet, [(front[k] - 0.002, s0, z0s[k] + H[k] + 0.001) for k in range(n)], [(front[k] - 0.002, s1, z0s[k] + H[k] + 0.001) for k in range(n)], 0.007, seg=10)
    P.box(sheet, (xs - 0.012, sy, d["z_slit"] + 0.008), (0.024, sl, 0.012))                                     # coming through the slit

    # ---- the pool: honed dark granite coping flush with the floor, a dark bed under thousands of small river stones, the water
    for ya in np.arange(ys_, yn, 1.2):
        a, b_ = float(ya) + 0.002, float(min(ya + 1.2, yn)) - 0.002
        P.box(gr, (xr - c / 2, (a + b_) / 2, d["z_bot"] / 2), (c, b_ - a, -d["z_bot"]))
    P.box(gr, ((xr - c + front[0]) / 2, (ys_ - 0.096 + yw) / 2, d["z_bot"] / 2), (front[0] - xr + c, ys_ - 0.096 - yw, -d["z_bot"]))  # past the slit
    P.box(gr, ((xr + front[0]) / 2, yn - 0.01, d["z_bot"] / 2), (front[0] - xr, 0.02, -d["z_bot"]))           # the pool's north end, dark
    P.box(bed, ((xr + front[0]) / 2, (ys_ + yn) / 2, d["z_bot"] + 0.01), (front[0] - xr, yn - ys_, 0.02))
    area = (front[0] - xr) * (yn - ys_); npb = int(area * 320)                                                  # the bed covered, sand between
    rr = 0.015 + 0.06 * rng.uniform(0, 1, npb) ** 1.8
    pts = np.stack([rng.uniform(xr + 0.02, front[0] - 0.01, npb), rng.uniform(ys_ + 0.02, yn - 0.02, npb), d["z_bot"] + 0.02 + rr * 0.3], 1)
    radii = np.stack([rr * rng.uniform(1.0, 1.5, npb), rr, rr * rng.uniform(0.4, 0.6, npb)], 1)[:, None, :]
    _pebbles(P, stones, pts, radii, rng)
    ang = (d["zw_n"] - d["zw_s"]) / (yn - ys_)
    P.box(wat, ((xr + front[0]) / 2 + 0.002, (ys_ + yn) / 2, (d["zw_n"] + d["zw_s"]) / 2 - 0.004), (front[0] - xr - 0.004, yn - ys_ - 0.004, 0.008), rx=ang)
    P.box(_led("den_pool_line", (1.0, 0.9, 0.78), 1.0), (xr + 0.006, (ys_ + yn) / 2, -0.075), (0.008, yn - ys_ - 0.1, 0.01))

    # ---- the outfall: over a steel lip into an open slit across the floor, and gone (the return to the river)
    zws = d["zw_s"]; wx = (xr + front[0]) / 2; ww = front[0] - xr
    P.box(M["felt"], (wx, ys_ - 0.048, -0.2), (ww, 0.096, 0.4))
    P.box(st, (wx, ys_ + 0.008, (d["z_bot"] + zws - 0.012) / 2), (ww, 0.016, zws - 0.012 - d["z_bot"]))
    P.rods(sheet, [(xr, ys_ - 0.002, zws - 0.008)], [(front[0], ys_ - 0.002, zws - 0.008)], 0.009, seg=10)
    P.box(sheet, (wx, ys_ - 0.012, zws - 0.17), (ww - 0.004, 0.004, 0.3))
    P.box(st, (wx, ys_ - 0.088, -0.006), (ww + c, 0.016, 0.012))



# ---------------------------------------------------------------- the glass lifts (Roman 2026-10-17: natural stone columns with glass lifts)
def _split_granite():
    """The split near-black granite of the den's river base, shared by the lifts' shafts and columns."""
    return M.setdefault("granite_split_dark", bc.pbr_material("granite_split_dark", "quarry_wall", 1.8, box=True, tint=(0.8, 0.82, 0.85), sat=0.2,
                                                            val=0.12, rough_mul=0.5, piece_var=0.1))


def _granite_face(P, mat, axis, u0, u1, z0, z1, plane, depth, rng, seed, hmin=0.16, hmax=0.38, lmin=0.5, lmax=1.3, jog=0.012):
    """A face of split granite laid in courses: blocks of their own length and height, each a touch proud or shy. axis 'x' runs the
    face along x at y = plane (depth toward -y if depth < 0); axis 'y' runs it along y at x = plane."""
    z = z0
    while z < z1 - 0.02:
        h = float(min(rng.uniform(hmin, hmax), z1 - z))
        if z1 - z - h < hmin * 0.6:
            h = z1 - z
        u = u0
        first = True
        while u < u1 - 0.01:
            L = float(min(rng.uniform(lmin, lmax) * (0.6 if first else 1.0), u1 - u))
            if u1 - u - L < lmin * 0.5:
                L = u1 - u
            first = False
            d = abs(depth) + float(rng.uniform(-jog, jog)); sgn = 1 if depth > 0 else -1
            c_d = plane + sgn * d / 2
            if axis == "x":
                _rough_block(P, mat, (u + L / 2, c_d, z + h / 2), (L - 0.006, d, h - 0.006), amp=0.006, seed=seed + u * 7 + z * 3, cuts=2)
            else:
                _rough_block(P, mat, (c_d, u + L / 2, z + h / 2), (d, L - 0.006, h - 0.006), amp=0.006, seed=seed + u * 7 + z * 3, cuts=2)
            u += L
        z += h


def glass_lift(P, shaft=(-1.1, 1.1, -2.24), front=(-1.1, 1.1), stops=((0.0, 3.0, 0.46, 0.5),), pit=-1.2, top=6.0, cab=0.0, cw=-1, name="lift"):
    """A glass lift in a shaft of split granite (Roman 2026-10-17: natural stone columns with glass lifts, all the lifts there are,
    nothing new through the middle of the floors). Local frame: +y = the room, y = 0 the glass plane of the landing fronts, x across.
    shaft = (x0, x1, back y) its inside; front = the two columns' centres (the wall opening's edges); stops = (z, glass height,
    reveal = room face in front of the glass, lintel = a split granite lintel over the glass on the columns, up to the ceiling[, proud,
    'frame' = no stone, only the door in a slim blackened steel outline]). At every stop two columns of split granite stand floor to ceiling, wrapping the reveal,
    with a full-height glass front between them: low-iron glass in slim blackened steel, centre-opening glass landing doors under a
    steel operator head, a granite threshold. Behind it the shaft is lined in split granite from the pit to the top, grazed by light
    lines in its front corners; the cab is glass on three sides in a blackened steel sling with a granite floor, an opal ceiling,
    a brass handrail; T-rails, the counterweight (filler plates in a steel frame) on one side, the ropes up to a gearless machine."""
    st, gl, br = M["steel"], M["glass"], M["brass"]
    split = _split_granite()
    honed = M.setdefault("granite_honed_dark", bc.pbr_material("granite_honed_dark", "granite_tile", 1.2, box=True, tint=(0.55, 0.55, 0.57), sat=0.3,
                                                               val=0.34, rough_mul=0.45, rough_add=0.05, piece_var=0.08))
    glow = _led("lift_shaft_line", (1.0, 0.86, 0.7), 40.0)
    opal = _led("lift_cab_opal", (1.0, 0.93, 0.84), 6.0)
    x0, x1, yb = shaft; f0, f1 = front
    k_ = sum(map(ord, name)); rng = np.random.default_rng(k_); seed = (k_ % 97) * 1.3

    # ---- the cab's place: the counterweight on one side, the car in the rest
    cww = 0.36
    cx0, cx1 = (x0 + cww + 0.1, x1 - 0.1) if cw < 0 else (x0 + 0.1, x1 - cww - 0.1)
    fc = (f0 + f1) / 2                                             # the car + its doors centred in the opening (Roman 2026-11-01:
    hc = min(fc - cx0, cx1 - fc)                                   # "the elevator is still weirdly not centered")
    cx0, cx1 = fc - hc, fc + hc
    cw_x = x0 + 0.06 + cww / 2 if cw < 0 else x1 - 0.06 - cww / 2
    cy0, cy1 = max(yb + 0.14, -1.62), -0.035                       # car depth: back glass .. front sill
    ccx, ccy = (cx0 + cx1) / 2, (cy0 + cy1) / 2

    # ---- the shaft: split granite on the back + both sides, pit to top
    sk = 0.07
    _granite_face(P, split, "x", x0, x1, pit, top, yb, sk, rng, seed)                         # back wall (stone grows into the shaft)
    _granite_face(P, split, "y", yb + sk, 0.0, pit, top, x0, sk, rng, seed + 11)               # side walls
    _granite_face(P, split, "y", yb + sk, 0.0, pit, top, x1, -sk, rng, seed + 23)
    P.box(M["felt"], ((x0 + x1) / 2, (yb + 0.0) / 2, pit - 0.03), (x1 - x0, -yb, 0.06))         # the pit floor
    for xs_ in (x0 + sk + 0.015, x1 - sk - 0.015):                                              # light lines in the front corners
        P.box(glow, (xs_, -0.06, (pit + top) / 2), (0.012, 0.012, top - pit - 0.2))
    P.box(st, ((x0 + x1) / 2, (yb + 0.0) / 2, top - 0.03), (x1 - x0, -yb, 0.06))                # the shaft head
    # gearless machine on its bedplate at the top, ropes down to the car and the counterweight
    P.box(st, ((x0 + x1) / 2, (yb + cy1) / 2, top - 0.25), (x1 - x0 - 0.2, 0.18, 0.16))
    P.ring(st, ((cx0 + cx1) / 2, (yb + cy1) / 2 + 0.2), 0.05, 0.22, top - 0.62, top - 0.36, seg=48)
    P.ring(br, ((cx0 + cx1) / 2, (yb + cy1) / 2 + 0.2), 0.22, 0.225, top - 0.6, top - 0.38, seg=48)  # its brass name ring

    # ---- rails: the car's T-rails on its sides, the counterweight's pair, brackets every 2.5 m
    ry = ccy
    for xr_ in (cx0 - 0.045, cx1 + 0.045):
        P.box(st, (xr_, ry, (pit + top) / 2), (0.016, 0.09, top - pit))
        P.box(st, (xr_ + (0.03 if xr_ > ccx else -0.03), ry, (pit + top) / 2), (0.045, 0.012, top - pit))
    for yr_ in (ry - 0.3, ry + 0.3):
        P.box(st, (cw_x, yr_, (pit + top) / 2), (0.07, 0.012, top - pit))
    for zb in np.arange(pit + 0.6, top, 2.5):
        for xr_ in (cx0 - 0.045, cx1 + 0.045):
            xw = x0 + sk if xr_ < ccx else x1 - sk
            P.box(st, ((xr_ + xw) / 2, ry, float(zb)), (abs(xw - xr_), 0.12, 0.08))

    # ---- the counterweight: opposite the car (high when the car is low)
    cwh = 2.2
    cwz = min(top - 0.9 - cwh, max(pit + 0.6, top - 0.9 - cwh - (cab - pit)))
    for yr_ in (ry - 0.27, ry + 0.27):
        P.box(st, (cw_x, yr_, cwz + cwh / 2), (0.1, 0.04, cwh))
    for k in range(int((cwh - 0.2) / 0.05)):
        P.box(st, (cw_x, ry, cwz + 0.1 + k * 0.05 + 0.024), (0.09, 0.5, 0.044))
    P.box(st, (cw_x, ry, cwz + 0.05), (0.12, 0.6, 0.1)); P.box(st, (cw_x, ry, cwz + cwh - 0.05), (0.12, 0.6, 0.1))
    P.rods(st, [(cw_x + dx, ry, cwz + cwh) for dx in (-0.02, 0.02)], [(cw_x + dx, ry, top - 0.3) for dx in (-0.02, 0.02)], 0.005, seg=6)

    # ---- the cab
    z = cab; ch = 2.35
    P.box(st, (ccx, ccy, z - 0.07), (cx1 - cx0, cy1 - cy0, 0.14))                               # platform frame
    P.box(honed, (ccx, ccy, z - 0.012), (cx1 - cx0 - 0.04, cy1 - cy0 - 0.04, 0.024))             # granite floor
    P.box(st, (ccx, cy1 - 0.2, z - 0.42), (cx1 - cx0, 0.012, 0.56))                              # toe guard under the sill
    P.box(st, (ccx, ccy, z + ch + 0.05), (cx1 - cx0 + 0.02, cy1 - cy0 + 0.02, 0.1))              # canopy
    P.box(opal, (ccx, ccy, z + ch - 0.002), (cx1 - cx0 - 0.3, cy1 - cy0 - 0.3, 0.004))           # opal light
    for xx in (cx0 + 0.012, cx1 - 0.012):                                                         # glass sides + back, corner posts
        P.box(gl, (xx, ccy, z + ch / 2), (0.012, cy1 - cy0 - 0.05, ch - 0.02))
    P.box(gl, (ccx, cy0 + 0.012, z + ch / 2), (cx1 - cx0 - 0.05, 0.012, ch - 0.02))
    for xx in (cx0 + 0.015, cx1 - 0.015):
        for yy in (cy0 + 0.015, cy1 - 0.015):
            P.box(st, (xx, yy, z + ch / 2), (0.03, 0.03, ch))
    for xs_ in (cx0 - 0.02, cx1 + 0.02):                                                         # the sling: stiles + crosshead
        P.box(st, (xs_, ccy, z + ch / 2 + 0.1), (0.04, 0.1, ch + 0.5))
    P.box(st, (ccx, ccy, z + ch + 0.33), (cx1 - cx0 + 0.08, 0.12, 0.14))
    P.rods(st, [(ccx + dx, ccy, z + ch + 0.4) for dx in (-0.06, -0.02, 0.02, 0.06)], [(ccx + dx, ccy, top - 0.3) for dx in (-0.06, -0.02, 0.02, 0.06)], 0.005, seg=6)
    P.rods(br, [(cx0 + 0.06, cy0 + 0.07, z + 0.92)], [(cx1 - 0.06, cy0 + 0.07, z + 0.92)], 0.018, seg=16)   # brass handrail
    P.rods(br, [(x_, cy0 + 0.024, z + 0.92) for x_ in (cx0 + 0.15, cx1 - 0.15)], [(x_, cy0 + 0.07, z + 0.92) for x_ in (cx0 + 0.15, cx1 - 0.15)], 0.008)
    dw = min(1.1, cx1 - cx0 - 0.3)
    for s_ in (-1, 1):                                                                            # car doors: glass leaves
        P.box(gl, (ccx + s_ * dw / 4, cy1 - 0.01, z + 1.08), (dw / 2 - 0.006, 0.012, 2.14))
        P.box(st, (ccx + s_ * (dw / 2 - 0.012), cy1 - 0.01, z + 1.08), (0.022, 0.024, 2.16))
    for s_ in (-1, 1):                                                                            # front returns + the panel
        P.box(st, (ccx + s_ * (dw / 2 + (cx1 - cx0 - dw) / 4), cy1 - 0.02, z + ch / 2), ((cx1 - cx0 - dw) / 2, 0.03, ch))
    px = ccx + dw / 2 + (cx1 - cx0 - dw) / 4
    for k in range(4):
        P.rod(br, (px, cy1 - 0.036, z + 1.0 + k * 0.09), (px, cy1 - 0.044, z + 1.0 + k * 0.09), 0.013, seg=16)
    P.box(_led("lift_display", (1.0, 0.9, 0.7), 4.0), (px, cy1 - 0.037, z + 1.45), (0.05, 0.003, 0.02))
    P.box(st, (ccx, cy1 - 0.02, z + 2.2), (dw + 0.04, 0.05, 0.08))                              # door head

    # ---- every stop: two stone columns, the glass front, landing doors, a granite threshold
    pw = 0.42
    lx = ccx                                                                                       # landing doors line up with the car's
    for zs, h, rv, lin, *pr in stops:
        dep = rv + (pr[0] if pr else 0.14)
        if pr[1:] == ["frame"]:                                                                   # just the door in a slim steel outline
            hw = dw / 2 + 0.05                                                                    # the opening: the doors + 50 mm jambs
            for s_ in (-1, 1):
                P.box(st, (lx + s_ * (hw - 0.01), rv / 2, zs + h / 2), (0.02, rv + 0.004, h))      # jamb linings
                P.box(st, (lx + s_ * (hw + 0.012), rv + 0.005, zs + h / 2 + 0.012), (0.024, 0.01, h + 0.024))  # the outline on the wall
            P.box(st, (lx, rv / 2, zs + h - 0.045), (2 * hw, rv + 0.004, 0.09))                   # head lining
            P.box(st, (lx, rv + 0.005, zs + h + 0.012), (2 * hw + 0.048, 0.01, 0.024))
            P.box(honed, (lx, rv / 2 + 0.02, zs - 0.05), (2 * hw, rv + 0.04, 0.1))                # threshold
            P.box(st, (lx, 0.03, zs + 0.003), (dw + 0.06, 0.09, 0.006))
            for s_ in (-1, 1):
                P.box(gl, (lx + s_ * dw / 4, 0.03, zs + 1.08), (dw / 2 - 0.006, 0.012, 2.14))
                P.box(st, (lx + s_ * (dw / 2 - 0.012), 0.03, zs + 1.08), (0.022, 0.024, 2.16))
            P.box(st, (lx, 0.04, zs + 2.24), (dw + 0.1, 0.07, 0.14))
            P.box(st, (lx + hw + 0.16, rv + 0.006, zs + 1.1), (0.07, 0.012, 0.14))               # call plate on the slats
            for dz in (0.03, -0.03):
                P.rod(br, (lx + hw + 0.16, rv + 0.012, zs + 1.1 + dz), (lx + hw + 0.16, rv + 0.022, zs + 1.1 + dz), 0.014, seg=20)
            continue
        if lin > 0.05:                                                                            # the stone lintel over the glass, on the columns
            _rough_block(P, split, ((f0 + f1) / 2, dep / 2 - 0.002, zs + h + lin / 2), (f1 - f0 + pw + 0.02, dep + 0.02, lin - 0.006), amp=0.009,
                         seed=seed + zs * 3, cuts=4)
        for xc in (f0, f1):                                                                       # the columns, floor to ceiling
            _granite_face(P, split, "x", xc - pw / 2, xc + pw / 2, zs, zs + h, -0.002, dep, rng, seed + zs * 5 + xc * 13, hmin=0.24, hmax=0.52, lmin=pw, lmax=pw, jog=0.018)
        g0, g1 = f0 + pw / 2, f1 - pw / 2
        P.box(honed, ((g0 + g1) / 2, rv / 2 + 0.02, zs - 0.05), (g1 - g0, rv + 0.04, 0.1))       # threshold, flush with the floor
        P.box(st, (lx, 0.03, zs + 0.003), (dw + 0.06, 0.09, 0.006))                               # door sill
        for s_ in (-1, 1):                                                                        # landing door leaves
            P.box(gl, (lx + s_ * dw / 4, 0.03, zs + 1.08), (dw / 2 - 0.006, 0.012, 2.14))
            P.box(st, (lx + s_ * (dw / 2 - 0.012), 0.03, zs + 1.08), (0.022, 0.024, 2.16))
        P.box(st, (lx, 0.04, zs + 2.24), (dw + 0.1, 0.07, 0.14))                                  # operator head
        for a, b in ((g0, lx - dw / 2 - 0.05), (lx + dw / 2 + 0.05, g1)):                         # fixed glass beside the doors
            if b - a > 0.03:
                P.box(gl, ((a + b) / 2, 0.03, zs + 1.155), (b - a, 0.012, 2.29))
        P.box(gl, ((g0 + g1) / 2, 0.03, zs + 2.31 + (h - 2.31) / 2), (g1 - g0, 0.012, h - 2.33))  # the glass above, to the ceiling
        P.box(st, ((g0 + g1) / 2, 0.03, zs + h - 0.02), (g1 - g0, 0.05, 0.04))                    # head channel
        for xx in (g0 + 0.01, g1 - 0.01):                                                         # slim side channels in the stone
            P.box(st, (xx, 0.03, zs + h / 2), (0.02, 0.05, h))
        P.box(st, (f1, dep + 0.004, zs + 1.1), (0.09, 0.012, 0.16))                 # call plate on the column face
        P.rod(br, (f1, dep + 0.004, zs + 1.13), (f1, dep + 0.016, zs + 1.13), 0.016, seg=20)
        P.rod(br, (f1, dep + 0.004, zs + 1.07), (f1, dep + 0.016, zs + 1.07), 0.016, seg=20)


# ---------------------------------------------------------------- F4: the lap pool (Roman 2026-10-17: blueish dark tile + stone, black stone, white as accent)
def lap_pool(P, x0=-16.25, x1=-6.65, y0=-28.38, y1=-3.3, d_n=1.25, d_s=1.5, raft=-1.6, water=-0.012):
    """The 25 m lap pool in the pool hall, built in the floor's frame (origin at the F4 floor, x/y world). A deep ink-blue glass mosaic
    basin (the river wall's face too, below the water), four lanes marked in black mosaic with T-ends and targets on the end walls;
    honed black stone coping with white veins on three sides, flush with the deck, the water a hand below it over a
    hidden overflow slot (blackened steel grate); a thin white stone line set in the deck round the pool (the white accent). Wide
    steps in the north-west corner: black stone treads with white stone nosings, a blackened steel rail. The water clear with a faint
    blue, gently moving; lit from underwater along the west wall. Roman 2026-10-18: a true 25 m between the finished end walls
    (25.02, inside the +0.03 tolerance) and a club depth, 1.25 m at the steps falling gently to 1.5 m at the south end (was 2.0 throughout);
    the fall is in the screed on the flat raft (top at `raft`)."""
    st = M["steel"]
    mos, mosb = bc.pool_mosaic(), bc.pool_mosaic("pool_mosaic_black", (0.010, 0.011, 0.013), (0.016, 0.017, 0.020))
    nero = M.get("stone_nero_honed") or bc.interior_materials()["stone_nero_honed"]
    white = M.get("stone_white") or bc.interior_materials()["stone_white"]
    wat = _pool_water()
    glow = _led("pool_light", (0.8, 0.93, 1.0), 25.0)
    t = 0.03                                                    # mosaic thickness on the structure
    cx = (x0 + x1) / 2
    zf = lambda y: -d_s + (d_s - d_n) * (y - y0) / (y1 - y0)   # the finished floor, falling to the south
    def wedge(mat, xa, xb, pts_yz):                             # a yz outline extruded along x (the sloped floor + side walls)
        bb = P.bm(mat)
        v0 = [bb.verts.new((xa, y, z)) for y, z in pts_yz]; v1 = [bb.verts.new((xb, y, z)) for y, z in pts_yz]
        bb.faces.new(v0[::-1]); bb.faces.new(v1)
        for i in range(len(pts_yz)):
            j = (i + 1) % len(pts_yz)
            bb.faces.new((v0[i], v0[j], v1[j], v1[i]))
        bmesh.ops.recalc_face_normals(bb, faces=bb.faces[-(len(pts_yz) + 2):])
    # ---- the basin: the screed + mosaic floor on the raft, falling south, and four walls in mosaic (inside faces at x0..x1, y0..y1)
    wedge(mos, x0, x1, [(y0, raft), (y1, raft), (y1, zf(y1)), (y0, zf(y0))])
    wedge(mos, x0, x0 + t, [(y0, raft), (y1, raft), (y1, -0.04), (y0, -0.04)])
    wedge(mos, x1 - 0.06, x1, [(y0, raft), (y1, raft), (y1, -0.04), (y0, -0.04)])                 # river wall face (over the pilasters)
    for yy, sg in ((y0, 1), (y1, -1)):
        P.box(mos, (cx, yy + sg * t / 2, (raft - 0.04) / 2), (x1 - x0, t, -raft - 0.04))
    x0 += t; y0 += t; y1 -= t; cy = (y0 + y1) / 2                                                 # the finished faces
    slope = math.atan2(d_s - d_n, y1 - y0)                                                        # the floor rises to the north
    # ---- lanes: four, black mosaic lines on the floor with T-ends, targets on the end walls (crossbar 0.3 m under the water)
    lw = (x1 - x0) / 4
    for k in range(4):
        lx = x0 + lw * (k + 0.5)
        P.box(mosb, (lx, cy, zf(cy) + 0.002), (0.25, y1 - y0 - 4.0, 0.004), rx=slope)
        for yy in (y0 + 2.0, y1 - 2.0):
            P.box(mosb, (lx, yy, zf(yy) + 0.002), (1.0, 0.25, 0.004), rx=slope)
        for yy, sg in ((y0, 1), (y1, -1)):
            za, zb_ = zf(yy) + 0.15, -0.3
            P.box(mosb, (lx, yy + sg * 0.003, (za + zb_) / 2), (0.25, 0.004, zb_ - za))
            P.box(mosb, (lx, yy + sg * 0.003, -0.3), (0.6, 0.004, 0.25))
    # ---- the steps, north-west corner: 6 risers down to the floor, black stone treads, white stone nosings, mosaic risers
    sw, n_, go = 3.0, 6, 0.3
    rise = d_n / n_
    for k in range(n_):
        zt_ = -rise * (k + 1); ya = y1 - go * k
        zb_ = zf(ya - go) - 0.01
        if zt_ - zb_ > 0.02:
            P.box(mos, (x0 + sw / 2, ya - go / 2, (zt_ + zb_) / 2), (sw, go, zt_ - zb_))           # the step block
        P.box(nero, (x0 + sw / 2, ya - go / 2, zt_ - 0.012), (sw, go, 0.024))
        P.box(white, (x0 + sw / 2, ya - go + 0.02, zt_ - 0.011), (sw, 0.04, 0.026))
    P.rods(st, [(x0 + sw + 0.05, y1 + 0.25, 0.0)], [(x0 + sw + 0.05, y1 + 0.25, 0.95)], 0.021, seg=16)  # the rail: up from the deck,
    pts = [(x0 + sw + 0.05, y1 + 0.25, 0.95), (x0 + sw + 0.05, y1 - 0.1, 0.95), (x0 + sw + 0.05, y1 - go * 5, -rise * 5 + 0.9),
           (x0 + sw + 0.05, y1 - go * 5, -rise * 5 + 0.1)]
    for a, b in zip(pts, pts[1:]):                                                                    # over the edge and down the steps
        P.rod(st, a, b, 0.021, seg=16)
    # ---- coping: honed black stone, 450 mm, flush with the deck (top 20 mm above the raft), on W, N + S; the overflow slot behind it
    cw_, gr = 0.45, 0.16
    def coping_run(xa, ya, xb, yb, inward):
        L = math.hypot(xb - xa, yb - ya); ux, uy = (xb - xa) / L, (yb - ya) / L; nx, ny = inward
        s = 0.0
        while s < L - 0.01:
            pl = min(1.0, L - s)
            ccx = xa + ux * (s + pl / 2) - nx * cw_ / 2; ccy = ya + uy * (s + pl / 2) - ny * cw_ / 2
            P.box(nero, (ccx, ccy, -0.02), (abs(ux) * (pl - 0.003) + abs(nx) * cw_, abs(uy) * (pl - 0.003) + abs(ny) * cw_, 0.08))
            s += pl
        gx = (xa + xb) / 2 - nx * (cw_ + gr / 2); gy = (ya + yb) / 2 - ny * (cw_ + gr / 2)
        P.box(st, (gx, gy, 0.012), (abs(ux) * L + abs(nx) * gr, abs(uy) * L + abs(ny) * gr, 0.016))        # overflow grate
        for k in range(int(L / 0.03)):
            px = xa + ux * (k * 0.03 + 0.015) - nx * (cw_ + gr / 2); py = ya + uy * (k * 0.03 + 0.015) - ny * (cw_ + gr / 2)
            P.box(M["felt"], (px, py, 0.0205), (abs(ux) * 0.012 + abs(nx) * (gr - 0.03), abs(uy) * 0.012 + abs(ny) * (gr - 0.03), 0.002))
        lx_ = (xa + xb) / 2 - nx * (cw_ + gr + 0.35); ly_ = (ya + yb) / 2 - ny * (cw_ + gr + 0.35)
        P.box(white, (lx_, ly_, 0.0205), (abs(ux) * (L + 2 * (cw_ + gr + 0.35)) + abs(nx) * 0.02, abs(uy) * (L + 2 * (cw_ + gr + 0.35)) + abs(ny) * 0.02, 0.002))
    coping_run(x0, y0, x0, y1, (1, 0))
    coping_run(x0, y1, x1, y1, (0, -1))
    coping_run(x0, y0, x1, y0, (0, 1))
    # ---- the water: a hand under the coping, gently moving
    P.box(wat, ((x0 + x1 - 0.06) / 2, cy, (water + raft) / 2), (x1 - 0.06 - x0 - 0.004, y1 - y0 - 0.004, water - raft))
    # ---- underwater lights: flush opal lenses along the west wall + the ends, 0.6 m down
    for yy in np.arange(y0 + 2.0, y1 - 1.0, 3.0):
        P.box(glow, (x0 + 0.002, float(yy), -0.6), (0.006, 0.3, 0.1))
    for xx in np.arange(x0 + 1.5, x1, 2.4):
        for yy, sg in ((y0, 1), (y1, -1)):
            if not (yy == y1 and xx < x0 + sw + 0.2):
                P.box(glow, (float(xx), yy + sg * 0.002, -0.6), (0.3, 0.006, 0.1))


def _rect_minus(r, holes):
    """An axis-aligned rect (a0, a1, b0, b1) minus holes: the pieces left, cut round each hole."""
    out = [r]
    for h0, h1, k0, k1 in holes:
        nxt = []
        for a0, a1, b0, b1 in out:
            if h1 <= a0 or h0 >= a1 or k1 <= b0 or k0 >= b1:
                nxt.append((a0, a1, b0, b1)); continue
            if b0 < k0: nxt.append((a0, a1, b0, k0))
            if k1 < b1: nxt.append((a0, a1, k1, b1))
            if a0 < h0: nxt.append((a0, h0, max(b0, k0), min(b1, k1)))
            if h1 < a1: nxt.append((h1, a1, max(b0, k0), min(b1, k1)))
        out = nxt
    return [p for p in out if p[1] - p[0] > 0.005 and p[3] - p[2] > 0.005]


def river_wall_f4(P, y0=-34.1, y1=12.1, top=5.2, face=-6.65, d=0.065, windows=(), pilasters=()):
    """F4's river wall (Roman 2026-10-17: the underwater windows kept; black round them; no marble, normal materials): black glazed
    tile 300 x 600 in stack bond wall to wall, cut round every window, the reveals lined in the same tile back to the acrylic, and where
    a pilaster runs through a window it is clad as a mullion. Built in the floor's frame (x/y world)."""
    nero = M.get("stone_nero") or bc.interior_materials()["stone_nero"]
    P.vary = True                                                                                 # every tile its own glaze tone
    holes = [(a, b, c, e) for a, b, c, e in windows]
    y = y0
    while y < y1 - 0.01:
        w = min(0.3, y1 - y); z = 0.0
        while z < top - 0.01:
            h = min(0.6, top - z)
            for a0, a1, b0, b1 in _rect_minus((y, y + w, z, z + h), holes):
                P.box(nero, (face - d / 2, (a0 + a1) / 2, (b0 + b1) / 2), (d, a1 - a0 - 0.002, b1 - b0 - 0.002))
            z += h
        y += w
    xa, xb = face - d, -6.25
    for wy0, wy1, wz0, wz1 in windows:
        for yy in (wy0 + 0.01, wy1 - 0.01):
            P.box(nero, ((xa + xb) / 2, yy, (wz0 + wz1) / 2), (xb - xa, 0.02, wz1 - wz0))
        for zz in (wz0 + 0.01, wz1 - 0.01):
            P.box(nero, ((xa + xb) / 2, (wy0 + wy1) / 2, zz), (xb - xa, wy1 - wy0, 0.02))
        for py in pilasters:
            a, b = max(wy0, py - 0.31), min(wy1, py + 0.31)
            if b > a:
                P.box(nero, ((xa + xb) / 2, (a + b) / 2, (wz0 + wz1) / 2), (xb - xa, b - a, wz1 - wz0))


def river_volume(P, x0=-6.25, x1=8.0, y0=-36.0, y1=14.0, z0=-1.3, z1=6.62, lamps=(), lamp_z=-0.85):
    """The river itself outside F4's windows (it had a surface but no body: the windows looked out through air): a body of water
    from just under the bed to the surface (-8.77), cool green-teal, light falling off with distance so the far bank fades into
    murk. No surface shader: only the volume. Built in the floor's frame (x/y world, z from F4)."""
    if "river_body" not in M:
        mt = bpy.data.materials.new("river_body"); mt.use_nodes = True
        N_, L_ = mt.node_tree.nodes, mt.node_tree.links
        N_.remove(N_["Principled BSDF"])
        v = N_.new("ShaderNodeVolumePrincipled")
        v.inputs["Color"].default_value = (0.018, 0.05, 0.045, 1); v.inputs["Density"].default_value = 0.13  # mostly absorbs: black at night, shafts by day
        v.inputs["Absorption Color"].default_value = (0.30, 0.70, 0.62, 1)
        L_.new(v.outputs[0], N_["Material Output"].inputs["Volume"])
        M["river_body"] = mt
    P.box(M["river_body"], ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0))
    for ly in lamps:                                                                              # the bed lights: small pucks at the wall's foot
        P.box(M["steel"], (x0 + 0.25, ly, lamp_z + 0.04), (0.16, 0.16, 0.08))
        P.box(_led("riverbed_lamp", (0.85, 0.95, 1.0), 6.0), (x0 + 0.25, ly, lamp_z + 0.081), (0.1, 0.1, 0.002))



# ------------------------------------------------------------------ F4: the thermal suite, the lobby, the deck, recovery, breathwork
def _pool_water():
    """Pool water: architectural glass (light passes to the mosaic), IOR 1.33, a faint blue, a slow noise on the surface."""
    if "pool_water" not in M:
        w = bc.arch_glass("pool_water", tint=(0.80, 0.92, 0.95))
        N_, L_ = w.node_tree.nodes, w.node_tree.links; g_ = next(n for n in N_ if n.type == "BSDF_GLASS"); g_.inputs["IOR"].default_value = 1.33
        tc_ = N_.new("ShaderNodeTexCoord"); nz_ = N_.new("ShaderNodeTexNoise"); nz_.inputs["Scale"].default_value = 1.2; nz_.inputs["Detail"].default_value = 3.0
        L_.new(tc_.outputs["Object"], nz_.inputs["Vector"])
        bp_ = N_.new("ShaderNodeBump"); bp_.inputs["Strength"].default_value = 0.12; bp_.inputs["Distance"].default_value = 0.01
        L_.new(nz_.outputs["Fac"], bp_.inputs["Height"]); L_.new(bp_.outputs[0], g_.inputs["Normal"])
        M["pool_water"] = w
    return M["pool_water"]


def plunge(P, w=2.8, d=3.6, depth=0.57, rim=0.45, hot=False):
    """A plunge pool in the thermal suite (VISION: a simple hot/cold plunge): sunk through the raft with a honed near-black stone kerb
    0.45 high and 0.3 wide (sit on it, swing your legs over), the water a hand under the kerb, ~1 m deep. Inside a deep glass mosaic
    (cold: ink blue, a cool light; hot: near-black, a warm light), a seat ledge you sit on with the water
    at your shoulders, a blackened-steel grab rail over the kerb. Origin = the basin's centre on the floor, the step-in side +y."""
    st = M["steel"]
    nero = M.get("stone_nero_honed") or bc.interior_materials()["stone_nero_honed"]
    tile = M.get("stone_nero") or bc.interior_materials()["stone_nero"]
    mos = bc.pool_mosaic("plunge_mosaic_hot", (0.012, 0.012, 0.014), (0.020, 0.019, 0.020), caustics=True) if hot else bc.pool_mosaic()
    k = 0.3; t = 0.03
    xi, yi = w / 2 - k, d / 2 - k                                                       # inner half-sizes (finished faces)
    zb = -depth
    P.box(mos, (0, 0, zb + t / 2), (2 * xi, 2 * yi, t))                                 # floor
    for sx in (-1, 1):
        P.box(mos, (sx * (xi + t / 2), 0, (zb + rim - 0.02) / 2), (t, 2 * yi + 2 * t, rim - 0.02 - zb))
    for sy in (-1, 1):
        P.box(mos, (0, sy * (yi + t / 2), (zb + rim - 0.02) / 2), (2 * xi, t, rim - 0.02 - zb))
    P.vary = True
    for sx in (-1, 1):                                                                  # the kerb: honed slabs, mitred look
        P.box(nero, (sx * (w / 2 - k / 2), 0, rim - 0.03), (k, d, 0.06))
    for sy in (-1, 1):
        P.box(nero, (0, sy * (d / 2 - k / 2), rim - 0.03), (w - 2 * k - 0.004, k, 0.06))
    for sx in (-1, 1):                                                                  # its outer faces in black glazed tile
        P.box(tile, (sx * (w / 2 - 0.01), 0, (rim - 0.06) / 2), (0.02, d, rim - 0.06))
    for sy in (-1, 1):
        P.box(tile, (0, sy * (d / 2 - 0.01), (rim - 0.06) / 2), (w, 0.02, rim - 0.06))
    for sx in (-1, 1):                                                                  # the kerb's core (between the tile skins)
        P.box(tile, (sx * (w / 2 - k / 2), 0, (rim - 0.06) / 2), (k - 0.04, d - 0.04, rim - 0.06))
    for sy in (-1, 1):
        P.box(tile, (0, sy * (d / 2 - k / 2), (rim - 0.06) / 2), (w - 2 * k, k - 0.04, rim - 0.06))
    P.vary = False
    sh = 0.42                                                                           # the seat ledge along the step-in side
    P.box(mos, (0, yi - sh / 2, (zb + t - 0.5) / 2 + 0.0), (2 * xi, sh, -0.5 - zb - t))
    P.box(nero, (0, yi - sh / 2, -0.5 + 0.015), (2 * xi, sh, 0.03))
    rx = xi - 0.35                                                                      # the rail, over the kerb and down onto the ledge
    pts = [(rx, d / 2 + 0.12, 0.0), (rx, d / 2 + 0.12, rim + 0.5), (rx, yi - 0.05, rim + 0.5), (rx, yi - 0.05, -0.47)]
    for a, b in zip(pts, pts[1:]):
        P.rod(st, a, b, 0.019, seg=16)
    P.cyl(st, (rx, d / 2 + 0.12, 0.0), 0.04, 0.008, seg=24)
    wl = rim - 0.09
    P.box(_pool_water(), (0, 0, (wl + zb + t) / 2), (2 * xi - 0.004, 2 * yi - 0.004, wl - zb - t))
    glow = _led("plunge_warm" if hot else "plunge_cool", (1.0, 0.72, 0.45) if hot else (0.75, 0.9, 1.0), 14.0)
    P.box(glow, (0, -yi + 0.002, -0.28), (0.24, 0.006, 0.08))                          # one lens in the back wall


def sauna_cabin(P, w=2.85, d=4.4, h=2.3, door=0.8):
    """The thermal suite's sauna (VISION: a simple thermal setup): a thermo-aspen room built into the corner, its front onto the suite
    bronze glass from floor to ceiling in aspen posts with the door in it, so the warm wood glows into the dark tile. Vertical aspen
    boards on the walls, a boarded ceiling at 2.3, slatted aspen duckboards on the floor; above the ceiling a closed box to the
    hall's ceiling line in black tile. The tiers, the heater, the bucket are their own pieces. Origin = the front's centre on the
    floor, the room behind it (-y), front +y."""
    _kulpen_mats(); a = M["aspen_thermo"]
    tint = M.setdefault("glass_bronze", bc.arch_glass("glass_bronze", tint=(0.86, 0.74, 0.58)))
    P.vary = True
    x = -w / 2 + 0.045                                                                  # the back wall's boards
    while x < w / 2 - 0.02:
        P.box(a, (x, -d + 0.01, h / 2), (0.088, 0.02, h)); x += 0.09
    for sx in (-1, 1):                                                                  # the side walls'
        y = -d + 0.045
        while y < -0.08:
            P.box(a, (sx * (w / 2 - 0.01), y, h / 2), (0.02, 0.088, h)); y += 0.09
    y = -d + 0.045
    while y < 0.0:                                                                      # the ceiling, boards across
        P.box(a, (0, y, h + 0.01), (w, 0.088, 0.02)); y += 0.09
    y = -d + 0.06
    while y < -0.08:                                                                    # duckboards
        P.box(a, (0, y, 0.025), (w - 0.06, 0.07, 0.025)); y += 0.095
    for sx in (-1, 1):
        P.box(a, (sx * (w / 2 - 0.1), -d / 2, 0.006), (0.05, d - 0.1, 0.012))
    P.vary = False
    # the front: aspen posts, bronze glass, the door
    xs = [-w / 2, door - 0.4, door + 0.4, w / 2]
    for xp in xs:
        P.box(a, (xp + (0.03 if xp == -w / 2 else -0.03 if xp == w / 2 else 0.0), -0.04, h / 2 + 0.06), (0.06, 0.08, h + 0.12))
    P.box(a, (0, -0.04, h + 0.06), (w, 0.08, 0.12))                                     # head
    P.box(a, (0, -0.04, 0.03), (w, 0.08, 0.06))                                         # sill
    for xa_, xb_ in ((-w / 2 + 0.06, door - 0.43), (door + 0.43, w / 2 - 0.06)):
        if xb_ - xa_ > 0.05:
            P.box(tint, ((xa_ + xb_) / 2, -0.04, h / 2 + 0.03), (xb_ - xa_, 0.01, h - 0.06))
    for sx in (-1, 1):                                                                  # the door leaf: aspen frame, bronze glass
        P.box(a, (door + sx * 0.355, -0.01, 0.98), (0.05, 0.05, 1.92))
    for z in (0.04, 1.92):
        P.box(a, (door, -0.01, z), (0.76, 0.05, 0.06))
    P.box(tint, (door, -0.01, 0.98), (0.66, 0.008, 1.82))
    for sy in (-1, 1):
        P.box(a, (door + 0.25, sy * 0.05, 1.0), (0.035, 0.03, 0.42))
    tile = M.get("stone_nero") or bc.interior_materials()["stone_nero"]
    P.box(tile, (0, -0.04, h + 0.12 + 0.06), (w, 0.1, 0.12))                            # a black band over the head (the box above)


def sauna_heater_el(P):
    """The thermal suite's sauna heater (electric; no fire underground): a tall soapstone-clad body, a deep open basket of stones on
    top for the löyly, a blackened-steel guard of rails; the controls are outside by the door. Origin = floor, front +y."""
    _kulpen_mats(); ss, st = M["soapstone"], M["steel"]
    W, D, H = 0.55, 0.45, 0.95
    for k, (z0, z1) in enumerate(((0.0, 0.32), (0.32, 0.64), (0.64, H))):
        P.box(ss, (0, 0, (z0 + z1) / 2), (W, D, z1 - z0 - 0.004))
    for sx in (-1, 1):
        P.box(st, (sx * (W / 2 - 0.004), 0, H + 0.14), (0.008, D, 0.28)); P.box(st, (0, sx * (D / 2 - 0.004), H + 0.14), (W, 0.008, 0.28))
    rng = np.random.default_rng(11)
    stone = M.setdefault("sauna_stones", bc.pbr_material("sauna_stones", "dark_rock", 0.6, box=True, tint=(0.75, 0.75, 0.75), sat=0.3, val=0.6, piece_var=0.15))
    for z in (H + 0.04, H + 0.11, H + 0.18, H + 0.25):
        for _ in range(16):
            r = float(rng.uniform(0.04, 0.06))
            P.blob(stone, (float(rng.uniform(-0.22, 0.22)), float(rng.uniform(-0.17, 0.17)), z), (r, r * float(rng.uniform(0.8, 1.1)), r * 0.7), seg=12)
    for sx in (-1, 1):                                                                  # guard
        for yy in (-D / 2 - 0.12, D / 2 + 0.12):
            P.rod(st, (sx * (W / 2 + 0.12), yy, 0.0), (sx * (W / 2 + 0.12), yy, 0.9), 0.012, seg=10)
        for z in (0.45, 0.88):
            P.rod(st, (sx * (W / 2 + 0.12), -D / 2 - 0.12, z), (sx * (W / 2 + 0.12), D / 2 + 0.12, z), 0.01, seg=10)
    for z in (0.45, 0.88):
        P.rod(st, (-W / 2 - 0.12, D / 2 + 0.12, z), (W / 2 + 0.12, D / 2 + 0.12, z), 0.01, seg=10)


def steam_room(P, w=2.95, d=3.8, h=2.5, door=0.9):
    """The thermal suite's steam room (VISION: a simple thermal setup): lined all over in deep ink glass mosaic, walls, benches and a
    ceiling that falls from front to back so the drips run down the walls, not onto you; L-shaped benches along the back + one side,
    tiled, raked backs; clear glass front in a blackened-steel frame with the door (no steam volume: at draft quality it rendered as
    blotchy noise), small warm pin lights in the ceiling, the steam outlet low by the bench. Origin = the front's centre on the floor, the
    room behind (-y), front +y."""
    st = M["steel"]
    mos = bc.pool_mosaic("steam_mosaic", (0.012, 0.030, 0.055), (0.022, 0.050, 0.085), caustics=False)
    tile = M.get("stone_nero") or bc.interior_materials()["stone_nero"]
    t = 0.03
    P.box(mos, (0, -d / 2, 0.01), (w, d, 0.02))                                         # floor
    P.box(mos, (0, -d + t / 2, h / 2), (w, t, h))                                       # back
    for sx in (-1, 1):
        P.box(mos, (sx * (w / 2 - t / 2), -d / 2, h / 2), (t, d, h))                    # sides
    fall = 0.25; ang = math.atan2(fall, d)
    P.box(mos, (0, -d / 2, h - fall / 2 + 0.02), (w, math.hypot(d, fall), t), rx=-ang)  # the sloped ceiling (high at the front)
    P.box(tile, (0, -d / 2, h + 0.12), (w, d, 0.06))                                    # the box's lid
    P.box(tile, (-w / 2 - 0.03, -d / 2, (h + 0.15) / 2), (0.06, d, h + 0.15))          # its outer skin on the side open to the suite
    for xp, yp in [(-w / 4, -0.8), (w / 4, -0.8), (-w / 4, -2.3), (w / 4, -2.3), (0, -1.55)]:
        zc = h - fall * (-yp) / d - 0.001
        P.cyl(_led("steam_pin", (1.0, 0.8, 0.55), 30.0), (xp, yp, zc - 0.012), 0.012, 0.012, seg=12)
    seat, sd = 0.46, 0.5                                                                 # benches: back run + west run
    P.box(mos, (0, -d + t + sd / 2, seat / 2), (w - 2 * t, sd, seat))
    P.box(mos, (-w / 2 + t + sd / 2, (-d + t + sd + -0.9) / 2, seat / 2), (sd, (-0.9) - (-d + t + sd), seat))
    for yy in (-d + t + 0.08,):
        P.box(mos, (0, yy, seat + 0.25), (w - 2 * t, 0.16, 0.5), rx=math.radians(-10))  # raked back
    P.box(mos, (-w / 2 + t + 0.08, (-d + t + sd - 0.9) / 2, seat + 0.25), (0.16, (-0.9) - (-d + t + sd), 0.5), ry=math.radians(10))
    P.box(st, (w / 2 - 0.25, -d + t + 0.002, 0.25), (0.12, 0.006, 0.08))               # the steam outlet
    P.box(st, (0, -0.3, 0.021), (w - 0.2, 0.05, 0.004))                                 # linear drain
    # the front: clear glass in a blackened-steel frame, the door
    P.box(st, (0, 0.0, h + 0.05), (w, 0.05, 0.1)); P.box(st, (0, 0.0, 0.02), (w, 0.05, 0.04))
    for xp in (-w / 2 + 0.02, door - 0.42, door + 0.42, w / 2 - 0.02):
        P.box(st, (xp, 0.0, h / 2), (0.04, 0.05, h))
    for xa_, xb_ in ((-w / 2 + 0.04, door - 0.44), (door + 0.44, w / 2 - 0.04)):
        if xb_ - xa_ > 0.05:
            P.box(M["glass"], ((xa_ + xb_) / 2, 0.0, h / 2), (xb_ - xa_, 0.01, h - 0.08))
    P.box(M["glass"], (door, 0.02, 1.02), (0.8, 0.01, 2.0))
    P.rod(st, (door + 0.3, 0.06, 0.8), (door + 0.3, 0.06, 1.4), 0.012, seg=12)
    for z in (0.8, 1.4):
        P.rod(st, (door + 0.3, 0.025, z), (door + 0.3, 0.06, z), 0.008, seg=8)


def rinse_shower(P, n=1, pitch=1.1):
    """Open rinse showers on a wall (before the sauna, after the plunge): per head a 250 square blackened-steel rain head on an arm
    at 2.25, a thermostatic push valve, a flush slot drain; a hook for the robe. Origin = the wall at the run's centre, front +y."""
    st = M["steel"]
    for k in range(n):
        x = (k - (n - 1) / 2) * pitch
        P.box(st, (x, 0.012, 2.3), (0.06, 0.024, 0.06))
        P.box(st, (x, 0.2, 2.3), (0.03, 0.36, 0.02))
        P.box(st, (x, 0.38, 2.27), (0.25, 0.25, 0.012))
        P.box(st, (x, 0.012, 1.1), (0.12, 0.024, 0.16))
        P.rod(M["brass"], (x, 0.024, 1.1), (x, 0.04, 1.1), 0.02, seg=20)                  # the push valve
        P.box(st, (x, 0.36, 0.002), (0.6, 0.05, 0.004))
        P.rod(st, (x + 0.45, 0.01, 1.7), (x + 0.45, 0.08, 1.74), 0.008, seg=8)


def pool_lounger(P):
    """A pool lounger: two side frames of blackened-steel flat bar (a floor runner, end posts, a top rail the full length) joined by
    cross rails; oiled oak slats across the rails; the back a hinged steel frame with its own slats, raised to 40° and held by a
    U-shaped prop that drops into a notch on the rails; one 60 mm charcoal cushion following the deck and the back, a headrest
    pillow, a rolled towel lying on the foot. 2.0 x 0.72, the seat at 0.36. Origin = floor centre, foot +y."""
    st, oak = M["steel"], M["oak"]
    cush = M.setdefault("cushion_charcoal", bc.pbr_material("cushion_charcoal", "caban", 0.274, box=True, tint=(0.5, 0.52, 0.56), sat=0.2, val=0.2, piece_var=0.02))
    W, zr, ye = 0.72, 0.3, 0.88                       # width, top of the rails, half length of the frame
    xr = W / 2 - 0.02
    for sx in (-1, 1):                                                                  # the side frames
        x = sx * xr
        P.box(st, (x, 0.0, 0.008), (0.04, 2 * ye, 0.016))                              # floor runner
        for y in (-ye + 0.02, ye - 0.02):
            P.box(st, (x, y, zr / 2), (0.04, 0.04, zr))                                # end posts, runner to rail
        P.box(st, (x, 0.0, zr - 0.015), (0.04, 2 * ye, 0.03))                          # top rail
    for y in (-ye + 0.02, 0.0, ye - 0.02):                                             # cross rails, rail to rail
        P.box(st, (0, y, zr - 0.03), (2 * xr, 0.03, 0.03))
    y0 = -0.42                                                                          # the hinge; the flat deck from here to the foot
    y = y0 + 0.04
    while y < ye - 0.03:
        P.box(oak, (0, y, zr + 0.011), (W - 0.02, 0.06, 0.022)); y += 0.075
    zs = zr + 0.022                                                                     # top of the slats
    P.box(cush, (0, (y0 + ye) / 2, zs + 0.03), (W - 0.06, ye - y0 - 0.02, 0.06))
    a = math.radians(40); Lb = 0.72
    d_ = (-math.cos(a), math.sin(a)); n_ = (math.sin(a), math.cos(a))                # along the back (up, to the head) / its face
    at = lambda s_, o_: (y0 + d_[0] * s_ + n_[0] * o_, zs - 0.03 + d_[1] * s_ + n_[1] * o_)
    for sx in (-1, 1):                                                                  # the back's side bars, inside the rails
        cy, cz = at(Lb / 2, 0.0)
        P.box(st, (sx * (xr - 0.04), cy, cz), (0.03, Lb, 0.03), rx=-a)
    P.rod(st, (-xr, y0, zs - 0.03), (xr, y0, zs - 0.03), 0.012, seg=12)              # the hinge bar, through the back's bars into the rails
    s_ = 0.06
    while s_ < Lb - 0.03:                                                               # its slats
        cy, cz = at(s_, 0.026)
        P.box(oak, (0, cy, cz), (W - 0.1, 0.06, 0.022), rx=-a); s_ += 0.075
    cy, cz = at(Lb / 2, 0.067)
    P.box(cush, (0, cy, cz), (W - 0.06, Lb, 0.06), rx=-a)                             # the cushion up the back
    cy, cz = at(Lb - 0.16, 0.13)
    P.box(cush, (0, cy, cz), (W - 0.16, 0.22, 0.07), rx=-a)                           # headrest pillow
    py, pz = at(0.42, -0.015)                                                           # the prop: from the back's bars into the rails' notch
    for sx in (-1, 1):
        P.rod(st, (sx * (xr - 0.04), py, pz), (sx * (xr - 0.04), -ye + 0.1, zr), 0.009, seg=10)
    P.rod(st, (-(xr - 0.04), -ye + 0.1, zr), (xr - 0.04, -ye + 0.1, zr), 0.009, seg=10)
    towel = M.setdefault("towel_white", bc.material("towel_white", (0.85, 0.84, 0.8), 0.95))
    P.rod(towel, (-0.25, ye - 0.3, zs + 0.06 + 0.055), (0.25, ye - 0.3, zs + 0.06 + 0.055), 0.055, seg=24)


def towel_bin(P):
    """Used towels: an open oak frame holding a heavy natural linen bag, a brass ring on its rim. Origin = floor, front +y."""
    oak = M["oak"]; W, D, H = 0.5, 0.42, 0.85
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.box(oak, (sx * (W / 2 - 0.015), sy * (D / 2 - 0.015), H / 2), (0.03, 0.03, H))
    for z in (0.05, H - 0.02):
        for sy in (-1, 1):
            P.box(oak, (0, sy * (D / 2 - 0.015), z), (W, 0.03, 0.03))
        for sx in (-1, 1):
            P.box(oak, (sx * (W / 2 - 0.015), 0, z), (0.03, D, 0.03))
    bag = M.setdefault("robe_linen_bag", bc.pbr_material("robe_linen_bag", "rough_linen", 0.27, box=True, tint=(0.9, 0.85, 0.75), sat=0.35, val=0.22, piece_var=0.03))
    P.box(bag, (0, 0, H / 2 + 0.02), (W - 0.07, D - 0.07, H - 0.12))
    towel = M.setdefault("towel_white", bc.material("towel_white", (0.85, 0.84, 0.8), 0.95))
    P.blob(towel, (0.05, 0.0, H - 0.08), (0.16, 0.13, 0.07), seg=16)


def breath_mat(P, colour="oat"):
    """A breathwork place: a thick wool mat (0.7 x 1.9), a round bolster across it, a folded wool blanket and an eye pillow at the
    head. Origin = floor centre, the head -y."""
    P.box(M["felt_" + colour], (0, 0, 0.015), (0.7, 1.9, 0.03))
    P.rod(M["felt_fjord"], (-0.3, 0.35, 0.12), (0.3, 0.35, 0.12), 0.11, seg=28)
    P.box(M["boucle"], (0.0, -0.78, 0.06), (0.5, 0.3, 0.06))
    P.blob(M["felt_heather"], (0.0, -0.62, 0.045), (0.11, 0.05, 0.015), seg=16)


def _zprism(P, mat, pts_xy, z0, z1):
    """A plan outline (x-y) extruded from z0 to z1 (rounded plinths, cushions)."""
    b = P.bm(mat)
    v0 = [b.verts.new((x, y, z0)) for x, y in pts_xy]; v1 = [b.verts.new((x, y, z1)) for x, y in pts_xy]
    b.faces.new(v0[::-1]); b.faces.new(v1)
    n = len(pts_xy)
    for i in range(n):
        j = (i + 1) % n
        b.faces.new((v0[i], v0[j], v1[j], v1[i]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces[-(n + 2):])


def _stadium(x0, x1, y0, y1, seg=16):
    """A plan outline square at y0, a full half-round at y1 (a daybed's foot)."""
    r = (x1 - x0) / 2; cx = (x0 + x1) / 2; yc = y1 - r
    pts = [(x0, y0), (x1, y0)]
    pts += [(cx + r * math.cos(a), yc + r * math.sin(a)) for a in np.linspace(0, math.pi, seg)]
    return pts


def _velvet():
    """Charcoal velvet (Remedy Place's lounge beds + curtains): the scanned velour, a soft sheen on the pile."""
    m = M.get("velvet_charcoal") or bc.interior_materials()["velvet_charcoal"]
    b = m.node_tree.nodes["Principled BSDF"]
    for k, v in (("Sheen Weight", 0.35), ("Sheen Roughness", 0.4), ("Sheen Tint", (0.3, 0.3, 0.32, 1.0))):
        if k in b.inputs:
            b.inputs[k].default_value = v
    M["velvet_charcoal"] = m
    return m


def _foliage():
    return M.setdefault("leaf_green", bc.material("leaf_green", (0.035, 0.075, 0.03), 0.45))


def plant_pot(P, species="sansevieria", h=0.9, r=0.22):
    """Greenery (Remedy Place: planted everywhere; under grow light here): a honed near-black stone pot, and either a
    sansevieria (stiff upright blades) or a strelitzia (tall stems, big paddle leaves). Origin = floor centre."""
    pot = M.get("stone_nero_honed") or bc.interior_materials()["stone_nero_honed"]
    ph = min(0.55, 0.3 * h) if species == "strelitzia" else min(0.45, 0.5 * h)
    P.cyl(pot, (0, 0, 0), r, ph, seg=48, r2=r * 0.92)
    P.cyl(M["sand"] if "sand" in M else M["felt"], (0, 0, ph - 0.03), r * 0.88, 0.02, seg=40)
    rng = np.random.default_rng(int(h * 100 + r * 1000))
    lf = _foliage()
    if species == "sansevieria":
        for k in range(14):
            a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0, r * 0.6); L = rng.uniform(0.5, 1.0) * (h - ph)
            tilt = rng.uniform(0.02, 0.18)
            x, y = rr * math.cos(a), rr * math.sin(a)
            P.box(lf, (x + math.cos(a) * tilt * L / 2, y + math.sin(a) * tilt * L / 2, ph + L / 2), (0.05, 0.008, L), rz=rng.uniform(0, math.pi),
                  rx=-math.sin(a) * tilt, ry=math.cos(a) * tilt)
    else:  # strelitzia (bird of paradise): tall bare stems, each with one big paddle leaf, split a little at the edges
        for k in range(15):
            a = 2 * math.pi * k / 15 + rng.uniform(-0.25, 0.25); tilt = rng.uniform(0.08, 0.3); L = rng.uniform(0.5, 1.0) * (h - ph)
            top = (math.cos(a) * tilt * L, math.sin(a) * tilt * L, ph + L * 0.7)
            P.rod(lf, (math.cos(a) * 0.04, math.sin(a) * 0.04, ph), top, 0.012, 0.008, seg=8)
            lw, ll = rng.uniform(0.075, 0.1), rng.uniform(0.55, 0.8)
            up = Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 1.0)).normalized()             # the paddle leans out with its stem
            side = Vector((-math.sin(a), math.cos(a), 0.0)); nrm = side.cross(up).normalized()
            b = P.bm(lf); base = Vector(top); ring = []
            for t in np.linspace(0, 2 * math.pi, 25)[:-1]:                                   # an elliptical blade, cupped a little
                u_, w_ = lw * math.sin(t), ll / 2 * (1 - math.cos(t))
                ring.append(base + side * u_ + up * w_ + nrm * (0.04 * (u_ / lw) ** 2))
            vf = [b.verts.new(q + nrm * 0.003) for q in ring]; vb = [b.verts.new(q - nrm * 0.003) for q in ring]
            b.faces.new(vf); b.faces.new(vb[::-1])
            for m_ in range(len(ring)):
                n_ = (m_ + 1) % len(ring); b.faces.new((vf[m_], vb[m_], vb[n_], vf[n_]))

def eclipse_sconce(P, d=0.36, mount=1.6):
    """A round wall light (after Remedy Place's): a honed plaster disc standing off the wall, a smaller dark disc in front of it,
    warm light washing out from behind both, a halo on the wall. Origin = the wall at its centre on the floor, front +y; z = mount
    (1.6; 2.8 over a mirror, in the oak band above the glass)."""
    z = mount
    b = P.bm(M["steel"]); g = bmesh.ops.create_cone(b, cap_ends=True, segments=48, radius1=0.05, radius2=0.05, depth=0.03)["verts"]
    bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X")); bmesh.ops.translate(b, verts=g, vec=(0, 0.015, z))
    for mat, r, y, t in ((_led("eclipse_glow", (1.0, 0.76, 0.5), 5.0), d / 2 - 0.01, 0.034, 0.006), (M.get("plaster_venetian") or bc.interior_materials()["plaster_venetian"], d / 2, 0.045, 0.012),
                         (M["steel"], d * 0.3, 0.06, 0.012)):
        b = P.bm(mat); g = bmesh.ops.create_cone(b, cap_ends=True, segments=48, radius1=r, radius2=r, depth=t)["verts"]
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X")); bmesh.ops.translate(b, verts=g, vec=(0, y, z))


def _loft(P, mat, rings, cap=True):
    """A skin through rings of points (each ring the same count, in order): sleeves, hoses, anything round that changes size."""
    b = P.bm(mat); vs = [[b.verts.new(q) for q in r] for r in rings]; n = len(rings[0])
    for r0, r1 in zip(vs, vs[1:]):
        for i in range(n):
            j = (i + 1) % n
            b.faces.new((r0[i], r0[j], r1[j], r1[i]))
    if cap:
        b.faces.new(vs[0][::-1]); b.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(b, faces=list({f for r in vs for v in r for f in v.link_faces}))


def _air_boot(P, x, y_hip, y_heel, z_bed, pump=None):
    """One air-compression boot (Normatec-style) lying on its back: a full-leg sleeve of five overlapping air chambers (each
    pillowed, a crease between), flattened where it lies, tapering from the thigh to the ankle; a boot-shaped foot standing up at
    the end; a zip along the inner side; a grey cuff at the top and the hose from its port to the pump. Matte graphite nylon."""
    fab = M.setdefault("boot_nylon", bc.material("boot_nylon", (0.03, 0.032, 0.036), 0.5))
    cuff = M.setdefault("boot_cuff", bc.material("boot_cuff", (0.16, 0.165, 0.17), 0.7))
    zipm = M.setdefault("boot_zip", bc.material("boot_zip", (0.008, 0.008, 0.009), 0.3))
    N, K = 36, 70; inner = -1 if x > 0 else 1
    rings, zips = [], []
    for k in range(K + 1):
        t = k / K; y = y_hip + (y_heel - y_hip) * t
        rx = 0.1 - 0.042 * t ** 1.3                                                    # thigh to ankle
        f = (t * 5) % 1.0; m = 0.93 + 0.08 * math.sin(math.pi * f) ** 0.6              # pillowed chambers, a crease between
        rx *= m; rz = rx * 0.72
        zc = z_bed + rz
        rings.append([(x + rx * math.cos(u), y, zc + rz * math.sin(u)) for u in np.linspace(0, 2 * math.pi, N + 1)[:-1]])
        u = math.radians(55); zips.append((x + inner * rx * 1.005 * math.cos(u), y, zc + rz * 1.005 * math.sin(u)))
    _loft(P, fab, rings)
    for p0, p1 in zip(zips, zips[1:]):
        P.rod(zipm, p0, p1, 0.0045, seg=6)
    r0 = rings[0]; zc0 = sum(q[2] for q in r0) / N
    _loft(P, cuff, [[(q[0] + (q[0] - x) * 0.04, y_hip - 0.002 + dy, zc0 + (q[2] - zc0) * 1.04) for q in r0] for dy in (0.0, 0.035)])
    # the foot (a lying leg's foot points up): a boot shape standing on the bed, heel overlapping the sleeve's end, a sole
    # rounded at the bottom, the toe box domed over the top
    foot, H = [], 0.27
    for i in range(19):
        f = i / 18; zc_ = z_bed + 0.004 + H * f
        sc = (0.9 + 0.1 * math.sin(f / 0.12 * math.pi / 2)) if f < 0.12 else (math.sqrt(max(0.0, 1 - ((f - 0.72) / 0.28) ** 2)) if f > 0.72 else 1.0)
        crease = 1.0 - 0.07 * math.exp(-((f - 0.45) / 0.04) ** 2)                      # the foot's own air chamber seam
        rxf, ryf = 0.07 * sc * crease * (1 - 0.2 * f), (0.118 - 0.03 * f) * sc * crease
        cy_ = y_heel + 0.06 + 0.06 * f ** 1.5                                             # the toes lean towards the foot of the bed
        foot.append([(x + max(rxf, 0.004) * math.cos(u), cy_ + max(ryf, 0.004) * math.sin(u), zc_) for u in np.linspace(0, 2 * math.pi, N + 1)[:-1]])
    _loft(P, fab, foot)
    port = (x, y_hip + 0.08, zc0 + 0.07)
    P.cyl(cuff, (port[0], port[1], port[2] - 0.005), 0.016, 0.02, seg=16)
    if pump:                                                                            # the hose: a soft curve up and over to the pump
        h0 = (port[0], port[1], port[2] + 0.015); h3 = pump
        h1 = (h0[0], h0[1] - 0.15, h0[2] + 0.12); h2 = (h3[0], h3[1] + 0.2, h3[2] + 0.25)
        pts = []
        for i in range(17):
            t = i / 16
            pts.append(tuple((1 - t) ** 3 * h0[c] + 3 * (1 - t) ** 2 * t * h1[c] + 3 * (1 - t) * t ** 2 * h2[c] + t ** 3 * h3[c] for c in range(3)))
        for p0, p1 in zip(pts, pts[1:]):
            P.rod(cuff, p0, p1, 0.007, seg=8)


def recovery_bay(P, w=2.4, d=2.5, ceiling=5.2, end=False):
    """One recovery bay (the recovery lounge, after Remedy Place LA's lounge beds; Roman 2026-10-17: look up real references):
    a charcoal velvet daybed, channel-tufted back, the foot a full half-round, on a recessed black plinth with a warm glow
    under it; floor-to-ceiling charcoal velvet curtains on a ceiling track between the bays; a slim articulated reading light on
    the wall; an opal glass globe hanging low on a long cord; a thin blackened-steel side table with a glass of water and a
    small plant; the air-compression boots laid on the bed, their pump on the table's shelf. Origin = the wall at the bay's
    centre on the floor, front +y (out into the room)."""
    st, vel = M["steel"], _velvet()
    # the daybed
    x0, x1, y0, y1 = -0.46, 0.46, 0.1, 2.15
    _zprism(P, M["felt"], _stadium(x0 + 0.06, x1 - 0.06, y0 + 0.06, y1 - 0.06), 0.0, 0.12)                # the recessed plinth
    P.box(_led("bay_plinth_glow", (1.0, 0.72, 0.45), 3.0), (0, (y0 + y1) / 2 - 0.2, 0.004), (0.7, 1.4, 0.004))
    _zprism(P, vel, _stadium(x0, x1, y0, y1), 0.12, 0.36)                                                   # the base
    _zprism(P, vel, _stadium(x0 + 0.015, x1 - 0.015, y0 + 0.015, y1 - 0.015), 0.36, 0.44)                  # the seat cushion
    for k in range(5):                                                                                       # channel-tufted back, raked:
        z = 0.5 + k * 0.088; yy = y0 + 0.1 + k * 0.03                                                        # flat pillowed channels,
        rings = []                                                                                           # rounded off at the ends
        for xx in np.linspace(x0 + 0.03, x1 - 0.03, 24):
            dd = min(1.0, min(xx - x0 - 0.03, x1 - 0.03 - xx) / 0.035)
            e = max(0.6, math.sqrt(max(0.0, 1 - (1 - dd) ** 2)))                                          # a round end, not a point
            rings.append([(xx, yy + 0.034 * e * math.cos(u), z + 0.046 * e * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 25)[:-1]])
        _loft(P, vel, rings)
    P.rod(vel, (-0.28, y0 + 0.36, 0.5), (0.28, y0 + 0.36, 0.5), 0.07, seg=24)                               # a bolster
    # the boots, laid side by side on the bed, the hoses to the pump on the table's shelf
    for sx in (-0.12, 0.12):
        _air_boot(P, sx, 0.72, 1.62, 0.44, pump=(0.72, 0.42 + (0.03 if sx > 0 else -0.03), 0.28))
    # the side table, its glass, a plant, the pump below
    tx, ty = 0.82, 0.42
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.box(st, (tx + sx * 0.16, ty + sy * 0.16, 0.29), (0.014, 0.014, 0.58))
    P.box(M.get("stone_nero_honed") or bc.interior_materials()["stone_nero_honed"], (tx, ty, 0.585), (0.36, 0.36, 0.02))
    P.box(st, (tx, ty, 0.18), (0.34, 0.34, 0.012))
    shell = M.setdefault("pump_shell", bc.material("pump_shell", (0.05, 0.052, 0.056), 0.35))
    P.box(shell, (tx, ty, 0.25), (0.2, 0.28, 0.13))                                       # the pump: a rounded graphite unit,
    P.box(_led("boot_screen", (0.6, 0.85, 1.0), 2.0), (tx + 0.02, ty, 0.3155), (0.09, 0.14, 0.002))  # its screen on top,
    for dy in (-0.03, 0.03):
        P.rod(M.setdefault("boot_cuff", bc.material("boot_cuff", (0.16, 0.165, 0.17), 0.7)), (tx - 0.1, ty + dy, 0.28), (tx - 0.12, ty + dy, 0.28), 0.012, seg=12)  # two ports
    P.cyl(M["glass"], (tx - 0.08, ty - 0.06, 0.595), 0.035, 0.12, seg=24)                                  # a glass of water
    P.cyl(M.setdefault("water_bath", bc.arch_glass("water_bath", tint=(0.8, 0.9, 0.86))), (tx - 0.08, ty - 0.06, 0.6), 0.03, 0.08, seg=24)
    pot = M.get("stone_nero_honed") or bc.interior_materials()["stone_nero_honed"]
    P.cyl(pot, (tx + 0.07, ty + 0.06, 0.595), 0.06, 0.1, seg=24)
    rng = np.random.default_rng(int(w * 10))
    for k in range(7):                                                                                       # a small sansevieria
        a = rng.uniform(0, 2 * math.pi); L = rng.uniform(0.15, 0.3)
        P.box(_foliage(), (tx + 0.07 + 0.02 * math.cos(a), ty + 0.06 + 0.02 * math.sin(a), 0.695 + L / 2), (0.025, 0.005, L), rz=a)
    # the reading light: a wall plate, a slim arm, a linear head angled down at the pillow
    lx = 0.62
    P.box(st, (lx, 0.01, 1.15), (0.05, 0.02, 0.09))
    P.rod(st, (lx, 0.02, 1.15), (lx - 0.05, 0.3, 1.32), 0.007, seg=8)
    P.rod(st, (lx - 0.05, 0.3, 1.32), (lx - 0.32, 0.36, 1.26), 0.009, seg=10)
    P.rod(_led("reading_line", (1.0, 0.78, 0.55), 8.0), (lx - 0.06, 0.315, 1.312), (lx - 0.3, 0.37, 1.252), 0.005, seg=8)
    # the globe pendant
    gz = 1.5
    P.rod(st, (tx, ty + 0.05, ceiling), (tx, ty + 0.05, gz + 0.14), 0.003, seg=6)
    P.cyl(st, (tx, ty + 0.05, gz + 0.12), 0.025, 0.03, seg=16)
    P.blob(M.setdefault("opal_globe", _opal("opal_globe", 4.0)), (tx, ty + 0.05, gz), (0.13, 0.13, 0.13), seg=32)
    # curtains between the bays: pleated velvet floor to track, the track on the soffit
    for cx_ in ((-w / 2, w / 2) if end else (-w / 2,)):
        P.box(st, (cx_, d / 2, ceiling - 0.02), (0.03, d, 0.03))
        yy = 0.04
        while yy < d - 0.02:                                                                                 # soft folds: a wave of round pleats
            P.rod(vel, (cx_ + 0.03 * math.sin(yy * 2 * math.pi / 0.16), yy, 0.015), (cx_ + 0.03 * math.sin(yy * 2 * math.pi / 0.16), yy, ceiling - 0.04), 0.03, seg=12)
            yy += 0.04


# ------------------------------------------------------------------ the gym floors' WCs (Roman 2026-10-18: darker, more efficient, still really
# clean and private; men's and women's fully separate; consistent on F2-F4; the pool floor's made for wet bare feet; a robot in each)
def _placed(P, fn, x, y, rz=0.0):
    """Build fn(tmp) in its own frame (wall at y=0, front +y), turn it rz about z and move it to (x, y) inside P."""
    tmp = Part("tmp"); fn(tmp)
    c, s = math.cos(rz), math.sin(rz)
    for mat, b in tmp.bms.items():
        for v in b.verts:
            v.co = Vector((x + v.co.x * c - v.co.y * s, y + v.co.x * s + v.co.y * c, v.co.z))
        tgt = P.bm(mat)
        me = bpy.data.meshes.new("tmp"); b.to_mesh(me); b.free(); tgt.from_mesh(me); bpy.data.meshes.remove(me)


def gym_wc(P, men=True, pool=False, hand=1, Wn=2.635, W=4.785, ub=2.9, L=8.6, H=2.7):
    """One of the gym floors' WC rooms in the rock annex (F2, F3, F4; men's + women's mirror-image either side of the concrete spine).
    The dark version of the house WC language: black glazed tile to the ceiling (interior.py), fluted fumed-oak cell fronts, blackened
    steel, white china (it reads clean and contrasts for low vision), a honed black stone trough. A T in plan (Roman: more spacious,
    doors that don't hit people walking past, the cells integrated flush, not boxes added after the fact):
      - the neck between the stair towers (Wn wide): the door from the gym, the wash zone (a floating black stone trough with two taps
        under a backlit mirror, towels + bin in the wall), a phone/bottle shelf, Vaskebjørn's dock in the corner behind the door
      - the body behind the towers (W wide): ONE run of cells along the outer wall from the step to the back wall, its fluted front in
        the plane of the neck's wall (it reads as the wall), the doors opening out into a 2.6 m aisle. Women: 3 cells + the accessible
        WC; men: the cleaner's cupboard, 2 cells + the accessible WC, and 4 splash-free urinals on the spine wall behind oak screens;
        the women's spine wall a grooming shelf under a long mirror
    pool=True (F4: wet bare feet; slips are the danger): a grab rail along the spine, a linear drain under it, a drained foot grate
    inside the door, robe hooks in every cell (the slip-resistant mosaic floor is in interior.py).
    Origin = the finished corner of the gym wall and the spine; local +y runs away from the gym (u), +x from the spine outwards (v);
    hand -1 mirrors it (the women's room). Lights are their own furnishings (tools/furnish.py, 'the gym WCs')."""
    oak0 = M["oak"]
    sm = M.setdefault("oak_smoked_dark", bc.pbr_material("oak_smoked_dark", "black_oak_veneer", 1.5, box=True, tint=(1.0, 0.92, 0.85), sat=0.7, val=0.38,
                                                         rough_mul=0.8, rough_add=0.08, piece_var=0.06))       # fumed oak, as the recovery floor
    nero = M.get("stone_nero_honed") or bc.interior_materials()["stone_nero_honed"]
    st, fe = M["steel"], M["felt"]
    paper = M.setdefault("paper_white", bc.material("paper_white", (0.86, 0.85, 0.82), 0.8))
    halo = _led("wc_halo", (1.0, 0.78, 0.55), 3.0)
    M.setdefault("led_free", bc.material("led_free", (0.02, 0.45, 0.1), 0.3, emit=((0.05, 1.0, 0.2), 0.5)))
    M.setdefault("led_busy", bc.material("led_busy", (0.6, 0.02, 0.01), 0.3, emit=((1.0, 0.05, 0.02), 0.5)))
    D = W - Wn                                                # the cells' depth: their front is the neck wall's plane
    vf = Wn + 0.02                                            # the 40 mm front's centre line
    M["oak"] = sm                                              # the shared WC helpers (door leaves) take the fumed oak here
    try:
        # ---- the neck: the wash zone. A wall-hung vanity 2.0 m long: a 120 mm honed black stone top with a trough carved into it
        # (sloped to a slot drain at the back), two slim wall spouts with the soap beside each, a fluted fumed-oak cabinet under it
        # floating 250 mm off the floor (a glow under it), a waste slot in the top at the far end under the towel dispenser set flush
        # in the tile, a long mirror in a fumed-oak frame with a halo over it. No freestanding bins.
        u0, u1, dv, top = 0.3, 2.3, 0.52, 0.86
        vb = Wn - dv                                                                               # the vanity's front edge
        t0, t1 = 0.45, 1.75                                                                        # the trough
        for (a_, b_) in ((u0, t0), (t1, u1)):                                                      # the solid top either side of it
            P.box(nero, (Wn - dv / 2, (a_ + b_) / 2, top - 0.06), (dv, b_ - a_, 0.12))
        P.box(nero, (vb + 0.04, (t0 + t1) / 2, top - 0.06), (0.08, t1 - t0, 0.12))                # front lip
        P.box(nero, (Wn - 0.05, (t0 + t1) / 2, top - 0.06), (0.1, t1 - t0, 0.12))                 # back strip (the drain slot in front of it)
        P.box(nero, ((vb + 0.08 + Wn - 0.1) / 2, (t0 + t1) / 2, top - 0.105), (Wn - 0.1 - vb - 0.08, t1 - t0, 0.03), rx=0.0, ry=math.radians(-6))  # sloped floor
        P.box(st, (Wn - 0.115, (t0 + t1) / 2, top - 0.11), (0.025, t1 - t0 - 0.06, 0.004))         # slot drain
        P.box(sm, (Wn - dv / 2 - 0.01, (u0 + u1) / 2, 0.52), (dv - 0.04, u1 - u0, 0.56))           # the cabinet under it
        for yg in np.arange(u0 + 0.015, u1, 0.03):
            P.box(fe, (vb + 0.019, yg, 0.52), (0.002, 0.003, 0.54))
        P.box(halo, (vb + 0.1, (u0 + u1) / 2, 0.235), (0.02, u1 - u0 - 0.1, 0.006))                # glow under it
        for yb in ((t0 + t1) / 2 - 0.33, (t0 + t1) / 2 + 0.33):
            P.box(st, (Wn - 0.004, yb, 1.05), (0.008, 0.06, 0.06))                                # rose
            P.rod(st, (Wn, yb, 1.05), (Wn - 0.2, yb, 1.05), 0.009, seg=12)                         # spout (sensor in its tip)
            P.box(st, (Wn - 0.004, yb + 0.16, 1.05), (0.008, 0.045, 0.045))
            P.rod(st, (Wn, yb + 0.16, 1.05), (Wn - 0.12, yb + 0.16, 1.05), 0.007, seg=10)          # soap spout
        P.box(st, (Wn - dv / 2, 2.1, top + 0.001), (dv - 0.16, 0.18, 0.003))                      # waste slot: a steel flap in the top
        P.box(fe, (Wn - dv / 2, 2.1, top + 0.003), (dv - 0.2, 0.012, 0.001))
        P.box(st, (Wn - 0.003, 2.1, 1.35), (0.006, 0.28, 0.4))                                     # towel dispenser, flush in the tile
        P.box(fe, (Wn - 0.007, 2.1, 1.17), (0.002, 0.2, 0.012))
        P.box(sm, (Wn - 0.012, (u0 + 1.85) / 2 + 0.0, 1.6), (0.024, 1.55, 0.96))                    # the mirror in its frame
        P.box(M["mirror"], (Wn - 0.026, (u0 + 1.85) / 2, 1.6), (0.004, 1.49, 0.9))
        P.box(halo, (Wn - 0.03, (u0 + 1.85) / 2, 2.095), (0.012, 1.5, 0.01))
        if pool:
            P.box(sm, (0.02, 1.4, 1.7), (0.04, 1.2, 0.1))
            for yh in np.arange(0.9, 1.95, 0.25):
                P.rod(st, (0.04, yh, 1.7), (0.12, yh, 1.74), 0.009, seg=8)
        else:
            P.box(sm, (0.13, 1.4, 1.1), (0.26, 1.0, 0.03))
            for ys in (1.0, 1.8):
                P.box(st, (0.05, ys, 1.06), (0.1, 0.03, 0.06))
            for yh in (1.05, 1.75):
                P.rod(st, (0.0, yh, 1.6), (0.09, yh, 1.63), 0.009, seg=8)
        _placed(P, lambda T: robot_dock(T), 0.4, 0.0, 0.0)
        _placed(P, lambda T: vaskebjorn(T, ring="lingon"), 0.4, 0.27, 0.0)
        P.box(st, (1.305, -0.255, 2.31), (1.04, 0.53, 0.02))                                       # the doorway's reveal, lined in steel
        for sx in (0.795, 1.815):
            P.box(st, (sx, -0.255, 1.155), (0.02, 0.53, 2.31))
        P.box(st, (1.305, -0.255, 0.003), (1.02, 0.53, 0.006))                                     # a steel threshold, level
        P.box(st, (1.305, 0.004, 2.33), (1.08, 0.008, 0.04))                                       # + a slim frame on the tile
        for sx in (0.785, 1.825):
            P.box(st, (sx, 0.004, 1.165), (0.04, 0.008, 2.33))
        P.box(st, (1.75, 0.01, 1.05), (0.022, 0.02, 0.36))
        # ---- the body: one run of cells, wall to wall, along the outer wall
        cells = ([("store", 1.134), ("wc", 1.133), ("wc", 1.133)] if men else [("wc", 1.133), ("wc", 1.133), ("wc", 1.134)]) + [("acc", L - ub - 3.4)]
        bounds, u = [], ub
        for kind, w in cells:
            bounds.append((kind, u, u + w)); u += w
        doors = []
        for i, (kind, a, b) in enumerate(bounds):
            dw = 1.0 if kind == "acc" else 0.8
            da = a + 0.12 if kind == "acc" else (a + b) / 2 - dw / 2
            doors.append((da, da + dw))
            if i:                                                                                  # the panel between two cells
                P.box(sm, ((vf + 0.02 + W) / 2, a, H / 2), (W - vf - 0.02, 0.03, H))
        cuts = [ub] + [v for d in doors for v in (d[0] - 0.003, d[1] + 0.003)] + [L]
        for k in range(0, len(cuts), 2):                                                           # the front between the doors: fluted
            u0, u1 = cuts[k], cuts[k + 1]
            P.box(sm, (vf, (u0 + u1) / 2, H / 2), (0.04, u1 - u0, H))
            for yg in np.arange(u0 + 0.015, u1 - 0.005, 0.03):
                P.box(fe, (vf - 0.0205, yg, H / 2), (0.002, 0.003, H - 0.02))
        for i, ((da, db), (kind, a, b)) in enumerate(zip(doors, bounds)):
            P.box(sm, (vf, (da + db) / 2, (2.1 + H) / 2 + 0.0015), (0.04, db - da + 0.006, H - 2.103))  # transom over the door
            for yg in np.arange(da + 0.015, db, 0.03):
                P.box(fe, (vf - 0.0205, yg, (2.1 + H) / 2 + 0.0015), (0.002, 0.003, H - 2.123))
            P.box(fe, (vf, (da + db) / 2, 2.1015), (0.042, db - da + 0.006, 0.003))
            for yl in (da - 0.004, db + 0.004):
                P.box(sm, (vf, yl, 1.05), (0.042, 0.005, 2.1))
            busy = (kind == "wc" and i == len(bounds) - 2)
            _placed(P, lambda T, w_=db - da, b_=busy: _leaf(T, (0.0, 0.0), w_, 2.1, 0.0, occupied=b_), vf, da, math.pi / 2)  # opens out
            if kind != "store":
                P.box(st, (vf - 0.025, (da + db) / 2, 2.4), (0.006, 0.16, 0.16))                    # the cell's plate + occupancy dot
                P.box(M["led_busy"] if busy else M["led_free"], (vf - 0.03, (da + db) / 2, 2.4), (0.004, 0.025, 0.025))
            if kind == "acc":
                for k_, fig in enumerate(("accessible", "baby")):
                    _placed(P, lambda T, f_=fig: pictogram_on(T, f_, 0.0, 0.0, 2.4, 0.16, plate=True), vf - 0.021, db + 0.15 + k_ * 0.21, math.pi / 2)
            w = b - a
            def wc_kit(T, w=w):
                _wc_pan(T, 0.0)
                T.rod(paper, (0.39, 0.12, 0.75), (0.5, 0.12, 0.75), 0.055, seg=20)
                _brush(T, (-0.36, 0.1)); _pedal_bin(T, (-w / 2 + 0.17, 0.16), h=0.3, r=0.09, lid=sm)
                T.box(st, (0.0, 0.004, 1.42), (0.12, 0.008, 0.08))
                T.box(sm, (w / 2 - 0.105, 0.75, 1.05), (0.15, 0.3, 0.02)); T.box(paper, (w / 2 - 0.105, 0.68, 1.1), (0.11, 0.11, 0.1))
                for k in range(2 if pool else 1):
                    T.rod(st, (-w / 2 + 0.12 + k * 0.12, D - 0.04, 1.7), (-w / 2 + 0.12 + k * 0.12, D - 0.11, 1.73), 0.009, seg=8)
                T.cyl(st, (0.0, 1.0, H - 0.012), 0.06, 0.012, seg=24); T.cyl(M["opal"], (0.0, 1.0, H - 0.014), 0.05, 0.003, seg=24)
            def store_kit(T, w=w):
                T.box(M["brushed"], (-w / 2 + 0.35, 0.22, 0.3), (0.5, 0.4, 0.3)); T.rod(st, (-w / 2 + 0.35, 0.0, 0.85), (-w / 2 + 0.35, 0.18, 0.85), 0.012, seg=10)
                for z in (1.2, 1.55, 1.9):
                    T.box(sm, (0.0, 0.15, z), (w - 0.06, 0.28, 0.02))
                    for k in range(5):
                        T.cyl(st, (-w / 2 + 0.2 + k * 0.17, 0.15, z + 0.01), 0.035, 0.2, seg=12)                    # bottles
                for k in range(3):
                    T.rod(sm, (w / 2 - 0.2 - k * 0.1, 0.06, 0.05), (w / 2 - 0.2 - k * 0.1, 0.06, 1.4), 0.012, seg=8)
                T.box(st, (0.0, 1.3, 0.45), (0.5, 0.8, 0.9))                                         # the cleaning cart
                T.cyl(st, (0.0, 1.0, H - 0.012), 0.06, 0.012, seg=24); T.cyl(M["opal"], (0.0, 1.0, H - 0.014), 0.05, 0.003, seg=24)
            def acc_kit(T, w=w):  # the accessible WC: the pan by the back wall, the basin on the far side panel, 1.5 m to turn
                px = w / 2 - 0.5
                _wc_pan(T, px)
                T.rod(paper, (px - 0.5, 0.12, 0.75), (px - 0.39, 0.12, 0.75), 0.055, seg=20)
                T.rod(st, (w / 2 - 0.035, 0.25, 0.8), (w / 2 - 0.035, 1.0, 0.8), 0.017, seg=12); T.rod(st, (w / 2 - 0.035, 0.25, 0.8), (w / 2 - 0.035, 0.25, 1.5), 0.017, seg=12)
                T.box(st, (px - 0.35, 0.03, 0.8), (0.07, 0.06, 0.16)); T.rod(st, (px - 0.35, 0.05, 0.8), (px - 0.35, 0.85, 0.8), 0.017, seg=12)
                _brush(T, (w / 2 - 0.15, 0.12)); _pedal_bin(T, (px - 0.6, 0.15), h=0.3, r=0.09, lid=sm)
                T.box(M["ceramic"], (w / 2 - 0.04, 1.2, 2.3), (0.08, 0.03, 0.08))                  # the alarm pull: cord + two red bangles
                T.rod(M["lino_lingon"], (w / 2 - 0.06, 1.2, 2.26), (w / 2 - 0.06, 1.2, 0.1), 0.0025, seg=6)
                for z in (0.1, 0.9):
                    T.cyl(M["lino_lingon"], (w / 2 - 0.06, 1.2, z - 0.02), 0.025, 0.04, seg=16)
                _placed(T, lambda Q: _accessible_basin(Q, 0.0), -w / 2, 1.25, -math.pi / 2)        # basin on the side panel, knee space
                T.box(sm, (-w / 2 + 0.012, 1.25, 1.45), (0.024, 0.54, 0.84)); T.box(M["mirror"], (-w / 2 + 0.026, 1.25, 1.45), (0.004, 0.5, 0.8))
                T.box(halo, (-w / 2 + 0.03, 1.25, 1.885), (0.01, 0.5, 0.01))
                T.box(st, (-w / 2 + 0.05, 1.57, 1.05), (0.1, 0.09, 0.18))
                T.box(sm, (-w / 2 + 0.03, 0.55, 1.25), (0.06, 0.36, 0.42)); T.box(st, (-w / 2 + 0.065, 0.55, 1.25), (0.012, 0.3, 0.36))
                _pedal_bin(T, (-w / 2 + 0.2, 0.3), h=0.42, r=0.12, lid=sm)
                T.box(sm, (-0.35, 0.06, 0.95), (0.8, 0.11, 0.55))                                   # fold-down changing table (folded)
                T.box(M["ceramic"], (0.2, D - 0.03, 1.0), (0.08, 0.02, 0.08)); T.box(M["lino_lingon"], (0.2, D - 0.044, 1.0), (0.04, 0.008, 0.04))  # alarm reset
                T.rod(st, (0.6, D - 0.02, 1.7), (0.6, D - 0.1, 1.72), 0.01, seg=8)
                _placed(T, lambda Q: floor_drain(Q), -0.2, 1.1, 0.0)
                for xs, ys in ((-0.3, 1.2), (0.55, 1.45)):
                    T.cyl(st, (xs, ys, H - 0.012), 0.06, 0.012, seg=24); T.cyl(M["opal"], (xs, ys, H - 0.014), 0.05, 0.003, seg=24)
            _placed(P, {"wc": wc_kit, "store": store_kit, "acc": acc_kit}[kind], W, (a + b) / 2, math.pi / 2)
        # ---- the spine wall in the body
        if men:  # four splash-free urinals (one lower), a fumed oak screen both sides of each, a grazing light over them
            yu = [3.6, 4.4, 5.2, 6.0]
            for k, y_ in enumerate(yu):
                _placed(P, lambda T, k=k: _nautilus(T, 0.0, rim=0.5 if k == 0 else 0.62), 0.0, y_, -math.pi / 2)
            for y_ in (3.2, 4.0, 4.8, 5.6, 6.4):                                                  # a screen both sides of every urinal
                P.box(sm, (0.27, y_, 1.0), (0.5, 0.025, 1.2))
                for z in (0.55, 1.45):
                    P.box(st, (0.02, y_, z), (0.04, 0.04, 0.04))
            P.box(st, (0.14, 4.8, H - 0.012), (0.08, 2.9, 0.024)); P.box(M["opal"], (0.14, 4.8, H - 0.025), (0.05, 2.86, 0.003))
        elif not pool:  # a grooming shelf under a long backlit mirror (hair, make-up, a bag down)
            P.box(sm, (0.011, 4.6, 1.6), (0.022, 2.4, 1.0)); P.box(M["mirror"], (0.025, 4.6, 1.6), (0.006, 2.34, 0.94))
            P.box(halo, (0.02, 4.6, 2.105), (0.01, 2.36, 0.012))
            P.box(sm, (0.14, 4.6, 0.95), (0.28, 2.4, 0.03))
            for ys in (3.6, 4.6, 5.6):
                P.box(st, (0.05, ys, 0.91), (0.1, 0.03, 0.06))
        if pool:  # a grab rail along the spine (round the urinals), a linear drain under it, the foot grate at the door
            spans = [(0.35, 3.15), (6.45, L - 0.15)] if men else [(0.35, L - 0.15)]
            for r0, r1 in spans:
                P.rod(st, (0.065, r0, 0.9), (0.065, r1, 0.9), 0.02, seg=14)
                for yr in np.arange(r0 + 0.15, r1, 0.9):
                    P.rod(st, (0.0, yr, 0.9), (0.065, yr, 0.9), 0.009, seg=8)
            if not men:
                P.box(sm, (0.02, 5.0, 1.7), (0.04, 2.4, 0.1))
                for yh in np.arange(3.95, 6.1, 0.3):
                    P.rod(st, (0.04, yh, 1.7), (0.12, yh, 1.74), 0.009, seg=8)
            P.box(st, (0.16, (0.7 + L - 0.2) / 2, 0.001), (0.07, L - 0.9, 0.002))
            for yg in np.arange(0.75, L - 0.23, 0.025):
                P.box(fe, (0.16, yg, 0.0022), (0.05, 0.006, 0.0005))
            P.box(st, (1.305, 0.35, 0.002), (1.1, 0.6, 0.004))
            for xg in np.arange(0.775, 1.84, 0.02):
                P.box(fe, (xg, 0.35, 0.0042), (0.006, 0.56, 0.0006))
        else:
            _placed(P, lambda T: floor_drain(T), 1.4, 4.8, 0.0)
        # the cove over the cell fronts (it grazes the fluting) + the downlights in the neck and the aisle
        P.box(st, (Wn - 0.32, (ub + L) / 2, H - 0.012), (0.08, L - ub - 0.1, 0.024)); P.box(M["opal"], (Wn - 0.32, (ub + L) / 2, H - 0.025), (0.05, L - ub - 0.14, 0.003))
        for xs, ys in ((1.2, 1.0), (1.3, 3.4), (1.3, 7.2)):
            P.cyl(st, (xs, ys, H - 0.012), 0.06, 0.012, seg=24); P.cyl(M["opal"], (xs, ys, H - 0.014), 0.05, 0.003, seg=24)
    finally:
        M["oak"] = oak0
    if hand < 0:  # the women's room: the same room in mirror image
        for b in P.bms.values():
            for v in b.verts:
                v.co.x = -v.co.x
            bmesh.ops.reverse_faces(b, faces=b.faces)


# ------------------------------------------------------------------ the south annex rooms (Roman 2026-10-18: "lets do those other rooms super
# high quality"): the posing room + the three private training pods (F2), the altitude room (F3). Fumed oak + blackened steel, the
# gym WCs' language; the joinery flush wall to wall and floor to ceiling, fronts in one plane (Roman's flush built-ins rule).
def _fumed():
    return M.setdefault("oak_smoked_dark", bc.pbr_material("oak_smoked_dark", "black_oak_veneer", 1.5, box=True, tint=(1.0, 0.92, 0.85), sat=0.7, val=0.38,
                                                           rough_mul=0.8, rough_add=0.08, piece_var=0.06))


def _flutes(P, x0, x1, y, z0, z1, pitch=0.03, skip=()):
    """The fluting on a fumed-oak front facing +y at y: a fine dark groove every pitch, interrupted over skip = [(x0, x1, z0, z1)]."""
    for xg in np.arange(x0 + pitch / 2, x1 - 0.005, pitch):
        zs = [z0, z1]
        for (a, b, c, d) in skip:
            if a <= xg <= b:
                zs = [z0, c, d, z1] if z0 < c and d < z1 else zs
        for k in range(0, len(zs), 2):
            if zs[k + 1] - zs[k] > 0.02:
                P.box(M["felt"], (xg, y + 0.0005, (zs[k] + zs[k + 1]) / 2), (0.003, 0.002, zs[k + 1] - zs[k] - 0.01))


def _screen_mat():
    return M.setdefault("screen_black", bc.material("screen_black", (0.006, 0.006, 0.007), 0.06))


def scene_keypad(P, mount=1.1):
    """The room's control plate by the door: blackened steel, four soft-lit scene keys (light, sound, climate), a small status line."""
    P.box(M["steel"], (0, 0.004, mount), (0.086, 0.008, 0.13))
    k = _led("keypad_glow", (1.0, 0.82, 0.62), 1.2)
    for i in range(4):
        P.box(k, (0, 0.0085, mount + 0.045 - i * 0.026), (0.05, 0.001, 0.004))


def booking_panel(P, room="POD 1", state="free", mount=1.4):
    """The booking screen beside a pod's (or the posing room's) door (Roman 2026-11-01: "a little tablet that's embedded in the wall
    that shows when they're reserved ... and then you can directly reserve them on that screen too"): a 10 in touch screen in a
    slim oak bezel set into the wall, its face flush; a status band at the top (green FREE / amber IN USE until when), the room's
    name, the day's slots below (booked ones dimmed amber, free ones green), a tap ring for the member card under it. Origin = the
    wall at the panel's centre on the floor, its face +y; mount = the screen's centre (1.4: readable standing, reachable seated)."""
    W, H, D = 0.19, 0.27, 0.014
    P.box(M["oak"], (0, D / 2 - 0.004, mount), (W + 0.03, D, H + 0.03))                     # the bezel, 4 mm proud of the wall
    scr = M.setdefault("screen_black", bc.material("screen_black", (0.004, 0.004, 0.005), 0.08))
    P.box(scr, (0, D - 0.003, mount), (W, 0.002, H))
    busy = state != "free"
    band = _led("booking_busy" if busy else "booking_free", (1.0, 0.55, 0.12) if busy else (0.2, 0.85, 0.35), 3.0)
    ink = _led("booking_ink", (0.95, 0.95, 0.92), 2.0)
    zt = mount + H / 2 - 0.025
    P.box(band, (0, D - 0.0018, zt), (W - 0.016, 0.0008, 0.036))
    P.text(ink, ("IN USE  until 15:00" if busy else "FREE  until 16:30"), (0, D - 0.001, zt), 0.014, depth=0.0004)
    P.text(ink, room, (0, D - 0.001, zt - 0.042), 0.02, depth=0.0004)
    for i, booked in enumerate((True, True, False, True, False, False, True)):                # the day's slots
        z = zt - 0.075 - i * 0.021
        P.box(_led("booking_slot_on" if booked else "booking_slot_free", (0.9, 0.45, 0.1) if booked else (0.2, 0.7, 0.3), 0.6 if booked else 1.2),
              (0.012, D - 0.0018, z), (W - 0.06, 0.0008, 0.013))
        P.text(ink, f"{13 + i}:00", (-W / 2 + 0.022, D - 0.001, z), 0.009, depth=0.0003)
    P.box(_led("booking_tap", (0.6, 0.75, 1.0), 1.5), (0, D - 0.0018, mount - H / 2 + 0.018), (0.05, 0.0008, 0.004))   # tap your card here


def ceiling_speaker(P, z_ceiling=3.4):
    """A flush round ceiling speaker: a thin blackened-steel ring round a dark micro-perforated grille."""
    P.cyl(M["steel"], (0, 0, z_ceiling - 0.004), 0.105, 0.004, seg=40)
    P.cyl(M["felt"], (0, 0, z_ceiling - 0.005), 0.095, 0.002, seg=40)


def posing_wall(P, L=5.55, D=0.47, H=3.375):
    """The posing room's mirror wall: one fumed-oak joinery wall, wall to wall and floor to ceiling, the 3-way mirror recessed into it
    (a 1.8 m centre glass and two 0.75 m wings turned 37° in towards the stage: front and both sides at once, as a tailor's mirror),
    a camera in the header over it (the screen beside it plays a pose back on a delay), a 50-inch screen flush in the north flank,
    a tall cabinet in the south one (posing trunks, tan, oil, bands, towels), a warm line in the niche's soffit lighting the poser
    from the front. Origin = the finished wall face at mid-length; front +y into the room, +x north."""
    sm, st, fe, mi = _fumed(), M["steel"], M["felt"], M["mirror"]
    C, Wg, ang = 1.8, 0.75, math.radians(37)
    xw = C / 2 + Wg * math.cos(ang)
    zm0, zm1 = 0.08, 2.6
    P.box(sm, (0, 0.01, (zm0 + zm1) / 2), (C, 0.02, zm1 - zm0))                                   # the centre glass on its backing
    P.box(mi, (0, 0.0215, (zm0 + zm1) / 2), (C - 0.012, 0.003, zm1 - zm0 - 0.012))
    P.box(st, (0, 0.03, zm0 / 2), (C, 0.06, zm0))                                                  # a blackened-steel kick under it
    for s in (-1, 1):                                                                              # the wings
        n = (-s * math.sin(ang), math.cos(ang))
        cx, cy = s * (C / 2 + Wg * math.cos(ang) / 2), 0.02 + Wg * math.sin(ang) / 2
        P.box(sm, (cx - n[0] * 0.01, cy - n[1] * 0.01, (zm0 + zm1) / 2), (Wg, 0.02, zm1 - zm0), rz=s * ang)
        P.box(mi, (cx + n[0] * 0.0015, cy + n[1] * 0.0015, (zm0 + zm1) / 2), (Wg - 0.012, 0.003, zm1 - zm0 - 0.012), rz=s * ang)
        P.box(st, (cx + n[0] * 0.03, cy + n[1] * 0.03, zm0 / 2), (Wg, 0.06, zm0), rz=s * ang)
        P.box(st, (s * C / 2, 0.03, (zm0 + zm1) / 2), (0.012, 0.03, zm1 - zm0))                    # the folds: a slim steel edge
    P.box(sm, (0, D / 2, zm1 + 0.02), (2 * xw, D, 0.04))                                           # the niche's soffit
    P.box(_led("pose_soffit", (1.0, 0.86, 0.72), 2.0), (0, D - 0.07, zm1 - 0.001), (2 * xw - 0.12, 0.03, 0.002))
    P.box(sm, (0, D - 0.02, (zm1 + 0.04 + H) / 2), (2 * xw, 0.04, H - zm1 - 0.04))                # the header over it, fluted
    _flutes(P, -xw, xw, D, zm1 + 0.04, H, skip=[(-0.06, 0.06, 2.84, 2.96)])
    P.box(st, (0, D + 0.006, 2.9), (0.09, 0.012, 0.09))                                            # the camera
    P.rod(_screen_mat(), (0, D + 0.012, 2.9), (0, D + 0.03, 2.9), 0.022, seg=24)
    P.cyl(M["glass"], (0, D + 0.031, 2.878), 0.016, 0.044, seg=20)
    for s in (-1, 1):                                                                              # the flanks
        a, b = sorted((s * xw, s * L / 2)); w = b - a; cx = (a + b) / 2
        P.box(sm, (cx, D / 2, (0.08 + H) / 2), (w, D - 0.04, H - 0.08))                            # carcass
        P.box(fe, (cx, D - 0.07, 0.04), (w, 0.04, 0.08))                                           # kick, set back
        P.box(sm, (cx, D - 0.02, (0.08 + H) / 2), (w, 0.04, H - 0.08))                             # the front
        if s > 0:   # north: the playback screen, flush
            sw, sh, sz = 1.107, 0.623, 1.55
            P.box(_screen_mat(), (cx, D + 0.0005, sz), (sw, 0.002, sh))
            P.box(st, (cx, D + 0.0003, sz), (sw + 0.02, 0.0015, sh + 0.02))
            _flutes(P, a, b, D, 0.08, H, skip=[(cx - sw / 2 - 0.012, cx + sw / 2 + 0.012, sz - sh / 2 - 0.012, sz + sh / 2 + 0.012)])
        else:       # south: a tall pair of doors to 2.6 m, a shadow gap round them, a finger groove down the meeting edge
            _flutes(P, a, b, D, 0.08, H)
            P.box(fe, (cx, D + 0.0008, zm1), (w, 0.0025, 0.003))
            P.box(fe, (cx, D + 0.0008, (0.08 + zm1) / 2), (0.004, 0.0025, zm1 - 0.08))
            P.box(st, (cx, D + 0.004, 1.1), (0.012, 0.008, 0.5))
        P.box(fe, (s * xw, D - 0.001, (0.08 + H) / 2), (0.004, 0.003, H - 0.08))                    # the shadow line at the niche


def posing_stage(P, w=1.8, d=1.8, h=0.2):
    """The posing stage: a solid fumed-oak platform 200 mm high on a recessed blackened-steel plinth, a warm glow out from under it
    so it floats, the top in wide boards with a brass centre mark (where the judges' light is aimed). Origin = its centre on the floor."""
    sm, st = _fumed(), M["steel"]
    P.box(st, (0, 0, 0.03), (w - 0.14, d - 0.14, 0.06))
    P.box(sm, (0, 0, (0.06 + h) / 2), (w, d, h - 0.06))
    for x in np.arange(-w / 2 + 0.3, w / 2 - 0.01, 0.3):                                           # board joints on the top
        P.box(M["felt"], (x, 0, h + 0.0004), (0.002, d - 0.004, 0.001))
    g = _led("stage_glow", (1.0, 0.75, 0.5), 3.0)
    for sx, sy, lx, ly in ((0, 1, w - 0.16, 0.01), (0, -1, w - 0.16, 0.01), (1, 0, 0.01, d - 0.16), (-1, 0, 0.01, d - 0.16)):
        P.box(g, (sx * (w / 2 - 0.075), sy * (d / 2 - 0.075), 0.055), (lx, ly, 0.006))
    P.cyl(M["brass"], (0, 0, h), 0.02, 0.0015, seg=24)


def stage_rig(P, w=2.6, z_ceiling=3.375, hang=0.55):
    """The posing light rig over the stage, after competition stage lighting (the top light carves the physique): a square frame in
    blackened steel hung on four rods, a 1.2 m soft top light in the middle of it and four spots on short yokes at its corners,
    two aimed in at the poser from the front at 45° (key), two from behind (rim). Warm 2700 K / cool 5000 K switchable.
    Origin = under its centre on the floor (the stage's centre), +y = towards the mirror."""
    st = M["steel"]; zf = z_ceiling - hang
    for s in (-1, 1):
        P.box(st, (0, s * w / 2, zf), (w + 0.05, 0.05, 0.1))
        P.box(st, (s * w / 2, 0, zf), (0.05, w - 0.05, 0.1))
        for t in (-1, 1):
            P.rod(st, (s * w / 2, t * w / 2, zf + 0.05), (s * w / 2, t * w / 2, z_ceiling), 0.008, seg=8)
            P.cyl(st, (s * w / 2, t * w / 2, z_ceiling - 0.006), 0.04, 0.006, seg=16)
        P.box(st, (0, s * 0.62, zf), (w - 0.05, 0.04, 0.04))                                       # the cross bars carrying the top light
    P.box(st, (0, 0, zf - 0.02), (1.24, 1.24, 0.1))
    P.box(_led("pose_top", (1.0, 0.95, 0.9), 2.5), (0, 0, zf - 0.071), (1.18, 1.18, 0.002))
    for s in (-1, 1):
        for t in (-1, 1):
            p0 = Vector((s * w / 2, t * w / 2, zf - 0.05)); tgt = Vector((0, 0, 1.3))
            dvec = (tgt - p0).normalized(); c0 = p0 + Vector((0, 0, -0.08))
            P.rod(st, p0, c0, 0.01, seg=8)
            P.rod(st, c0 - dvec * 0.06, c0 + dvec * 0.16, 0.055, seg=24)
            P.rod(_led("pose_spot", (1.0, 0.93, 0.85), 8.0), c0 + dvec * 0.16, c0 + dvec * 0.163, 0.045, seg=24)


def light_boom(P, H=3.375, z0=0.45, z1=2.75):
    """A side light: a 40 x 40 blackened-steel post floor to ceiling on two plates, carrying a tall slim LED bar behind a black
    honeycomb grid (the side light that shows the lines of a pose). Origin = its foot; front +y = where it throws."""
    st = M["steel"]
    P.box(st, (0, 0, 0.006), (0.22, 0.22, 0.012)); P.box(st, (0, 0, H - 0.006), (0.14, 0.14, 0.012))
    P.box(st, (0, 0, H / 2), (0.04, 0.04, H))
    P.box(st, (0, 0.05, (z0 + z1) / 2), (0.1, 0.07, z1 - z0))
    P.box(_led("pose_side", (1.0, 0.93, 0.86), 2.5), (0, 0.0855, (z0 + z1) / 2), (0.08, 0.002, z1 - z0 - 0.02))
    for z in np.arange(z0 + 0.04, z1 - 0.02, 0.04):
        P.box(M["felt"], (0, 0.088, z), (0.084, 0.004, 0.003))
    for z in (z0 + 0.1, z1 - 0.1):
        P.box(st, (0, 0.02, z), (0.05, 0.02, 0.04))


def velvet_backdrop(P, L=5.55, H=3.375):
    """A charcoal velvet curtain wall to wall on a ceiling track, floor to ceiling (the black backdrop for posing photos + video;
    it soaks up the sound too). Origin = the wall it hangs in front of, at mid-length; front +y."""
    st, vel = M["steel"], _velvet()
    P.box(st, (0, 0.12, H - 0.02), (L, 0.04, 0.03))
    xs = np.arange(-L / 2 + 0.03, L / 2 - 0.02, 0.04)
    yy = 0.12 + 0.03 * np.sin(xs * 2 * math.pi / 0.16)
    P.rods(vel, np.c_[xs, yy, np.full_like(xs, 0.015)], np.c_[xs, yy, np.full_like(xs, H - 0.04)], 0.03, seg=10)


def pod_wall(P, L=5.55, D=0.5, H=3.375):
    """A private training pod's west wall: one fumed-oak joinery wall, wall to wall and floor to ceiling, fronts in one plane. From the
    door end: towels + water (a glass-front fridge of cold water under a lit open niche of rolled towels, a phone shelf with a charger,
    two hooks, a cupboard for a bag), the screen (65-inch, flush, a fabric speaker line over it, drawers of straps, chalk + bands
    under it), the kit wall by the platform (an open lit niche, a fumed-oak peg board of bands, belts, straps + ropes, foam rollers and
    mats in the cubbies under it). Origin = the finished wall face at mid-length; front +y into the room, -x = the door end."""
    sm, st, fe = _fumed(), M["steel"], M["felt"]
    bays = [(-L / 2, -L / 2 + 1.6), (-L / 2 + 1.6, -L / 2 + 3.6), (-L / 2 + 3.6, L / 2)]
    P.box(fe, (0, D - 0.07, 0.04), (L, 0.04, 0.08))                                                # recessed kick
    for (a, b) in bays[1:]:
        P.box(fe, (a, D - 0.001, (0.08 + H) / 2), (0.004, 0.003, H - 0.08))                         # shadow lines between the bays
    glow = _led("pod_niche", (1.0, 0.8, 0.58), 3.0)
    # -- towels + water
    a, b = bays[0]; cx = (a + b) / 2; nz0, nz1 = 0.92, 2.05
    fr0, fr1 = a + 0.06, a + 0.66
    skip = [(a, b, nz0 - 0.005, nz1 + 0.005), (fr0 - 0.004, fr1 + 0.004, 0.1, 0.86)]
    for x0_, x1_ in ((a, fr0 - 0.004), (fr1 + 0.004, b)):                                           # solid either side of the fridge
        P.box(sm, ((x0_ + x1_) / 2, D / 2, (0.08 + nz0) / 2), (x1_ - x0_, D, nz0 - 0.08))
    for z0_, z1_ in ((0.08, 0.1), (0.86, nz0)):
        P.box(sm, ((fr0 + fr1) / 2, D / 2, (z0_ + z1_) / 2), (fr1 - fr0 + 0.008, D, z1_ - z0_))
    P.box(sm, ((fr0 + fr1) / 2, 0.02, 0.48), (fr1 - fr0, 0.04, 0.76))                               # the fridge's back
    P.box(sm, (cx, D / 2, (nz1 + H) / 2), (b - a, D, H - nz1))                                     # solid over the niche
    P.box(sm, (cx, 0.02, (nz0 + nz1) / 2), (b - a, 0.04, nz1 - nz0))                               # the niche's back
    P.box(sm, (cx, D - 0.24, nz0 + 0.01), (b - a - 0.06, 0.48, 0.02))  # its shelf
    P.box(glow, (cx, D - 0.06, nz1 - 0.003), (b - a - 0.1, 0.02, 0.003))
    _flutes(P, a, b, D, 0.08, H, skip=skip)
    tw = M.setdefault("towel_char", bc.material("towel_char", (0.06, 0.058, 0.055), 0.95))
    for i in range(4):
        for j in range(2):
            P.rod(tw, (a + 0.28 + i * 0.16, D - 0.42, nz0 + 0.1 + j * 0.15), (a + 0.28 + i * 0.16, D - 0.08, nz0 + 0.1 + j * 0.15), 0.07, seg=16)
    P.box(st, (b - 0.36, D - 0.2, nz0 + 0.03), (0.3, 0.2, 0.012))                                   # phone shelf + charger pad
    P.cyl(M["felt"], (b - 0.36, D - 0.2, nz0 + 0.037), 0.04, 0.003, seg=24)
    for xh in (b - 0.42, b - 0.26):
        P.rod(st, (xh, 0.2, nz1 - 0.25), (xh, 0.3, nz1 - 0.22), 0.008, seg=8)
    for x_ in (fr0 + 0.01, fr1 - 0.01):                                                             # the fridge: a steel frame, a glass door
        P.box(st, (x_, D - 0.02, 0.48), (0.02, 0.04, 0.76))
    for z_ in (0.11, 0.85):
        P.box(st, ((fr0 + fr1) / 2, D - 0.02, z_), (fr1 - fr0, 0.04, 0.02))
    P.box(M["glass"], ((fr0 + fr1) / 2, D - 0.004, 0.48), (fr1 - fr0 - 0.04, 0.008, 0.72))
    P.box(_led("fridge_glow", (0.9, 0.95, 1.0), 1.5), ((fr0 + fr1) / 2, D - 0.42, 0.48), (fr1 - fr0 - 0.08, 0.004, 0.66))
    bot = M.setdefault("bottle_glass", bc.arch_glass("bottle_glass", tint=(0.85, 0.92, 0.95)))
    for z in (0.22, 0.48, 0.72):
        P.box(M["glass"], ((fr0 + fr1) / 2, D - 0.24, z - 0.005), (fr1 - fr0 - 0.08, 0.36, 0.006))
        for i in range(5):
            P.cyl(bot, (fr0 + 0.08 + i * 0.105, D - 0.2, z), 0.032, 0.2, seg=16)
            P.cyl(st, (fr0 + 0.08 + i * 0.105, D - 0.2, z + 0.2), 0.018, 0.025, seg=12)
    P.box(st, (fr1 - 0.04, D + 0.006, 0.6), (0.012, 0.012, 0.3))
    P.box(fe, ((fr1 + b) / 2, D + 0.0008, 0.47), (0.004, 0.0025, 0.78))                             # the bag cupboard's door
    # -- the screen
    a, b = bays[1]; cx = (a + b) / 2; sw, sh, sz = 1.43, 0.805, 1.55
    P.box(sm, (cx, D / 2, (0.08 + H) / 2), (b - a, D, H - 0.08))
    P.box(_screen_mat(), (cx, D + 0.0005, sz), (sw, 0.002, sh)); P.box(st, (cx, D + 0.0003, sz), (sw + 0.02, 0.0015, sh + 0.02))
    P.box(M.setdefault("speaker_cloth", bc.material("speaker_cloth", (0.03, 0.03, 0.032), 0.97)), (cx, D + 0.0006, 2.2), (b - a - 0.2, 0.002, 0.16))
    _flutes(P, a, b, D, 0.08, H, skip=[(cx - sw / 2 - 0.012, cx + sw / 2 + 0.012, sz - sh / 2 - 0.012, sz + sh / 2 + 0.012),
                                        (a + 0.1, b - 0.1, 2.115, 2.285)])
    for z in (0.37, 0.65):                                                                          # drawer joints under it
        P.box(fe, (cx, D + 0.0008, z), (b - a - 0.02, 0.0025, 0.003))
    P.box(fe, (cx, D + 0.0008, 0.93), (b - a - 0.02, 0.0025, 0.003))
    # -- the kit wall: an open niche
    a, b = bays[2]; cx = (a + b) / 2; kz0, kz1 = 0.5, 2.45
    P.box(sm, (cx, D / 2, (0.08 + kz0) / 2), (b - a, D, kz0 - 0.08))
    P.box(sm, (cx, D / 2, (kz1 + H) / 2), (b - a, D, H - kz1))
    _flutes(P, a, b, D, 0.08, kz0); _flutes(P, a, b, D, kz1, H)
    P.box(sm, (cx, 0.03, (kz0 + kz1) / 2), (b - a - 0.04, 0.06, kz1 - kz0))                         # peg board back
    for xp in np.arange(a + 0.12, b - 0.05, 0.1):
        for zp in np.arange(kz0 + 0.95, kz1 - 0.05, 0.1):
            P.box(fe, (xp, 0.0605, zp), (0.008, 0.001, 0.008))
    P.box(sm, (cx, D / 2, kz0 + 0.01), (b - a - 0.04, D - 0.04, 0.02))                               # the cubby shelf
    for xs in (a + (b - a) / 3, a + 2 * (b - a) / 3):
        P.box(sm, (xs, D / 2, (kz0 + kz0 + 0.62) / 2), (0.02, D - 0.04, 0.62))
    P.box(sm, (cx, D / 2, kz0 + 0.63), (b - a - 0.04, D - 0.04, 0.02))
    P.box(glow, (cx, D - 0.06, kz1 - 0.003), (b - a - 0.1, 0.02, 0.003))
    cols = [M.setdefault(f"band_{n}", bc.material(f"band_{n}", c, 0.6)) for n, c in
            (("black", (0.02, 0.02, 0.02)), ("moss", (0.12, 0.16, 0.08)), ("rust", (0.32, 0.1, 0.05)), ("sand", (0.5, 0.42, 0.3)))]
    for i, mat in enumerate(cols):                                                                   # bands on pegs
        xp = a + 0.22 + i * 0.16
        P.rod(st, (xp, 0.06, 2.2), (xp, 0.16, 2.21), 0.008, seg=8)
        for s in (-1, 1):
            P.rod(mat, (xp + s * 0.012, 0.14, 2.2), (xp + s * 0.03, 0.13, 1.45 + i * 0.05), 0.007, seg=8)
    xb_ = a + 1.0                                                                                   # a lifting belt
    P.rod(st, (xb_, 0.06, 2.2), (xb_, 0.16, 2.21), 0.008, seg=8)
    P.box(M["rubber"], (xb_, 0.13, 1.85), (0.1, 0.012, 0.7))
    for i in range(2):                                                                              # straps, a jump rope
        xs_ = a + 1.25 + i * 0.12
        P.rod(st, (xs_, 0.06, 2.2), (xs_, 0.16, 2.21), 0.008, seg=8)
        P.box(M["rubber"] if i else cols[1], (xs_, 0.135, 1.95), (0.035, 0.006, 0.5))
    P.rod(st, (b - 0.3, 0.06, 2.2), (b - 0.3, 0.16, 2.21), 0.008, seg=8)
    for s in (-1, 1):
        P.rod(M["rubber"], (b - 0.3 + s * 0.02, 0.15, 2.19), (b - 0.3 + s * 0.08, 0.14, 1.3), 0.004, seg=6)
    for i, (xc_, kind) in enumerate(((a + (b - a) / 6, "roller"), (a + (b - a) / 2, "mat"), (a + 5 * (b - a) / 6, "roller"))):
        if kind == "roller":
            for j in range(2):
                P.rod(cols[0] if j else cols[3], (xc_ - 0.28, 0.12 + j * 0.2, kz0 + 0.1), (xc_ + 0.28, 0.12 + j * 0.2, kz0 + 0.1), 0.075, seg=24)
        else:
            for j in range(3):
                P.rod(cols[(j + 1) % 4], (xc_ - 0.3, 0.1 + j * 0.15, kz0 + 0.09), (xc_ + 0.3, 0.1 + j * 0.15, kz0 + 0.09), 0.065, seg=20)


def platform_inlay(P, s=2.44):
    """A lifting platform set flush into the pod's floor (top at the floor): a light oak centre 1.22 m wide where the lifter stands,
    30 mm recycled-rubber drop zones either side where the plates land, a slim blackened-steel frame round it, the centre in boards.
    Origin = its centre on the floor; x = the way the lifter faces."""
    t = 0.03
    P.box(M["oak"], (0, 0, -t / 2), (s - 0.02, 1.22, t))
    for y in np.arange(-0.61 + 0.2033, 0.6, 0.2033):
        P.box(M["felt"], (0, y, -0.0004), (s - 0.03, 0.002, 0.001))
    for sy in (-1, 1):
        P.box(M["rubber"], (0, sy * (0.61 + (s / 2 - 0.62) / 2), -t / 2), (s - 0.02, s / 2 - 0.63, t))
        P.box(M["steel"], (0, sy * 0.615, -t / 2 + 0.0003), (s - 0.02, 0.01, t))
    for sx, sy, lx, ly in ((0, 1, s, 0.01), (0, -1, s, 0.01), (1, 0, 0.01, s), (-1, 0, 0.01, s)):
        P.box(M["steel"], (sx * (s / 2 - 0.005), sy * (s / 2 - 0.005), -t / 2 + 0.0003), (lx, ly, t))


def airlock(P, w=3.0, d=2.0, h=2.7, door=1.4):
    """The altitude room's airlock inside its door from the gym: a glass lobby in slim blackened-steel frames, a glass lid, a pair of
    automatic sliding glass doors in the far side, interlocked with the door from the gym (only one side opens at a time, so the
    thin air stays in), a grate to stand on, the room's altitude on a small display on the door post. Origin = the finished wall face
    at its middle, front +y into the room."""
    fr = M["frame"]
    _placed(P, lambda T: glass_screen(T, w, h, door=door), 0.0, d, 0.0)
    for s in (-1, 1):
        _placed(P, lambda T: glass_screen(T, d, h), s * w / 2, d / 2, math.pi / 2)
    P.box(M["glass"], (0, d / 2, h - 0.01), (w - 0.1, d - 0.1, 0.012))
    for s in (-1, 1):
        P.box(fr, (0, d / 2 + s * (d / 2 - 0.03), h - 0.02), (w, 0.06, 0.04))
        P.box(fr, (s * (w / 2 - 0.03), d / 2, h - 0.02), (0.06, d, 0.04))
    _placed(P, lambda T: entrance_mat(T, size=(w - 0.3, d - 0.3), style="wiper"), 0.0, d / 2, 0.0)
    dz = 1.45; x0 = door / 2 + 0.17
    P.box(fr, (x0, d + 0.07, dz), (0.14, 0.012, 0.09))
    P.box(_screen_mat(), (x0, d + 0.077, dz), (0.13, 0.002, 0.08))
    P.text(_led("alt_text", (0.75, 0.88, 1.0), 3.0), "2800 m", (x0, d + 0.079, dz + 0.008), 0.03)
    P.cyl(_led("alt_ok", (0.2, 1.0, 0.4), 2.0), (x0 + 0.045, d + 0.078, dz - 0.028), 0.004, 0.002, seg=12)


def _sky_mat():
    """A backlit stretched ceiling printed with nothing but sky: a soft emissive field, palest in the middle, a deeper clear blue
    towards the edges (high-altitude sky, as an artificial skylight in a windowless room)."""
    m = bpy.data.materials.get("alt_sky")
    if m:
        return m
    m = bpy.data.materials.new("alt_sky"); m.use_nodes = True
    N, Lk = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(tc.outputs["Generated"], sep.inputs[0])
    def dist(o):
        a = N.new("ShaderNodeMath"); a.operation = "SUBTRACT"; a.inputs[1].default_value = 0.5; Lk.new(o, a.inputs[0])
        b = N.new("ShaderNodeMath"); b.operation = "ABSOLUTE"; Lk.new(a.outputs[0], b.inputs[0])
        c = N.new("ShaderNodeMath"); c.operation = "MULTIPLY"; c.inputs[1].default_value = 2.0; Lk.new(b.outputs[0], c.inputs[0])
        return c.outputs[0]
    dx, dy = dist(sep.outputs[0]), dist(sep.outputs[1])
    sq = []
    for dd in (dx, dy):
        p = N.new("ShaderNodeMath"); p.operation = "POWER"; p.inputs[1].default_value = 2.0; Lk.new(dd, p.inputs[0]); sq.append(p)
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; Lk.new(sq[0].outputs[0], ad.inputs[0]); Lk.new(sq[1].outputs[0], ad.inputs[1])
    sr = N.new("ShaderNodeMath"); sr.operation = "SQRT"; Lk.new(ad.outputs[0], sr.inputs[0])
    ramp = N.new("ShaderNodeValToRGB"); Lk.new(sr.outputs[0], ramp.inputs[0])
    ramp.color_ramp.elements[0].color = (0.56, 0.74, 1.0, 1); ramp.color_ramp.elements[1].color = (0.16, 0.34, 0.85, 1)
    ramp.color_ramp.elements[1].position = 1.25; ramp.color_ramp.interpolation = "EASE"
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 0.45; Lk.new(ramp.outputs[0], em.inputs["Color"])
    Lk.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    return m


def sky_coffer(P, w=11.7, d=3.65, depth=0.36, z_ceiling=4.1):
    """The altitude room's sky: a coffer 0.36 m up into the ceiling plenum, its reveals in charcoal, its lid a backlit stretched
    ceiling of clear sky (a windowless room in the rock under a sky; dimmable, dawn to noon). Linear slot diffusers along both long
    sides breathe the hypoxic air in; the return is low on the east wall. Origin = under its centre on the floor."""
    rv = M.setdefault("coffer_charcoal", bc.material("coffer_charcoal", (0.035, 0.035, 0.037), 0.9))
    z0, z1 = z_ceiling, z_ceiling + depth
    for s in (-1, 1):
        P.box(rv, (0, s * (d / 2 + 0.01), (z0 + z1) / 2), (w + 0.04, 0.02, depth))
        P.box(rv, (s * (w / 2 + 0.01), 0, (z0 + z1) / 2), (0.02, d, depth))
    P.box(_sky_mat(), (0, 0, z1 - 0.005), (w, d, 0.01))
    for s in (-1, 1):                                                                                # the slot diffusers
        P.box(M["steel"], (0, s * (d / 2 + 0.17), z0 - 0.002), (w, 0.06, 0.004))
        P.box(M["felt"], (0, s * (d / 2 + 0.17), z0 - 0.0045), (w - 0.02, 0.025, 0.001))


def altitude_display(P, w=2.6, h=1.46, mount=1.75):
    """The altitude display on the end wall, read from every bike, rower and treadmill: a black glass panel, the set altitude large
    (2 800 m), under it the room's air (O2 15.1 %, CO2 0.09 %, 18 °C, 45 % RH), a thin ridge line of the Rondane peaks along the top.
    Origin = the finished wall face; front +y."""
    st = M["steel"]
    P.box(st, (0, 0.012, mount), (w + 0.03, 0.024, h + 0.03))
    P.box(_screen_mat(), (0, 0.0245, mount), (w, 0.002, h))
    tx = _led("alt_text", (0.75, 0.88, 1.0), 3.0); dim = _led("alt_dim", (0.55, 0.7, 0.9), 1.4)
    P.text(dim, "HØYDE  ·  ALTITUDE", (0, 0.026, mount + 0.33), 0.06)
    P.text(tx, "2 800 m", (0, 0.026, mount + 0.06), 0.34)
    P.text(dim, "O2 15.1 %     CO2 0.09 %     18 °C     45 % RH", (0, 0.026, mount - 0.33), 0.055)
    ridge = [(-1.15, 0.58), (-0.9, 0.6), (-0.7, 0.66), (-0.5, 0.62), (-0.3, 0.69), (-0.1, 0.64), (0.1, 0.67), (0.3, 0.61), (0.55, 0.65), (0.8, 0.6), (1.15, 0.585)]
    for (x0, z0), (x1, z1) in zip(ridge, ridge[1:]):
        L_ = math.hypot(x1 - x0, z1 - z0)
        P.box(dim, ((x0 + x1) / 2, 0.0262, mount + (z0 + z1) / 2), (L_, 0.0005, 0.004), ry=-math.atan2(z1 - z0, x1 - x0))


def altitude_station(P):
    """By the inner airlock door: the room's control screen (set the altitude, the session timer), the oxygen + CO2 sensor head at
    breathing height, a red fresh-air purge button under a flip cover (it floods the room with outside air), and a small steel shelf
    with fingertip pulse oximeters (check your SpO2 between sets). Origin = the finished wall face; front +y."""
    st = M["steel"]
    P.box(st, (0, 0.008, 1.35), (0.3, 0.016, 0.2)); P.box(_screen_mat(), (0, 0.0165, 1.35), (0.28, 0.002, 0.18))
    tx = _led("alt_text", (0.75, 0.88, 1.0), 3.0)
    P.text(tx, "2800 m", (0, 0.018, 1.37), 0.045)
    P.box(M["ceramic"], (0.32, 0.025, 1.55), (0.1, 0.05, 0.14)); P.cyl(_led("alt_ok", (0.2, 1.0, 0.4), 2.0), (0.32, 0.051, 1.6), 0.005, 0.002, seg=12)
    for z in np.arange(1.5, 1.56, 0.015):
        P.box(st, (0.32, 0.0505, z), (0.07, 0.001, 0.004))
    yel = M.setdefault("purge_yellow", bc.material("purge_yellow", (0.75, 0.55, 0.02), 0.5))
    P.box(yel, (0.32, 0.01, 1.15), (0.12, 0.02, 0.12))
    P.rod(M["lino_lingon"], (0.32, 0.02, 1.15), (0.32, 0.045, 1.15), 0.03, seg=20)
    P.box(M["glass"], (0.32, 0.06, 1.15), (0.11, 0.004, 0.11))
    P.box(st, (0, 0.08, 1.0), (0.3, 0.16, 0.01))
    for x in (-0.07, 0.07):
        P.box(M["ceramic"], (x, 0.08, 1.02), (0.035, 0.06, 0.03)); P.box(_screen_mat(), (x, 0.08, 1.036), (0.02, 0.025, 0.001))


def vent_grille(P, w=1.2, h=0.4, z0=0.15):
    """A low return-air grille in blackened steel (the sealed room's air goes back to the generators through it). Origin = wall face."""
    P.box(M["steel"], (0, 0.01, z0 + h / 2), (w, 0.02, h))
    for z in np.arange(z0 + 0.03, z0 + h - 0.02, 0.025):
        P.box(M["felt"], (0, 0.0205, z), (w - 0.04, 0.002, 0.012))


def hypoxic_plant(P):
    """The altitude room's plant bay (staff): two hypoxic generators (membrane air separation: compressors + nitrogen membranes in
    grey steel cabinets), a buffer tank, the control cabinet, the ducts up to the ceiling plenum. Origin = the middle of the bay floor."""
    gr = M.setdefault("plant_grey", bc.material("plant_grey", (0.32, 0.33, 0.33), 0.5, metal=0.3))
    for x in (-2.2, -1.1):
        P.box(gr, (x, -1.6, 0.9), (0.9, 0.7, 1.8)); P.box(M["felt"], (x, -1.24, 1.5), (0.6, 0.004, 0.3))
        P.box(gr, (x, -1.6, 2.5), (0.4, 0.4, 1.4))
    P.cyl(gr, (0.4, -1.8, 0.0), 0.35, 1.7, seg=24)
    P.box(gr, (1.6, -2.4, 1.0), (0.8, 0.3, 1.6))
    P.box(gr, (-1.6, -1.6, 3.6), (2.2, 0.5, 0.4))


BUILDERS = {
    "lounge_chair": lounge_chair, "sofa": sofa, "dining_chair": dining_chair, "bar_stool": bar_stool, "cafe_table": cafe_table,
    "side_table": side_table, "coffee_table": coffee_table, "communal_table": communal_table, "bench": bench, "boot_bench": boot_bench,
    "rug": rug, "reception_desk": reception_desk, "cafe_island": cafe_island, "ring_pendant": ring_pendant, "pendant_opal": pendant_opal,
    "glass_screen": glass_screen, "sliding_doors": sliding_doors, "vestibule_lid": vestibule_lid, "door_slatted": door_slatted,
    "lift_doors": lift_doors, "glass_door": glass_door, "baffle_screen": baffle_screen, "window_counter": window_counter,
    "relief_art": relief_art, "porch_floor": porch_floor, "canvas_art": canvas_art,
    "wall_light": wall_light, "downlight": downlight, "gallery_spot": gallery_spot, "entrance_mat": entrance_mat,
    "wc_cells": wc_cells, "wc_run": wc_run, "vanity": vanity, "urinals": urinals, "cell_light": cell_light, "light_only": light_only,
    "kid_wc_cells": kid_wc_cells, "changing_unit": changing_unit, "cubbies": cubbies, "drying_cabinet": drying_cabinet,
    "kid_table": kid_table, "kid_chair": kid_chair, "play_loft": play_loft, "stair_guard": stair_guard, "felt_cloud": felt_cloud,
    "soft_play": soft_play, "low_shelf": low_shelf, "gate": gate, "story_wall": story_wall, "floor_cushion": floor_cushion,
    "rug_round": rug_round, "kitchenette": kitchenette, "art_labels": art_labels,
    "climbing_wall": climbing_wall, "wall_bars": wall_bars, "nest_swing": nest_swing, "balance_beam": balance_beam, "sleep_mat": sleep_mat, "mat_shelf": mat_shelf,
    "star_ceiling": star_ceiling, "pram": pram, "gear_rack": gear_rack, "gapahuk": gapahuk, "fire_pit": fire_pit, "log_bench": log_bench,
    "sandbox": sandbox, "swing_frame": swing_frame, "playhouse": playhouse, "mud_kitchen": mud_kitchen, "trike_loop": trike_loop,
    "terrace_slide": terrace_slide, "pram_shelter": pram_shelter, "stump": stump,
    "tube_slide": tube_slide, "foam_fortress": foam_fortress, "ripstick": ripstick, "tricycle": tricycle, "strider": strider,
    "wheel_rack": wheel_rack, "rolling_hill": rolling_hill, "floor_track": floor_track, "hopscotch": hopscotch,
    "music_wall": music_wall, "dance_mirror": dance_mirror, "balance_trail": balance_trail,
    "felt_banner": felt_banner, "bunting": bunting, "staff_wc_fit": staff_wc_fit, "staff_lockers": staff_lockers,
    "canopy_crown": canopy_crown, "nest": nest, "pikler_arch": pikler_arch, "window_nest": window_nest, "sensory_panel": sensory_panel,
    "toddler_table": toddler_table, "pictogram": pictogram, "portal_frame": portal_frame,
    "conversation_ring": conversation_ring, "boulder_table": boulder_table, "elva": elva, "towel_station": towel_station, "sanitiser": sanitiser, "recycling": recycling,
    "wall_sign": wall_sign, "exit_sign": exit_sign, "safety_point": safety_point, "ceiling_services": ceiling_services,
    "floor_drain": floor_drain, "amenity_tray": amenity_tray, "table_setting": table_setting, "water_station": water_station, "slat_canopy": slat_canopy, "eyelid_sconce": eyelid_sconce,
    "menu_board": menu_board, "high_chair": high_chair, "coat_rack": coat_rack, "floor_lamp": floor_lamp, "magazines": magazines,
    "laksetrappa": laksetrappa, "glass_floor": glass_floor, "speed_gates": speed_gates, "glass_fence": glass_fence, "floor_strip": floor_strip,
    "bridge_bench": bridge_bench, "standing_table": standing_table, "deck_sofa": deck_sofa, "deck_chair": deck_chair, "deck_table": deck_table,
    "blanket_basket": blanket_basket, "ir_heater": ir_heater, "gate_release": gate_release, "slide_wall": slide_wall, "kilden": kilden,
    "linear_light": linear_light, "floor_grazer": floor_grazer, "oculus": oculus,
    "locker_hall": locker_hall, "round_seat": round_seat, "wall_waterfall": wall_waterfall, "grooming_bar": grooming_bar,
    "shoe_cubbies": shoe_cubbies, "towel_shelf": towel_shelf, "uvc_plate": uvc_plate, "auto_door": auto_door,
    "shower_cell": shower_cell, "fossen": fossen, "wash_place": wash_place, "stone_bench": stone_bench, "vaskebjorn": vaskebjorn,
    "robot_dock": robot_dock, "tap_station": tap_station, "stone_lining": stone_lining, "log_store": log_store, "duckboard": duckboard, "gym_line": gym_line, "ring_guard": ring_guard, "spiral_planter": spiral_planter, "den_stream": den_stream, "glass_lift": glass_lift, "lap_pool": lap_pool, "river_wall_f4": river_wall_f4, "river_volume": river_volume, "core_door": core_door, "stair_landing": stair_landing, "spiral_balustrade": spiral_balustrade, "wipe_station": wipe_station, "wall_washer": wall_washer, "sauna_tier": sauna_tier, "sauna_heater": sauna_heater, "sauna_bucket": sauna_bucket, "kindling_basket": kindling_basket, "firewood_stack": firewood_stack, "peg_rail": peg_rail, "sauna_gauges": sauna_gauges, "split_log_bench": split_log_bench, "porch_lantern": porch_lantern, "plank_door": plank_door, "sauna_glass_door": sauna_glass_door, "deck_door": deck_door, "badestamp": badestamp, "stamp_stove": stamp_stove, "stamp_steps": stamp_steps, "tip_bucket": tip_bucket, "slipper_cabinet": slipper_cabinet, "far_uvc": far_uvc, "booking_panel": booking_panel, "robe_wall": robe_wall, "towel_warmer": towel_warmer,
    "plunge": plunge, "sauna_cabin": sauna_cabin, "sauna_heater_el": sauna_heater_el, "steam_room": steam_room, "rinse_shower": rinse_shower,
    "pool_lounger": pool_lounger, "recovery_bay": recovery_bay, "plant_pot": plant_pot, "eclipse_sconce": eclipse_sconce, "towel_bin": towel_bin, "breath_mat": breath_mat,
    "gym_wc": gym_wc, "scene_keypad": scene_keypad, "ceiling_speaker": ceiling_speaker, "posing_wall": posing_wall, "posing_stage": posing_stage,
    "stage_rig": stage_rig, "light_boom": light_boom, "velvet_backdrop": velvet_backdrop, "pod_wall": pod_wall, "platform_inlay": platform_inlay,
    "airlock": airlock, "sky_coffer": sky_coffer, "altitude_display": altitude_display, "altitude_station": altitude_station, "vent_grille": vent_grille,
    "hypoxic_plant": hypoxic_plant,
}
PARAMS = {"eclipse_sconce": ("mount",), "gym_wc": ("men", "pool", "hand"), "scene_keypad": ("mount",), "ceiling_speaker": ("z_ceiling",), "posing_wall": ("L", "D", "H"),
          "posing_stage": ("w", "d", "h"), "stage_rig": ("w", "z_ceiling", "hang"), "light_boom": ("H",), "velvet_backdrop": ("L", "H"), "pod_wall": ("L", "D", "H"),
          "platform_inlay": ("s",), "airlock": ("w", "d", "h", "door"), "sky_coffer": ("w", "d", "depth", "z_ceiling"), "altitude_display": ("w", "h", "mount"),
          "vent_grille": ("w", "h", "z0"), "far_uvc": ("z_ceiling",), "booking_panel": ("room", "state", "mount"), "recovery_bay": ("w", "d", "ceiling", "end"), "plant_pot": ("species", "h", "r"), "plunge": ("w", "d", "depth", "rim", "hot"), "sauna_cabin": ("w", "d", "h", "door"), "steam_room": ("w", "d", "h", "door"), "rinse_shower": ("n", "pitch"), "breath_mat": ("colour",), "river_volume": ("lamps", "lamp_z"), "river_wall_f4": ("y0", "y1", "top", "face", "d", "windows", "pilasters"), "glass_lift": ("shaft", "front", "stops", "pit", "top", "cab", "cw", "name"), "core_door": ("width", "height", "finish", "exit_"), "stair_landing": ("r_in", "r_out", "a_from", "a_to", "h", "t"), "ring_guard": ("r", "gap_a", "gap_b", "h", "band"), "spiral_planter": ("ri", "ro", "rise", "risers", "step_deg", "a0", "head"), "spiral_balustrade": ("ri", "ro", "rise", "risers", "step_deg", "a0", "gaps"),
          "gym_line": ("L", "z_ceiling", "temp"), "wall_washer": ("L", "z_ceiling", "temp"), "duckboard": ("w", "d"), "sauna_tier": ("L", "d", "seat", "back"), "firewood_stack": ("L", "h", "d"), "peg_rail": ("L",), "split_log_bench": ("L",), "plank_door": ("width", "height"), "sauna_glass_door": ("width", "height"), "deck_door": ("width", "height"), "badestamp": ("d", "h"), "stamp_steps": ("w",), "porch_lantern": ("z",),
          "sofa": ("length",), "communal_table": ("length",), "bench": ("length",), "boot_bench": ("length",), "rug": ("size",),
          "reception_desk": ("length",), "cafe_island": ("r_out", "gap_deg"), "ring_pendant": ("r", "hang"), "pendant_opal": ("hang",),
          "glass_screen": ("width", "height", "door"), "sliding_doors": ("width", "height"), "vestibule_lid": ("size", "height"),
          "door_slatted": ("width", "height"), "lift_doors": ("width", "height"), "glass_door": ("width", "height", "privacy"),
          "baffle_screen": ("width", "height"), "window_counter": ("length",), "bar_stool": ("height",), "relief_art": ("width", "height"), "porch_floor": ("size",), "canvas_art": ("width", "height", "image", "z0"), "downlight": ("z_ceiling",), "gallery_spot": ("z_ceiling",), "entrance_mat": ("size", "style"),
          "wc_cells": ("n", "w", "depth", "style", "door_at", "pan_at", "number0", "occupied"),
          "wc_run": ("cells", "depth", "open_", "occupied", "pan_side"), "vanity": ("length", "n", "top"), "urinals": ("n", "pitch"), "cell_light": ("z_ceiling",),
          "kid_wc_cells": ("n", "w", "depth"), "changing_unit": ("length",), "cubbies": ("length", "n"), "kid_table": ("colour",),
          "kid_chair": ("colour", "seat"), "dance_mirror": ("length", "h", "barre"), "window_nest": ("length",), "sensory_panel": ("style",), "pictogram": ("figure", "size", "mount"), "portal_frame": ("width", "height", "depth"), "wall_sign": ("text", "w", "h", "mount", "size", "blade"), "exit_sign": ("mount", "hang_to"), "safety_point": ("aed",),
          "ceiling_services": ("z_local", "ceiling", "device"), "amenity_tray": ("products",), "table_setting": ("carafe",), "play_loft": ("length", "D", "deck"), "felt_cloud": ("colour", "s", "hang"), "low_shelf": ("length", "h"),
          "gate": ("width",), "story_wall": ("length",), "floor_cushion": ("colour", "r"), "rug_round": ("d", "colour"), "kitchenette": ("length",),
          "stair_guard": ("gap", "gaps", "gates", "r_in", "a0"), "felt_banner": ("motif", "colour", "h"), "staff_lockers": ("n",), "bunting": ("length", "sag"),
          "tube_slide": ("hatches", "a_top", "turns_deg", "run", "stair_a0"), "ripstick": ("colour",), "tricycle": ("colour",), "strider": ("colour",), "wheel_rack": ("length",), "art_labels": ("width", "height", "z0", "labels", "size"),
          "climbing_wall": ("length",), "wall_bars": ("length",), "nest_swing": ("top",), "balance_beam": ("length",), "sleep_mat": ("colour",), "mat_shelf": ("length",),
          "star_ceiling": ("size", "hang"), "pram": ("colour",), "gear_rack": ("length",), "log_bench": ("length",), "trike_loop": ("rx", "ry"),
          "terrace_slide": ("drop",), "stump": ("r", "h"),
          "laksetrappa": ("rails", "rungs", "cables", "fish"), "glass_floor": ("depth",), "speed_gates": ("cabs", "lanes", "open_"),
          "glass_fence": ("length",), "floor_strip": ("length", "w", "style"), "bridge_bench": ("length",), "deck_sofa": ("length",),
          "deck_table": ("d", "h"), "ir_heater": ("z_top",), "slide_wall": ("length", "rise", "n", "state", "head"), "linear_light": ("length", "z_ceiling"),
          "floor_grazer": ("length",), "oculus": ("r", "z_ceiling"),
          "locker_hall": ("length", "D", "drums", "r_in", "r_out", "mouth", "n", "slots"), "round_seat": ("d",), "wall_waterfall": ("length", "d"),
          "grooming_bar": ("length",), "shoe_cubbies": ("length",), "towel_shelf": ("length",), "uvc_plate": ("length", "D"), "auto_door": ("w", "h"),
          "shower_cell": ("w", "d", "open_door", "accessible"), "fossen": ("w", "d"), "wash_place": ("w", "d"), "stone_bench": ("length",),
          "vaskebjorn": ("ring",), "slat_canopy": ("L", "W"), "stone_lining": ("length",), "slipper_cabinet": ("length",), "robe_wall": ("length",), "towel_warmer": ("length",)}
ARGNAME = {"length": "L", "height": "h"}


def proto_key(f):
    """A furnishing's builder kwargs + its prototype key (kind + parameter set)."""
    kind = f["kind"]
    keys = PARAMS.get(kind, ())
    kw = {}
    for k in keys:
        if k in f:
            name = k
            if kind in ("sofa", "communal_table", "bench", "boot_bench", "reception_desk", "window_counter", "vanity", "changing_unit", "cubbies",
                        "play_loft", "low_shelf", "story_wall", "kitchenette", "climbing_wall", "wall_bars", "balance_beam",
                        "gear_rack", "log_bench", "mat_shelf", "wheel_rack", "bunting", "window_nest", "dance_mirror", "music_wall",
                        "glass_fence", "floor_strip", "bridge_bench", "deck_sofa", "slide_wall", "linear_light", "floor_grazer",
                        "locker_hall", "wall_waterfall", "grooming_bar", "shoe_cubbies", "towel_shelf", "uvc_plate", "stone_bench",
                        "slipper_cabinet", "robe_wall", "towel_warmer", "stone_lining") and k == "length":
                name = "L"
            if kind == "bar_stool" and k == "height":
                name = "h"
            if kind == "gate" and k == "width":
                name = "w"
            kw[name] = tuple(tuple(v) if isinstance(v, list) else v for v in f[k]) if isinstance(f[k], list) else f[k]
    key = kind + "|" + "|".join(f"{k}={v}" for k, v in sorted(kw.items()))
    return kw, key


def build_all(model, MAT, coll):
    """Instance every furnishing in model['furnishings'] (one prototype collection per kind + parameter set)."""
    materials(MAT)
    count = 0
    for f in model.get("furnishings", []):
        kind = f["kind"]
        kw, key = proto_key(f)
        if key not in PROTO:
            pc = bpy.data.collections.new(f"proto_{kind}_{len(PROTO)}")
            P = Part(pc.name)
            BUILDERS[kind](P, **kw)
            P.build(pc, bevel={"wipe_station": 0.0, "rug": 0.0, "rug_round": 0.0, "soft_play": 0.03, "floor_cushion": 0.0, "foam_fortress": 0.04, "floor_track": 0.0, "hopscotch": 0.0}.get(kind, 0.004))
            PROTO[key] = pc
        e = bpy.data.objects.new(f["id"], None)
        e.instance_type = "COLLECTION"; e.instance_collection = PROTO[key]
        e.location = (f["at"][0], f["at"][1], f["z"]); e.rotation_euler = (0, 0, math.radians(f.get("rot_deg", 0)))
        coll.objects.link(e); count += 1
        L_ = f.get("light")
        if L_:  # a real light source with the fitting
            ld = bpy.data.lights.new(f["id"] + "_light", L_["type"]); ld.energy = L_["energy"]; ld.color = L_.get("color", (1, 1, 1))
            if L_["type"] == "SPOT":
                ld.spot_size = math.radians(L_.get("spot_deg", 45)); ld.spot_blend = L_.get("blend", 0.6); ld.shadow_soft_size = L_.get("radius", 0.03)
            elif L_["type"] == "AREA":
                ld.shape = "RECTANGLE"; ld.size = L_.get("size", 0.1); ld.size_y = L_.get("size_y", 0.1)
            lo = bpy.data.objects.new(f["id"] + "_light", ld); coll.objects.link(lo)
            ox, oy, oz = L_.get("offset", (0, 0, 0)); r = math.radians(f.get("rot_deg", 0))
            lo.location = (f["at"][0] + ox * math.cos(r) - oy * math.sin(r), f["at"][1] + ox * math.sin(r) + oy * math.cos(r), f["z"] + oz)
            if L_.get("aim"):
                lo.rotation_euler = (Vector(L_["aim"]) - lo.location).to_track_quat("-Z", "Y").to_euler()
            else:  # wall light: emit away from the wall
                lo.rotation_euler = (Vector((math.cos(r - math.pi / 2), math.sin(r - math.pi / 2), 0)) * -1).to_track_quat("-Z", "Y").to_euler()
    return count

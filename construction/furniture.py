"""Furniture, fixtures and doors, designed for The Gym (every piece generated here; only textures are downloaded).

Language: Nordic mid-century, regional, minimal. Light oak with soft (bevelled) edges, tapered round legs, cream wool boucle,
cognac leather, sheepskin, light honed stone tops, dark bronze / blackened steel only for small hardware.
Local frame of every piece: origin on the floor, width along x, FRONT (where you sit / face from) towards +y.
Real sizes throughout (see tools/furnish.py). Pieces are built once per kind (+ size) and instanced.
"""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import bl_common as bc

PROTO = {}
M = {}


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

    def box(self, mat, c, size, rz=0.0, rx=0.0, ry=0.0):
        b = self.bm(mat)
        g = bmesh.ops.create_cube(b, size=1.0)["verts"]
        bmesh.ops.scale(b, vec=size, verts=g)
        R = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X")
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=R)
        bmesh.ops.translate(b, verts=g, vec=c)

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

    def rod(self, mat, p0, p1, r0, r1=None, seg=16):
        """Tapered round member between two points (legs, spindles, cables)."""
        p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
        b = self.bm(mat)
        g = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r0, radius2=r0 if r1 is None else r1, depth=L)["verts"]
        bmesh.ops.translate(b, verts=g, vec=(0, 0, L / 2))
        bmesh.ops.rotate(b, verts=g, cent=(0, 0, 0), matrix=d.to_track_quat("Z", "Y").to_matrix())
        bmesh.ops.translate(b, verts=g, vec=p0)

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
def lounge_chair(P):
    """'Elverum' lounge chair: walnut frame with wide flat arms, deep oat wool cushions raked back 14°, a sheepskin over the back.
    0.78 x 0.82 x 0.76; seat at 0.40."""
    wd = M["walnut"]
    W = 0.78
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.035)
        P.rod(wd, (x, 0.34, 0), (x, 0.31, 0.6), 0.022, 0.019)        # front leg runs up into the arm
        P.rod(wd, (x, -0.37, 0), (x, -0.33, 0.58), 0.022, 0.019)
        P.box(wd, (x, -0.01, 0.605), (0.075, 0.76, 0.028))           # wide flat arm
        P.box(wd, (x, -0.02, 0.2), (0.028, 0.66, 0.04))              # side rail carrying the seat
    P.box(wd, (0, 0.31, 0.2), (W - 0.07, 0.035, 0.05))
    P.box(wd, (0, -0.33, 0.2), (W - 0.07, 0.035, 0.05))
    P.box(M["boucle"], (0, 0.03, 0.33), (W - 0.13, 0.66, 0.15))      # seat cushion
    P.box(M["boucle"], (0, -0.27, 0.61), (W - 0.13, 0.15, 0.5), rx=math.radians(14))  # back cushion raked back
    P.box(M["sheepskin"], (0, -0.205, 0.66), (W - 0.24, 0.025, 0.44), rx=math.radians(14))


def sofa(P, L=2.2):
    wd = M["walnut"]
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.035)
        P.rod(wd, (x, 0.36, 0), (x, 0.33, 0.6), 0.024, 0.02); P.rod(wd, (x, -0.39, 0), (x, -0.35, 0.58), 0.024, 0.02)
        P.box(wd, (x, -0.01, 0.605), (0.08, 0.8, 0.028)); P.box(wd, (x, -0.02, 0.2), (0.028, 0.7, 0.04))
    P.box(wd, (0, 0.33, 0.2), (L - 0.07, 0.035, 0.05)); P.box(wd, (0, -0.35, 0.2), (L - 0.07, 0.035, 0.05))
    for x in (-L * 0.15, L * 0.15):  # extra centre legs
        P.rod(wd, (x, 0.33, 0), (x, 0.33, 0.18), 0.02); P.rod(wd, (x, -0.35, 0), (x, -0.35, 0.18), 0.02)
    cw = (L - 0.15) / 3
    for k in (-1, 0, 1):
        P.box(M["boucle"], (k * cw, 0.03, 0.33), (cw - 0.012, 0.7, 0.15))
        P.box(M["boucle"], (k * cw, -0.29, 0.61), (cw - 0.012, 0.15, 0.5), rx=math.radians(13))
    P.box(M["sheepskin"], (-cw, -0.225, 0.66), (0.52, 0.025, 0.44), rx=math.radians(13))


def dining_chair(P):
    """Cafe chair: walnut, a curved steam-bent back band (100° arc) carried by the rear legs that run straight up into it,
    an upholstered cognac leather seat on a walnut frame at 0.45. Light, calm, mid-century."""
    wd = M["walnut"]
    for sx in (-1, 1):
        P.rod(wd, (sx * 0.205, 0.205, 0), (sx * 0.185, 0.185, 0.43), 0.014, 0.019)          # front legs, tapered
        P.rod(wd, (sx * 0.2, -0.235, 0), (sx * 0.175, -0.185, 0.8), 0.014, 0.018)          # rear legs up into the back
        P.rod(wd, (sx * 0.19, -0.15, 0.16), (sx * 0.19, 0.16, 0.16), 0.009)                 # side stretchers
    P.rod(wd, (-0.19, 0.0, 0.2), (0.19, 0.0, 0.2), 0.009)
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
    r = 0.205
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


def glass_door(P, width=1.6, height=2.3):
    """Framed glass secure door (pair) with a long oak pull."""
    fr = M["frame"]
    for s in (-1, 1):
        cx = s * width / 4
        P.box(M["glass"], (cx, 0, height / 2), (width / 2 - 0.08, 0.012, height - 0.08))
        for x in (cx - width / 4 + 0.025, cx + width / 4 - 0.025):
            P.box(fr, (x, 0, height / 2), (0.05, 0.06, height))
        for z in (0.03, height - 0.03):
            P.box(fr, (cx, 0, z), (width / 2, 0.06, 0.06))
        P.rod(M["oak"], (s * 0.06, 0.06, 0.8), (s * 0.06, 0.06, 1.5), 0.014)


def baffle_screen(P, width=2.6, height=2.4):
    """WC privacy baffle: oak slats 45 @ 65 on a black core, so the open entry hides the room behind."""
    P.box(M["felt"], (0, -0.02, height / 2), (width, 0.03, height))
    for x in np.arange(-width / 2 + 0.0325, width / 2, 0.065):
        P.box(M["oak"], (x, 0.0, height / 2), (0.045, 0.02, height))


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


def _wc_pan(P, x, side_rail=0):
    """Wall-hung white WC (seat at 0.46) with a blackened-steel flush plate, roll holder and (accessible) fold-up rails."""
    P.box(M["ceramic"], (x, 0.09, 0.4), (0.36, 0.18, 0.2))
    P.blob(M["ceramic"], (x, 0.33, 0.36), (0.18, 0.25, 0.12), z_cut=0.28)
    P.box(M["ceramic"], (x, 0.32, 0.455), (0.37, 0.46, 0.02))
    P.box(M["steel"], (x, 0.004, 1.05), (0.25, 0.008, 0.16))
    P.rod(M["steel"], (x + 0.38, 0.0, 0.75), (x + 0.38, 0.12, 0.75), 0.008, seg=8)
    P.rod(M["steel"], (x + 0.38, 0.12, 0.75), (x + 0.5, 0.12, 0.75), 0.008, seg=8)
    for s_ in ([-1, 1] if side_rail else []):  # fold-up grab rails either side, 0.35 off the pan centre, at 0.8
        xr = x + s_ * 0.35
        P.box(M["steel"], (xr, 0.03, 0.8), (0.07, 0.06, 0.16))
        P.rod(M["steel"], (xr, 0.05, 0.8), (xr, 0.85, 0.8), 0.016, seg=12)


def wc_cells(P, n=4, w=1.1, depth=1.65, h=2.6, style="wc", door_at=0.0, pan_at=0.0):
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
    _staved_front(P, -W / 2, W / 2, h, depth + 0.01, doors)
    P.box(M["oak"], (0, depth - 0.04, h / 2), (W - 0.03, 0.012, h))  # plain oak face on the inside of the front (doors closed)
    for (xa, xb, hd) in doors:  # small brass pull on the latch side (an accent) + a blackened-steel occupancy turn
        P.box(M["brass"], (xb - 0.09, depth + 0.035, 1.05), (0.016, 0.02, 0.3))
        P.cyl(M["steel"], (xb - 0.09, depth + 0.025, 1.3), 0.022, 0.012, seg=20)
    if style == "wc":
        for k in range(n):
            _wc_pan(P, -W / 2 + (k + 0.5) * w)
            P.rod(M["steel"], (-W / 2 + (k + 0.5) * w - 0.2, depth - 0.02, 1.7), (-W / 2 + (k + 0.5) * w - 0.2, depth - 0.08, 1.7), 0.01, seg=8)  # coat hook
    elif style == "accessible":
        _wc_pan(P, pan_at, side_rail=1)
        bx = -pan_at * 0.9 if abs(pan_at) > 0.3 else W / 2 - 0.45
        P.box(M["stone"], (bx, 0.24, 0.80), (0.5, 0.45, 0.06))  # small basin slab, knee space below (accessible)
        P.box(M["ceramic"], (bx, 0.24, 0.775), (0.38, 0.3, 0.02))
        P.rod(M["steel"], (bx, 0.0, 0.98), (bx, 0.16, 0.98), 0.012, seg=12)
        P.box(M["mirror"], (bx, 0.004, 1.45), (0.5, 0.006, 0.8))
        sx = W / 2 - 0.015 if bx < 0 else -W / 2 + 0.015  # fold-down changing table on the side panel away from the basin
        P.box(M["oak"], (sx - np.sign(sx) * 0.05, depth / 2, 0.9), (0.1, 0.8, 0.5))


def vanity(P, L=3.0, n=3):
    """Honed-stone trough vanity on the wall: 120 mm slab, top at 0.86, 0.5 deep, n basins sunk into it; wall-mounted
    blackened-steel spouts; a full-length mirror (1.0 tall) in a slim oak frame; a slim steel light channel above it."""
    d, t, top = 0.5, 0.12, 0.86
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
    P.box(M["oak"], (0, 0.012, top + 0.25 + 0.52), (L + 0.03, 0.022, 1.04))   # oak frame behind the mirror
    P.box(M["mirror"], (0, 0.025, top + 0.25 + 0.52), (L - 0.02, 0.006, 1.0))
    P.box(M["steel"], (0, 0.04, top + 1.37), (L, 0.06, 0.04))                 # light channel above the mirror
    P.box(M["opal"], (0, 0.04, top + 1.349), (L - 0.04, 0.05, 0.003))


def urinals(P, n=3, pitch=0.75):
    """Wall-hung white urinals (rim 0.62; the first lower, 0.5, for children) with oak privacy screens between them."""
    for k in range(n):
        x = -(n - 1) * pitch / 2 + k * pitch
        rim = 0.5 if k == 0 else 0.62
        P.cyl(M["ceramic"], (x, 0.13, rim - 0.48), 0.165, 0.62, seg=40)       # a slim upright pod, round to the front
        P.box(M["ceramic"], (x, 0.04, rim - 0.17), (0.33, 0.08, 0.62))        # flat back on the wall
        P.cyl(M["steel"], (x, 0.16, rim - 0.48), 0.035, 0.004, seg=16)        # outlet glimpse at the base
        P.box(M["steel"], (x, 0.004, rim + 0.42), (0.08, 0.008, 0.12))
    for k in range(n - 1):
        x = -(n - 1) * pitch / 2 + (k + 0.5) * pitch
        P.box(M["oak"], (x, 0.24, 1.05), (0.03, 0.45, 0.9))


def cell_light(P, z_ceiling=2.6):
    """Small opal disc under a WC cell lid."""
    P.cyl(M["steel"], (0, 0, z_ceiling - 0.012), 0.06, 0.012, seg=24)
    P.cyl(M["opal"], (0, 0, z_ceiling - 0.014), 0.05, 0.003, seg=24)


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


BUILDERS = {
    "lounge_chair": lounge_chair, "sofa": sofa, "dining_chair": dining_chair, "bar_stool": bar_stool, "cafe_table": cafe_table,
    "side_table": side_table, "coffee_table": coffee_table, "communal_table": communal_table, "bench": bench, "boot_bench": boot_bench,
    "rug": rug, "reception_desk": reception_desk, "cafe_island": cafe_island, "ring_pendant": ring_pendant, "pendant_opal": pendant_opal,
    "glass_screen": glass_screen, "sliding_doors": sliding_doors, "vestibule_lid": vestibule_lid, "door_slatted": door_slatted,
    "lift_doors": lift_doors, "glass_door": glass_door, "baffle_screen": baffle_screen, "window_counter": window_counter,
    "relief_art": relief_art, "porch_floor": porch_floor, "canvas_art": canvas_art,
    "wall_light": wall_light, "downlight": downlight, "gallery_spot": gallery_spot, "entrance_mat": entrance_mat,
    "wc_cells": wc_cells, "vanity": vanity, "urinals": urinals, "cell_light": cell_light, "light_only": light_only,
}
PARAMS = {"sofa": ("length",), "communal_table": ("length",), "bench": ("length",), "boot_bench": ("length",), "rug": ("size",),
          "reception_desk": ("length",), "cafe_island": ("r_out", "gap_deg"), "ring_pendant": ("r", "hang"), "pendant_opal": ("hang",),
          "glass_screen": ("width", "height", "door"), "sliding_doors": ("width", "height"), "vestibule_lid": ("size", "height"),
          "door_slatted": ("width", "height"), "lift_doors": ("width", "height"), "glass_door": ("width", "height"),
          "baffle_screen": ("width", "height"), "window_counter": ("length",), "bar_stool": ("height",), "relief_art": ("width", "height"), "porch_floor": ("size",), "canvas_art": ("width", "height", "image"), "downlight": ("z_ceiling",), "gallery_spot": ("z_ceiling",), "entrance_mat": ("size", "style"),
          "wc_cells": ("n", "w", "depth", "style", "door_at", "pan_at"), "vanity": ("length", "n"), "urinals": ("n", "pitch"), "cell_light": ("z_ceiling",)}
ARGNAME = {"length": "L", "height": "h"}


def build_all(model, MAT, coll):
    """Instance every furnishing in model['furnishings'] (one prototype collection per kind + parameter set)."""
    materials(MAT)
    count = 0
    for f in model.get("furnishings", []):
        kind = f["kind"]
        keys = PARAMS.get(kind, ())
        kw = {}
        for k in keys:
            if k in f:
                name = k
                if kind in ("sofa", "communal_table", "bench", "boot_bench", "reception_desk", "window_counter", "vanity") and k == "length":
                    name = "L"
                if kind == "bar_stool" and k == "height":
                    name = "h"
                kw[name] = tuple(f[k]) if isinstance(f[k], list) else f[k]
        key = kind + "|" + "|".join(f"{k}={v}" for k, v in sorted(kw.items()))
        if key not in PROTO:
            pc = bpy.data.collections.new(f"proto_{kind}_{len(PROTO)}")
            P = Part(pc.name)
            BUILDERS[kind](P, **kw)
            P.build(pc, bevel=0.0 if kind in ("rug",) else 0.004)
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

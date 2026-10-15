"""Kulpen, the outdoor sauna (stage 6; VISION "Kulpen", Roman 2026-10-14): the shell, from model/layouts/sauna.json.

Built like the real thing, in order: foundation (slab on grade, the buried walls in concrete), the frame (timber walls, the plates,
ridge, rafters, the porch post + header), the envelope (tarred board-on-board, the window, the sod roof on oak sarking, the berm
the roof runs down into, the granite chimney), the inside (thermo-aspen hot room, light aspen changing room, slate floors), and
the decks (Kebony on joists, beams and piles to the rock; the steps; granite slab steps into the pool; the flume).
The furniture, heater, doors and the tub are furnishings (tools/furnish.py, construction/furniture.py).

The roof: a gable over the porch (south), a hip to the north; the west and north planes carry on into the berm, so from the trail it
reads as a grassy mound with a stone chimney. One function gives the sod's top everywhere (zroof); the berm is that surface carried
on past the walls and eased down to the ground at 1:1.6.
"""
import json
import math
from pathlib import Path

import bmesh
import bpy
import numpy as np

import bl_common as bc
import furniture as fu

ROOT = Path(__file__).resolve().parents[1]
LAY = json.loads((ROOT / "model" / "layouts" / "sauna.json").read_text())
LV = LAY["levels"]
FL, DECK, WATER, PLATE, HOT_C = LV["floor"], LV["deck"], LV["water"], LV["plate"], LV["hot_ceiling"]
CH_C = FL + 2.4                       # the changing room's ceiling
X0, X1, Y0, Y1 = -25.5, -20.5, 92.0, 100.0
YP, YH, T, TP = 93.4, 96.05, 0.25, 0.15
XI0, XI1 = X0 + T, X1 - T
XR = -23.0                            # the ridge
S = math.tan(math.radians(27))        # torvtak pitch
EAVE_E, GABLE = 0.6, 0.4              # east eave, the porch gable's overhang
SOD, SARK, RAFT = 0.425, 0.025, 0.2   # sod + soil + membrane, oak sarking, rafters
R = PLATE + RAFT + SARK + SOD + S * (XR - X0)
YHIP = Y1 - (XR - X0)                 # 97.5: the hip starts here
XE = X1 + EAVE_E
CHIM = (-23.35, 96.6)
BERM = 1 / 1.6
LANDING = FL - 0.02
DECKS = [  # (x0, y0, x1, y1, top): the porch + landing at the floor, the lower deck by the pool
    (XI0, Y0, -18.6, YP, LANDING), (X1, YP, -18.6, 95.6, LANDING),
    (-17.4, Y0, -14.4, 95.6, DECK), (-18.0, 95.6, -14.4, 98.6, DECK)]


def zroof(x, y):
    """Top of the sod (and of the berm right at the walls)."""
    return R - S * max(abs(x - XR), y - YHIP)


def _hb(H, x, y):
    """Finished ground, bilinear on the 1 m grid (H[r, c] sits at x = c - 999.5, y = r - 999.5)."""
    fx, fy = x + 999.5, y + 999.5; i, j = int(math.floor(fy)), int(math.floor(fx)); ty, tx = fy - i, fx - j
    return float(H[i, j] * (1 - tx) * (1 - ty) + H[i, j + 1] * tx * (1 - ty) + H[i + 1, j] * (1 - tx) * ty + H[i + 1, j + 1] * tx * ty)


def grade(H):
    """Stage 6 earthworks: the ground under the decks taken down just clear of the beams (the piles go on to the rock)."""
    H = H.copy()
    for x0, y0, x1, y1, top in DECKS + [(-18.6, 92.6, -17.4, 95.0, DECK)]:
        for r in range(int(math.floor(y0 + 999.5)), int(math.ceil(y1 + 999.5)) + 1):
            for c in range(int(math.floor(x0 + 999.5)), int(math.ceil(x1 + 999.5)) + 1):
                H[r, c] = min(H[r, c], top - 0.42)
    return H


def berm_z(x, y):
    """The mound: the roof's west + north planes carried on past the walls and eased down at 1:1.6. West of the west wall (south of
    the porch only behind the wing wall), north of the north wall up to the east wall's line; None elsewhere."""
    if y < Y0 and x > X0 - 0.4:
        return None
    if not (x <= X0 + 1e-6 or (y >= Y1 - 1e-6 and x <= X1 + 1e-6)):
        return None
    xc, yc = min(max(x, X0), X1), min(max(y, Y0), Y1)
    return zroof(xc, yc) - math.hypot(x - xc, y - yc) * BERM


def wing_walls(H):
    """The two granite wing walls where the mound ends open: (x0, x1, y0, y1, berm-side x) each, as far as the berm stands above
    the ground."""
    out = []
    for xa, xb, ys, sg, xl in ((X0 - 0.4, X0, Y0, -1, X0 - 0.4), (X1, X1 + 0.4, Y1, 1, X1)):
        y = ys
        while abs(y - ys) < 9:
            zt = berm_z(xl, y + sg * 0.1)
            if zt is None or zt < _hb(H, (xa + xb) / 2, y + sg * 0.1) + 0.05:
                break
            y += sg * 0.1
        out.append((xa, xb, min(ys, y), max(ys, y), xl, sg))
    return out


PATCH = (-37.5, 83.5, -7.5, 110.5)   # the fine ground round Kulpen (on the 1 m grid's lines)


def patch_slices(DX0, DY0):
    """The 1 m terrain quads the fine patch replaces: (rows, cols) into the cropped grid's quads."""
    return slice(int(PATCH[1] - DY0 - 0.5), int(PATCH[3] - DY0 - 0.5)), slice(int(PATCH[0] - DX0 - 0.5), int(PATCH[2] - DX0 - 0.5))


def ground_patch(H, GM, DX0, DY0, TM, coll, res=0.25):
    """The ground round Kulpen at 0.25 m with the mound grown out of it (no separate sheet): the finished ground, raised to the
    berm with a soft toe, the site's own ground masks (+ meadow on the mound, patchy), cut exactly round the enclosed sauna and
    the wing walls."""
    xs = np.arange(PATCH[0], PATCH[2] + 1e-6, res); ys = np.arange(PATCH[1], PATCH[3] + 1e-6, res)
    X, Y = np.meshgrid(xs, ys)
    def bil(A, ox, oy):
        fx, fy = X - ox, Y - oy; j, i = np.floor(fx).astype(int), np.floor(fy).astype(int); tx, ty = fx - j, fy - i
        return A[i, j] * (1 - tx) * (1 - ty) + A[i, j + 1] * tx * (1 - ty) + A[i + 1, j] * (1 - tx) * ty + A[i + 1, j + 1] * tx * ty
    g = bil(H, -999.5, -999.5)
    b = np.vectorize(lambda x, y: np.nan if berm_z(x, y) is None else berm_z(x, y))(X, Y)
    k = 0.22
    lift = np.where(np.isnan(b), 0.0, k * np.logaddexp(0, (np.nan_to_num(b, nan=-99) - g) / k))
    Z = g + lift
    w = np.clip(lift / 0.5, 0, 1)
    nz = 0.5 + 0.25 * np.sin(X * 1.7 + Y * 0.6) * np.sin(Y * 1.3 - X * 0.4) + 0.25 * np.sin(X * 4.1 + 1.3) * np.sin(Y * 3.7 + 0.4)
    attrs = {k_: bil(v, DX0 + 0.5, DY0 + 0.5).astype(np.float32) for k_, v in GM.items()}
    attrs["lawn"] = np.maximum(attrs["lawn"], w * (0.35 + 0.65 * nz)).astype(np.float32)
    attrs["clear"] = np.maximum(attrs["clear"], w * 0.8).astype(np.float32)
    attrs["meadow"] = np.clip(w * 1.3 + 0.25 * (lift > 0.02), 0, 1).astype(np.float32)
    ob = bc.grid_mesh("terrain_kulpen", Z.astype(np.float32), PATCH[0], PATCH[1], res, attrs, coll=coll)
    ob.data.materials.append(TM)
    vs, fs = [], []
    boxes = [(X0, YP, X1, Y1), (X0, Y0, X0 + T + 0.1, YP)] + [(xa, ya, xb, yb) for xa, xb, ya, yb, _, _ in wing_walls(H)]
    for x0_, y0_, x1_, y1_ in boxes:
        q = len(vs)
        vs += [(x0_, y0_, -4), (x1_, y0_, -4), (x1_, y1_, -4), (x0_, y1_, -4), (x0_, y0_, 9), (x1_, y0_, 9), (x1_, y1_, 9), (x0_, y1_, 9)]
        fs += [(q, q + 3, q + 2, q + 1), (q + 4, q + 5, q + 6, q + 7), (q, q + 1, q + 5, q + 4), (q + 1, q + 2, q + 6, q + 5), (q + 2, q + 3, q + 7, q + 6), (q + 3, q, q + 4, q + 7)]
    cut = bc.mesh_from("kulpen_voids", vs, fs, smooth=False, coll=coll); cut.hide_render = True; cut.hide_viewport = True
    md = ob.modifiers.new("voids", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cut; md.solver = "EXACT"
    for a_ in ("use_hole_tolerant", "use_self"):
        try:
            setattr(md, a_, True)
        except AttributeError:
            pass
    ob.data.polygons.foreach_set("use_smooth", np.ones(len(ob.data.polygons), bool))
    return ob


def meadow_nodes(name, protos, density, attr=None, seed=0):
    """Natural grass: patchy (density from a noise field, x the named attribute), three kinds of tuft mixed, sizes 0.45-1.4, each
    leaning a little; never the even carpet of a lawn."""
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.inputs["Seed"].default_value = seed
    L.new(gi.outputs[0], dp.inputs["Mesh"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.55; nz.inputs["Detail"].default_value = 3.0
    nz2 = N.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 3.0
    mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.38; mr.inputs[2].default_value = 0.66; mr.inputs[3].default_value = 0.08; mr.inputs[4].default_value = 1.0
    L.new(nz.outputs["Fac"], mr.inputs[0])
    m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY_ADD"; L.new(nz2.outputs["Fac"], m2.inputs[0]); m2.inputs[1].default_value = 0.8; m2.inputs[2].default_value = 0.6
    d = N.new("ShaderNodeMath"); d.operation = "MULTIPLY"; L.new(mr.outputs[0], d.inputs[0]); L.new(m2.outputs[0], d.inputs[1])
    d2 = N.new("ShaderNodeMath"); d2.operation = "MULTIPLY"; L.new(d.outputs[0], d2.inputs[0]); d2.inputs[1].default_value = density
    dens = d2.outputs[0]
    if attr:
        na = N.new("GeometryNodeInputNamedAttribute"); na.data_type = "FLOAT"; na.inputs["Name"].default_value = attr
        d3 = N.new("ShaderNodeMath"); d3.operation = "MULTIPLY"; L.new(dens, d3.inputs[0]); L.new(na.outputs["Attribute"], d3.inputs[1]); dens = d3.outputs[0]
    L.new(dens, dp.inputs["Density"])
    nrm = N.new("GeometryNodeInputNormal"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(nrm.outputs[0], sep.inputs[0])
    cmp = N.new("FunctionNodeCompare"); cmp.data_type = "FLOAT"; cmp.operation = "GREATER_THAN"; cmp.inputs["B"].default_value = 0.5
    L.new(sep.outputs["Z"], cmp.inputs["A"]); L.new(cmp.outputs[0], dp.inputs["Selection"])
    jn = N.new("GeometryNodeGeometryToInstance")
    for p in protos:
        oi = N.new("GeometryNodeObjectInfo"); oi.inputs[0].default_value = p; oi.transform_space = "ORIGINAL"; L.new(oi.outputs["Geometry"], jn.inputs[0])
    ip = N.new("GeometryNodeInstanceOnPoints"); ip.inputs["Pick Instance"].default_value = True
    rnd = N.new("FunctionNodeRandomValue"); rnd.data_type = "INT"; rnd.inputs["Max"].default_value = len(protos) - 1; rnd.inputs["Seed"].default_value = seed + 3
    L.new(rnd.outputs["Value"], ip.inputs["Instance Index"])
    rot = N.new("FunctionNodeRandomValue"); rot.data_type = "FLOAT_VECTOR"; rot.inputs["Min"].default_value = (-0.22, -0.22, 0); rot.inputs["Max"].default_value = (0.22, 0.22, 6.283)
    rot.inputs["Seed"].default_value = seed + 5
    sc = N.new("FunctionNodeRandomValue"); sc.data_type = "FLOAT"; sc.inputs["Min"].default_value = 0.45; sc.inputs["Max"].default_value = 1.4; sc.inputs["Seed"].default_value = seed + 7
    e2r = N.new("FunctionNodeEulerToRotation"); L.new(rot.outputs["Value"], e2r.inputs[0]); L.new(e2r.outputs[0], ip.inputs["Rotation"])
    L.new(sc.outputs["Value"], ip.inputs["Scale"])
    L.new(dp.outputs["Points"], ip.inputs["Points"]); L.new(jn.outputs[0], ip.inputs["Instance"])
    jo = N.new("GeometryNodeJoinGeometry"); L.new(gi.outputs[0], jo.inputs[0]); L.new(ip.outputs[0], jo.inputs[0])
    L.new(jo.outputs[0], go.inputs[0])
    return ng


def add_grass(protos):
    """Grass on the mound (the ground patch, where 'meadow' says) and on the sod roof."""
    pa = bpy.data.objects.get("terrain_kulpen")
    if pa:
        md = pa.modifiers.new("grass", "NODES"); md.node_group = meadow_nodes("GN_grass_kulpen_berm", protos, 70, attr="meadow", seed=11)
    for o in [o for o in bpy.data.objects if o.name.startswith("KU-sodroof")]:
        md = o.modifiers.new("grass", "NODES"); md.node_group = meadow_nodes("GN_grass_kulpen_roof", protos, 70, seed=12)


def keep_trees(x, y):
    """Forest points that stay: none whose trunk or crown (~4 m) would reach into the building, the berm or the decks."""
    return ~((x > X0 - 5.5) & (x < -12.0) & (y > Y0 - 3.0) & (y < Y1 + 5.0))


def _vprism(P, mat, pts, ztop, thick):
    """A plan polygon (CCW) with a sloped top (ztop(x, y)), extruded straight down by thick."""
    b = P.bm(mat)
    t = [b.verts.new((x, y, ztop(x, y))) for x, y in pts]; u = [b.verts.new((x, y, ztop(x, y) - thick)) for x, y in pts]
    b.faces.new(t); b.faces.new(u[::-1]); n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        b.faces.new((t[i], u[i], u[j], t[j]))


def _zbox(P, mat, x0, y0, z0, x1, y1, z1):
    P.box(mat, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)))


def _wall(P, mat, axis, s0, s1, c0, c1, z0, z1, ops=()):
    """An axis-aligned wall layer from s0 to s1 (along x if axis == 'x' else along y), c0..c1 across, holes for the openings
    (s_a, s_b, z_a, z_b)."""
    cuts = sorted({s0, s1, *[v for o in ops for v in o[:2] if s0 < v < s1]})
    for a, b in zip(cuts, cuts[1:]):
        o = next((o for o in ops if o[0] <= (a + b) / 2 <= o[1]), None)
        bands = [(z0, z1)] if o is None else [(z0, o[2]), (o[3], z1)]
        for za, zb in bands:
            if zb - za > 0.005:
                _zbox(P, mat, *((a, c0, za, b, c1, zb) if axis == "x" else (c0, a, za, c1, b, zb)))


def _boards(P, mat, axis, s0, s1, c, n, z0, z1, ops=(), pitch=0.1, w=0.092, t=0.016, top=None):
    """Vertical boards on a wall face at c (thickness out along n = +-1), split round openings; top(s) can slope the board ends."""
    s = s0 + pitch / 2
    while s < s1 - 0.01:
        o = next((o for o in ops if o[0] - w / 2 < s < o[1] + w / 2), None)
        zt = z1 if top is None else top(s)
        for za, zb in ([(z0, zt)] if o is None else [(z0, o[2]), (o[3], zt)]):
            if zb - za > 0.01:
                cc = c + n * t / 2
                _zbox(P, mat, *((s - w / 2, cc - t / 2, za, s + w / 2, cc + t / 2, zb) if axis == "x" else (cc - t / 2, s - w / 2, za, cc + t / 2, s + w / 2, zb)))
        s += pitch


def build(MAT, H, coll):
    """Everything above; H = the (graded) finished ground. Returns the parts made."""
    M = fu.materials(MAT); fu._kulpen_mats()
    tar, oak, st, a_hot, a_lt = M["tar"], M["oak"], M["steel"], M["aspen_thermo"], M["aspen"]
    conc, clt, deck = MAT["concrete"], MAT.get("clt_natural", MAT["clt"]), MAT["decking"]
    sod = MAT["sod"]; gran, slate = M["granite_split"], M["slate_floor"]
    glulam = MAT["glulam"]; memb = MAT["membrane"]
    parts = {k: fu.Part(f"KU-{k}") for k in ("foundation", "frame", "envelope", "inside", "decks")}
    Pf, Pr, Pe, Pi, Pd = parts["foundation"], parts["frame"], parts["envelope"], parts["inside"], parts["decks"]
    rng = np.random.default_rng(66)
    ops_e = [(94.3, 95.2, FL, FL + 2.05), (96.6, 99.1, FL + 0.7, FL + 2.1)]   # east wall: the deck door, the window
    ops_p = [(-24.6, -23.7, FL, FL + 2.05)]                                    # porch wall: the front door
    ops_h = [(-23.75, -23.25, FL + 0.3, FL + 0.75), (-21.75, -21.0, FL, FL + 1.9)]  # hot-room wall: the heater's neck, the door

    # ---------------------------------------------------------------- foundation: slab on grade, the buried walls (concrete, membrane)
    _zbox(Pf, conc, X0, YP, FL - 0.42, X1, Y1, FL - 0.012)
    _zbox(Pf, conc, X0, Y0, FL - 0.42, X0 + T, YP, FL - 0.1)
    _zbox(Pf, conc, X0, Y0, FL - 0.42, X0 + T, Y1, PLATE)                       # west, retaining the berm
    _zbox(Pf, conc, X0, Y1 - T, FL - 0.42, X1, Y1, PLATE)                       # north, the same
    _zbox(Pf, memb, X0 - 0.01, Y0, FL - 0.42, X0, Y1 + 0.01, PLATE)
    _zbox(Pf, memb, X0 - 0.01, Y1, FL - 0.42, X1, Y1 + 0.01, PLATE)
    for x, y in ((-25.0, 91.85), (-20.62, 91.8)):                              # pad under the porch post / the wall end
        _zbox(Pf, conc, x - 0.25, y - 0.25, FL - 1.2, x + 0.25, y + 0.25, FL - 0.62)
    # granite plinth where the slab edge shows (east + the porch wall), dry-laid, 150 deep
    for (x0, y0, x1, y1) in ((X1 - 0.05, YP, X1 + 0.1, Y1), (XI0, YP - 0.15, X1 + 0.1, YP)):
        _zbox(Pf, gran, x0, y0, FL - 0.5, x1, y1, FL - 0.03)

    # ---------------------------------------------------------------- frame: timber walls (core), plates, ridge, rafters, porch post + header
    _wall(Pr, clt, "y", YP, Y1 - T, X1 - 0.23, X1 - 0.05, FL - 0.012, PLATE - 0.09, ops_e)       # east
    _wall(Pr, clt, "x", XI0, X1, YP + 0.02, YP + 0.2, FL - 0.012, PLATE - 0.09, ops_p)           # porch wall
    _wall(Pr, clt, "x", XI0, XI1, YH + 0.025, YH + 0.125, FL - 0.012, CH_C, ops_h)               # hot-room wall
    _zbox(Pr, glulam, X1 - 0.23, Y0 - GABLE, PLATE - 0.09, X1 - 0.05, Y1 - T, PLATE)             # east plate (on to the porch post)
    _zbox(Pr, glulam, X0, Y0 - GABLE, PLATE - 0.09, X0 + T, Y1, PLATE)                          # sill plate on the west wall
    _zbox(Pr, glulam, X0 + T, Y0 - 0.25, PLATE - 0.3, X1 - 0.23, Y0 - 0.15, PLATE)               # porch header (warm glulam)
    Pr.rod(M["tar"], (-20.62, 91.8, FL - 0.62), (-20.62, 91.8, PLATE - 0.09), 0.1, 0.09, seg=16)  # the porch post: a tarred round log
    rt = R - SOD - SARK                                                                           # rafter tops at the ridge
    _zbox(Pr, glulam, XR - 0.06, Y0 - GABLE, rt - 0.36, XR + 0.06, YHIP + 0.1, rt)                # ridge beam
    zr = lambda x, y: zroof(x, y) - SOD - SARK
    y = Y0 - GABLE + 0.04
    while y < Y1 - 0.1:                                                                           # common + jack rafters, east and west
        hx = max(0.0, y - YHIP)
        for xa, xb in ((X0 + 0.02, XR - 0.06 - hx), (XR + 0.06 + hx, XE - 0.02)):
            if xb - xa > 0.1:
                Pr.prism(glulam, [(xa, zr(xa, y)), (xb, zr(xb, y)), (xb, zr(xb, y) - RAFT), (xa, zr(xa, y) - RAFT)], y - 0.035, y + 0.035)
        y += 0.6
    x = X0 + 0.3
    while x < X1 - 0.2:                                                                           # north jacks, wall to hip
        ya = YHIP + abs(x - XR) + 0.06
        if Y1 - 0.02 - ya > 0.1:
            fu._xprism(Pr, glulam, [(ya, zr(x, ya)), (Y1 - 0.02, zr(x, Y1 - 0.02)), (Y1 - 0.02, zr(x, Y1 - 0.02) - RAFT), (ya, zr(x, ya) - RAFT)], x - 0.035, x + 0.035)
        x += 0.6
    for xe in (X0, X1):                                                                           # hip rafters
        Pr.rod(glulam, (XR, YHIP, rt - 0.1), (xe, Y1, zr(xe, Y1) - 0.1), 0.06, seg=8)

    # ---------------------------------------------------------------- envelope: cladding, the window, sarking + sod, barge boards, berm, chimney
    _wall(Pe, M["felt"], "y", YP, Y1, X1 - 0.05, X1 - 0.03, FL - 0.03, PLATE, ops_e)               # wind barrier (black)
    _wall(Pe, tar, "y", YP, Y1, X1 - 0.03, X1 - 0.01, FL - 0.03, PLATE, ops_e)                     # under-boards
    _boards(Pe, tar, "y", YP, Y1, X1 - 0.01, 1, FL - 0.03, PLATE, ops_e, pitch=0.3, w=0.1, t=0.022)  # board-on-board
    _wall(Pe, tar, "x", X0 + T, X1, YP - 0.0, YP + 0.02, FL - 0.03, PLATE, ops_p)
    _boards(Pe, tar, "x", X0 + T, X1, YP, -1, FL - 0.03, PLATE, ops_p, pitch=0.3, w=0.1, t=0.022)
    # the hot room's window: three panes in blackened-steel frames, aspen reveals + sill inside, a steel sill outside
    fr = MAT["frame"]; wy0, wy1, wz0, wz1 = 96.6, 99.1, FL + 0.7, FL + 2.1
    xf0, xf1 = X1 - 0.09, X1 - 0.01
    for z0_, z1_ in ((wz0, wz0 + 0.06), (wz1 - 0.06, wz1)):
        _zbox(Pe, fr, xf0, wy0, z0_, xf1, wy1, z1_)
    for yy in np.linspace(wy0, wy1, 4):
        _zbox(Pe, fr, xf0, max(wy0, yy - 0.03), wz0, xf1, min(wy1, yy + 0.03), wz1)
    _zbox(Pe, M["glass"], X1 - 0.062, wy0, wz0, X1 - 0.038, wy1, wz1)
    _zbox(Pe, st, X1 - 0.01, wy0 - 0.03, wz0 - 0.03, X1 + 0.05, wy1 + 0.03, wz0)
    _zbox(Pi, a_hot, XI1 - 0.05, wy0 - 0.02, wz0 - 0.03, X1 - 0.09, wy1 + 0.02, wz0)                # sill
    for yy, sg in ((wy0, -1), (wy1, 1)):
        _zbox(Pi, a_hot, XI1, yy + sg * 0.0, wz0, X1 - 0.09, yy + sg * 0.02, wz1)
    _zbox(Pi, a_hot, XI1, wy0, wz1, X1 - 0.09, wy1, wz1 + 0.02)
    # door reveals (oak, the deck door; tarred, the front door)
    for yy, sg in ((94.3, -1), (95.2, 1)):
        _zbox(Pi, oak, XI1, yy, FL, X1 - 0.03, yy + sg * 0.02, FL + 2.05)
    _zbox(Pi, oak, XI1, 94.3, FL + 2.05, X1 - 0.03, 95.2, FL + 2.07)
    # sarking (oak: the porch soffit + the east eave are seen from below) + the sod in three planes; grass grows on EN-sod-*
    Ps = fu.Part("KU-sodroof")
    sod = bc.pbr_material("sod_natural", "sparse_grass", 1.6, box=True, tint=(0.72, 0.85, 0.55), sat=0.9, val=0.85, piece_var=0.0)
    W_ = [(X0, Y0 - GABLE), (XR, Y0 - GABLE), (XR, YHIP), (X0, Y1)]
    E_ = [(XR, Y0 - GABLE), (XE, Y0 - GABLE), (XE, Y1), (X1, Y1), (XR, YHIP)]
    N_ = [(X0, Y1), (XR, YHIP), (X1, Y1)]
    for pl in (W_, E_, N_):
        _vprism(Ps, sod, pl, zroof, SOD)
        _vprism(Pe, oak, pl, lambda x, y: zroof(x, y) - SOD, SARK)
        _vprism(Pe, memb, pl, lambda x, y: zroof(x, y) - SOD + 0.004, 0.004)
    ze = zroof(XE, 95)
    Pe.rod(M["log"], (XE - 0.09, Y0 - GABLE, ze - 0.1), (XE - 0.09, Y1, ze - 0.1), 0.075, seg=14)                 # torvvol, holds the sod
    _zbox(Pe, tar, XE, Y0 - GABLE - 0.03, ze - SOD - SARK - 0.06, XE + 0.03, Y1, ze - 0.06)                    # fascia over the edge
    for xa, xb in ((X0, XR), (XR, XE)):                                                            # barge boards on the gable
        Pe.prism(tar, [(xa, zroof(xa, 92) - 0.04), (xb, zroof(xb, 92) - 0.04), (xb, zroof(xb, 92) - SOD - SARK - 0.06), (xa, zroof(xa, 92) - SOD - SARK - 0.06)],
                 Y0 - GABLE - 0.03, Y0 - GABLE)
    # two dry-laid granite wing walls where the mound ends open (south of the porch on the west line, north of the east wall),
    # stepping down with the berm until it meets the ground
    for xa_, xb_, ya_, yb_, xl, sg in wing_walls(H):
        y_ = yb_ if sg < 0 else ya_
        while (y_ > ya_ + 0.05) if sg < 0 else (y_ < yb_ - 0.05):
            ln = min(float(rng.uniform(0.35, 0.7)), abs((ya_ if sg < 0 else yb_) - y_)); yy0, yy1 = sorted((y_, y_ + sg * ln))
            zt = berm_z(xl, (yy0 + yy1) / 2) or 0.0
            z = min(_hb(H, (xa_ + xb_) / 2, yy0), _hb(H, (xa_ + xb_) / 2, yy1)) - 0.25
            while z < zt:
                hgt = float(rng.uniform(0.15, 0.24)); top = min(z + hgt, zt + 0.05)
                if top - z > 0.06:
                    _zbox(Pe, gran, xa_ + float(rng.uniform(0, 0.03)), yy0 + 0.004, z, xb_ - float(rng.uniform(0, 0.03)), yy1 - 0.004, top - 0.006)
                z += hgt
            y_ += sg * ln
    # the granite chimney: dry-laid courses from inside the roof to 0.8 over the ridge, a slate cap, the steel flue tip
    cx, cy = CHIM; zc0, zc1 = zroof(cx, cy) - SOD - SARK - RAFT, R + 0.8
    z = zc0
    while z < zc1 - 0.05:
        hgt = float(rng.uniform(0.15, 0.22)); n = int(rng.integers(2, 4)); cuts = np.sort(rng.uniform(-0.4, 0.4, n - 1))
        for side in range(4):
            e = [-0.4, *cuts, 0.4]
            for a_, b_ in zip(e, e[1:]):
                j_ = float(rng.uniform(-0.012, 0.012))
                if side == 0:
                    _zbox(Pe, gran, cx + a_ + 0.004, cy - 0.4 + j_, z, cx + b_ - 0.004, cy - 0.22, z + hgt - 0.006)
                elif side == 1:
                    _zbox(Pe, gran, cx + a_ + 0.004, cy + 0.22, z, cx + b_ - 0.004, cy + 0.4 + j_, z + hgt - 0.006)
                elif side == 2:
                    _zbox(Pe, gran, cx - 0.4 + j_, cy - 0.22, z, cx - 0.22, cy + 0.22, z + hgt - 0.006)
                else:
                    _zbox(Pe, gran, cx + 0.22, cy - 0.22, z, cx + 0.4 + j_, cy + 0.22, z + hgt - 0.006)
        z += hgt
    _zbox(Pe, slate, cx - 0.48, cy - 0.48, z, cx + 0.48, cy + 0.48, z + 0.08)
    Pe.cyl(st, (cx, cy, z + 0.08), 0.085, 0.3, seg=20)
    Pe.cyl(st, (cx, cy, FL + 2.3), 0.085, zc0 - FL - 2.3 + 0.05, seg=20)
    # the porch's west wall: faced in dry-laid granite on the porch side
    z = FL - 0.02
    while z < PLATE - 0.3:
        hgt = float(rng.uniform(0.14, 0.24)); e = np.sort(np.concatenate([[Y0], rng.uniform(Y0 + 0.2, YP - 0.2, 2), [YP]]))
        for a_, b_ in zip(e, e[1:]):
            _zbox(Pe, gran, XI0, a_ + 0.004, z, XI0 + 0.08 + float(rng.uniform(0, 0.02)), b_ - 0.004, z + hgt - 0.006)
        z += hgt

    # ---------------------------------------------------------------- inside: linings, slate floors, ceilings
    # hot room (thermo-aspen): west, north, east (round the window), the hot-room wall's hot face
    _boards(Pi, a_hot, "y", YH + TP, Y1 - T, XI0, 1, FL, HOT_C)
    _boards(Pi, a_hot, "x", XI0, XI1, Y1 - T, -1, FL, HOT_C)
    _boards(Pi, a_hot, "y", YH + TP, Y1 - T, XI1, -1, FL, HOT_C, ops=[(96.6, 99.1, FL + 0.7, FL + 2.1)])
    _boards(Pi, a_hot, "x", XI0, XI1, YH + TP, 1, FL, HOT_C, ops=ops_h)
    # changing room (light aspen)
    _boards(Pi, a_lt, "y", YP + T, YH, XI0, 1, FL, CH_C)
    _boards(Pi, a_lt, "y", YP + T, YH, XI1, -1, FL, CH_C, ops=[(94.3, 95.2, FL, FL + 2.05)])
    _boards(Pi, a_lt, "x", XI0, XI1, YP + T, 1, FL, CH_C, ops=ops_p)
    _boards(Pi, a_lt, "x", XI0, XI1, YH, -1, FL, CH_C, ops=[o for o in ops_h if o[0] > -23])
    # ceilings: boards running east-west
    for y0_, y1_, zc, mat in ((YH + TP, Y1 - T, HOT_C, a_hot), (YP + T, YH, CH_C, a_lt)):
        yy = y0_ + 0.05
        while yy < y1_ - 0.02:
            _zbox(Pi, mat, XI0, yy - 0.046, zc, XI1, yy + 0.046, zc + 0.016); yy += 0.095
    # slate floors (600 x 300, staggered, 4 mm joints; the concrete shows dark in the joints) + a drain in each room
    for y0_, y1_ in ((YP + T, YH), (YH + TP, Y1 - T)):
        for r_, yy in enumerate(np.arange(y0_, y1_, 0.3)):
            off = 0.3 if r_ % 2 else 0.0
            xx = XI0 - off
            while xx < XI1:
                xa, xb = max(XI0, xx), min(XI1, xx + 0.6)
                if xb - xa > 0.02:
                    _zbox(Pi, slate, xa + 0.002, yy + 0.002, FL - 0.012, xb - 0.002, min(y1_, yy + 0.3) - 0.002, FL - 0.0005 + float(rng.uniform(0, 0.001)))
                xx += 0.6
    for x, y in ((-22.4, 98.0), (-22.0, 94.8)):
        _zbox(Pi, st, x - 0.075, y - 0.075, FL - 0.011, x + 0.075, y + 0.075, FL + 0.0005)

    # ---------------------------------------------------------------- decks: Kebony 28 x 120 boards east-west, joists, beams, piles to the rock
    for x0, y0, x1, y1, top in DECKS:
        yy = y0 + 0.063
        while yy < y1 - 0.02:
            _zbox(Pd, deck, x0, yy - 0.06, top - 0.028, x1, yy + 0.06, top); yy += 0.126
        xx = x0 + 0.05
        while xx < x1:
            _zbox(Pd, deck, xx - 0.024, y0, top - 0.178, xx + 0.024, y1, top - 0.028); xx += 0.4
        for yb in np.linspace(y0 + 0.2, y1 - 0.2, max(2, math.ceil((y1 - y0) / 1.6) + 1)):
            _zbox(Pd, glulam, x0, yb - 0.045, top - 0.378, x1, yb + 0.045, top - 0.178)
            for xp in np.linspace(x0 + 0.3, x1 - 0.3, max(2, math.ceil((x1 - x0) / 1.8) + 1)):
                Pd.cyl(st, (xp, yb, min(_hb(H, xp, yb), top - 0.4) - 0.4), 0.07, top - 0.378 - min(_hb(H, xp, yb), top - 0.4) + 0.4, seg=14)
        for y_, sg in ((y0, -1), (y1, 1)):                                                        # fascia boards round the edges
            _zbox(Pd, deck, x0, y_, top - 0.2, x1, y_ + sg * 0.022, top - 0.03)
        for x_, sg in ((x0, -1), (x1, 1)):
            if not (top == LANDING and x_ in (XI0, X1)):
                _zbox(Pd, deck, x_, y0, top - 0.2, x_ + sg * 0.022, y1, top - 0.03)
    # skirts: Kebony slats from the porch + landing edge down into the ground (the deck sits on the ground, it does not hover)
    for (xa, ya, xb, yb, nx, ny) in ((XI0, Y0, -18.6, Y0, 0, -1), (X1, 95.6, -18.6, 95.6, 0, 1), (-18.6, Y0, -18.6, 92.6, 1, 0), (-18.6, 95.0, -18.6, 95.6, 1, 0)):
        L_ = math.hypot(xb - xa, yb - ya); n = max(1, int(L_ / 0.09))
        for k in range(n):
            t = (k + 0.5) / n; x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
            gz = _hb(H, x + nx * 0.3, y + ny * 0.3) - 0.08
            if LANDING - 0.03 - gz > 0.03:
                ex, ey = (0.035, 0.011) if ny else (0.011, 0.035)
                cx_, cy_ = x + nx * 0.011, y + ny * 0.011
                _zbox(Pd, deck, cx_ - ex, cy_ - ey, gz, cx_ + ex, cy_ + ey, LANDING - 0.03)
    # a few mossy boulders half sunk at the mound's foot and by the path
    for (bx, by, r_) in ((-30.4, 93.5, 0.55), (-29.6, 99.8, 0.7), (-26.8, 104.6, 0.5), (-21.9, 90.6, 0.35), (-27.4, 90.3, 0.6), (-18.6, 102.8, 0.45)):
        Pd.blob(M.setdefault("pool_boulders", bc.pbr_material("pool_boulders", "mossy_rock", 1.6, box=True, sat=0.6, val=0.75, piece_var=0.1)),
                (bx, by, _hb(H, bx, by) - r_ * 0.35), (r_ * 1.25, r_, r_ * 0.7), seg=16)
    # steps from the landing down to the lower deck: 5 risers on three steel stringers
    rise = (LANDING - DECK) / 5
    for k in range(1, 5):
        za = LANDING - k * rise; xa = -18.6 + (k - 1) * 0.3
        for b_ in range(2):
            _zbox(Pd, deck, xa + b_ * 0.15 + 0.004, 92.6, za - 0.028, xa + (b_ + 1) * 0.15 - 0.004, 95.0, za)
        Pd.box(fu._led("step_line", (1.0, 0.72, 0.45), 2.5), (xa + 0.3 - 0.01, 93.8, za - 0.045), (0.01, 2.3, 0.008))
    for yy in (92.68, 93.8, 94.92):
        Pd.prism(st, [(-18.62, LANDING - 0.03), (-17.4, DECK - 0.03), (-17.4, DECK - 0.2), (-18.62, LANDING - 0.2)], yy - 0.006, yy + 0.006)
    for xx, zz in ((-18.55, LANDING), (-17.45, DECK)):
        Pd.rod(st, (xx, 95.05, zz), (xx, 95.05, zz + 0.9), 0.02, seg=10)
    Pd.rod(st, (-18.55, 95.05, LANDING + 0.9), (-17.45, 95.05, DECK + 0.9), 0.02, seg=10)
    # granite slab steps into the pool: six steps of two split slabs each, solid to the bed, a steel handrail, boulders either side
    DE = -14.4
    for k in range(6):
        top = DECK - 0.17 - 0.3 * k; xa = DE + 0.35 * k; xb = xa + 0.35 if k < 5 else xa + 0.6
        for ya, yb in ((93.4, 94.2), (94.2, 95.0)):
            j_ = float(rng.uniform(-0.012, 0.012))
            _zbox(Pd, gran, xa + 0.004, ya + 0.004, min(_hb(H, xa, ya), -2.4) - 0.3, xb - 0.004, yb - 0.004, top + j_)
    Pd.rod(st, (DE - 0.15, 95.12, DECK), (DE - 0.15, 95.12, DECK + 0.95), 0.022, seg=12)
    Pd.rod(st, (DE + 1.9, 95.12, DECK - 0.17 - 1.5), (DE + 1.9, 95.12, DECK - 0.17 - 1.5 + 0.95), 0.022, seg=12)
    Pd.rod(st, (DE - 0.15, 95.12, DECK + 0.95), (DE + 1.9, 95.12, DECK - 0.72 + 0.0), 0.022, seg=12)
    stone = M.setdefault("pool_boulders", bc.pbr_material("pool_boulders", "mossy_rock", 1.6, box=True, sat=0.6, val=0.75, piece_var=0.1))
    for (bx, by, r_) in ((-13.6, 92.9, 0.55), (-12.6, 95.6, 0.45), (-14.0, 96.0, 0.35), (-12.2, 92.7, 0.4)):
        Pd.blob(stone, (bx, by, WATER - 0.4), (r_ * 1.3, r_, r_ * 0.85), seg=16)
    # the flume: split-log trough on log posts from a pump at the far post, falling gently to the tipping bucket
    pts = next(i["pts"] for i in LAY["items"] if i["kind"] == "flume")
    zs = [DECK + 2.32, DECK + 2.36, DECK + 2.42]
    pts = [(-15.3, 92.55)] + [tuple(p) for p in pts]; zs = [DECK + 2.3] + zs
    for (xa, ya), (xb, yb), za, zb in zip(pts, pts[1:], zs, zs[1:]):
        Pd.rod(M["log"], (xa, ya, za - 0.06), (xb, yb, zb - 0.06), 0.09, seg=12)
        Pd.rod(M["water_running"] if "water_running" in M else MAT["acrylic"], (xa, ya, za + 0.03), (xb, yb, zb + 0.03), 0.035, seg=8)
    for (xp, yp), zp in zip(pts[1:], zs[1:]):
        Pd.rod(M["log"], (xp, yp, min(_hb(H, xp, yp), DECK - 0.3) - 0.3), (xp, yp, zp - 0.12), 0.07, seg=12)
    xp, yp = pts[-1]
    Pd.rod(st, (xp + 0.1, yp, WATER - 0.6), (xp + 0.1, yp, zs[-1]), 0.025, seg=10)

    out = []
    for P in (Pf, Pr, Pe, Pi, Pd, Ps):
        out += P.build(coll, bevel=0.0)
    for o in out:
        o.data.polygons.foreach_set("use_smooth", np.zeros(len(o.data.polygons), bool))
    return len(out)

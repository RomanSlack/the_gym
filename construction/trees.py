"""Generated trees for the site (Roman, 2026-10-11: every asset is ours; only textures are downloaded).

Species of the Elverum forest, built from their real habit (reference: Wikimedia "Frøtrær furu", CC0, in ~/.cache/the_gym/ref):
  - Scots pine (Pinus sylvestris): 18-26 m, long self-pruned trunk with a few dead stubs, grey-brown plated bark below turning
    orange-red in the crown, an irregular open crown in the top third, limbs near horizontal with upturned ends, needles in
    clumps (pads) at the branch tips only, sky visible through the crown.
  - Norway spruce (Picea abies), forest grown: 20-30 m, straight, a narrow cone of whorled branches every ~0.6 m, upper
    branches rising, lower ones dropping with upturned tips, pendulous branchlets, dense dark blue-green needles; the lowest
    third is dead twigs in a closed stand.
Everything is real geometry: tapered tubes for wood (UVs in metres for the scanned bark), needles as thin strips on instanced
shoots. Every vertex and shoot carries wind weights ('wind_trunk' = height / H, 'wind_branch' = how far out along its branch,
0..1), so motion follows the tree's own structure (see add_wind).
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import bl_common as bc


# ------------------------------------------------------------------ wood: tapered tubes
LOD = {"near": 0, "mid": 1}  # LOD 2 is an impostor (bake_impostor)


class Wood:
    lod = 0  # set per build: LOD 1 halves the tube sides and drops twigs thinner than 1 cm

    def __init__(self):
        self.v, self.f, self.uv, self.wt, self.wb = [], [], [], [], []

    def tube(self, pts, radii, sides, H, wb0=0.0, wb1=0.0, tex=1.5):
        """pts / radii along a branch; wind_branch ramps wb0 -> wb1 along it."""
        if Wood.lod >= 1:
            if max(radii) < 0.01:
                return
            sides = max(3, sides // 2)
            pts, radii = pts[::2] + ([pts[-1]] if len(pts) % 2 == 0 else []), radii[::2] + ([radii[-1]] if len(radii) % 2 == 0 else [])
        n = len(pts)
        if n < 2:
            return
        base = len(self.v)
        s_acc = 0.0
        prev_side = None
        for i, (p, r) in enumerate(zip(pts, radii)):
            d = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
            side = d.orthogonal().normalized() if prev_side is None else (prev_side - d * prev_side.dot(d)).normalized()
            prev_side = side
            up = d.cross(side)
            if i:
                s_acc += (pts[i] - pts[i - 1]).length
            t = i / (n - 1)
            for k in range(sides):
                a = 2 * math.pi * k / sides
                self.v.append(tuple(p + (side * math.cos(a) + up * math.sin(a)) * r))
                self.uv.append((k / sides * max(2 * math.pi * r / tex, 0.05), s_acc / tex))
                self.wt.append(p.z / H)
                self.wb.append(wb0 + (wb1 - wb0) * t)
        for i in range(n - 1):
            for k in range(sides):
                a, b = base + i * sides + k, base + i * sides + (k + 1) % sides
                self.f.append((a, b, b + sides, a + sides))

    def build(self, name, mat, coll):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        uvl = me.uv_layers.new(name="UVMap")
        loops = np.array([li for poly in me.polygons for li in poly.loop_indices])
        vidx = np.array([me.loops[li].vertex_index for li in loops])
        uvs = np.array(self.uv, np.float32)
        # seam fix: the last column of each ring wraps, so take u + 1 ring step where the quad crosses k = sides-1 -> 0
        uvl.data.foreach_set("uv", uvs[vidx].ravel())
        for nm, arr in (("wind_trunk", self.wt), ("wind_branch", self.wb)):
            at = me.attributes.new(nm, "FLOAT", "POINT"); at.data.foreach_set("value", np.array(arr, np.float32))
        me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
        ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
        ob.data.materials.append(mat)
        return ob


def curve_path(p0, d0, length, step, rng, bend_up=0.0, droop=0.0, wander=0.08, end_up=0.0):
    """A branch centre line: starts at p0 heading d0, wanders, bends up (phototropism) or droops (weight), tip can turn up."""
    pts, d, p = [p0.copy()], d0.normalized(), p0.copy()
    n = max(2, int(length / step))
    for i in range(n):
        t = (i + 1) / n
        d = (d + Vector((rng.gauss(0, wander), rng.gauss(0, wander), rng.gauss(0, wander))) + Vector((0, 0, bend_up - droop * (1 - t) + end_up * t * t))).normalized()
        p = p + d * (length / n)
        pts.append(p.copy())
    return pts


# ------------------------------------------------------------------ shoots (needle clusters), built once per species
def shoot_proto(name, kind, mat, coll, lod=0):
    """One foliage shoot along +Z: a thin twig with needles. pine: 2-needle fascicles, long (6 cm), brushed forward into a tuft;
    spruce: short (2 cm) needles all round a flat-ish spray."""
    rng = random.Random(7 if kind == "pine" else 11)
    vs, fs = [], []

    keep = [0]

    def needle(base, direction, length, width):
        keep[0] += 1
        if lod >= 1:  # LOD 1: every 5th needle, 5x wider -> same coverage and colour from 40 m on, a fifth of the geometry
            if keep[0] % 5:
                return
            width *= 5.0
        side = direction.orthogonal().normalized() * width / 2
        mid = base + direction * length * 0.5 + Vector((0, 0, -length * 0.06))
        tip = base + direction * length
        b = len(vs)
        vs.extend([base - side, base + side, mid + side * 0.9, mid - side * 0.9, tip])
        fs.extend([(b, b + 1, b + 2, b + 3), (b + 3, b + 2, b + 4, b + 4)])

    twigs = []  # (base, direction, length) of the woody axes in the shoot
    if kind == "pine":
        # bottle-brush tuft: ~150 fascicles of 2 needles (5-7 cm) round a 30 cm shoot, sweeping forward, densest at the tip
        L, n = 0.30, 150
        twigs.append((Vector((0, 0, 0)), Vector((0, 0, 1)), L))
        for k in range(n):
            f = (k / n) ** 0.6
            z = L * f
            az = rng.random() * 2 * math.pi
            fwd = 0.25 + 0.55 * f
            dvec = Vector((math.cos(az) * (1 - fwd), math.sin(az) * (1 - fwd), fwd)).normalized()
            for j in range(2):
                dj = (dvec + Vector((rng.gauss(0, 0.15), rng.gauss(0, 0.15), rng.gauss(0, 0.05)))).normalized()
                needle(Vector((0, 0, z)), dj, rng.uniform(0.05, 0.07), 0.0015)
    else:
        # spruce spray: 45 cm axis with side shoots (comb), needles all round each shoot (~25 per 10 cm), brushed upward
        L = 0.45
        axes = [(Vector((0, 0, 0)), Vector((0, 0, 1)), L)]
        for j in range(13):
            z = L * (0.08 + 0.85 * j / 13)
            sgn = 1 if j % 2 else -1
            d = Vector((sgn * 0.85, rng.gauss(0, 0.15), 0.55)).normalized()
            axes.append((Vector((0, 0, z)), d, (0.17 - 0.11 * j / 13) * rng.uniform(0.8, 1.2)))
        for base, d, ln in axes:
            twigs.append((base, d, ln))
            nn = int(ln * 420)
            side = d.orthogonal().normalized()
            for k in range(nn):
                t = ln * k / nn
                az = rng.random() * 2 * math.pi
                radial = (side * math.cos(az) + d.cross(side) * math.sin(az))
                dv = (radial + d * 0.7 + Vector((0, 0, 0.35))).normalized()  # forward and a bit upward, like a real shoot
                needle(base + d * t, dv, rng.uniform(0.014, 0.022), 0.0012)
    # the woody axes themselves
    for base, d, ln in twigs:
        b = len(vs)
        side = d.orthogonal().normalized(); up = d.cross(side)
        for i in range(2):
            for k in range(3):
                a = 2 * math.pi * k / 3
                vs.append(base + d * (ln * i) + (side * math.cos(a) + up * math.sin(a)) * (0.0025 if i == 0 else 0.0012))
        fs.extend([(b + k, b + (k + 1) % 3, b + 3 + (k + 1) % 3, b + 3 + k) for k in range(3)])
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in vs], [], [tuple(f) if f[2] != f[3] else (f[0], f[1], f[2]) for f in fs])
    me.polygons.foreach_set("use_smooth", np.zeros(len(me.polygons), bool))
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    ob.data.materials.append(mat)
    ob.location = (0, 0, -1000); ob.hide_render = False
    return ob


class Shoots:
    """Instance points for foliage: position, orientation (Euler), scale, wind weights."""
    def __init__(self):
        self.p, self.r, self.s, self.wt, self.wb = [], [], [], [], []

    def add(self, p, d, scale, H, wb, rng):
        q = d.to_track_quat("Z", "Y")
        q = q @ Matrix.Rotation(rng.random() * 2 * math.pi, 4, "Z").to_quaternion()
        self.p.append(tuple(p)); self.r.append(tuple(q.to_euler())); self.s.append(scale); self.wt.append(p.z / H); self.wb.append(wb)

    def build(self, name, proto, coll):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.p, [], [])
        for nm, arr, typ in (("rot", self.r, "FLOAT_VECTOR"), ("scl", self.s, "FLOAT"), ("wind_trunk", self.wt, "FLOAT"), ("wind_branch", self.wb, "FLOAT")):
            at = me.attributes.new(nm, typ, "POINT")
            at.data.foreach_set("vector" if typ == "FLOAT_VECTOR" else "value", np.array(arr, np.float32).ravel())
        ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
        ng = shoot_nodes(proto)
        md = ob.modifiers.new("shoots", "NODES"); md.node_group = ng
        return ob


def shoot_nodes(proto):
    key = f"GN_shoots_{proto.name}"
    if key in bpy.data.node_groups:
        return bpy.data.node_groups[key]
    ng = bpy.data.node_groups.new(key, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    wind = wind_offset_nodes(ng)
    sp = N.new("GeometryNodeSetPosition"); L.new(gi.outputs[0], sp.inputs["Geometry"]); L.new(wind, sp.inputs["Offset"])
    oi = N.new("GeometryNodeObjectInfo"); oi.inputs[0].default_value = proto; oi.transform_space = "ORIGINAL"
    rot = N.new("GeometryNodeInputNamedAttribute"); rot.data_type = "FLOAT_VECTOR"; rot.inputs["Name"].default_value = "rot"
    scl = N.new("GeometryNodeInputNamedAttribute"); scl.data_type = "FLOAT"; scl.inputs["Name"].default_value = "scl"
    ip = N.new("GeometryNodeInstanceOnPoints")
    L.new(sp.outputs[0], ip.inputs["Points"]); L.new(oi.outputs["Geometry"], ip.inputs["Instance"])
    e2r = N.new("FunctionNodeEulerToRotation") if "FunctionNodeEulerToRotation" in dir(bpy.types) else None
    if e2r:
        L.new(rot.outputs["Attribute"], e2r.inputs[0]); L.new(e2r.outputs[0], ip.inputs["Rotation"])
    else:
        L.new(rot.outputs["Attribute"], ip.inputs["Rotation"])
    L.new(scl.outputs["Attribute"], ip.inputs["Scale"])
    # flutter: each shoot rocks a little on its own
    L.new(ip.outputs[0], go.inputs[0])
    return ng


# ------------------------------------------------------------------ wind
def wind_offset_nodes(ng, amp_trunk=0.35, amp_branch=0.12):
    """Offset = slow sway (grows with height^2) + faster branch bob (grows along the branch). Same field on wood and shoots,
    so needles stay on their twigs."""
    N, L = ng.nodes, ng.links
    t = N.new("GeometryNodeInputSceneTime")
    pos = N.new("GeometryNodeInputPosition")
    def attr(name):
        a = N.new("GeometryNodeInputNamedAttribute"); a.data_type = "FLOAT"; a.inputs["Name"].default_value = name
        return a.outputs["Attribute"]
    def math_(op, a, b):
        m = N.new("ShaderNodeMath"); m.operation = op
        for i, x in enumerate((a, b)):
            if isinstance(x, (int, float)):
                m.inputs[i].default_value = x
            else:
                L.new(x, m.inputs[i])
        return m.outputs[0]
    def noise(scale, speed, wscale):
        tsec = math_("MULTIPLY", t.outputs["Seconds"], speed)
        nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"; nz.inputs["Scale"].default_value = scale
        L.new(pos.outputs[0], nz.inputs["Vector"]); L.new(tsec, nz.inputs["W"])
        c = N.new("ShaderNodeVectorMath"); c.operation = "SUBTRACT"; L.new(nz.outputs["Color"], c.inputs[0]); c.inputs[1].default_value = (0.5, 0.5, 0.5)
        sc = N.new("ShaderNodeVectorMath"); sc.operation = "SCALE"; L.new(c.outputs[0], sc.inputs[0]); L.new(wscale, sc.inputs["Scale"])
        return sc.outputs[0]
    wt = attr("wind_trunk"); wb = attr("wind_branch")
    sway = noise(0.02, 0.35, math_("MULTIPLY", math_("MULTIPLY", wt, wt), amp_trunk))
    bob = noise(0.35, 1.6, math_("MULTIPLY", math_("MULTIPLY", wb, wb), amp_branch))
    flat = N.new("ShaderNodeVectorMath"); flat.operation = "MULTIPLY"; L.new(sway, flat.inputs[0]); flat.inputs[1].default_value = (1, 1, 0.15)
    add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"; L.new(flat.outputs[0], add.inputs[0]); L.new(bob, add.inputs[1])
    return add.outputs[0]


def add_wind(ob):
    ng = bpy.data.node_groups.get("GN_wind_wood")
    if ng is None:
        ng = bpy.data.node_groups.new("GN_wind_wood", "GeometryNodeTree")
        ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        gi, go = ng.nodes.new("NodeGroupInput"), ng.nodes.new("NodeGroupOutput")
        sp = ng.nodes.new("GeometryNodeSetPosition")
        ng.links.new(gi.outputs[0], sp.inputs["Geometry"]); ng.links.new(wind_offset_nodes(ng), sp.inputs["Offset"]); ng.links.new(sp.outputs[0], go.inputs[0])
    md = ob.modifiers.new("wind", "NODES"); md.node_group = ng


# ------------------------------------------------------------------ species
def scots_pine(seed, H=None):
    rng = random.Random(seed)
    H = H or rng.uniform(18, 25)
    wood, shoots, dead = Wood(), Shoots(), Wood()
    r0 = 0.012 * H + rng.uniform(0.0, 0.05)
    # trunk: straight-ish with a slight lean and a soft kink
    trunk = curve_path(Vector((0, 0, -0.3)), Vector((rng.gauss(0, 0.03), rng.gauss(0, 0.03), 1)), H, 0.6, rng, wander=0.012)
    tr = [r0 * (1 - 0.88 * (i / (len(trunk) - 1)) ** 0.9) + 0.004 for i in range(len(trunk))]
    wood.tube(trunk, tr, 14, H)
    crown0 = rng.uniform(0.6, 0.72) * H  # forest-grown: crown in the top ~third
    # a few dead stubs on the bare trunk
    for _ in range(rng.randint(3, 7)):
        z = rng.uniform(0.25, 0.55) * H; k = int(z / H * (len(trunk) - 1)); az = rng.random() * 2 * math.pi
        d = Vector((math.cos(az), math.sin(az), rng.uniform(-0.3, 0.1)))
        pts = curve_path(trunk[k], d, rng.uniform(0.25, 0.9), 0.15, rng, wander=0.1, droop=0.05)
        dead.tube(pts, [tr[k] * 0.2 * (1 - 0.7 * i / (len(pts) - 1)) for i in range(len(pts))], 5, H)
    # limbs in the crown: irregular, few and heavy low in the crown, many and short at the top
    n_limbs = rng.randint(18, 26)
    zs = sorted(rng.uniform(crown0, H * 0.97) for _ in range(n_limbs))
    az = rng.random() * 2 * math.pi
    for z in zs:
        az += 2.4 + rng.gauss(0, 0.5)  # roughly golden-angle spiral
        k = min(int(z / H * (len(trunk) - 1)), len(trunk) - 2)
        h = (z - crown0) / (H - crown0)
        L = (6.0 * (1 - h ** 1.6) ** 0.9 + 0.8) * rng.uniform(0.65, 1.15) * H / 22  # widest mid-crown, rounded top
        elev = rng.uniform(-0.1, 0.35) + 0.7 * h  # limbs climb more toward the top
        d = Vector((math.cos(az), math.sin(az), elev))
        limb = curve_path(trunk[k], d, L, 0.25, rng, wander=0.07, bend_up=0.0, droop=0.04, end_up=0.25)
        lr0 = tr[k] * rng.uniform(0.32, 0.45)
        lrad = [lr0 * (1 - 0.85 * i / (len(limb) - 1)) + 0.004 for i in range(len(limb))]
        wood.tube(limb, lrad, 8, H, 0.0, 1.0)
        # second order along the outer 75 % of the limb, mostly sideways and up
        nsec = max(3, int(L / 0.3))
        for j in range(nsec):
            f = 0.25 + 0.75 * (j + rng.random() * 0.5) / nsec
            i = min(int(f * (len(limb) - 1)), len(limb) - 2)
            dl = (limb[i + 1] - limb[i]).normalized()
            sidev = dl.cross(Vector((0, 0, 1))).normalized() * (1 if j % 2 else -1)
            d2 = (dl * 0.6 + sidev * 0.6 + Vector((0, 0, rng.uniform(0.25, 0.8)))).normalized()
            L2 = (1.4 * (1 - f) + 0.35) * rng.uniform(0.7, 1.2) * H / 22
            br = curve_path(limb[i], d2, L2, 0.12, rng, wander=0.12, end_up=0.35)
            wood.tube(br, [lrad[i] * 0.45 * (1 - 0.8 * q / (len(br) - 1)) + 0.002 for q in range(len(br))], 4, H, f, min(1.0, f + 0.3))
            # third-order twigs on the outer half, each ending in a pad of tufts (the pine "cloud")
            tips = [(br, len(br) - 1)]
            for q in range(len(br) // 3, len(br) - 1):
                dq = (br[q + 1] - br[q]).normalized()
                for sg in (-1, 1):
                    d3 = (dq * 0.7 + dq.cross(Vector((0, 0, 1))).normalized() * sg * 0.6 + Vector((0, 0, rng.uniform(0.1, 0.5)))).normalized()
                    tw = curve_path(br[q], d3, rng.uniform(0.25, 0.5) * H / 22, 0.08, rng, wander=0.15, end_up=0.3)
                    wood.tube(tw, [0.008 * (1 - 0.6 * i / (len(tw) - 1)) + 0.002 for i in range(len(tw))], 3, H, min(1.0, f + 0.3), min(1.0, f + 0.4))
                    tips.append((tw, len(tw) - 1))
            for tw, last in tips:
                # needles stay 2-4 years, so foliage runs along the outer 70 % of every shoot: a continuous cloud, not pom-poms
                for q in range(max(1, int(last * 0.3)), last + 1):
                    dq = (tw[q] - tw[q - 1]).normalized()
                    for _ in range(2):
                        dd = (dq * 0.7 + Vector((rng.gauss(0, 0.7), rng.gauss(0, 0.7), rng.uniform(-0.1, 0.9)))).normalized()
                        shoots.add(tw[q] + Vector((rng.gauss(0, 0.05), rng.gauss(0, 0.05), rng.gauss(0, 0.03))), dd, rng.uniform(0.8, 1.15), H, min(1.0, f + 0.4), rng)
                dl = (tw[last] - tw[max(last - 1, 0)]).normalized()
                for _ in range(rng.randint(4, 7)):  # the shoot tips fan out a little more
                    dd = (dl * 0.5 + Vector((rng.gauss(0, 0.8), rng.gauss(0, 0.8), rng.uniform(-0.2, 1.0)))).normalized()
                    shoots.add(tw[last] - dl * rng.uniform(0.0, 0.2), dd, rng.uniform(0.85, 1.2), H, min(1.0, f + 0.4), rng)
        for q in range(int(len(limb) * 0.75), len(limb)):  # the limb's own leader tuft
            for _ in range(6):
                dd = ((limb[min(q + 1, len(limb) - 1)] - limb[q - 1]).normalized() + Vector((rng.gauss(0, 0.5), rng.gauss(0, 0.5), rng.uniform(0.2, 0.8)))).normalized()
                shoots.add(limb[q], dd, rng.uniform(0.9, 1.3), H, 1.0, rng)
    # two or three secondary leaders that round off the top (older Scots pines lose apical dominance)
    for _ in range(rng.randint(2, 3)):
        k = int(len(trunk) * rng.uniform(0.8, 0.9)); az = rng.random() * 2 * math.pi
        sl = curve_path(trunk[k], Vector((math.cos(az) * 0.6, math.sin(az) * 0.6, 1)), rng.uniform(2.5, 4.0) * H / 22, 0.2, rng, wander=0.08, end_up=0.2)
        wood.tube(sl, [tr[k] * 0.5 * (1 - 0.8 * i / (len(sl) - 1)) + 0.003 for i in range(len(sl))], 6, H, 0.2, 0.8)
        for q in range(len(sl) // 3, len(sl)):
            for _ in range(5):
                dd = (Vector((0, 0, 0.6)) + Vector((rng.gauss(0, 0.8), rng.gauss(0, 0.8), rng.uniform(-0.2, 0.6)))).normalized()
                shoots.add(sl[q] + Vector((rng.gauss(0, 0.25), rng.gauss(0, 0.25), rng.gauss(0, 0.15))), dd, rng.uniform(0.9, 1.25), H, 0.8, rng)
    for q in range(int(len(trunk) * 0.93), len(trunk)):  # leader
        for _ in range(4):
            dd = (Vector((0, 0, 1)) + Vector((rng.gauss(0, 0.6), rng.gauss(0, 0.6), 0))).normalized()
            shoots.add(trunk[q], dd, 1.1, H, 0.6, rng)
    return H, wood, dead, shoots


def norway_spruce(seed, H=None, dead_frac=0.3):
    rng = random.Random(seed)
    H = H or rng.uniform(21, 28)
    wood, shoots, dead = Wood(), Shoots(), Wood()
    r0 = 0.013 * H + rng.uniform(0.0, 0.04)
    trunk = curve_path(Vector((0, 0, -0.3)), Vector((rng.gauss(0, 0.01), rng.gauss(0, 0.01), 1)), H, 0.5, rng, wander=0.005)
    tr = [r0 * (1 - 0.95 * (i / (len(trunk) - 1))) + 0.003 for i in range(len(trunk))]
    wood.tube(trunk, tr, 12, H)
    z = 1.5
    while z < H - 0.4:
        h = z / H
        k = min(int(h * (len(trunk) - 1)), len(trunk) - 2)
        n_w = rng.randint(4, 6)
        az0 = rng.random() * 2 * math.pi
        live = h > dead_frac
        for w in range(n_w):
            az = az0 + 2 * math.pi * w / n_w + rng.gauss(0, 0.25)
            L = (0.36 * H * (1 - h) ** 0.95 + 0.25) * rng.uniform(0.8, 1.15) if live else rng.uniform(0.4, 1.2)
            elev = 0.6 * (h - 0.55) + rng.gauss(0, 0.08)  # rising at the top, dropping low down
            d = Vector((math.cos(az), math.sin(az), elev))
            br = curve_path(trunk[k], d, L, 0.2, rng, wander=0.05, droop=0.12 * (1 - h) if live else 0.05, end_up=0.25 if live else 0.0)
            brad = [(tr[k] * 0.28 if live else 0.012) * (1 - 0.85 * i / (len(br) - 1)) + 0.003 for i in range(len(br))]
            (wood if live else dead).tube(br, brad, 6 if live else 4, H, 0.0, 1.0)
            if not live:  # dead lower branches: thin, with brittle side twigs
                for i in range(1, len(br)):
                    for sg in (-1, 1):
                        if rng.random() < 0.6:
                            dt = ((br[i] - br[i - 1]).normalized() + Vector((rng.gauss(0, 0.6), rng.gauss(0, 0.6), rng.gauss(0, 0.3)))).normalized()
                            tw = curve_path(br[i], dt, rng.uniform(0.1, 0.35), 0.1, rng, wander=0.2)
                            dead.tube(tw, [0.003, 0.0015][:len(tw)] + [0.0015] * (len(tw) - 2), 3, H)
                continue
            # pendulous branchlets hanging off the branch (the spruce curtain), denser outward
            for i in range(2, len(br)):
                f = i / (len(br) - 1)
                for sgn in (-1, -1, 1, 1):
                    dl = (br[i] - br[i - 1]).normalized()
                    d2 = (dl.cross(Vector((0, 0, 1))).normalized() * sgn * 0.8 + dl * 0.4 + Vector((0, 0, -0.55 * (1 - h) - 0.05))).normalized()
                    L2 = (0.25 + 0.6 * f * (1 - h) ** 0.5) * rng.uniform(0.7, 1.2)
                    tw = curve_path(br[i] + (br[i - 1] - br[i]) * rng.random() * 0.5, d2, L2, 0.08, rng, wander=0.1, droop=0.2)
                    wood.tube(tw, [0.006 * (1 - 0.6 * q / (len(tw) - 1)) + 0.002 for q in range(len(tw))], 3, H, f, min(1.0, f + 0.25))
                    for q in range(1, len(tw)):
                        dd = ((tw[q] - tw[q - 1]).normalized() + Vector((rng.gauss(0, 0.3), rng.gauss(0, 0.3), rng.gauss(0, 0.15)))).normalized()
                        for _ in range(2):
                            shoots.add(tw[q] + Vector((rng.gauss(0, 0.05), rng.gauss(0, 0.05), rng.gauss(0, 0.03))), dd, rng.uniform(0.8, 1.2), H, min(1.0, f + 0.25), rng)
                for _ in range(3):
                    dd = ((br[i] - br[i - 1]).normalized() + Vector((rng.gauss(0, 0.4), rng.gauss(0, 0.4), 0.3))).normalized()
                    shoots.add(br[i] + Vector((rng.gauss(0, 0.06), rng.gauss(0, 0.06), 0)), dd, 1.1, H, f, rng)
        z += rng.uniform(0.5, 0.75)
    for q in range(int(len(trunk) * 0.9), len(trunk)):
        for _ in range(4):
            shoots.add(trunk[q], (Vector((0, 0, 1)) + Vector((rng.gauss(0, 0.5), rng.gauss(0, 0.5), 0))).normalized(), 1.0, H, 0.5, rng)
    return H, wood, dead, shoots


# ------------------------------------------------------------------ materials
def tex_material(name, tid, tint=None, scale=1.0, orange_above=None):
    """Scanned CC0 PBR (diffuse, normal, roughness) on the mesh UVs (metres / texture size)."""
    from pathlib import Path
    d = Path.home() / ".cache" / "the_gym" / "textures" / "polyhaven" / tid
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    uv = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(uv.outputs["UV"], mp.inputs["Vector"])
    def img(fn, non_color=False):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(str(d / fn), check_existing=True)
        if non_color:
            t.image.colorspace_settings.name = "Non-Color"
        L.new(mp.outputs[0], t.inputs["Vector"]); return t
    col = img("diff.jpg").outputs["Color"]
    if orange_above is not None:  # Scots pine: orange-red flaky bark in the upper trunk and crown
        at = N.new("ShaderNodeAttribute"); at.attribute_name = "wind_trunk"
        mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = orange_above - 0.12; mr.inputs[2].default_value = orange_above + 0.08
        L.new(at.outputs["Fac"], mr.inputs[0])
        mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["B"].default_value = (1.35, 0.62, 0.33, 1)
        L.new(mr.outputs[0], mix.inputs["Factor"]); L.new(col, mix.inputs["A"]); col = mix.outputs["Result"]
    if tint:
        mt = N.new("ShaderNodeMix"); mt.data_type = "RGBA"; mt.blend_type = "MULTIPLY"; mt.inputs["Factor"].default_value = 1.0
        mt.inputs["B"].default_value = (*tint, 1); L.new(col, mt.inputs["A"]); col = mt.outputs["Result"]
    L.new(col, b.inputs["Base Color"])
    L.new(img("rough.jpg", True).outputs["Color"], b.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap"); L.new(img("nor_gl.jpg", True).outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    return m


def needle_material(name, rgb):
    """Thin needles: mostly diffuse/glossy with light coming through (translucent), colour varies per shoot."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    out = N["Material Output"]; b = N["Principled BSDF"]
    oi = N.new("ShaderNodeObjectInfo")
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[c * 0.75 for c in rgb], 1); ramp.color_ramp.elements[1].color = (*[min(1, c * 1.25) for c in rgb], 1)
    L.new(oi.outputs["Random"], ramp.inputs[0])
    L.new(ramp.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.45
    tl = N.new("ShaderNodeBsdfTranslucent"); L.new(ramp.outputs[0], tl.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.3
    L.new(b.outputs[0], mx.inputs[1]); L.new(tl.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs["Surface"])
    return m


def make_tree(kind, seed, coll, at=(0, 0, 0), H=None, wind=True, lod=0):
    """Builds one tree (wood, dead wood, foliage instances) parented to an empty at `at`. Returns the empty.
    lod 0 = every needle; lod 1 = same skeleton and silhouette, a fraction of the geometry (for 40 m+)."""
    Wood.lod = lod
    mats = bpy.data.materials
    if kind == "pine":
        H, wood, dead, shoots = scots_pine(seed, H)
        bark = mats.get("bark_pine") or tex_material("bark_pine", "pine_bark", scale=1.0, orange_above=0.62)
        needles = mats.get("needles_pine") or needle_material("needles_pine", (0.075, 0.12, 0.035))
    else:
        H, wood, dead, shoots = norway_spruce(seed, H)
        bark = mats.get("bark_spruce") or tex_material("bark_spruce", "tree_bark_03", tint=(0.8, 0.72, 0.65))
        needles = mats.get("needles_spruce") or needle_material("needles_spruce", (0.03, 0.065, 0.035))
    deadm = mats.get("dead_wood") or tex_material("dead_wood", "knotted_pine_bark", tint=(0.6, 0.6, 0.6))
    if lod >= 1:  # LOD 1: a third of the shoots, 1.5x larger (coverage ~ count x scale^2 stays about the same)
        for k_ in ("p", "r", "s", "wt", "wb"):
            setattr(shoots, k_, getattr(shoots, k_)[::3])
        shoots.s = [v * 1.5 for v in shoots.s]
    pn = f"shoot_{kind}" + ("" if lod == 0 else f"_lod{lod}")
    proto = bpy.data.objects.get(pn) or shoot_proto(pn, kind, needles, coll, lod)
    tag = f"{kind}_{seed}" + ("" if lod == 0 else f"_lod{lod}")
    root = bpy.data.objects.new(tag, None); coll.objects.link(root); root.location = at
    for ob in (wood.build(f"{tag}_wood", bark, coll), dead.build(f"{tag}_dead", deadm, coll) if dead.v else None,
               shoots.build(f"{tag}_needles", proto, coll)):
        if ob is None:
            continue
        ob.parent = root
        if wind and ob.name.endswith(("_wood", "_dead")):
            add_wind(ob)
    Wood.lod = 0
    return root, H, len(shoots.p)


# ------------------------------------------------------------------ LOD 2: impostor (baked from our own LOD 0 tree)
def bake_impostor(tree_root, H, out_png, views=4, res=(512, 1024)):
    """Renders the LOD 0 tree orthographically from `views` azimuths (alpha) into one strip; returns crossed-quads data."""
    import os
    sc = bpy.context.scene
    keep = (sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.film_transparent, sc.render.filepath, sc.cycles.samples)
    hide = [o for o in sc.objects if o.visible_get() and o not in tree_root.children_recursive and o != tree_root and o.type in ("MESH", "CURVE", "LIGHT")]
    for o in hide:
        o.hide_render = True
    world_keep = sc.world  # bake under an even overcast sky: the impostor gets lit again where it stands
    flat = bpy.data.worlds.new("impostor_bake_sky"); flat.use_nodes = True
    flat.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1); flat.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    sc.world = flat
    vt = (sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure)
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = 0.0  # store colour, not a graded image
    cam = bpy.data.objects.new("impostor_cam", bpy.data.cameras.new("impostor_cam")); sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"; W = H * 0.62; cam.data.ortho_scale = H * 1.05
    sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.film_transparent = True; sc.cycles.samples = 64
    c = tree_root.matrix_world.translation
    files = []
    for k in range(views):
        a = math.pi * k / views
        cam.location = c + Vector((math.sin(a) * 60, -math.cos(a) * 60, H * 0.5))
        cam.rotation_euler = (math.pi / 2, 0, a)
        f = f"{out_png}_{k}.png"; sc.render.filepath = f; bpy.ops.render.render(write_still=True); files.append(f)
    sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.film_transparent, sc.render.filepath, sc.cycles.samples = keep
    bpy.data.objects.remove(cam)
    sc.world = world_keep
    sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure = vt
    for o in hide:
        o.hide_render = False
    return files, H * 1.05 * res[0] / res[1], H * 1.05


def impostor_object(name, files, w, h, coll):
    """Crossed vertical quads, one per baked view, each with its own alpha image; casts shadows, no wind (far away)."""
    vs, fs, mats = [], [], []
    n = len(files)
    me = bpy.data.meshes.new(name)
    for k, f in enumerate(files):
        a = math.pi * k / n
        ux, uy = math.cos(a) * w / 2, math.sin(a) * w / 2
        b = len(vs)
        vs += [(-ux, -uy, -0.02 * h), (ux, uy, -0.02 * h), (ux, uy, h * 0.98), (-ux, -uy, h * 0.98)]
        fs.append((b, b + 1, b + 2, b + 3))
        m = bpy.data.materials.new(f"{name}_{k}"); m.use_nodes = True
        N, L = m.node_tree.nodes, m.node_tree.links
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(f, check_existing=True); t.image.alpha_mode = "STRAIGHT"
        bsdf = N["Principled BSDF"]; L.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.8
        up = N.new("ShaderNodeCombineXYZ"); up.inputs[2].default_value = 1.0; L.new(up.outputs[0], bsdf.inputs["Normal"])  # lit like a crown, from any side
        lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
        fade = N.new("ShaderNodeMapRange"); fade.inputs[1].default_value = 0.55; fade.inputs[2].default_value = 0.9; fade.inputs[3].default_value = 1.0; fade.inputs[4].default_value = 0.0
        L.new(lw.outputs["Facing"], fade.inputs[0])
        am = N.new("ShaderNodeMath"); am.operation = "MULTIPLY"; L.new(t.outputs["Alpha"], am.inputs[0]); L.new(fade.outputs[0], am.inputs[1])
        L.new(am.outputs[0], bsdf.inputs["Alpha"])  # planes fade out as they turn edge-on: no dark seams
        tl = N.new("ShaderNodeBsdfTranslucent"); L.new(t.outputs["Color"], tl.inputs["Color"])  # light through the needles, as on LOD 0
        mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.3
        tr_ = N.new("ShaderNodeBsdfTransparent")
        mxa = N.new("ShaderNodeMixShader")  # alpha applied after the translucent mix
        L.new(bsdf.outputs[0], mx.inputs[1]); L.new(tl.outputs[0], mx.inputs[2])
        L.new(am.outputs[0], mxa.inputs[0]); L.new(tr_.outputs[0], mxa.inputs[1]); L.new(mx.outputs[0], mxa.inputs[2])
        bsdf.inputs["Alpha"].default_value = 1.0
        for l_ in list(bsdf.inputs["Alpha"].links):
            m.node_tree.links.remove(l_)
        L.new(mxa.outputs[0], N["Material Output"].inputs["Surface"])
        mats.append(m)
    me.from_pydata(vs, [], fs)
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li, (u, v) in zip(poly.loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
            uvl.data[li].uv = (u, v)
        poly.material_index = poly.index
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    for m in mats:
        ob.data.materials.append(m)
    return ob

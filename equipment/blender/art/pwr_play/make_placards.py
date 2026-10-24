"""Our own station placards for the PWR Play model (drawn here, not copied; laid out like the real ones, ref_03): the
warning label, the maker's mark, the station's name, the muscles panel and two step panels with the figure in blue.
python3 make_placards.py -> placard_<station>.png (0.05 x 0.30 m on a leg's face)."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 240, 1440
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OBL = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"
BLUE, PALE, GREY = (95, 160, 225), (205, 225, 245), (110, 112, 118)

# the two step poses per station, joints in a 1 x 1 panel (x right, y down): head, neck, hip, knee, foot, elbow, hand;
# `kit` = grey machine lines in the same frame
STATIONS = {
    "pulldown": ("PULLDOWN", [
        dict(head=(.42, .30), hip=(.45, .72), knee=(.70, .72), foot=(.72, .95), elbow=(.38, .12), hand=(.36, .02)),
        dict(head=(.42, .30), hip=(.45, .72), knee=(.70, .72), foot=(.72, .95), elbow=(.30, .45), hand=(.36, .30))],
        [((.30, .78), (.62, .78)), ((.62, .62), (.78, .62)), ((.20, .02), (.55, .02))]),
    "row": ("SEATED ROW", [
        dict(head=(.36, .34), hip=(.30, .72), knee=(.55, .58), foot=(.80, .72), elbow=(.55, .50), hand=(.75, .52)),
        dict(head=(.30, .32), hip=(.30, .72), knee=(.55, .58), foot=(.80, .72), elbow=(.18, .50), hand=(.42, .52))],
        [((.10, .78), (.60, .78)), ((.85, .55), (.85, .85))]),
    "triceps": ("TRICEPS\nPUSHDOWN", [
        dict(head=(.45, .16), hip=(.46, .58), knee=(.46, .78), foot=(.46, .98), elbow=(.50, .40), hand=(.66, .24)),
        dict(head=(.45, .16), hip=(.46, .58), knee=(.46, .78), foot=(.46, .98), elbow=(.50, .40), hand=(.62, .58))],
        [((.80, .02), (.80, .20))]),
    "crossover": ("CABLE\nCROSSOVER", [
        dict(head=(.50, .16), hip=(.50, .58), knee=(.50, .78), foot=(.50, .98), elbow=(.28, .30), hand=(.08, .30)),
        dict(head=(.50, .16), hip=(.50, .58), knee=(.50, .78), foot=(.50, .98), elbow=(.62, .36), hand=(.56, .44))],
        [((.04, .05), (.04, .98))]),
    "adjustable": ("ADJUSTABLE\nPULLEY", [
        dict(head=(.50, .16), hip=(.50, .58), knee=(.50, .78), foot=(.50, .98), elbow=(.66, .40), hand=(.80, .50)),
        dict(head=(.50, .16), hip=(.50, .58), knee=(.50, .78), foot=(.50, .98), elbow=(.40, .30), hand=(.30, .14))],
        [((.92, .05), (.92, .98))]),
    "dualhigh": ("DUAL CABLE\nHIGH", [
        dict(head=(.45, .16), hip=(.46, .58), knee=(.40, .78), foot=(.38, .98), elbow=(.66, .20), hand=(.82, .08)),
        dict(head=(.45, .16), hip=(.46, .58), knee=(.40, .78), foot=(.38, .98), elbow=(.50, .40), hand=(.40, .55))],
        [((.92, .02), (.92, .20))]),
    "duallow": ("DUAL CABLE\nLOW", [
        dict(head=(.45, .16), hip=(.46, .58), knee=(.46, .78), foot=(.46, .98), elbow=(.54, .44), hand=(.62, .62)),
        dict(head=(.45, .16), hip=(.46, .58), knee=(.46, .78), foot=(.46, .98), elbow=(.60, .26), hand=(.76, .14))],
        [((.92, .80), (.92, .98))]),
    "dip": ("DIP", [
        dict(head=(.50, .14), hip=(.50, .56), knee=(.50, .76), foot=(.46, .94), elbow=(.50, .40), hand=(.52, .44)),
        dict(head=(.50, .30), hip=(.50, .72), knee=(.50, .88), foot=(.46, .99), elbow=(.66, .36), hand=(.52, .44))],
        [((.20, .44), (.80, .44))]),
}


def figure(d, box, p, kit):
    x0, y0, x1, y1 = box
    def P(q):
        return (x0 + q[0] * (x1 - x0), y0 + q[1] * (y1 - y0))
    for a, b in kit:
        d.line([P(a), P(b)], fill=GREY, width=7)
    neck = (p["head"][0] + (p["hip"][0] - p["head"][0]) * 0.18, p["head"][1] + (p["hip"][1] - p["head"][1]) * 0.18)
    sh = (p["head"][0] + (p["hip"][0] - p["head"][0]) * 0.28, p["head"][1] + (p["hip"][1] - p["head"][1]) * 0.28)
    for a, b, w in ((neck, p["hip"], 26), (p["hip"], p["knee"], 20), (p["knee"], p["foot"], 16), (sh, p["elbow"], 14),
                    (p["elbow"], p["hand"], 12)):
        d.line([P(a), P(b)], fill=BLUE, width=w)
        for q in (a, b):
            r = w / 2
            d.ellipse([P(q)[0] - r, P(q)[1] - r, P(q)[0] + r, P(q)[1] + r], fill=BLUE)
    hx, hy = P(p["head"])
    d.ellipse([hx - 17, hy - 19, hx + 17, hy + 19], fill=PALE)


def muscles(d, box):
    """The muscles panel: a torso from behind, grey, the worked muscles in blue."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    d.ellipse([cx - 20, y0 + 20, cx + 20, y0 + 66], fill=(150, 152, 158))
    d.polygon([(cx - 70, y0 + 80), (cx + 70, y0 + 80), (cx + 45, y1 - 25), (cx - 45, y1 - 25)], fill=(150, 152, 158))
    for s in (-1, 1):
        d.polygon([(cx + s * 12, y0 + 105), (cx + s * 64, y0 + 95), (cx + s * 42, y1 - 50), (cx + s * 12, y1 - 60)], fill=BLUE)


def placard(key):
    title, poses, kit = STATIONS[key]
    im = Image.new("RGB", (W, H), (16, 16, 18))
    d = ImageDraw.Draw(im)
    d.rectangle([18, 24, W - 18, 230], fill=(240, 240, 238))                   # the warning label
    d.rectangle([18, 24, W - 18, 62], fill=(232, 120, 28))
    d.text((W / 2, 43), "WARNING", font=ImageFont.truetype(BOLD, 22), fill=(10, 10, 10), anchor="mm")
    for i in range(8):
        d.line([(30, 80 + i * 18), (W - 30 - (i % 3) * 22, 80 + i * 18)], fill=(150, 150, 150), width=4)
    d.text((W / 2, 272), "Life Fitness", font=ImageFont.truetype(OBL, 27), fill=(235, 235, 235), anchor="mm")
    d.multiline_text((W / 2, 335), title, font=ImageFont.truetype(BOLD, 24), fill=(235, 235, 235), anchor="mm",
                     align="center", spacing=6)
    tops = (395, 735, 1075)
    for i, t in enumerate(tops):
        box = (24, t, W - 24, t + 320)
        d.rounded_rectangle(box, 14, outline=(120, 122, 128), width=3)
        inner = (box[0] + 22, box[1] + 22, box[2] - 22, box[3] - 22)
        if i == 0:
            muscles(d, inner)
        else:
            figure(d, inner, poses[i - 1], kit)
    d.text((W / 2, H - 22), "lifefitness.com", font=ImageFont.truetype(BOLD, 14), fill=(150, 150, 150), anchor="mm")
    return im


for key in STATIONS:
    placard(key).save(HERE / f"placard_{key}.png")
print("placards written")

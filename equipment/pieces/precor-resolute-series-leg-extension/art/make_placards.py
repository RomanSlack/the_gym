"""Our own instruction placards for the Precor leg extension model (drawn here, not copied): a muscle figure with the
quadriceps lit, and step sketches of a person on the machine. python3 make_placards.py -> placard_left.png, placard_right.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
W, H = 560, 760


def panel():
    im = Image.new("RGB", (W, H), (60, 63, 68))
    g = Image.linear_gradient("L").transpose(Image.Transpose.ROTATE_90).resize((W, H))
    light = Image.new("RGB", (W, H), (215, 218, 222))
    return Image.composite(light, im, g.point(lambda v: 90 + v * 0.55))


def person(d, x, y, s, legs_out=0.0, col=(250, 250, 250)):
    """A seated figure on a leg extension, side on, facing left: head, torso, thigh, shin (legs_out: 0 bent .. 1 straight)."""
    import math
    hip = (x, y)
    d.ellipse([x - 0.10 * s, y - 0.95 * s, x + 0.06 * s, y - 0.79 * s], fill=col)               # head
    d.line([hip, (x - 0.01 * s, y - 0.75 * s)], fill=col, width=int(0.11 * s))                   # torso
    knee = (x - 0.42 * s, y)
    d.line([hip, knee], fill=col, width=int(0.11 * s))                                            # thigh
    a = math.radians(-90 + 90 * legs_out)
    foot = (knee[0] + 0.40 * s * math.cos(math.radians(180)) * math.sin(math.radians(90 * legs_out)) - 0.0, knee[1] + 0.40 * s * math.cos(math.radians(90 * legs_out)))
    d.line([knee, foot], fill=col, width=int(0.09 * s))                                           # shin
    d.ellipse([foot[0] - 0.06 * s, foot[1] - 0.06 * s, foot[0] + 0.06 * s, foot[1] + 0.06 * s], fill=(235, 120, 30))   # the roller
    d.line([(x + 0.06 * s, y + 0.05 * s), (x + 0.18 * s, y - 0.7 * s)], fill=(40, 40, 44), width=int(0.05 * s))  # back pad
    d.line([(x - 0.45 * s, y + 0.07 * s), (x + 0.08 * s, y + 0.07 * s)], fill=(40, 40, 44), width=int(0.05 * s))  # seat


def left():
    im = panel(); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 200, H], fill=(46, 49, 54))
    # the muscle figure, front on, quadriceps lit
    c = (100, 0)
    d.ellipse([78, 110, 122, 160], fill=(235, 235, 235))
    d.rounded_rectangle([62, 165, 138, 360], 26, fill=(235, 235, 235))
    for sx in (-1, 1):
        d.rounded_rectangle([100 + sx * 48 - 12, 175, 100 + sx * 48 + 12, 340], 10, fill=(230, 230, 230))
        d.rounded_rectangle([100 + sx * 22 - 20, 350, 100 + sx * 22 + 20, 520], 16, fill=(70, 200, 230))   # quads
        d.rounded_rectangle([100 + sx * 22 - 16, 520, 100 + sx * 22 + 16, 690], 14, fill=(230, 230, 230))
    for i, out in enumerate((0.0, 0.5, 1.0)):
        y0 = 30 + i * 245
        d.line([(210, y0 + 238), (W - 10, y0 + 228)], fill=(90, 92, 96), width=3)
        person(d, 460, y0 + 200, 185, out)
    return im.filter(ImageFilter.SMOOTH)


def right():
    im = panel(); d = ImageDraw.Draw(im)
    for i, out in enumerate((0.0, 1.0)):
        y0 = 20 + i * 370
        d.line([(10, y0 + 360), (W - 10, y0 + 350)], fill=(90, 92, 96), width=3)
        person(d, 400, y0 + 300, 280, out)
    d.rectangle([W - 70, 40, W - 20, 90], outline=(40, 40, 44), width=4)                          # the QR corner
    for i in range(4):
        for j in range(4):
            if (i * 3 + j) % 3:
                d.rectangle([W - 66 + i * 11, 44 + j * 11, W - 58 + i * 11, 52 + j * 11], fill=(40, 40, 44))
    return im.filter(ImageFilter.SMOOTH)


left().save(HERE / "placard_left.png"); right().save(HERE / "placard_right.png")
print("placards written")

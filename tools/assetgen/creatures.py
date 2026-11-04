"""The fifteen Bunnyland creatures: geometry builders and colour variants.

Each builder takes a palette dict ``v`` (with v["_variant"], v["_rare"]) and returns a Model.
Geometry must not depend on the variant (all variants share one .geo.json); only decals may.
"""
import math

from .core import darken, lighten, mix
from .geo import Model, mask_ellipse, mask_tear, mask_petal
from . import rig
from .paint import antler_shape


def sx(side, x0, w):
    """Mirror an x origin for the right-hand side (side = -1)."""
    return x0 if side > 0 else -(x0 + w)


def face_rect_eye_center(head_cube, y, w_tex, spread, density=2):
    """Model-space centre of the left eye for a head cube (used to place glasses)."""
    x0, y0, z0 = head_cube.origin
    fw = int(round(head_cube.size[0] * density))
    fh = int(round(head_cube.size[1] * density))
    gap = max(1, int(round(fw * spread)))
    left = (fw - gap) // 2 - w_tex
    cx_tex = left + w_tex / 2.0
    eye_dx = abs(fw / 2.0 - cx_tex) / density
    eye_y = y0 + head_cube.size[1] * (1 - y)
    return eye_dx, eye_y


def sparkle_body(v, cube, faces=("east", "west", "up"), count=5, seed=3):
    """Rare-variant glitter: glowing stars sprinkled over a cube."""
    if v.get("_rare") and "glitter" in v:
        for f in faces:
            cube.decal(f, "stars", count=count, color="glitter", seed=seed + len(f), glow_on=True)


# =========================================================================== BUNNIES

def _bunny(v, *, body=(7, 6, 8), head=(7, 6, 5.5), ear="up", ear_len=7.0, ear_w=2.0, tail=4.0,
           chest=True, cheeks=False, eye=None, bow_side=1, ear_tilt=12.0):
    m = Model(v["_species"])
    BW, BH, BD = body
    HW, HH, HD = head
    eye = eye or {}
    m.bone("root", [0, 0, 0])
    bod = m.bone("body", [0, 4, 1.5], parent="root")
    bz0 = -2.5
    main = bod.box([-BW / 2, 1, bz0], [BW, BH, BD], "fur")
    main.decal("north", "patch", x=0.5, y=0.6, rx=0.34, ry=0.42, color="belly")
    main.decal("down", "patch", x=0.5, y=0.5, rx=0.4, ry=0.45, color="belly")
    parts = {"main": main}
    if chest:
        parts["chest"] = bod.cbox([0, 1 + BH * 0.55, bz0 - 0.4], [BW - 1.2, BH * 0.62, 1.6], "fluff", inflate=0.25)
    # back legs: chunky haunch + long flat foot
    for side, name in ((1, "foot_l"), (-1, "foot_r")):
        f = m.bone(name, [side * (BW / 2 - 0.8), 2.5, bz0 + BD * 0.65], parent="body")
        f.box([sx(side, BW / 2 - 1.6, 2.4), 0.6, bz0 + BD * 0.47], [2.4, min(3.6, BH * 0.6), 3.6], "fur")
        foot = f.box([sx(side, BW / 2 - 1.4, 2.0), 0, bz0 + BD * 0.24], [2.0, 1.1, 4.2], "fur")
        foot.decal("down", "toe_beans", color="pad")
        foot.decal("north", "patch", x=0.5, y=0.5, rx=0.5, ry=0.6, color="belly")
    # front paws
    for side, name in ((1, "paw_l"), (-1, "paw_r")):
        p = m.bone(name, [side * 1.6, 3.0, bz0 + 0.7], parent="body")
        paw = p.box([sx(side, 0.9, 1.4), 0, bz0 - 0.1], [1.4, 3.0, 1.4], "fur")
        paw.decal("down", "toe_beans", color="pad")
        paw.decal("north", "band", start=0.65, end=1.0, color="belly")
    tl = m.bone("tail", [0, 1 + BH * 0.6, bz0 + BD], parent="body")
    parts["tail"] = tl.cbox([0, 1 + BH * 0.62, bz0 + BD + tail * 0.28], [tail, tail, tail * 0.75], "fluff", inflate=0.3)

    hy0 = 1 + BH - 1.4
    hz1 = bz0 + 0.7
    look = m.bone("look", [0, hy0 + 1.2, hz1], parent="body")
    hd = m.bone("head", [0, hy0 + 1.2, hz1], parent="look")
    hc = hd.box([-HW / 2, hy0, hz1 - HD], [HW, HH, HD], "fur")
    fy = eye.get("y", 0.44)
    fw_ = eye.get("w", 4)
    fh_ = eye.get("h", 5)
    spread = eye.get("spread", 0.15)
    style = eye.get("style", "sparkle")
    for d in rig.face_decals(y=fy, w=fw_, h=fh_, spread=spread, style=style, lashes=eye.get("lashes", False),
                             nose=None, mouth=None, blush=(0.8, 2)):
        hc.decal("north", d[0], **d[1])
    hc.decal("up", "patch", x=0.5, y=0.5, rx=0.3, ry=0.35, color="fur")
    face_z = hz1 - HD
    muz = hd.cbox([0, hy0 + 1.25, face_z - 0.2], [3, 2, 0.4], "muzzle")
    muz.decal("north", "nose", y=0.2, w=2, h=1)
    muz.decal("north", "mouth", style="u", y=0.5)
    if cheeks:
        hd.cbox([0, hy0 + 1.1, face_z + 2.4], [HW + 1.0, 2.2, 3.0], "fluff", inflate=0.1)
    rig.eyelids(m, hd, hc, y=fy, w=fw_, h=fh_, spread=spread)
    parts["head"] = hc

    top = hy0 + HH
    zc = hz1 - HD / 2
    if ear == "up":
        for side, name in ((1, "ear_l"), (-1, "ear_r")):
            ex = side * (HW / 2 - 1.9)
            e = m.bone(name, [ex, top - 0.2, zc], parent="head", rotation=[-6, 0, side * ear_tilt])
            base = e.box([ex - ear_w / 2, top - 0.4, zc - 0.5], [ear_w, ear_len - 1.0, 1.0], "fur")
            base.decal("north", "inner_ear", inset=0.25, top=0.1, bottom=0.0)
            tip = e.cbox([ex, top - 0.4 + ear_len - 1.0 + 0.35, zc], [ear_w * 0.7, 0.7, 0.9], "fur")
            tip.decal("north", "inner_ear", inset=0.3, top=0.0, bottom=0.4)
            parts[name] = base
    else:  # lop ears hang down the sides of the head
        for side, name in ((1, "ear_l"), (-1, "ear_r")):
            ex = side * (HW / 2 - 0.2)
            e = m.bone(name, [ex, top - 0.3, zc - 0.3], parent="head", rotation=[0, 0, -side * 6])
            lop = e.box([sx(side, HW / 2 - 0.25, 1.1), top - 0.3 - ear_len, zc - 1.8], [1.1, ear_len, 3.0], "fur")
            lop.decal("north", "band", start=0.82, end=1.0, color="fur2")
            lop.decal("south", "band", start=0.82, end=1.0, color="fur2")
            for f in ("east", "west"):
                lop.decal(f, "band", start=0.85, end=1.0, color="fur2")
            e.cbox([side * (HW / 2 + 0.3), top - 0.3 - ear_len - 0.2, zc - 0.3], [1.2, 0.6, 2.4], "fur2")
            parts[name] = lop

    eye_dx, eye_y = face_rect_eye_center(hc, fy, fw_, spread)
    bow_pos = [bow_side * (HW / 2 - 1.2), top + 0.4, zc - 0.9] if ear == "up" else [bow_side * (HW / 2 - 1.0), top + 0.1, zc - 1.2]
    rig.accessories(m, hd, top=(0, top, zc), hw=HW, hd=HD, face_z=face_z, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, hy0 - 0.6, bz0 + 1.0], w=BW, d=5.2),
                    bow=dict(parent="head", pos=bow_pos, rot=[0, 0, -bow_side * 14], s=0.85))
    m.anchors.update(parts=parts, head_top=top, head_zc=zc, face_z=face_z, hy0=hy0, body=body, head=head)
    return m


def build_cotton_bunny(v):
    m = _bunny(v, body=(7, 6, 8), head=(7, 6, 5.5), ear_len=7.0, tail=4.4)
    p = m.anchors["parts"]
    sparkle_body(v, p["main"])
    if v["_variant"] == "cotton_candy":
        p["main"].decal("up", "gradient", top="fur", bottom="fluff", alpha=0.5)
    return m


def build_strawberry_bunny(v):
    m = _bunny(v, body=(7, 6, 7.5), head=(7, 6, 5.5), ear_len=6.0, tail=3.4, ear_tilt=16)
    p = m.anchors["parts"]
    top, zc = m.anchors["head_top"], m.anchors["head_zc"]
    glow = v.get("_rare", False)
    for f in ("east", "west", "up", "south"):
        p["main"].decal(f, "spots", density=0.035, color="seed", kind="seed", seed=11 + len(f), glow_on=glow)
    for f in ("north", "south", "east", "west"):
        p["ear_l"].decal(f, "spots", count=3, color="seed", kind="seed", seed=5 + len(f), glow_on=glow)
        p["ear_r"].decal(f, "spots", count=3, color="seed", kind="seed", seed=7 + len(f), glow_on=glow)
    if v["_variant"] == "chocolate_dipped":
        for f in ("north", "south", "east", "west"):
            p["main"].decal(f, "band", start=0.55, end=1.0, color="fur2")
    # strawberry tail: red with seeds and a tiny green top
    p["tail"].mat = "berry"
    for f in ("east", "west", "south", "up"):
        p["tail"].decal(f, "spots", count=3, color="seed", kind="seed", seed=3 + len(f), glow_on=glow)
    tl = m["tail"]
    tz = p["tail"].origin[2] + p["tail"].size[2]
    tl.cbox([0, p["tail"].origin[1] + p["tail"].size[1] + 0.1, p["tail"].origin[2] + p["tail"].size[2] / 2], [2.2, 0.5, 2.2], "leaf")
    # leafy calyx crown and stem on the head
    cal = m.bone("calyx", [0, top, zc], parent="head")
    for k in range(5):
        lf = m.bone(f"calyx_leaf{k}", [0, top, zc], parent="calyx", rotation=[-16, k * 72, 0])
        lf.box([-0.9, top + 0.05, zc - 3.6], [1.8, 0, 3.4], "leaf", mask=lambda u, v_, f: mask_tear(u, 1 - v_))
    cal.cbox([0, top + 0.9, zc], [0.7, 1.8, 0.7], "stem")
    return m


def _moon_mask(u, v, face=None):
    x, y = u - 0.5, v - 0.5
    return x * x + y * y <= 0.2 and (x - 0.2) ** 2 + (y + 0.12) ** 2 > 0.13


def build_moon_bunny(v):
    m = _bunny(v, body=(6.5, 5.5, 7.5), head=(6.5, 5.8, 5.2), ear_len=9.0, ear_w=1.8, tail=3.8, ear_tilt=8)
    p = m.anchors["parts"]
    top, zc = m.anchors["head_top"], m.anchors["head_zc"]
    many = v["_variant"] == "starlight"
    for f in ("east", "west", "up", "south"):
        p["main"].decal(f, "stars", count=7 if many else 3, color="star", seed=2 + len(f), glow_on=True)
    p["head"].decal("north", "crescent", x=0.5, y=0.14, r=2.2, color="moon", glow_on=True)
    for n in ("ear_l", "ear_r"):
        p[n].decal("north", "band", start=0.0, end=0.12, color="moon", glow_on=True, soft=False)
    p["tail"].glow = "fluff_glow" if "fluff_glow" in v else None
    # the little crescent moon that floats above its head
    mx, my = 6.5 / 2 + 2.6, top + 2.6
    mb = m.bone("moon", [mx, my, zc - 0.8], parent="head")
    mb.cbox([mx, my, zc - 0.8], [3.8, 3.8, 0], "moon", mask=_moon_mask, glow="moon")
    mb.cbox([mx + 1.8, my + 1.6, zc - 0.8], [0.7, 0.7, 0], "star", glow="star")
    return m


def build_lavender_bunny(v):
    m = _bunny(v, body=(7, 6, 8), head=(7, 6, 5.5), ear="lop", ear_len=6.5, tail=4.0,
               eye={"lashes": True, "y": 0.46}, bow_side=-1)
    p = m.anchors["parts"]
    top, zc = m.anchors["head_top"], m.anchors["head_zc"]
    rare = v.get("_rare", False)
    if rare:
        for f in ("east", "west", "up"):
            p["main"].decal(f, "gradient", top="fur", bottom="fur3", alpha=0.6)
        sparkle_body(v, p["main"])
    # lavender sprig tucked behind the right ear
    sp = m.bone("sprig", [2.2, top, zc + 0.6], parent="head", rotation=[-20, 0, 18])
    sp.cbox([2.2, top + 1.6, zc + 0.6], [0.4, 3.4, 0.4], "stem")
    for k in range(5):
        c = sp.cbox([2.2 + (0.25 if k % 2 else -0.25), top + 2.0 + k * 0.6, zc + 0.6], [0.9 - k * 0.08, 0.7, 0.9 - k * 0.08], "petal",
                    glow="sprig_glow" if rare else None)
    sp.box([1.9, top + 0.6, zc + 0.6], [1.6, 0, 1.0], "leaf", mask=lambda u, v_, f: mask_tear(u, 1 - v_), rotation=[0, 30, 0],
           pivot=[2.2, top + 0.6, zc + 0.6])
    return m


def build_snowball_bunny(v):
    m = _bunny(v, body=(8, 7, 8), head=(8, 6.4, 6), ear_len=3.4, ear_w=2.2, tail=4.6, chest=False,
               eye={"y": 0.46, "w": 4, "h": 5, "spread": 0.18}, ear_tilt=20)
    p = m.anchors["parts"]
    p["main"].inflate = 0.4
    p["head"].inflate = 0.3
    for f in ("east", "west", "up", "south"):
        p["main"].decal(f, "spots", count=4, color="flake", kind="sparkle", size=2, seed=4 + len(f),
                        glow_on=v.get("_rare", False))
    if v["_variant"] == "peppermint":
        for f in ("east", "west", "north", "south", "up"):
            p["main"].decal(f, "stripes", color="fur2", every=6, width=2, diagonal=True)
    if v["_variant"] == "aurora":
        for f in ("east", "west", "up", "south"):
            p["main"].decal(f, "band", start=0.15, end=0.35, color="aurora1", glow_on=True)
            p["main"].decal(f, "band", start=0.4, end=0.55, color="aurora2", glow_on=True)
    top, zc = m.anchors["head_top"], m.anchors["head_zc"]
    tuft = m.bone("tuft", [0, top, zc], parent="head")
    tuft.cbox([0, top + 0.5, zc + 0.4], [3.0, 1.2, 2.6], "fluff", inflate=0.2)
    return m


# =========================================================================== QUADRUPED HELPERS

def leg(m, name, parent, x, z, top, w, mat="fur", sock=None, sock_h=0.35, beans=True, depth=None, hoof=False):
    d = depth if depth is not None else w
    b = m.bone(name, [x, top, z], parent=parent)
    c = b.box([x - w / 2, 0, z - d / 2], [w, top, d], mat)
    if sock:
        for f in ("north", "south", "east", "west"):
            c.decal(f, "band", start=1 - sock_h, end=1.0, color=sock, soft=not hoof)
    if beans:
        c.decal("down", "toe_beans", color="pad")
    return b, c


def ear_tri(m, name, parent, x, y, z, w=2.5, h=3.5, d=1.0, side=1, tilt=10.0, inner="inner", tip_mat="fur",
            rot_x=-4.0):
    """A pointy ear built from three shrinking blocks."""
    e = m.bone(name, [x, y, z], parent=parent, rotation=[rot_x, 0, side * tilt])
    segs = ((1.0, 0.45), (0.62, 0.33), (0.3, 0.22))
    yy = y
    first = None
    for k, (fw, fh) in enumerate(segs):
        c = e.box([x - w * fw / 2, yy, z - d / 2 * (1 - 0.1 * k)], [w * fw, h * fh, d * (1 - 0.1 * k)], tip_mat if k == 2 else "fur")
        if k < 2:
            c.decal("north", "inner_ear", color=inner, inset=0.25, top=0.0 if k else 0.2, bottom=0.0)
        yy += h * fh
        first = first or c
    return e, first


def ear_round(m, name, parent, x, y, z, w=2.5, h=2.5, d=1.0, side=1, tilt=8.0, inner="inner", plane=False):
    e = m.bone(name, [x, y, z], parent=parent, rotation=[0, 0, side * tilt])
    if plane:
        c = e.cbox([x, y + h / 2, z], [w, h, 0], "fur", mask=mask_ellipse)
        i = e.cbox([x, y + h / 2 - 0.1, z - 0.05], [w * 0.62, h * 0.62, 0], "inner", mask=mask_ellipse, faces={"south": None})
    else:
        c = e.box([x - w / 2, y, z - d / 2], [w, h, d], "fur")
        c.decal("north", "patch", x=0.5, y=0.55, rx=0.32, ry=0.32, color=inner)
    return e, c


def whisker_planes(m, head, y, z, half_w, length=2.6, h=1.4):
    for side in (1, -1):
        cx = side * (half_w + length / 2 - 0.3)
        c = head.cbox([cx, y, z - 0.06], [length, h, 0], "whisker", faces={"south": None})
        c.decal("north", "whiskers", side="r" if side > 0 else "l")


# =========================================================================== BLOSSOM FOX

def build_blossom_fox(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    bod = m.bone("body", [0, 7, 1.5], parent="root")
    main = bod.box([-2.6, 4.5, -3.0], [5.2, 4.8, 9.0], "fur")
    main.decal("down", "patch", x=0.5, y=0.5, rx=0.4, ry=0.45, color="belly")
    sparkle_body(v, main)
    bod.cbox([0, 6.4, -3.6], [4.6, 4.2, 1.8], "belly", inflate=0.25)
    for name, x, z in (("leg_fl", 1.4, -1.9), ("leg_fr", -1.4, -1.9), ("leg_bl", 1.4, 4.9), ("leg_br", -1.4, 4.9)):
        leg(m, name, "body", x, z, 5.0, 1.5, sock="sock", sock_h=0.45)
    # big fluffy tail with a white tip and a blossom
    tl = m.bone("tail", [0, 8.4, 5.8], parent="body", rotation=[24, 0, 0])
    tl.cbox([0, 8.4, 7.4], [2.6, 2.6, 3.4], "fur")
    tail_main = tl.cbox([0, 8.4, 10.4], [3.8, 3.8, 4.4], "fur", inflate=0.25)
    tl.cbox([0, 8.4, 13.4], [3.0, 3.0, 2.2], "fur2", inflate=0.2)
    sparkle_body(v, tail_main, faces=("east", "west"), count=3)
    tl.cbox([1.6, 9.9, 12.6], [1.6, 1.6, 0], "petal", mask=mask_ellipse, faces={"south": None},
            decals={"north": [("flower", dict(petal="petal", center="gold", glow_on=v.get("_rare", False)))]},
            rotation=[0, 70, 0], pivot=[1.6, 9.9, 12.6])

    look = m.bone("look", [0, 8.6, -3.0], parent="body")
    hd = m.bone("head", [0, 8.6, -3.0], parent="look")
    hc = hd.box([-3.5, 6.6, -8.0], [7.0, 5.6, 5.0], "fur")
    ey = 0.4
    for d in rig.face_decals(y=ey, w=4, h=4, spread=0.2, nose=None, mouth=None, blush=(0.78, 2)):
        hc.decal("north", d[0], **d[1])
    hc.decal("north", "patch", x=0.5, y=0.95, rx=0.42, ry=0.3, color="belly")
    sn = hd.box([-1.5, 6.6, -10.0], [3.0, 2.3, 2.0], "belly")
    sn.decal("north", "nose", y=0.18, w=2, h=1)
    sn.decal("north", "mouth", style="u", y=0.55)
    sn.decal("up", "patch", x=0.5, y=0.2, rx=0.3, ry=0.25, color="nose")
    for side in (1, -1):
        hd.box([sx(side, 3.35, 0.6), 6.6, -6.9], [0.6, 1.8, 2.0], "belly", inflate=0.1)
    rig.eyelids(m, hd, hc, y=ey, w=4, h=4, spread=0.2)
    for side, name in ((1, "ear_l"), (-1, "ear_r")):
        ear_tri(m, name, "head", side * 2.0, 12.0, -5.4, w=2.8, h=4.2, d=1.0, side=side, tilt=12, tip_mat="fur2")
    # cherry blossom behind the left ear
    bl = m.bone("blossom", [2.6, 12.0, -4.6], parent="head")
    bl.cbox([2.9, 12.3, -4.5], [1.9, 1.9, 0], "petal", mask=mask_ellipse,
            decals={"north": [("flower", dict(petal="petal", center="gold", glow_on=v.get("_rare", False)))],
                    "south": [("flower", dict(petal="petal", center="gold"))]})
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 4, 0.2)
    rig.accessories(m, hd, top=(0, 12.2, -5.5), hw=7.0, hd=5.0, face_z=-8.0, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 8.0, -3.2], w=5.4, d=3.4),
                    bow=dict(parent="head", pos=[-2.1, 12.4, -6.1], rot=[0, 0, 14], s=0.85),
                    clip=dict(pos=[-2.6, 11.4, -8.12], rot=[0, 0, -15]))
    return m


# =========================================================================== CLOUD KITTY

def build_cloud_kitty(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    bod = m.bone("body", [0, 6.2, 1.5], parent="root")
    main = bod.box([-2.5, 4.0, -2.5], [5.0, 4.6, 8.0], "fur")
    main.decal("east", "patch", x=0.6, y=0.3, rx=0.25, ry=0.3, color="fur2")
    main.decal("west", "patch", x=0.35, y=0.35, rx=0.22, ry=0.3, color="fur2")
    main.decal("up", "patch", x=0.5, y=0.6, rx=0.3, ry=0.25, color="fur2")
    if v["_variant"] == "storm":
        main.decal("east", "lightning", color="spark")
        main.decal("west", "lightning", color="spark")
    sparkle_body(v, main)
    # cloud ruff around the neck
    for c, s in (([0, 6.8, -4.2], [7.4, 2.4, 3.2]), ([3.4, 7.4, -3.2], [1.8, 2.6, 2.6]), ([-3.4, 7.4, -3.2], [1.8, 2.6, 2.6])):
        bod.cbox(c, s, "cloud", inflate=0.3)
    for name, x, z in (("leg_fl", 1.3, -1.4), ("leg_fr", -1.3, -1.4), ("leg_bl", 1.3, 4.4), ("leg_br", -1.3, 4.4)):
        leg(m, name, "body", x, z, 4.2, 1.5, sock="belly", sock_h=0.3)
    tl = m.bone("tail", [0, 8.0, 5.4], parent="body", rotation=[55, 0, 0])
    tl.box([-0.7, 7.3, 5.2], [1.4, 1.4, 5.0], "fur")
    tt = m.bone("tail_tip", [0, 8.0, 10.2], parent="tail", rotation=[35, 0, 0])
    tip = tt.cbox([0, 8.0, 11.2], [3.0, 3.0, 3.0], "cloud", inflate=0.3)
    if v["_variant"] == "rainbow":
        for f in ("north", "south", "east", "west", "up"):
            tip.decal(f, "rainbow")

    look = m.bone("look", [0, 8.0, -2.5], parent="body")
    hd = m.bone("head", [0, 8.0, -2.5], parent="look")
    hc = hd.box([-3.5, 7.0, -7.5], [7.0, 6.0, 5.0], "fur")
    ey = 0.46
    for d in rig.face_decals(y=ey, w=4, h=5, spread=0.2, nose=(0.68, 2, 1), mouth=("w", 0.77), blush=(0.74, 2)):
        hc.decal("north", d[0], **d[1])
    hc.decal("up", "patch", x=0.5, y=0.7, rx=0.3, ry=0.3, color="fur2")
    whisker_planes(m, hd, 8.6, -7.5, 3.5)
    rig.eyelids(m, hd, hc, y=ey, w=4, h=5, spread=0.2)
    for side, name in ((1, "ear_l"), (-1, "ear_r")):
        ear_tri(m, name, "head", side * 2.0, 12.8, -5.0, w=2.6, h=3.0, d=0.9, side=side, tilt=14)
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 4, 0.2)
    rig.accessories(m, hd, top=(0, 13.0, -5.0), hw=7.0, hd=5.0, face_z=-7.5, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 7.0, -2.2], w=6.0, d=3.6),
                    bow=dict(parent="head", pos=[-2.2, 13.3, -5.6], rot=[0, 0, 14], s=0.85))
    return m


# =========================================================================== STRAWBERRY MOUSE

def build_strawberry_mouse(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    glow = v.get("_rare", False)
    bod = m.bone("body", [0, 2.6, 1.5], parent="root")
    main = bod.box([-2.0, 0.9, -1.5], [4.0, 3.5, 5.5], "fur")
    main.decal("down", "patch", color="belly")
    main.decal("north", "patch", y=0.65, color="belly")
    for name, x, z in (("leg_fl", 1.2, -0.6), ("leg_fr", -1.2, -0.6), ("leg_bl", 1.3, 3.0), ("leg_br", -1.3, 3.0)):
        leg(m, name, "body", x, z, 1.1, 1.0, depth=1.6)
    tl = m.bone("tail", [0, 2.0, 4.0], parent="body", rotation=[8, 0, 0])
    tl.box([-0.3, 1.7, 3.9], [0.6, 0.6, 4.0], "tailskin")
    tt = m.bone("tail_tip", [0, 2.0, 7.9], parent="tail", rotation=[40, 0, 0])
    tt.box([-0.25, 1.75, 7.8], [0.5, 0.5, 3.2], "tailskin")
    tt.cbox([0, 2.0, 11.0], [1.1, 1.1, 0], "berry", mask=rig.heart_mask)

    look = m.bone("look", [0, 3.6, -1.2], parent="body")
    hd = m.bone("head", [0, 3.6, -1.2], parent="look")
    hc = hd.box([-2.3, 2.6, -5.0], [4.6, 4.0, 4.0], "fur")
    ey = 0.5
    for d in rig.face_decals(y=ey, w=2, h=3, spread=0.3, nose=None, mouth=None, blush=(0.8, 2), blush_inset=0):
        hc.decal("north", d[0], **d[1])
    sn = hd.box([-1.0, 2.7, -6.4], [2.0, 1.7, 1.4], "belly")
    sn.decal("north", "nose", y=0.25, w=2, h=1)
    sn.decal("north", "mouth", style="v", y=0.75)
    whisker_planes(m, hd, 3.6, -6.4, 1.0, length=2.4, h=1.2)
    rig.eyelids(m, hd, hc, y=ey, w=2, h=3, spread=0.3)
    # big round ears (planes) poking out of the strawberry hood
    for side, name in ((1, "ear_l"), (-1, "ear_r")):
        ear_round(m, name, "head", side * 2.4, 5.6, -2.6, w=3.0, h=3.0, side=side, tilt=16, plane=True)
    # strawberry hood with seeds and a leafy top
    cap = m.bone("cap", [0, 6.6, -3.0], parent="head")
    cc = cap.box([-2.6, 5.4, -5.3], [5.2, 2.0, 4.6], "berry")
    for f in ("north", "east", "west", "up", "south"):
        cc.decal(f, "spots", density=0.06, color="seed", kind="seed", seed=21 + len(f), glow_on=glow)
    cap.cbox([0, 7.7, -3.0], [3.6, 0.7, 3.4], "berry")
    for k in range(5):
        lf = m.bone(f"cap_leaf{k}", [0, 8.05, -3.0], parent="cap", rotation=[-20, k * 72, 0])
        lf.box([-0.7, 8.05, -5.3], [1.4, 0, 2.4], "leaf", mask=lambda u, v_, f: mask_tear(u, 1 - v_))
    cap.cbox([0, 8.6, -3.0], [0.5, 1.2, 0.5], "stem")
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 2, 0.3)
    rig.accessories(m, hd, top=(0, 8.1, -3.0), hw=4.6, hd=4.0, face_z=-5.0, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 3.1, -1.2], w=4.0, d=2.6),
                    bow=dict(parent="tail_tip", pos=[0, 2.2, 9.6], rot=[0, 90, 0], s=0.55), s=0.6,
                    clip=dict(pos=[1.9, 5.0, -5.4], rot=[0, 0, 15]))
    return m


# =========================================================================== HONEY BEAR

def build_honey_bear(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    glow = v.get("_rare", False)
    bod = m.bone("body", [0, 7.0, 1.5], parent="root")
    main = bod.box([-4.5, 3.5, -4.0], [9.0, 8.0, 10.5], "fur")
    main.decal("north", "patch", y=0.6, rx=0.36, ry=0.42, color="belly")
    main.decal("down", "patch", color="belly")
    sparkle_body(v, main, count=6)
    for name, x, z in (("leg_fl", 2.6, -2.2), ("leg_fr", -2.6, -2.2), ("leg_bl", 2.6, 4.6), ("leg_br", -2.6, 4.6)):
        leg(m, name, "body", x, z, 4.2, 3.0, sock="fur2", sock_h=0.25)
    tl = m.bone("tail", [0, 9.0, 6.5], parent="body")
    tl.cbox([0, 9.0, 6.9], [2.2, 2.2, 1.4], "belly", inflate=0.2)

    look = m.bone("look", [0, 9.6, -3.6], parent="body")
    hd = m.bone("head", [0, 9.6, -3.6], parent="look")
    hc = hd.box([-4.0, 8.2, -9.6], [8.0, 7.0, 6.4], "fur")
    ey = 0.42
    for d in rig.face_decals(y=ey, w=4, h=4, spread=0.3, nose=None, mouth=None, blush=(0.8, 2)):
        hc.decal("north", d[0], **d[1])
    hc.decal("north", "drip", color="honey", depth=0.24)
    hc.decal("up", "patch", x=0.5, y=0.75, rx=0.45, ry=0.3, color="honey", glow_on=glow)
    mz = hd.box([-2.0, 8.4, -11.0], [4.0, 2.8, 1.6], "muzzle")
    mz.decal("north", "nose", y=0.2, w=4, h=2, color="nose")
    mz.decal("north", "mouth", style="u", y=0.66)
    rig.eyelids(m, hd, hc, y=ey, w=4, h=4, spread=0.3)
    for side, name in ((1, "ear_l"), (-1, "ear_r")):
        ear_round(m, name, "head", side * 3.2, 14.6, -6.4, w=2.6, h=2.4, d=1.2, side=side, tilt=10)
    # the bee buddy that orbits the bear's head
    orbit = m.bone("bee_orbit", [0, 15.4, -6.4], parent="look")
    bee = m.bone("bee", [5.2, 16.2, -6.4], parent="bee_orbit")
    bb = bee.cbox([5.2, 16.2, -6.4], [1.6, 1.3, 1.9], "beeyellow")
    for f in ("east", "west", "up", "down"):
        bb.decal(f, "stripes", color="beestripe", every=3, width=1)
    bee.cbox([5.2, 16.2, -7.4], [1.0, 1.0, 0.3], "beestripe")
    for side in (1, -1):
        bee.box([5.2 + (0 if side > 0 else -1.4), 16.9, -6.9], [1.4, 0, 1.2], "beewing", mask=mask_ellipse,
                rotation=[0, 0, side * 20], pivot=[5.2, 16.9, -6.4])
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 4, 0.3)
    rig.accessories(m, hd, top=(0, 15.2, -6.4), hw=8.0, hd=6.4, face_z=-9.6, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 8.6, -3.8], w=8.0, d=3.8),
                    bow=dict(parent="head", pos=[-3.1, 15.5, -7.1], rot=[0, 0, 12], s=1.0), s=1.1)
    return m


# =========================================================================== MOON DEER

def build_moon_deer(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    glow_spots = v.get("spots_glow", False)
    bod = m.bone("body", [0, 13.0, 1.0], parent="root")
    main = bod.box([-3.0, 10.0, -5.0], [6.0, 6.0, 12.0], "fur")
    main.decal("down", "patch", color="belly")
    for f in ("east", "west", "up"):
        main.decal(f, "spots", count=6 if f != "up" else 4, size=2, color="fur2", seed=31 + len(f), glow_on=glow_spots)
        main.decal(f, "stars", count=3, color="star", seed=7 + len(f), glow_on=True)
    for name, x, z in (("leg_fl", 1.8, -3.3), ("leg_fr", -1.8, -3.3), ("leg_bl", 1.8, 5.4), ("leg_br", -1.8, 5.4)):
        leg(m, name, "body", x, z, 10.4, 1.7, sock="hoof", sock_h=0.14, beans=False, hoof=True)
    tl = m.bone("tail", [0, 15.4, 7.0], parent="body", rotation=[30, 0, 0])
    tl.cbox([0, 15.0, 7.6], [2.0, 2.6, 1.4], "belly", inflate=0.15)
    nk = m.bone("neck", [0, 15.2, -4.0], parent="body", rotation=[15, 0, 0])
    nc = nk.box([-1.6, 14.6, -6.2], [3.2, 6.6, 3.2], "fur")
    nc.decal("north", "patch", y=0.6, rx=0.35, ry=0.5, color="belly")
    look = m.bone("look", [0, 20.6, -4.8], parent="neck")
    hd = m.bone("head", [0, 20.6, -4.8], parent="look")
    hc = hd.box([-2.7, 19.6, -9.0], [5.4, 4.8, 5.0], "fur")
    ey = 0.42
    for d in rig.face_decals(y=ey, w=3, h=4, spread=0.22, nose=None, mouth=None, blush=(0.76, 2), lashes=True):
        hc.decal("north", d[0], **d[1])
    hc.decal("north", "crescent", x=0.5, y=0.1, r=1.6, color="star", glow_on=True)
    mz = hd.box([-1.4, 19.6, -10.8], [2.8, 2.4, 1.8], "muzzle")
    mz.decal("north", "nose", y=0.2, w=2, h=1, color="nose")
    mz.decal("north", "mouth", style="u", y=0.62)
    rig.eyelids(m, hd, hc, y=ey, w=3, h=4, spread=0.22)
    for side, name in ((1, "ear_l"), (-1, "ear_r")):
        e = m.bone(name, [side * 2.6, 23.4, -6.4], parent="head", rotation=[0, 0, side * 28])
        c = e.box([sx(side, 2.4, 3.2), 23.0, -6.9], [3.2, 1.6, 0.8], "fur")
        c.decal("north", "inner_ear", inset=0.15, top=0.2, bottom=0.2)
    # glowing branching antlers: two crossed planes each side
    for side, name in ((1, "antler_l"), (-1, "antler_r")):
        a = m.bone(name, [side * 1.4, 24.2, -6.4], parent="head", rotation=[0, 0, side * 10])
        mir = side < 0
        a.box([sx(side, 0.6, 4.6), 24.0, -6.4], [4.6, 6.4, 0], "antler", glow="antler_glow",
              mask=lambda u, v_, f, mir=mir: antler_shape(u, v_, mirror=mir))
        a.box([side * 1.6, 24.0, -8.6], [0, 6.0, 4.0], "antler", glow="antler_glow",
              mask=lambda u, v_, f: antler_shape(u, v_))
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 3, 0.22)
    rig.accessories(m, hd, top=(0, 24.4, -6.5), hw=5.4, hd=5.0, face_z=-9.0, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="neck", center=[0, 17.2, -4.6], w=3.2, d=3.2),
                    bow=dict(parent="head", pos=[-2.2, 24.6, -7.2], rot=[0, 0, 14], s=0.85), s=0.9, hat_tilt=6)
    return m


# =========================================================================== PASTEL AXOLOTL

def _gill_mask(u, v, face=None):
    # feathery frond: tapered with notches
    t = v
    half = 0.5 * (1 - t) ** 0.6 + 0.05
    notch = (math.sin(t * 22) > 0.65) and abs(u - 0.5) > half * 0.55
    return abs(u - 0.5) <= half and not notch


def _fin_mask(u, v, face=None):
    # u along the tail (0 = base .. 1 = tip), v top->bottom
    h = 0.5 * math.sin(math.pi * min(1.0, 0.2 + u * 0.8)) * (1.15 - u * 0.5)
    return abs(v - 0.5) <= max(0.06, h)


def build_pastel_axolotl(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    rare = v.get("_rare", False)
    bod = m.bone("body", [0, 2.8, 2.0], parent="root")
    main = bod.box([-2.5, 1.0, -2.0], [5.0, 3.6, 8.2], "fur")
    main.decal("down", "patch", color="belly")
    main.decal("up", "spots", count=1, kind="heart", color="heart", seed=5, glow_on=rare)
    for f in ("east", "west", "up"):
        main.decal(f, "stars", count=4 if v["_variant"] == "galaxy" else 2, color="glitter", seed=3 + len(f), glow_on=rare)
    for name, x, z in (("leg_fl", 2.6, -0.6), ("leg_fr", -2.6, -0.6), ("leg_bl", 2.6, 4.8), ("leg_br", -2.6, 4.8)):
        side = 1 if x > 0 else -1
        b = m.bone(name, [x, 1.8, z], parent="body", rotation=[0, 0, -side * 35])
        b.box([x - 0.6, 0.0, z - 0.6], [1.2, 1.9, 1.2], "fur")
    tl = m.bone("tail", [0, 2.8, 6.2], parent="body")
    tl.box([-1.0, 1.8, 6.0], [2.0, 2.0, 3.6], "fur")
    tl.box([0, 0.2, 6.2], [0, 5.2, 7.4], "fin", mask=lambda u, v_, f: _fin_mask(u if f == "east" else 1 - u, v_),
           glow="fin_glow" if "fin_glow" in v else None)

    look = m.bone("look", [0, 3.2, -2.0], parent="body")
    hd = m.bone("head", [0, 3.2, -2.0], parent="look")
    hc = hd.box([-4.0, 1.0, -7.4], [8.0, 4.6, 5.4], "fur")
    ey = 0.36
    for d in rig.face_decals(y=ey, w=2, h=3, spread=0.56, nose=None, mouth=("smile", 0.72), blush=(0.62, 3),
                             blush_inset=2):
        hc.decal("north", d[0], **d[1])
    hc.decal("down", "patch", color="belly")
    rig.eyelids(m, hd, hc, y=ey, w=2, h=3, spread=0.56)
    for side, name in ((1, "gills_l"), (-1, "gills_r")):
        g = m.bone(name, [side * 4.0, 4.0, -3.6], parent="head")
        for k, ang in enumerate((40, 5, -30)):
            g.box([sx(side, 4.0, 3.6), 3.4, -3.6 - k * 0.3], [3.6, 1.4, 0], "gill", rotation=[0, 0, -side * ang],
                  pivot=[side * 4.0, 4.0, -3.6], mask=lambda u, v_, f, s=side: _gill_mask(v_, u if s > 0 else 1 - u),
                  glow="gill_glow" if "gill_glow" in v else None)
    gt = m.bone("gills_t", [0, 5.6, -3.0], parent="head")
    gt.box([-3.0, 5.4, -3.2], [6.0, 2.4, 0], "gill", rotation=[-20, 0, 0], pivot=[0, 5.6, -3.0],
           mask=lambda u, v_, f: _gill_mask(abs(u - 0.5) * 2 * 0.6 + 0.2, 1 - v_),
           glow="gill_glow" if "gill_glow" in v else None)
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 2, 0.56)
    rig.accessories(m, hd, top=(0, 5.6, -4.7), hw=8.0, hd=5.4, face_z=-7.4, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 2.9, -2.1], w=5.6, d=1.8),
                    bow=dict(parent="head", pos=[2.6, 5.9, -5.4], rot=[0, 0, -12], s=0.8), s=0.85)
    return m


# =========================================================================== TINY SWAN

def build_tiny_swan(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    rare = v.get("_rare", False)
    bod = m.bone("body", [0, 4.0, 1.0], parent="root")
    main = bod.box([-3.0, 1.6, -3.0], [6.0, 4.8, 8.0], "fur")
    main.decal("up", "feathers", color="feather2", rows=3)
    sparkle_body(v, main)
    bod.cbox([0, 4.0, -3.2], [5.0, 3.6, 1.6], "fur", inflate=0.2)
    bod.box([-2.0, 4.6, 4.6], [4.0, 2.6, 2.4], "fur", rotation=[25, 0, 0], pivot=[0, 4.6, 4.6])
    tf = m.bone("tail", [0, 6.0, 6.4], parent="body", rotation=[35, 0, 0])
    tf.box([-1.8, 6.0, 6.0], [3.6, 0, 3.0], "feather2", mask=lambda u, v_, f: mask_petal(u, v_))
    for side, name in ((1, "wing_l"), (-1, "wing_r")):
        w = m.bone(name, [side * 3.0, 5.6, -1.4], parent="body")
        wc = w.box([sx(side, 2.6, 1.2), 2.6, -1.6], [1.2, 3.8, 7.4], "feather")
        for f in ("east", "west", "up"):
            wc.decal(f, "feathers", color="feather2", rows=3)
        w.box([sx(side, 2.7, 1.0), 4.4, 5.4], [1.0, 2.0, 2.2], "feather", rotation=[30, 0, 0], pivot=[side * 3.2, 5.4, 5.6])
    for side, name in ((1, "foot_l"), (-1, "foot_r")):
        f = m.bone(name, [side * 1.4, 1.8, 1.2], parent="body")
        f.box([side * 1.4 - 0.3, 0.6, 0.9], [0.6, 1.4, 0.6], "beak")
        f.box([side * 1.4 - 0.9, 0, 0.0], [1.8, 0.6, 2.0], "beak")
    nl = m.bone("neck_low", [0, 5.6, -2.4], parent="body", rotation=[12, 0, 0])
    nl.box([-1.0, 5.0, -3.4], [2.0, 5.6, 2.0], "fur")
    nu = m.bone("neck_up", [0, 10.4, -2.4], parent="neck_low", rotation=[-24, 0, 0])
    nu.box([-0.9, 10.0, -3.3], [1.8, 3.6, 1.8], "fur")
    look = m.bone("look", [0, 13.4, -2.4], parent="neck_up")
    hd = m.bone("head", [0, 13.4, -2.4], parent="look", rotation=[14, 0, 0])
    hc = hd.box([-1.6, 12.6, -5.2], [3.2, 3.0, 4.2], "fur")
    ey = 0.42
    for d in rig.face_decals(y=ey, w=1, h=2, spread=0.66, style="round", nose=None, mouth=None, blush=None):
        hc.decal("north", d[0], **d[1])
    bk = hd.box([-0.8, 12.9, -7.4], [1.6, 1.2, 2.2], "beak")
    bk.decal("up", "band", start=0.85, end=1.0, color="knob")
    hd.box([-0.5, 13.6, -5.45], [1.0, 0.8, 0.3], "knob")
    rig.eyelids(m, hd, hc, y=ey, w=1, h=2, spread=0.66)
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 1, 0.66)
    rig.accessories(m, hd, top=(0, 15.6, -3.1), hw=3.2, hd=4.2, face_z=-5.2, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="neck_low", center=[0, 8.2, -2.4], w=2.0, d=2.0, rot=[12, 0, 0]),
                    bow=dict(parent="head", pos=[-1.4, 15.4, -3.2], rot=[0, 0, 20], s=0.6), s=0.55, hat_tilt=6)
    return m


# =========================================================================== RAINBOW BUTTERFLY

def build_rainbow_butterfly(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    rare = v.get("_rare", False)
    bod = m.bone("body", [0, 4.2, 0.0], parent="root")
    bod.cbox([0, 4.2, -0.1], [1.4, 1.4, 2.2], "fur", inflate=0.1)
    ab = bod.box([-0.55, 3.65, 1.0], [1.1, 1.1, 2.4], "fur")
    ab.decal("up", "stripes", color="fur2", every=2, width=1)
    bod.box([-0.4, 3.75, 3.4], [0.8, 0.8, 1.4], "fur2")
    look = m.bone("look", [0, 4.4, -1.2], parent="body")
    hd = m.bone("head", [0, 4.4, -1.2], parent="look")
    hc = hd.box([-1.3, 3.3, -3.4], [2.6, 2.4, 2.2], "fur")
    for d in rig.face_decals(y=0.45, w=2, h=2, spread=0.2, style="round", nose=None, mouth=None, blush=(0.85, 1), blush_inset=0):
        hc.decal("north", d[0], **d[1])
    rig.eyelids(m, hd, hc, y=0.45, w=2, h=2, spread=0.2)
    for side, name in ((1, "antenna_l"), (-1, "antenna_r")):
        a = m.bone(name, [side * 0.6, 5.6, -2.6], parent="head", rotation=[30, 0, side * 20])
        a.box([side * 0.6 - 0.15, 5.6, -2.75], [0.3, 3.0, 0.3], "fur2")
        a.cbox([side * 0.6, 8.7, -2.6], [0.7, 0.7, 0.7], "wing1", glow="wing1" if rare else None)
    for side, name, kind, ox, oz, w, d in ((1, "wing_l", "upper", 0.6, -3.4, 6.4, 5.2), (-1, "wing_r", "upper", 0.6, -3.4, 6.4, 5.2),
                                            (1, "wing_l2", "lower", 0.5, 0.4, 4.6, 4.4), (-1, "wing_r2", "lower", 0.5, 0.4, 4.6, 4.4)):
        b = m.bone(name, [side * 0.6, 4.6 if kind == "upper" else 4.3, oz + d / 2], parent="body")
        c = b.box([sx(side, ox, w), 4.6 if kind == "upper" else 4.3, oz], [w, 0, d], "wing")
        mir = side < 0
        c.decal("up", "wing", kind=kind, mirror=mir, glow_on=rare)
        c.decal("down", "wing", kind=kind, mirror=mir, under=True, glow_on=rare)
    eye_dx, eye_y = face_rect_eye_center(hc, 0.45, 2, 0.2)
    rig.accessories(m, hd, top=(0, 5.7, -2.3), hw=2.6, hd=2.2, face_z=-3.4, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 4.2, -1.1], w=1.4, d=1.2),
                    bow=dict(parent="body", pos=[0, 4.9, 1.6], rot=[0, 0, 0], s=0.5), s=0.42, hat_tilt=10)
    return m


# =========================================================================== CHERRY BLOSSOM BIRD

def build_cherry_blossom_bird(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    rare = v.get("_rare", False)
    bod = m.bone("body", [0, 4.0, 0.5], parent="root")
    main = bod.box([-2.6, 1.5, -2.6], [5.2, 5.0, 6.0], "fur", inflate=0.1)
    main.decal("north", "patch", y=0.7, rx=0.38, ry=0.38, color="belly")
    main.decal("up", "patch", y=0.6, rx=0.45, ry=0.5, color="fur2")
    for f in ("east", "west"):
        main.decal(f, "band", start=0.0, end=0.3, color="fur2")
    main.decal("south", "patch", y=0.3, rx=0.45, ry=0.4, color="fur2")
    sparkle_body(v, main)
    for side, name in ((1, "wing_l"), (-1, "wing_r")):
        w = m.bone(name, [side * 2.6, 5.6, -0.8], parent="body")
        wc = w.box([sx(side, 2.5, 1.0), 2.6, -1.2], [1.0, 3.4, 5.0], "fur2")
        for f in ("east", "west"):
            wc.decal(f, "feathers", color="wingtip", rows=2)
        w.box([sx(side, 2.6, 0.8), 2.9, 3.6], [0.8, 1.8, 1.6], "wingtip")
    tl = m.bone("tail", [0, 3.6, 3.4], parent="body", rotation=[20, 0, 0])
    tl.box([-1.5, 3.3, 3.2], [3.0, 0.6, 4.0], "fur2", decals={"up": [("feathers", dict(color="wingtip", rows=2))]})
    tl.box([-1.0, 3.35, 6.8], [2.0, 0.5, 1.2], "wingtip")
    for side, name in ((1, "foot_l"), (-1, "foot_r")):
        f = m.bone(name, [side * 1.1, 1.6, 0.6], parent="body")
        f.box([side * 1.1 - 0.25, 0.4, 0.35], [0.5, 1.3, 0.5], "beak")
        f.box([side * 1.1 - 0.6, 0.0, -0.4], [1.2, 0.4, 1.6], "beak")
    look = m.bone("look", [0, 6.0, -0.8], parent="body")
    hd = m.bone("head", [0, 6.0, -0.8], parent="look")
    hc = hd.box([-2.5, 5.4, -3.6], [5.0, 4.2, 4.4], "fur", inflate=0.05)
    ey = 0.48
    for d in rig.face_decals(y=ey, w=2, h=3, spread=0.36, nose=None, mouth=None, blush=(0.75, 2), blush_inset=0):
        hc.decal("north", d[0], **d[1])
    hc.decal("up", "patch", y=0.4, rx=0.4, ry=0.4, color="fur2")
    hd.box([-0.55, 6.6, -4.8], [1.1, 0.9, 1.2], "beak")
    rig.eyelids(m, hd, hc, y=ey, w=2, h=3, spread=0.36)
    cr = m.bone("crest", [0, 9.6, -1.6], parent="head", rotation=[-18, 0, 0])
    for k, (ang, dz) in enumerate(((-24, 0.0), (0, 0.4), (24, 0.0))):
        cr.box([-0.8, 9.5, -1.6 + dz], [1.6, 2.6, 0], "petal", rotation=[0, 0, ang], pivot=[0, 9.5, -1.6],
               mask=lambda u, v_, f: mask_petal(u, 1 - v_), glow="petal" if rare else None)
    cr.cbox([0, 9.8, -1.9], [1.4, 1.4, 0], "petal", mask=mask_ellipse,
            decals={"north": [("flower", dict(petal="petal", center="gold", glow_on=rare))]})
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 2, 0.36)
    rig.accessories(m, hd, top=(0, 9.6, -1.4), hw=5.0, hd=4.4, face_z=-3.6, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 5.4, -1.2], w=4.6, d=3.6),
                    bow=dict(parent="head", pos=[-1.9, 9.6, -2.4], rot=[0, 0, 16], s=0.6), s=0.6)
    return m


# =========================================================================== DREAMY HAMSTER

def build_dreamy_hamster(v):
    m = Model(v["_species"])
    m.bone("root", [0, 0, 0])
    rare = v.get("_rare", False)
    bod = m.bone("body", [0, 3.0, 2.0], parent="root")
    main = bod.box([-3.25, 0.5, -2.0], [6.5, 5.4, 7.5], "fur", inflate=0.15)
    main.decal("north", "patch", y=0.7, rx=0.4, ry=0.4, color="belly")
    main.decal("down", "patch", color="belly")
    for f in ("east", "west", "up"):
        main.decal(f, "patch", x=0.5, y=0.3, rx=0.3, ry=0.25, color="fur2")
        main.decal(f, "stars", count=3, color="glitter", seed=4 + len(f), glow_on=rare)
    for name, x, z in (("leg_fl", 1.5, -1.2), ("leg_fr", -1.5, -1.2), ("leg_bl", 2.0, 4.2), ("leg_br", -2.0, 4.2)):
        leg(m, name, "body", x, z, 0.9, 1.2, depth=1.8)
    tl = m.bone("tail", [0, 2.2, 5.5], parent="body")
    tl.cbox([0, 2.2, 5.8], [1.0, 1.0, 0.8], "fur2")
    for side, name in ((1, "paw_l"), (-1, "paw_r")):
        p = m.bone(name, [side * 1.2, 3.4, -2.6], parent="body")
        p.cbox([side * 1.2, 3.0, -2.7], [1.1, 1.2, 1.0], "belly")

    look = m.bone("look", [0, 4.8, -1.4], parent="body")
    hd = m.bone("head", [0, 4.8, -1.4], parent="look")
    hc = hd.box([-3.0, 3.6, -5.6], [6.0, 5.0, 4.8], "fur")
    ey = 0.46
    for d in rig.face_decals(y=ey, w=4, h=4, spread=0.2, nose=(0.68, 2, 1),
                             mouth=("u", 0.8), blush=(0.74, 2), blush_inset=0):
        hc.decal("north", d[0], **d[1])
    hc.decal("north", "patch", x=0.5, y=0.85, rx=0.3, ry=0.25, color="belly")
    rig.eyelids(m, hd, hc, y=ey, w=4, h=4, spread=0.2)
    for side, name in ((1, "cheek_l"), (-1, "cheek_r")):
        ck = m.bone(name, [side * 2.6, 4.8, -3.8], parent="head")
        ck.cbox([side * 2.8, 4.7, -3.9], [2.2, 2.2, 2.4], "belly", inflate=0.1)
    for side, name in ((1, "ear_l"), (-1, "ear_r")):
        ear_round(m, name, "head", side * 2.3, 8.2, -2.4, w=1.9, h=1.8, d=0.6, side=side, tilt=12)
    # the dreamy nightcap (hidden whenever the hamster wears a hat accessory)
    cap = m.bone("headwear", [0, 8.6, -3.2], parent="head", rotation=[0, 0, 6])
    cb = cap.box([-3.2, 8.2, -5.8], [6.4, 1.4, 5.2], "felt2")
    for f in ("north", "south", "east", "west", "up"):
        cb.decal(f, "stars", count=3, color="capstar", seed=9 + len(f), glow_on=True)
    cap.box([-3.25, 8.0, -5.85], [6.5, 0.5, 5.3], "pom")
    s1 = cap.box([-2.2, 9.6, -4.9], [4.4, 1.8, 3.6], "felt2", rotation=[0, 0, 14], pivot=[0, 9.6, -3.2])
    s1.decal("north", "stars", count=2, color="capstar", seed=3, glow_on=True)
    cap.box([-0.4, 10.6, -4.3], [3.2, 1.6, 2.4], "felt2", rotation=[0, 0, 40], pivot=[0, 10.6, -3.2])
    cap.cbox([3.3, 10.5, -3.2], [1.6, 1.6, 1.6], "pom", inflate=0.1)
    eye_dx, eye_y = face_rect_eye_center(hc, ey, 4, 0.2)
    rig.accessories(m, hd, top=(0, 8.6, -3.2), hw=6.0, hd=4.8, face_z=-5.6, eye_y=eye_y, eye_dx=eye_dx,
                    neck=dict(parent="body", center=[0, 4.0, -1.8], w=6.4, d=3.0),
                    bow=dict(parent="head", pos=[-2.6, 8.2, -4.6], rot=[0, 0, 16], s=0.75), s=0.85)
    return m


BUILDERS = {
    "cotton_bunny": build_cotton_bunny,
    "strawberry_bunny": build_strawberry_bunny,
    "moon_bunny": build_moon_bunny,
    "lavender_bunny": build_lavender_bunny,
    "snowball_bunny": build_snowball_bunny,
    "blossom_fox": build_blossom_fox,
    "cloud_kitty": build_cloud_kitty,
    "strawberry_mouse": build_strawberry_mouse,
    "honey_bear": build_honey_bear,
    "moon_deer": build_moon_deer,
    "pastel_axolotl": build_pastel_axolotl,
    "tiny_swan": build_tiny_swan,
    "rainbow_butterfly": build_rainbow_butterfly,
    "cherry_blossom_bird": build_cherry_blossom_bird,
    "dreamy_hamster": build_dreamy_hamster,
}

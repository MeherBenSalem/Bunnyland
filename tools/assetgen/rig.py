"""Shared building blocks for creature models: faces, eyelids and the cosmetic accessories
(collar, bell, bow, flower crown, top hat, party hat, star clip, heart glasses, cozy scarf).

Accessory bone names are part of the contract with the Java renderer:
  collar        tinted with the pet's collar colour
  collar_bell   gold bell, shown with the collar
  bow           tinted with the pet's bow colour
  acc_<id>      one bone per accessory, shown only while that accessory is worn
  eyelids       closed eyes, shown while blinking or asleep
  headwear      a creature's own hat, hidden while it wears a hat accessory
"""
import math

from . import paint
from .geo import mask_ellipse

paint.STYLES.update({
    "crown_leaf": "leaf", "crown_a": "petal", "crown_b": "petal", "crown_c": "petal",
    "crown_mid": "flat", "lens": "clear", "pom": "fluff",
})

ACCESSORY_PALETTE = {
    "tint": "#F4F2F4", "bow": "#F7F5F7", "gold": "#F5C542", "bell": "#F8D25C",
    "crown_leaf": "#86CC7E", "crown_a": "#FFB0C8", "crown_b": "#FFF0A6", "crown_c": "#CDB8FF", "crown_mid": "#FFD45E",
    "felt": "#3D3554", "band": "#FF9EC4", "paper": "#FFC4DE", "paper2": "#8FDDFB", "pom": "#FFFFFF",
    "star": "#FFE36E", "frame": "#F0609A", "lens": "#FFFFFF", "knit": "#FF9DB2", "knit2": "#FFF2F5",
    "pupil": "#2A2140", "mouth": "#B45C7C", "whisker": "#FFFFFF",
}

ACCESSORIES = ("flower_crown", "top_hat", "party_hat", "star_clip", "heart_glasses", "cozy_scarf")


def face_decals(y=0.45, w=3, h=4, spread=0.22, style="sparkle", iris="eye", lashes=False,
                nose=None, mouth=("w", 0.82), blush=(0.7, 2), blush_inset=None):
    """Decals for a head's front face. nose=(y, w, h) or None, mouth=(style, y) or None."""
    out = [("eyes", dict(y=y, w=w, h=h, spread=spread, style=style, iris=iris, lashes=lashes))]
    if blush:
        out.append(("blush", dict(y=blush[0], size=blush[1], inset=blush_inset)))
    if nose:
        out.append(("nose", dict(y=nose[0], w=nose[1], h=nose[2])))
    if mouth:
        out.append(("mouth", dict(style=mouth[0], y=mouth[1])))
    return out


def eyelids(m, head_bone, head_cube, y=0.45, w=3, h=4, spread=0.22, cover="fur"):
    """A plane just in front of the head's face that shows closed eyes."""
    x0, y0, z0 = head_cube.origin
    sw, sh, _ = head_cube.size
    lids = m.bone("eyelids", head_bone.pivot, parent=head_bone.name)
    lids.box([x0, y0, z0 - 0.04], [sw, sh, 0], cover, faces={"south": None},
             decals={"north": [("closed_eyes", dict(y=y, w=w, h=h, spread=spread, cover=cover))]})
    return lids


def _flower_cube(bone, center, s, mat):
    c = bone.cbox(center, [1.5 * s, 1.5 * s, 0.6 * s], mat,
                  decals={"north": [("flower", dict(petal=mat, center="crown_mid"))],
                          "south": [("flower", dict(petal=mat, center="crown_mid"))]},
                  mask=lambda u, v, f: f not in ("north", "south") or mask_ellipse(u, v))
    return c


def heart_mask(u, v, face=None):
    x = u * 2 - 1
    y = (1 - v * 2) * 1.15 + 0.15
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0


def star_mask(u, v, face=None):
    x, y = u - 0.5, 0.5 - v
    a = math.atan2(y, x)
    r = math.hypot(x, y)
    edge = 0.24 + 0.24 * (0.5 + 0.5 * math.cos(5 * (a - math.pi / 2)))
    return r <= edge


def heart_frame_mask(u, v, face=None):
    """Heart outline: inside the heart but not deep inside it."""
    if not heart_mask(u, v):
        return False
    ring = 0.18
    for du, dv in ((ring, 0), (-ring, 0), (0, ring), (0, -ring)):
        if not heart_mask(min(1, max(0, u + du * 0.6)), min(1, max(0, v + dv * 0.6))):
            return True
    return False


def accessories(m, head, top, hw, hd, face_z, eye_y, eye_dx, neck, bow, clip=None, s=1.0, hat_tilt=8.0):
    """Adds every accessory bone.

    head: head bone; top: (x, y, z) centre of the head's top face; hw/hd: head width/depth;
    face_z: z of the head's front face; eye_y/eye_dx: eye centre height and x offset;
    neck: dict(parent, center=(x,y,z), w, d, rot=None); bow: dict(parent, pos, rot, s);
    clip: dict(pos, rot) for the star clip (defaults to the head's front top corner).
    """
    tx, ty, tz = top
    # ----- collar + bell
    nx, ny, nz = neck["center"]
    collar = m.bone("collar", [nx, ny, nz], parent=neck["parent"], rotation=neck.get("rot"))
    collar.cbox([nx, ny, nz], [neck["w"] + 0.7 * s, 1.1 * s, neck["d"] + 0.7 * s], "tint",
                faces={"up": None, "down": None})
    bell = m.bone("collar_bell", [nx, ny, nz], parent=neck["parent"], rotation=neck.get("rot"))
    bz = nz - neck["d"] / 2 - 0.35 * s - 0.5 * s
    bell.cbox([nx, ny - 0.95 * s, bz], [1.1 * s, 1.1 * s, 1.0 * s], "bell")
    bell.cbox([nx, ny - 0.95 * s - 0.6 * s, bz - 0.01], [0.3 * s, 0.2 * s, 1.02 * s], "dark")

    # ----- bow (knot + two loops + tails), tinted as one bone
    bs = bow.get("s", s)
    bx, by, bz2 = bow["pos"]
    b = m.bone("bow", [bx, by, bz2], parent=bow["parent"], rotation=bow.get("rot"))
    b.cbox([bx, by, bz2], [0.9 * bs, 0.9 * bs, 0.8 * bs], "bow")
    for side in (-1, 1):
        b.cbox([bx + side * 1.2 * bs, by + 0.15 * bs, bz2], [1.5 * bs, 1.6 * bs, 0.6 * bs], "bow",
               rotation=[0, 0, side * -12], pivot=[bx, by, bz2])
        b.cbox([bx + side * 0.5 * bs, by - 0.9 * bs, bz2], [0.5 * bs, 1.1 * bs, 0.4 * bs], "bow",
               rotation=[0, 0, side * 18], pivot=[bx, by, bz2])

    # ----- flower crown
    fc = m.bone("acc_flower_crown", [tx, ty, tz], parent=head.name)
    rw, rd = hw + 0.5 * s, hd + 0.5 * s
    vy = ty - 0.35 * s
    fc.cbox([tx, vy, tz - rd / 2], [rw, 0.7 * s, 0.6 * s], "crown_leaf")
    fc.cbox([tx, vy, tz + rd / 2], [rw, 0.7 * s, 0.6 * s], "crown_leaf")
    fc.cbox([tx - rw / 2, vy, tz], [0.6 * s, 0.7 * s, rd], "crown_leaf")
    fc.cbox([tx + rw / 2, vy, tz], [0.6 * s, 0.7 * s, rd], "crown_leaf")
    mats = ("crown_a", "crown_b", "crown_c")
    fz = tz - rd / 2 - 0.15 * s
    for k, fx in enumerate((-0.36, 0.0, 0.36)):
        _flower_cube(fc, [tx + fx * rw, vy + 0.35 * s, fz], s, mats[k % 3])
    for k, side in enumerate((-1, 1)):
        c = fc.cbox([tx + side * (rw / 2 + 0.1 * s), vy + 0.3 * s, tz - rd * 0.12], [0.6 * s, 1.5 * s, 1.5 * s], mats[(k + 1) % 3],
                    decals={"east": [("flower", dict(petal=mats[(k + 1) % 3], center="crown_mid"))],
                            "west": [("flower", dict(petal=mats[(k + 1) % 3], center="crown_mid"))]},
                    mask=lambda u, v, f: f not in ("east", "west") or mask_ellipse(u, v))

    # ----- top hat
    th = m.bone("acc_top_hat", [tx, ty, tz], parent=head.name, rotation=[0, 0, -hat_tilt])
    brim_w = min(hw * 0.78, 7.0 * s + hw * 0.2)
    th.cbox([tx, ty + 0.2 * s, tz], [brim_w, 0.4 * s, min(hd * 0.78, brim_w)], "felt")
    cw = brim_w * 0.62
    crown_h = 2.6 * s
    th.box([tx - cw / 2, ty + 0.4 * s, tz - cw / 2], [cw, crown_h, cw], "felt",
           decals={f: [("band", dict(start=0.62, end=0.86, color="band"))] for f in ("north", "south", "east", "west")})

    # ----- party hat (stacked cone + pom pom)
    ph = m.bone("acc_party_hat", [tx, ty, tz], parent=head.name, rotation=[0, 0, hat_tilt + 4])
    base = min(hw * 0.55, 4.5 * s + hw * 0.1)
    y = ty
    for k, frac in enumerate((1.0, 0.68, 0.4)):
        sz = base * frac
        hgt = 1.3 * s
        ph.box([tx - sz / 2, y, tz - sz / 2], [sz, hgt, sz], "paper",
               decals={f: [("spots", dict(count=3, size=1, color="paper2", seed=k + 1))] for f in ("north", "south", "east", "west")})
        y += hgt
    ph.cbox([tx, y + 0.45 * s, tz], [1.0 * s, 1.0 * s, 1.0 * s], "pom")

    # ----- star clip (a star-shaped plane at the head's front top corner)
    sc = m.bone("acc_star_clip", clip["pos"] if clip else [tx + hw / 2 - 0.6 * s, ty - 0.7 * s, face_z - 0.12],
                parent=head.name)
    cx, cy, cz = clip["pos"] if clip else (tx + hw / 2 - 0.6 * s, ty - 0.7 * s, face_z - 0.12)
    sc.cbox([cx, cy, cz], [2.2 * s, 2.2 * s, 0], "star", mask=star_mask, rotation=clip.get("rot") if clip else [0, 0, 15],
            pivot=[cx, cy, cz])

    # ----- heart glasses (frames only, so the eyes still show)
    hg = m.bone("acc_heart_glasses", [tx, eye_y, face_z], parent=head.name)
    lw = max(1.6 * s, min(2.6 * s, eye_dx * 1.5))
    for side in (-1, 1):
        hg.cbox([tx + side * eye_dx, eye_y, face_z - 0.16], [lw, lw * 0.9, 0], "frame", mask=heart_frame_mask)
    gap = max(0.2, eye_dx * 2 - lw)
    hg.cbox([tx, eye_y + lw * 0.2, face_z - 0.16], [gap + 0.2, 0.3 * s, 0.2 * s], "frame")
    for side in (-1, 1):
        ax = tx + side * (hw / 2 + 0.05)
        hg.box([ax - 0.1 * s, eye_y + lw * 0.2 - 0.15 * s, face_z - 0.16], [0.2 * s, 0.3 * s, min(hd * 0.6, 4 * s)], "frame")

    # ----- cozy scarf
    sf = m.bone("acc_cozy_scarf", [nx, ny, nz], parent=neck["parent"], rotation=neck.get("rot"))
    sf.cbox([nx, ny, nz], [neck["w"] + 1.1 * s, 1.7 * s, neck["d"] + 1.1 * s], "knit",
            decals={f: [("knit", dict(color="knit2", every=2))] for f in ("north", "south", "east", "west")})
    sf.box([nx + neck["w"] * 0.18, ny - 3.2 * s, nz - neck["d"] / 2 - 0.9 * s], [1.5 * s, 3.0 * s, 0.6 * s], "knit",
           rotation=[0, 0, -8], pivot=[nx, ny, nz - neck["d"] / 2],
           decals={f: [("knit", dict(color="knit2", every=2))] for f in ("north", "south")})

"""Item sprites (16x16 pixel art drawn procedurally), item models, block models and
blockstates, particle textures, the Pet Journal GUI texture and the mod logo."""
import math

from .core import ASSETS, C, MODID, ROOT, Img, darken, hash01, lighten, mix, write_json
from .species import IDS

M = MODID + ":"
ITEM_TEX = ASSETS / "textures" / "item"
BLOCK_TEX = ASSETS / "textures" / "block"

BED_COLORS = {
    "pink": ("#FFB6CF", "#FFE3EE", "#F28AB0"),
    "lavender": ("#CDB8F5", "#EFE7FF", "#A68BE0"),
    "mint": ("#A8E6CF", "#E3FBF0", "#76C9A8"),
    "sky": ("#A9D8FF", "#E6F4FF", "#78B6EA"),
}


def outlined(draw, outline_factor=0.45):
    """Runs draw(img) on a fresh 16x16 sprite and adds a soft darker outline."""
    img = Img(16, 16)
    draw(img)
    src = bytes(img.data)
    out = Img(16, 16)
    out.data[:] = src
    for y in range(16):
        for x in range(16):
            if src[(y * 16 + x) * 4 + 3]:
                continue
            neigh = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 16 and 0 <= ny < 16 and src[(ny * 16 + nx) * 4 + 3]:
                    i = (ny * 16 + nx) * 4
                    neigh.append(tuple(src[i:i + 4]))
            if neigh:
                c = neigh[0]
                out.set(x, y, darken(c, outline_factor))
    return out


def shine(img, x, y):
    img.set(x, y, (255, 255, 255, 255))


# --------------------------------------------------------------------------- treats

def bunny_biscuit(img):
    tan, light = C("#E9B97A"), C("#F7D9A8")
    img.ellipse(5.5, 4.2, 1.6, 3.2, tan)
    img.ellipse(10.5, 4.2, 1.6, 3.2, tan)
    img.ellipse(5.5, 4.6, 0.7, 2.0, C("#FFB3C6"))
    img.ellipse(10.5, 4.6, 0.7, 2.0, C("#FFB3C6"))
    img.ellipse(8, 10.2, 5.4, 4.4, tan)
    img.ellipse(7.2, 9.2, 3.2, 2.2, light)
    for x, y in ((6, 10), (10, 10)):
        img.set(x, y, C("#5A3A2A"))
    img.set(5, 11, C("#FF9AB4"))
    img.set(11, 11, C("#FF9AB4"))
    img.set(8, 11, C("#FF7A99"))
    for x, y in ((4, 9), (12, 12), (7, 13)):
        img.set(x, y, C("#FFFFFF"))


def strawberry_tart(img):
    img.rect(2, 10, 14, 14, C("#E8B060"))
    for x in range(2, 14):
        img.set(x, 13, C("#C98A40") if x % 2 else C("#D99A4C"))
    img.rect(3, 8, 13, 10, C("#FFF3E0"))
    for cx in (5, 8, 11):
        img.ellipse(cx, 7.2, 1.9, 1.9, C("#FF5C7A"))
        img.set(cx, 5, C("#7CC46E"))
        img.set(cx - 1, 7, C("#FFE58A"))
        img.set(cx + 1, 8, C("#FFE58A"))
    shine(img, 4, 6)


def moon_cookie(img):
    base = C("#FFE6A0")
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            if dx * dx + dy * dy <= 36 and (dx - 3) ** 2 + (dy + 2) ** 2 > 20:
                img.set(x, y, mix(base, C("#F2C46A"), (y / 16) * 0.6))
    for x, y in ((4, 7), (6, 11), (5, 4), (8, 13)):
        img.set(x, y, C("#FFFFFF"))
    for x, y in ((12, 3), (13, 2), (13, 4), (14, 3)):
        img.set(x, y, C("#FFF6C9"))


def blossom_mochi(img):
    img.ellipse(8, 12.5, 6.5, 2.2, C("#86CC7E"))
    img.ellipse(8, 9.5, 5.6, 4.6, C("#FFC6DA"))
    img.ellipse(7, 8.2, 3.0, 2.2, C("#FFE3EE"))
    img.set(6, 10, C("#5A3A4A"))
    img.set(10, 10, C("#5A3A4A"))
    img.set(5, 11, C("#FF9AB4"))
    img.set(11, 11, C("#FF9AB4"))
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        img.set(11 + dx, 5 + dy, C("#FF8DB4"))
    img.set(11, 5, C("#FFE36E"))


def fish_cracker(img):
    body = C("#F2A85A")
    img.ellipse(7, 8, 5.2, 3.6, body)
    for y in range(4, 13):
        w = abs(y - 8)
        for x in range(12, 15 - w // 2 + 1):
            if w <= 4:
                img.set(x, y, body)
    img.ellipse(6, 7, 2.5, 1.5, lighten(body, 0.3))
    img.set(4, 7, C("#4A2A1A"))
    for x, y in ((7, 9), (9, 7), (8, 10), (10, 9)):
        img.set(x, y, C("#FFF3DA"))


def honey_cake(img):
    for y in range(5, 14):
        for x in range(2, 14):
            img.set(x, y, C("#FFE9B8") if (y - 5) % 3 else C("#FFF8EA"))
    img.rect(2, 4, 14, 6, C("#FFC93C"))
    for x in (3, 6, 9, 12):
        img.set(x, 6, C("#FFC93C"))
        img.set(x, 7, C("#F2A62A"))
    img.rect(2, 13, 14, 14, C("#E8B060"))
    img.ellipse(8, 3, 1.4, 1.4, C("#FF5C7A"))
    shine(img, 4, 4)


def seed_medley(img):
    img.ellipse(8, 10, 5.4, 4.8, C("#FFC4D6"))
    img.rect(5, 3, 11, 6, C("#FFC4D6"))
    img.rect(5, 5, 11, 6, C("#A68BE0"))
    for x, y in ((6, 9), (9, 11), (11, 9), (7, 12), (10, 8)):
        img.set(x, y, C("#F2C46A") if (x + y) % 2 else C("#8A6A3A"))
    for x, y in ((3, 14), (13, 14), (12, 13)):
        img.set(x, y, C("#F2C46A"))
    shine(img, 5, 8)


def flower_nectar(img):
    img.rect(6, 2, 10, 4, C("#C9905A"))
    img.rect(6, 4, 10, 6, C("#E6F4FF"))
    img.ellipse(8, 10.5, 4.8, 4.5, C("#E6F4FF"))
    img.ellipse(8, 11.2, 3.8, 3.4, C("#FF8DC0"))
    img.ellipse(7, 10.2, 1.5, 1.1, C("#FFC2DE"))
    shine(img, 6, 8)
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        img.set(12 + dx, 5 + dy, C("#FFE36E"))
    img.set(12, 5, C("#FF9AB4"))


def pet_kibble(img):
    shapes = [((4, 6), "#FF9AB4", "heart"), ((10, 5), "#A9D8FF", "star"), ((7, 10), "#FFE36E", "bone"),
              ((11, 11), "#B5EAD7", "heart"), ((4, 12), "#CDB8F5", "star")]
    for (cx, cy), col, kind in shapes:
        c = C(col)
        if kind == "heart":
            for dx, dy in ((-1, 0), (0, 0), (1, 0), (-1, -1), (1, -1), (0, 1), (-2, -1), (2, -1), (-1, 1), (1, 1)):
                img.set(cx + dx, cy + dy, c)
        elif kind == "star":
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (-1, 1), (1, 1)):
                img.set(cx + dx, cy + dy, c)
        else:
            for dx in range(-2, 3):
                img.set(cx + dx, cy, c)
            for dx, dy in ((-2, -1), (-2, 1), (2, -1), (2, 1)):
                img.set(cx + dx, cy + dy, c)


# --------------------------------------------------------------------------- cosmetics

def collar_base(img):
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - 8) / 6.4, (y + 0.5 - 7) / 4.6
            r = dx * dx + dy * dy
            if 0.55 <= r <= 1.0:
                img.set(x, y, C("#F4F2F4") if y < 7 else C("#DCD8DC"))
    for x in range(3, 13, 2):
        img.set(x, 3, C("#E2DEE2"))


def collar_bell(img):
    img.ellipse(8, 13, 2.2, 2.2, C("#F8D25C"))
    img.set(8, 14, C("#7A5A20"))
    img.set(7, 12, C("#FFFFFF"))


def bow_base(img):
    for y in range(4, 12):
        w = abs(y - 8)
        for x in range(1, 7 - w // 2):
            img.set(x, y, C("#F7F5F7"))
            img.set(15 - x, y, C("#F7F5F7"))
    img.rect(6, 6, 10, 10, C("#E6E2E6"))
    img.rect(6, 10, 8, 14, C("#ECE8EC"))
    img.rect(9, 10, 11, 14, C("#ECE8EC"))
    img.set(2, 6, C("#FFFFFF"))


def flower_crown(img):
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - 8) / 6.5, (y + 0.5 - 9) / 4.0
            if 0.6 <= dx * dx + dy * dy <= 1.0:
                img.set(x, y, C("#86CC7E"))
    for (cx, cy), col in (((3, 9), "#FFB0C8"), ((8, 5), "#FFF0A6"), ((13, 9), "#CDB8FF"), ((8, 13), "#FFB0C8"), ((5, 6), "#CDB8FF"), ((11, 6), "#FFB0C8")):
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            img.set(cx + dx, cy + dy, C(col))
        img.set(cx, cy, C("#FFD45E"))


def top_hat(img):
    img.rect(1, 12, 15, 14, C("#3D3554"))
    img.rect(4, 3, 12, 12, C("#3D3554"))
    img.rect(4, 9, 12, 11, C("#FF9EC4"))
    img.rect(5, 4, 6, 9, C("#5A5078"))
    img.set(11, 9, C("#FFF3B0"))


def party_hat(img):
    for y in range(3, 14):
        half = (y - 2) * 0.45
        for x in range(16):
            if abs(x + 0.5 - 8) <= half:
                stripe = ((x + y) // 3) % 2
                img.set(x, y, C("#FFC4DE") if stripe else C("#8FDDFB"))
    img.ellipse(8, 2.2, 1.8, 1.8, C("#FFFFFF"))
    img.rect(2, 13, 14, 14, C("#FFE36E"))


def star_clip(img):
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            a = math.atan2(-dy, dx)
            r = math.hypot(dx, dy)
            edge = 3.2 + 3.2 * (0.5 + 0.5 * math.cos(5 * (a - math.pi / 2)))
            if r <= edge:
                img.set(x, y, mix(C("#FFF3B0"), C("#F5C542"), y / 16))
    img.set(6, 6, C("#FFFFFF"))
    img.rect(7, 13, 9, 16, C("#C9CED9"))


def heart_glasses(img):
    def heart(cx, cy, col):
        for y in range(16):
            for x in range(16):
                u = (x + 0.5 - cx) / 3.2
                v = -(y + 0.5 - cy) / 3.0 * 1.15 + 0.15
                inside = (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0
                if inside:
                    img.set(x, y, col)
    heart(4.5, 8, C("#F0609A"))
    heart(11.5, 8, C("#F0609A"))
    for cx in (4.5, 11.5):
        for y in range(16):
            for x in range(16):
                u = (x + 0.5 - cx) / 2.0
                v = -(y + 0.5 - 8) / 1.9 * 1.15 + 0.15
                if (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0:
                    img.set(x, y, C("#FFC9E0"))
    img.rect(7, 6, 9, 7, C("#F0609A"))
    img.set(3, 6, C("#FFFFFF"))
    img.set(10, 6, C("#FFFFFF"))


def cozy_scarf(img):
    for y in range(3, 8):
        for x in range(1, 15):
            img.set(x, y, C("#FF9DB2") if (y // 2) % 2 == 0 else C("#FFF2F5"))
    for y in range(7, 15):
        for x in range(9, 13):
            img.set(x, y, C("#FF9DB2") if (y // 2) % 2 == 0 else C("#FFF2F5"))
    for x in (9, 11):
        img.set(x, 15, C("#FF9DB2"))


# --------------------------------------------------------------------------- toys & care

def yarn_ball(img):
    img.ellipse(8, 8.5, 5.6, 5.6, C("#FF9DB2"))
    for k in range(-2, 3):
        for x in range(16):
            y = int(8.5 + k * 2.2 + math.sin(x * 0.6) * 0.8)
            dx, dy = x + 0.5 - 8, y + 0.5 - 8.5
            if dx * dx + dy * dy < 28:
                img.set(x, y, C("#F07A96"))
    img.line(12, 12, 15, 15, C("#F07A96"))
    img.set(6, 5, C("#FFFFFF"))


def squeaky_carrot(img):
    for y in range(4, 15):
        half = max(0.5, (15 - y) * 0.42)
        for x in range(16):
            if abs(x + 0.5 - 8) <= half:
                img.set(x, y, C("#FFA45C"))
    for x, y in ((6, 1), (7, 2), (8, 1), (9, 2), (10, 1), (8, 3), (7, 3), (9, 3)):
        img.set(x, y, C("#7CC46E"))
    img.set(6, 7, C("#4A2A1A"))
    img.set(10, 7, C("#4A2A1A"))
    img.set(7, 9, C("#B04A2A"))
    img.set(8, 10, C("#B04A2A"))
    img.set(9, 9, C("#B04A2A"))
    img.set(5, 8, C("#FF8DAA"))
    img.set(11, 8, C("#FF8DAA"))


def feather_wand(img):
    img.line(2, 14, 9, 7, C("#D9A066"))
    img.line(9, 7, 10, 5, C("#FF9DB2"))
    for y in range(0, 8):
        for x in range(9, 16):
            dx, dy = x - 12.5, y - 3.5
            if (dx * 0.8 + dy * 0.6) ** 2 / 9 + (dx * 0.6 - dy * 0.8) ** 2 / 2.2 <= 1:
                img.set(x, y, C("#B9A6F2") if (x + y) % 3 else C("#E6DCFF"))
    img.set(13, 2, C("#FFFFFF"))


def pet_carrier(img, full=False):
    img.rect(1, 5, 15, 15, C("#FFB6CF"))
    img.rect(1, 13, 15, 15, C("#F28AB0"))
    img.rect(5, 2, 11, 3, C("#F28AB0"))
    img.set(5, 3, C("#F28AB0"))
    img.set(5, 4, C("#F28AB0"))
    img.set(10, 3, C("#F28AB0"))
    img.set(10, 4, C("#F28AB0"))
    img.rect(4, 7, 12, 13, C("#5A4A66") if full else C("#7A6A86"))
    if full:
        img.ellipse(8, 10.5, 3.2, 2.6, C("#FFF9F5"))
        img.set(6, 7, C("#FFF9F5"))
        img.set(10, 7, C("#FFF9F5"))
        img.set(6, 8, C("#FFF9F5"))
        img.set(10, 8, C("#FFF9F5"))
        img.set(7, 10, C("#2A2140"))
        img.set(9, 10, C("#2A2140"))
        img.set(8, 11, C("#FF8DAA"))
    for x in range(4, 12, 2):
        for y in range(7, 13):
            if not full or not (5 <= x <= 11 and 8 <= y <= 12):
                img.set(x, y, C("#E6E2E6"))
    for y in range(7, 13, 2):
        for x in range(4, 12):
            if not full or not (5 <= x <= 11 and 8 <= y <= 12):
                img.set(x, y, C("#E6E2E6"))
    img.set(2, 6, C("#FFFFFF"))


def pet_journal(img):
    img.rect(2, 1, 14, 15, C("#C9B6F0"))
    img.rect(2, 1, 4, 15, C("#A68BE0"))
    img.rect(13, 2, 14, 14, C("#FFF8F0"))
    img.ellipse(9, 7, 2.6, 2.2, C("#FFFFFF"))
    for x, y in ((7, 4), (11, 4), (6, 6), (12, 6)):
        img.set(x, y, C("#FFFFFF"))
    img.set(9, 7, C("#FF8DAA"))
    img.rect(8, 11, 10, 16, C("#FF8DAA"))
    img.set(8, 15, (0, 0, 0, 0))
    img.set(5, 3, C("#E6DCFF"))


def cotton_fluff(img):
    for cx, cy, r in ((6, 9, 3.6), (10, 8, 3.8), (8, 6, 3.2), (8, 11, 3.0)):
        img.ellipse(cx, cy, r, r * 0.92, C("#FFFFFF"))
    for x, y in ((9, 10), (6, 11), (11, 10)):
        img.set(x, y, C("#EEF0F5"))
    img.set(7, 5, C("#FFFFFF"))


SPRITES = {
    "bunny_biscuit": bunny_biscuit, "strawberry_tart": strawberry_tart, "moon_cookie": moon_cookie,
    "blossom_mochi": blossom_mochi, "fish_cracker": fish_cracker, "honey_cake": honey_cake,
    "seed_medley": seed_medley, "flower_nectar": flower_nectar, "pet_kibble": pet_kibble,
    "flower_crown": flower_crown, "tiny_top_hat": top_hat, "party_hat": party_hat, "star_clip": star_clip,
    "heart_glasses": heart_glasses, "cozy_scarf": cozy_scarf, "yarn_ball": yarn_ball,
    "squeaky_carrot": squeaky_carrot, "feather_wand": feather_wand, "pet_journal": pet_journal,
    "cotton_fluff": cotton_fluff,
}


# --------------------------------------------------------------------------- block textures

def _noise_fill(img, col, seed, amount=0.05):
    for y in range(img.h):
        for x in range(img.w):
            img.set(x, y, darken(col, (hash01(x, y, seed) - 0.5) * amount * 2) if hash01(x, y, seed) < 0.5
                    else lighten(col, (hash01(x, y, seed) - 0.5) * amount * 2))


def bed_textures(color, main, light, dark):
    main, light, dark = C(main), C(light), C(dark)
    side = Img(16, 16)
    _noise_fill(side, main, 3)
    for x in range(16):
        side.set(x, 0, lighten(main, 0.2))
        side.set(x, 15, dark)
        if x % 4 == 1:
            side.set(x, 7, light)
    side.save(BLOCK_TEX / f"{color}_pet_bed_side.png")
    top = Img(16, 16)
    _noise_fill(top, light, 5, 0.03)
    for y in range(16):
        for x in range(16):
            if (x + y) % 8 == 0 or (x - y) % 8 == 0:
                top.set(x, y, mix(light, main, 0.45))
    for x, y in ((4, 4), (12, 4), (4, 12), (12, 12), (8, 8)):
        top.set(x, y, main)
    top.save(BLOCK_TEX / f"{color}_pet_bed_top.png")
    rim = Img(16, 16)
    _noise_fill(rim, main, 7)
    for y in range(16):
        for x in range(16):
            if y % 4 == 0:
                rim.set(x, y, lighten(main, 0.12))
    rim.save(BLOCK_TEX / f"{color}_pet_bed_rim.png")


def bowl_textures():
    side = Img(16, 16)
    _noise_fill(side, C("#FFC4D6"), 11, 0.03)
    for x in range(16):
        side.set(x, 0, C("#FFE3EE"))
        side.set(x, 15, C("#E89AB4"))
    for x, y in ((4, 7), (5, 6), (6, 7), (5, 8), (10, 7), (11, 6), (12, 7), (11, 8)):
        side.set(x, y, C("#FFFFFF"))
    side.save(BLOCK_TEX / "feeding_bowl_side.png")
    inner = Img(16, 16)
    _noise_fill(inner, C("#FFF3F7"), 13, 0.02)
    inner.save(BLOCK_TEX / "feeding_bowl_inner.png")
    food = Img(16, 16)
    cols = [C("#E9B97A"), C("#D9A066"), C("#F2C994"), C("#FF9AB4"), C("#A9D8FF")]
    for y in range(16):
        for x in range(16):
            k = int(hash01(x // 2, y // 2, 5) * len(cols))
            c = cols[k]
            if (x + y) % 2 == 0:
                c = lighten(c, 0.1)
            food.set(x, y, c)
    food.save(BLOCK_TEX / "feeding_bowl_food.png")


# --------------------------------------------------------------------------- models

def item_model(name, layers=None, parent="minecraft:item/generated", overrides=None):
    layers = layers or [M + "item/" + name]
    m = {"parent": parent, "textures": {f"layer{i}": t for i, t in enumerate(layers)}}
    if overrides:
        m["overrides"] = overrides
    write_json(ASSETS / "models" / "item" / f"{name}.json", m)


def el(frm, to, tex, faces=("north", "south", "east", "west", "up", "down"), uv=None, cull=False):
    out = {}
    for f in faces:
        t = tex[f] if isinstance(tex, dict) else tex
        if f in ("up", "down"):
            u = [frm[0], frm[2], to[0], to[2]]
        elif f in ("north", "south"):
            u = [frm[0], 16 - to[1], to[0], 16 - frm[1]]
        else:
            u = [frm[2], 16 - to[1], to[2], 16 - frm[1]]
        out[f] = {"uv": u, "texture": t}
    return {"from": frm, "to": to, "faces": out}


def bed_model(color):
    tx = {"side": f"{M}block/{color}_pet_bed_side", "top": f"{M}block/{color}_pet_bed_top",
          "rim": f"{M}block/{color}_pet_bed_rim", "particle": f"{M}block/{color}_pet_bed_side"}
    elements = [
        el([1, 0, 1], [15, 3, 15], {"north": "#side", "south": "#side", "east": "#side", "west": "#side", "up": "#top", "down": "#side"}),
        el([2, 3, 2], [14, 4, 14], "#top", faces=("north", "south", "east", "west", "up")),
        el([1, 3, 1], [15, 6, 3], "#rim"), el([1, 3, 13], [15, 6, 15], "#rim"),
        el([1, 3, 3], [3, 6, 13], "#rim"), el([13, 3, 3], [15, 6, 13], "#rim"),
    ]
    write_json(ASSETS / "models" / "block" / f"{color}_pet_bed.json",
               {"parent": "minecraft:block/block", "textures": tx, "elements": elements,
                "display": _block_display()})
    write_json(ASSETS / "blockstates" / f"{color}_pet_bed.json", {"variants": {"": {"model": f"{M}block/{color}_pet_bed"}}})
    write_json(ASSETS / "models" / "item" / f"{color}_pet_bed.json", {"parent": f"{M}block/{color}_pet_bed"})


def bowl_models():
    tx = {"side": f"{M}block/feeding_bowl_side", "inner": f"{M}block/feeding_bowl_inner",
          "food": f"{M}block/feeding_bowl_food", "particle": f"{M}block/feeding_bowl_side"}
    walls = [
        el([3, 0, 3], [13, 1, 13], {"north": "#side", "south": "#side", "east": "#side", "west": "#side", "up": "#inner", "down": "#side"}),
        el([3, 1, 3], [13, 4, 4], {"north": "#side", "south": "#inner", "east": "#side", "west": "#side", "up": "#side", "down": "#side"}),
        el([3, 1, 12], [13, 4, 13], {"north": "#inner", "south": "#side", "east": "#side", "west": "#side", "up": "#side", "down": "#side"}),
        el([3, 1, 4], [4, 4, 12], {"north": "#side", "south": "#side", "east": "#inner", "west": "#side", "up": "#side", "down": "#side"}),
        el([12, 1, 4], [13, 4, 12], {"north": "#side", "south": "#side", "east": "#side", "west": "#inner", "up": "#side", "down": "#side"}),
    ]
    levels = {0: None, 1: 1.6, 2: 2.6, 3: 3.5}
    for lvl, h in levels.items():
        els = list(walls)
        if h:
            els.append(el([4, 1, 4], [12, h, 12], "#food", faces=("up",)))
            # little heaped centre for the fuller bowls
            if lvl >= 2:
                els.append(el([6, h, 6], [10, h + 0.6, 10], "#food", faces=("north", "south", "east", "west", "up")))
        name = "feeding_bowl" if lvl == 0 else f"feeding_bowl_{['', 'low', 'half', 'full'][lvl]}"
        write_json(ASSETS / "models" / "block" / f"{name}.json",
                   {"parent": "minecraft:block/block", "textures": tx, "elements": els, "display": _block_display()})
    variants = {}
    for food in range(9):
        lvl = 0 if food == 0 else 1 if food <= 2 else 2 if food <= 5 else 3
        name = "feeding_bowl" if lvl == 0 else f"feeding_bowl_{['', 'low', 'half', 'full'][lvl]}"
        variants[f"food={food}"] = {"model": f"{M}block/{name}"}
    write_json(ASSETS / "blockstates" / "feeding_bowl.json", {"variants": variants})
    write_json(ASSETS / "models" / "item" / "feeding_bowl.json", {"parent": f"{M}block/feeding_bowl_full"})


def _block_display():
    return {
        "gui": {"rotation": [30, 225, 0], "translation": [0, 2, 0], "scale": [0.8, 0.8, 0.8]},
        "ground": {"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.4, 0.4, 0.4]},
        "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.6, 0.6, 0.6]},
        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.4, 0.4, 0.4]},
        "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
        "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
    }


# --------------------------------------------------------------------------- particles

def particles():
    tex = ASSETS / "textures" / "particle"
    frames = []
    for k, r in enumerate((1, 2, 3, 2)):
        img = Img(8, 8)
        col = C("#FFF6C9")
        for i in range(-r, r + 1):
            img.set(3 + i, 3, col if abs(i) < r else lighten(col, 0.3))
            img.set(3, 3 + i, col if abs(i) < r else lighten(col, 0.3))
        img.set(3, 3, C("#FFFFFF"))
        if r >= 2:
            for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
                img.set(3 + dx, 3 + dy, mix(col, C("#FFB3D9"), 0.5))
        img.save(tex / f"sparkle_{k}.png")
        frames.append(f"{M}sparkle_{k}")
    write_json(ASSETS / "particles" / "sparkle.json", {"textures": frames})
    zf = []
    for k, size in enumerate((0, 1)):
        img = Img(8, 8)
        col = C("#C9D8FF") if k == 0 else C("#E6DCFF")
        rows = ["#####.", "...#..", "..#...", ".#....", "#####."] if size else ["####", "..#.", ".#..", "####"]
        img.stamp(1, 1, rows, {"#": col})
        img.save(tex / f"zzz_{k}.png")
        zf.append(f"{M}zzz_{k}")
    write_json(ASSETS / "particles" / "zzz.json", {"textures": zf})


# --------------------------------------------------------------------------- GUI

def journal_gui():
    """512x256 sheet: the open book (292x184 at 0,0) plus small sprites below it."""
    img = Img(512, 256)
    cover, edge, page, line = C("#F7B2C8"), C("#D9809E"), C("#FFF8F0"), C("#F3E6DC")
    W, H = 292, 184
    for y in range(H):
        for x in range(W):
            corner = min(x, W - 1 - x) + min(y, H - 1 - y)
            if (x < 3 or x > W - 4) and (y < 3 or y > H - 4) and corner < 3:
                continue
            img.set(x, y, edge if x < 2 or y < 2 or x > W - 3 or y > H - 3 else cover)
    for y in range(4, H - 4):
        for x in range(4, W - 4):
            if hash01(x // 3, y // 3, 1) > 0.985:
                img.set(x, y, lighten(cover, 0.25))
    for px0 in (8, 148):
        for y in range(8, H - 8):
            for x in range(px0, px0 + 136):
                c = page
                if (y - 8) % 12 == 11 and 14 < (x - px0) < 122:
                    c = line
                shade_edge = (x - px0) if px0 == 148 else (px0 + 135 - x)
                if shade_edge < 4:
                    c = darken(c, 0.06 * (4 - shade_edge))
                img.set(x, y, c)
        for x in range(px0, px0 + 136):
            if x % 6 < 3:
                img.set(x, 8, C("#FFE3EE"))
                img.set(x, H - 9, C("#FFE3EE"))
    for y in range(8, H - 8):
        img.set(145, y, darken(page, 0.18))
        img.set(146, y, darken(page, 0.1))
    img.rect(266, 0, 274, 8, C("#B9A6F2"))
    for (cx, cy) in ((16, 172), (276, 16), (276, 172), (16, 16)):
        for dx, dy in ((-1, 0), (0, 0), (1, 0), (-1, -1), (1, -1), (0, 1)):
            img.set(cx + dx, cy + dy, C("#FFB3C9"))
    # sprites row at y=192: arrows (18x10 normal + hover), check, lock, star, paw, heart
    def arrow(x0, y0, right, hover):
        col = C("#F28AB0") if not hover else C("#E05A8C")
        for y in range(10):
            w = 9 - abs(y - 4.5) * 1.6
            for x in range(18):
                xx = x if right else 17 - x
                if xx < 9 and 3 <= y <= 6:
                    img.set(x0 + x, y0 + y, col)
                elif 9 <= xx < 9 + max(0, w):
                    img.set(x0 + x, y0 + y, col)
    arrow(0, 192, True, False)
    arrow(20, 192, True, True)
    arrow(40, 192, False, False)
    arrow(60, 192, False, True)
    img.stamp(80, 192, ["........#", ".......##", "#.....##.", "##...##..", ".##.##...", "..###....", "...#....."], {"#": C("#5CC48E")})
    img.stamp(92, 192, ["..###..", ".#...#.", ".#...#.", "#######", "##.####", "##.####", "#######"],
              {"#": C("#B5A8C9")})
    img.stamp(102, 192, ["....#....", "...###...", "#########", ".#######.", "..#####..", ".###.###.", ".#.....#."],
              {"#": C("#FFC93C")})
    img.stamp(114, 192, [".#...#.", "##.#.##", ".#####.", "#######", "#######", ".#####.", "..###.."], {"#": C("#E6A0C0")})
    img.stamp(124, 192, [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."], {"#": C("#FF7AA8")})
    img.save(ASSETS / "textures" / "gui" / "pet_journal.png")


def logo():
    img = Img(128, 128)
    for y in range(128):
        for x in range(128):
            d = math.hypot(x - 64, y - 64)
            if d < 62:
                img.set(x, y, mix(C("#FFE3EE"), C("#E6DCFF"), y / 128))
    fur, inner = C("#FFFFFF"), C("#FFB3C9")
    img.ellipse(44, 34, 11, 26, fur)
    img.ellipse(84, 34, 11, 26, fur)
    img.ellipse(44, 36, 5, 18, inner)
    img.ellipse(84, 36, 5, 18, inner)
    img.ellipse(64, 76, 36, 30, fur)
    for ex in (50, 78):
        img.ellipse(ex, 72, 5, 6.5, C("#2A2140"))
        img.ellipse(ex - 1.5, 69.5, 1.8, 1.8, C("#FFFFFF"))
    img.ellipse(42, 84, 6, 3.5, C("#FF9AB4"))
    img.ellipse(86, 84, 6, 3.5, C("#FF9AB4"))
    img.ellipse(64, 82, 3, 2.2, C("#FF7A99"))
    for dx, dy in ((-4, 0), (-2, 2), (0, 0), (2, 2), (4, 0)):
        img.rect(64 + dx, 88 + dy, 65 + dx, 89 + dy, C("#8A4258"))
    for sx_, sy_ in ((20, 22), (106, 26), (110, 96), (18, 100)):
        for i in range(-3, 4):
            img.set(sx_ + i, sy_, C("#FFD45E"))
            img.set(sx_, sy_ + i, C("#FFD45E"))
    img.save(ROOT / "bunnyland_logo.png")


# --------------------------------------------------------------------------- entry

SPAWN_EGG_COLORS = {
    "cotton_bunny": ("#FFF9F5", "#FFB3C9"), "strawberry_bunny": ("#FF8FA4", "#7CC46E"),
    "moon_bunny": ("#5E5CAB", "#FFF0A6"), "lavender_bunny": ("#C9B6F0", "#9B7FE0"),
    "snowball_bunny": ("#FFFFFF", "#A9D8FF"), "blossom_fox": ("#FFB4CA", "#FFFFFF"),
    "cloud_kitty": ("#FFFFFF", "#C4E5FF"), "strawberry_mouse": ("#FFD7DF", "#FF5C7A"),
    "honey_bear": ("#F2B45B", "#FFE3B0"), "moon_deer": ("#6B6DB8", "#CFEAFF"),
    "pastel_axolotl": ("#FFB9DA", "#FF7FB6"), "tiny_swan": ("#FFFFFF", "#FF9E5E"),
    "rainbow_butterfly": ("#C7CEEA", "#FF9AA2"), "cherry_blossom_bird": ("#FFCADB", "#FFFFFF"),
    "dreamy_hamster": ("#FFE9C8", "#B9A6F2"),
}

ITEMS_SIMPLE = list(SPRITES)


def generate():
    for name, fn in SPRITES.items():
        outlined(fn).save(ITEM_TEX / f"{name}.png")
        item_model(name)
    outlined(collar_base).save(ITEM_TEX / "pet_collar.png")
    outlined(collar_bell).save(ITEM_TEX / "pet_collar_bell.png")
    item_model("pet_collar", [M + "item/pet_collar", M + "item/pet_collar_bell"])
    outlined(bow_base).save(ITEM_TEX / "pet_bow.png")
    item_model("pet_bow")
    outlined(lambda i: pet_carrier(i, False)).save(ITEM_TEX / "pet_carrier.png")
    outlined(lambda i: pet_carrier(i, True)).save(ITEM_TEX / "pet_carrier_full.png")
    item_model("pet_carrier_full")
    item_model("pet_carrier", overrides=[{"predicate": {M + "occupied": 1}, "model": M + "item/pet_carrier_full"}])
    for sid in IDS:
        write_json(ASSETS / "models" / "item" / f"{sid}_spawn_egg.json", {"parent": "minecraft:item/template_spawn_egg"})
    for color, cols in BED_COLORS.items():
        bed_textures(color, *cols)
        bed_model(color)
    bowl_textures()
    bowl_models()
    particles()
    journal_gui()
    logo()
    print(f"  {len(SPRITES) + 3} item sprites, {len(BED_COLORS)} pet beds, feeding bowl, particles, journal GUI, logo")

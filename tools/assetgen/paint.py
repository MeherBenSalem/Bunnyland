"""Texture painting for creature models: per-face materials plus decals (faces, patterns,
markings). Every function paints into a rectangle (x, y, w, h) of an Img.

Palettes map material names to colours. Decal colour arguments may be palette keys or
literal colours. Decals with ``glow=True`` also paint into the emissive glow mask, which the
game renders full-bright on top of the model.
"""
import math

from .core import C, Img, darken, hash01, lighten, mix, shade, value_noise

# Material -> painting style. Anything not listed paints as "fur".
STYLES = {
    "fur": "fur", "fur2": "fur", "fur3": "fur", "belly": "fur", "muzzle": "fur", "sock": "fur",
    "fluff": "fluff", "cloud": "fluff", "pom": "fluff",
    "inner": "soft", "nose": "smooth", "pad": "soft", "hoof": "smooth", "beak": "smooth",
    "eyewhite": "flat", "dark": "flat", "tint": "cloth", "bow": "cloth",
    "gold": "metal", "silver": "metal", "bell": "metal",
    "leaf": "leaf", "stem": "flat", "petal": "petal", "petal2": "petal",
    "feather": "feather", "feather2": "feather", "wingtip": "feather",
    "gill": "petal", "fin": "petal",
    "antler": "smooth", "moon": "smooth", "star": "smooth",
    "knit": "knit", "knit2": "knit", "felt": "felt", "felt2": "felt", "band": "flat",
    "lens": "glass", "frame": "smooth", "paper": "felt", "paper2": "felt",
    "berry": "berry", "honey": "honey", "clear": "clear",
    "wing": "wing", "wing2": "wing",
}


def resolve(pal, c):
    if c is None:
        return None
    if isinstance(c, str) and not c.startswith("#"):
        if c not in pal:
            raise KeyError(f"palette has no colour '{c}'")
        return C(pal[c])
    return C(c)


# --------------------------------------------------------------------------- materials

MISSING = set()


def paint_material(img, rect, mat, pal, seed, face):
    x0, y0, w, h = rect
    style = STYLES.get(mat, "fur")
    if mat not in pal:
        MISSING.add((pal.get("_species"), pal.get("_variant"), mat))
    base = resolve(pal, mat if mat in pal else "fur")
    for j in range(h):
        for i in range(w):
            px, py = x0 + i, y0 + j
            v = (j + 0.5) / h
            c = base
            if style in ("fur", "fluff", "soft", "feather", "felt", "knit", "berry", "honey"):
                # Soft top-lit gradient on the sides, brighter tops, shadowed undersides.
                if face in ("north", "south", "east", "west"):
                    f = 1.06 - 0.14 * v
                elif face == "up":
                    f = 1.05
                else:
                    f = 0.86
                c = shade(c, f)
            if style == "fur":
                n = value_noise(px, py, seed, 2.5) - 0.5
                fine = hash01(px, py, seed) - 0.5
                c = shade(c, 1.0 + n * 0.07 + fine * 0.035)
                if hash01(px * 3, py * 7, seed + 11) > 0.93:
                    c = lighten(c, 0.08)
            elif style == "fluff":
                n = value_noise(px, py, seed + 3, 1.8)
                c = shade(c, 0.95 + n * 0.1)
                if hash01(px, py, seed + 5) > 0.88:
                    c = lighten(c, 0.12)
            elif style == "soft":
                c = shade(c, 1.0 + (value_noise(px, py, seed, 3) - 0.5) * 0.05)
            elif style == "smooth":
                c = shade(c, 1.08 - 0.16 * v) if face not in ("up", "down") else shade(c, 1.04 if face == "up" else 0.9)
                if i == 0 and j == 0 and w > 2 and h > 2:
                    c = lighten(c, 0.35)
            elif style == "metal":
                t = (i + j * 0.6) / max(1, w + h * 0.6)
                c = mix(lighten(base, 0.45), darken(base, 0.25), t)
                if (i + j) % 5 == 0 and j < h / 2:
                    c = lighten(c, 0.25)
            elif style == "leaf":
                c = shade(c, 1.0 + (value_noise(px, py, seed, 2) - 0.5) * 0.12)
                if abs(i - (w - 1) / 2.0) < 0.6:
                    c = darken(c, 0.15)
            elif style == "petal":
                c = mix(base, lighten(base, 0.45), v)
                if abs(i - (w - 1) / 2.0) < 0.6 and v > 0.3:
                    c = lighten(c, 0.12)
            elif style == "feather":
                n = value_noise(px, py * 0.5, seed, 2)
                c = shade(c, 0.96 + n * 0.08)
                if j % 3 == 2:
                    c = shade(c, 0.94)
            elif style == "cloth":
                c = shade(base, 1.0 + (value_noise(px, py, seed, 1.5) - 0.5) * 0.06)
                if j == 0 or j == h - 1:
                    c = shade(c, 0.9)
                elif h >= 3 and j == 1 and i % 2 == 0:
                    c = shade(c, 0.86)
            elif style == "knit":
                k = (i + (j // 2)) % 2
                c = shade(c, 0.92 if k else 1.04)
                if j % 2 == 1:
                    c = shade(c, 0.96)
            elif style == "felt":
                c = shade(c, 1.0 + (hash01(px, py, seed) - 0.5) * 0.06)
            elif style == "berry":
                c = shade(c, 1.0 + (value_noise(px, py, seed, 2) - 0.5) * 0.06)
            elif style == "honey":
                c = mix(lighten(base, 0.2), darken(base, 0.1), v)
            elif style == "glass":
                c = mix(lighten(base, 0.4), base, v)
                if i == j or i == j + 1:
                    c = lighten(c, 0.5)
            elif style == "clear":
                c = (0, 0, 0, 0)
            elif style == "wing":
                c = base
            img.set(px, py, c)


# --------------------------------------------------------------------------- decal helpers

def _put(img, glow, x, y, col, glow_on=False, alpha=None):
    if col is None:
        return
    if alpha is None:
        img.set(x, y, col)
    else:
        img.blend(x, y, col, alpha)
    if glow_on and glow is not None:
        glow.set(x, y, col if alpha is None else (col[0], col[1], col[2], int(255 * alpha)))


def _in(rect, x, y):
    x0, y0, w, h = rect
    return x0 <= x < x0 + w and y0 <= y < y0 + h


def eyes(img, glow, rect, pal, face, y=0.5, w=3, h=4, gap=None, style="sparkle", iris="eye",
         lashes=False, pupil="pupil", glow_on=False, spread=None):
    """Big cute eyes. y = centre (0 top .. 1 bottom), w/h = eye size in texels,
    gap = texels between the two eyes (default: proportional to the face width)."""
    x0, y0, fw, fh = rect
    iris_c = resolve(pal, iris)
    dark = resolve(pal, pupil)
    white = (255, 255, 255, 255)
    if gap is None:
        gap = max(1, int(round(fw * (spread if spread else 0.22))))
    cy = y0 + int(round(fh * y - h / 2.0))
    left = x0 + (fw - gap) // 2 - w
    right = x0 + (fw + gap + 1) // 2
    for side, ex in (("l", left), ("r", right)):
        for j in range(h):
            for i in range(w):
                # round the corners of bigger eyes (small eyes stay solid so they don't look like crosses)
                corner = (i in (0, w - 1)) and (j in (0, h - 1)) and w >= 4 and h >= 4
                if corner and style != "dot":
                    continue
                col = dark
                if style in ("sparkle", "round") and j >= h // 2 and h >= 3:
                    col = mix(dark, iris_c, 0.75 if j == h - 1 or (h >= 4 and j == h - 2) else 0.45)
                if style == "sleepy" and j < h // 2:
                    continue
                _put(img, glow, ex + i, cy + j, col, glow_on)
        if style == "sleepy":
            # a soft lid line
            for i in range(w):
                _put(img, glow, ex + i, cy + h // 2 - 1, darken(resolve(pal, "fur"), 0.35))
        if style in ("sparkle", "round") and w >= 2 and h >= 2:
            # Light comes from the upper left for both eyes: a big white catch-light and a small soft one.
            hx = ex + (1 if w >= 4 else 0)
            hy = cy + (1 if h >= 4 else 0)
            _put(img, glow, hx, hy, white)
            if w >= 4 and h >= 5:
                _put(img, glow, hx + 1, hy, white)
            if w >= 3 and h >= 4:
                _put(img, glow, ex + w - 2, cy + h - 2, lighten(iris_c, 0.55))
        if lashes:
            lx = ex - 1 if side == "l" else ex + w
            _put(img, glow, lx, cy, dark)
            _put(img, glow, lx, cy - 1 if h >= 4 else cy, dark)


def closed_eyes(img, glow, rect, pal, face, y=0.5, w=3, h=4, gap=None, cover="fur", spread=None):
    """For the eyelid plane: covers each eye with fur and draws a happy closed 'u' line.
    Everything else on the plane stays transparent."""
    x0, y0, fw, fh = rect
    for i in range(fw):
        for j in range(fh):
            img.set(x0 + i, y0 + j, (0, 0, 0, 0))
    if gap is None:
        gap = max(1, int(round(fw * (spread if spread else 0.22))))
    cy = y0 + int(round(fh * y - h / 2.0))
    left = x0 + (fw - gap) // 2 - w
    right = x0 + (fw + gap + 1) // 2
    cov = resolve(pal, cover)
    line = darken(resolve(pal, "pupil"), 0.0)
    for ex in (left, right):
        for j in range(h):
            for i in range(w):
                img.set(ex + i, cy + j, shade(cov, 1.0 - 0.06 * j / max(1, h)))
        # curved lash line in the lower half
        mid = cy + max(1, h // 2)
        for i in range(w):
            dy = 1 if (i == 0 or i == w - 1) and w >= 3 else 0
            img.set(ex + i, mid + (0 if dy else 1) - (1 if h <= 2 else 0), line)


def blush(img, glow, rect, pal, face, y=0.72, size=2, inset=None, color="blush", alpha=0.5):
    """Two soft rosy cheeks near the outer edges of the face."""
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    inset = inset if inset is not None else max(0, fw // 10)
    cy = y0 + fh * y
    w = max(1, size)
    for cx in (x0 + inset, x0 + fw - inset - w):
        for i in range(w):
            img.blend(cx + i, int(cy), col, alpha)
            if size >= 3 and 0 < i < w - 1:
                img.blend(cx + i, int(cy) + 1, col, alpha * 0.6)


def nose(img, glow, rect, pal, face, y=0.5, w=2, h=1, color="nose", x=0.5):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    cx = x0 + int(round(fw * x - w / 2.0))
    cy = y0 + int(round(fh * y - h / 2.0))
    for j in range(h):
        inset = j if w - 2 * j > 0 and h > 1 else 0
        for i in range(inset, w - inset):
            img.set(cx + i, cy + j, col if j else lighten(col, 0.15))


def mouth(img, glow, rect, pal, face, y=0.8, style="w", color="mouth", width=None):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    cx = x0 + fw // 2
    cy = y0 + int(round(fh * y))
    if style == "w":
        # ω: two little curves meeting under the nose, symmetric for odd and even widths
        if fw % 2 == 1:
            pts = ((-2, 0), (-1, 1), (0, 0), (1, 1), (2, 0))
        else:
            pts = ((-3, 0), (-2, 1), (-1, 0), (0, 0), (1, 1), (2, 0))
        for dx, dy in pts:
            img.set(cx + dx, cy + dy, col)
    elif style == "u":
        # a small soft smile, centred for odd and even widths
        pts = ((-2, 0), (-1, 1), (0, 1), (1, 0)) if fw % 2 == 0 else ((-1, 0), (0, 1), (1, 0))
        for dx, dy in pts:
            img.set(cx + dx, cy + dy, col)
    elif style == "smile":
        half = (width or max(2, fw // 3)) // 2
        for dx in range(-half, half + (0 if fw % 2 == 0 else 1)):
            edge = abs(dx + (0.5 if fw % 2 == 0 else 0)) >= half - 0.5
            img.set(cx + dx, cy - (1 if edge else 0), col)
    elif style == "v":
        img.set(cx - 1, cy, col)
        img.set(cx, cy + (0 if fw % 2 == 0 else 1), col)
        if fw % 2 == 1:
            img.set(cx + 1, cy, col)
    elif style == "dot":
        img.set(cx, cy, col)


def patch(img, glow, rect, pal, face, x=0.5, y=0.5, rx=0.3, ry=0.3, color="belly", alpha=None, glow_on=False):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    cx, cy = x0 + fw * x, y0 + fh * y
    for j in range(fh):
        for i in range(fw):
            dx = (x0 + i + 0.5 - cx) / max(0.01, rx * fw)
            dy = (y0 + j + 0.5 - cy) / max(0.01, ry * fh)
            if dx * dx + dy * dy <= 1.0:
                under = img.get(x0 + i, y0 + j)
                c = mix(col, under, 0.15) if under[3] else col
                _put(img, glow, x0 + i, y0 + j, c, glow_on, alpha)


def band(img, glow, rect, pal, face, start=0.0, end=0.3, color="fur2", vertical=False, soft=True, glow_on=False):
    """Horizontal (or vertical) band across the face, start/end as 0..1 fractions."""
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    n = fw if vertical else fh
    a, b = int(round(start * n)), int(round(end * n))
    for k in range(a, b):
        for m in range(fh if vertical else fw):
            px, py = (x0 + k, y0 + m) if vertical else (x0 + m, y0 + k)
            under = img.get(px, py)
            c = mix(col, under, 0.12) if soft and under[3] else col
            _put(img, glow, px, py, shade(c, 1.0 + (hash01(px, py, 9) - 0.5) * 0.05), glow_on)


def gradient(img, glow, rect, pal, face, top="fur", bottom="fur2", alpha=1.0):
    x0, y0, fw, fh = rect
    a, b = resolve(pal, top), resolve(pal, bottom)
    for j in range(fh):
        col = mix(a, b, (j + 0.5) / fh)
        for i in range(fw):
            under = img.get(x0 + i, y0 + j)
            img.set(x0 + i, y0 + j, mix(under, col, alpha) if under[3] else col)


def drip(img, glow, rect, pal, face, color="honey", depth=0.35, seed=3):
    """Honey drips running down from the top edge."""
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    for i in range(fw):
        d = int(fh * depth * (0.35 + 0.65 * hash01(i // 2, seed)))
        if (i // 2) % 3 == 1:
            d += 2
        for j in range(min(fh, d)):
            img.set(x0 + i, y0 + j, shade(col, 1.1 - 0.2 * j / max(1, d)))
        if d < fh and d > 0:
            img.set(x0 + i, y0 + d - 1, lighten(col, 0.25) if i % 2 == 0 else col)


def spots(img, glow, rect, pal, face, count=6, size=1, color="fur2", seed=1, kind="dot", glow_on=False,
          margin=1, density=None):
    """Scattered spots: dots, strawberry seeds, sparkles or tiny stars."""
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    if density is not None:
        count = max(1, int(fw * fh * density))
    placed = []
    tries = 0
    while len(placed) < count and tries < count * 30:
        tries += 1
        px = x0 + margin + int(hash01(tries, seed, fw) * max(1, fw - 2 * margin))
        py = y0 + margin + int(hash01(seed, tries, fh) * max(1, fh - 2 * margin))
        if any(abs(px - qx) + abs(py - qy) < size + 2 for qx, qy in placed):
            continue
        placed.append((px, py))
        if kind == "dot":
            for j in range(size):
                for i in range(size):
                    _put(img, glow, px + i, py + j, col, glow_on)
        elif kind == "seed":
            _put(img, glow, px, py, col, glow_on)
            _put(img, glow, px, py + 1, darken(col, 0.18), glow_on)
        elif kind == "sparkle":
            _put(img, glow, px, py, col, glow_on)
            if size > 1:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if _in(rect, px + dx, py + dy):
                        _put(img, glow, px + dx, py + dy, mix(col, img.get(px + dx, py + dy), 0.45), glow_on)
        elif kind == "heart":
            heart(img, glow, (px - 2, py - 2, 5, 4), pal, face, color=color, glow_on=glow_on)


def stars(img, glow, rect, pal, face, count=4, color="star", seed=2, glow_on=False, big=False):
    spots(img, glow, rect, pal, face, count=count, size=2 if big else 1, color=color, seed=seed, kind="sparkle",
          glow_on=glow_on, margin=1)


def crescent(img, glow, rect, pal, face, x=0.5, y=0.5, r=None, color="moon", glow_on=False, fill=False):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    r = r if r is not None else min(fw, fh) * 0.4
    cx, cy = x0 + fw * x, y0 + fh * y
    for j in range(fh):
        for i in range(fw):
            px, py = x0 + i + 0.5, y0 + j + 0.5
            d1 = (px - cx) ** 2 + (py - cy) ** 2
            d2 = (px - cx - r * 0.45) ** 2 + (py - cy + r * 0.25) ** 2
            if d1 <= r * r and d2 > (r * 0.8) ** 2:
                _put(img, glow, x0 + i, y0 + j, shade(col, 1.08 - 0.15 * (py - cy + r) / (2 * r)), glow_on)
            elif fill:
                img.set(x0 + i, y0 + j, (0, 0, 0, 0))


def heart(img, glow, rect, pal, face, color="blush", glow_on=False, clear=False):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    for j in range(fh):
        for i in range(fw):
            u = (i + 0.5) / fw * 2 - 1
            v = 1 - (j + 0.5) / fh * 2
            v = v * 1.15 + 0.15
            inside = (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0
            if inside:
                _put(img, glow, x0 + i, y0 + j, shade(col, 1.08 - 0.15 * j / max(1, fh)), glow_on)
            elif clear:
                img.set(x0 + i, y0 + j, (0, 0, 0, 0))


def flower(img, glow, rect, pal, face, x=0.5, y=0.5, r=None, petal="petal", center="gold", glow_on=False):
    """A five-petal blossom."""
    x0, y0, fw, fh = rect
    pc, cc = resolve(pal, petal), resolve(pal, center)
    r = r if r is not None else min(fw, fh) * 0.48
    cx, cy = x0 + fw * x, y0 + fh * y
    for j in range(fh):
        for i in range(fw):
            px, py = x0 + i + 0.5 - cx, y0 + j + 0.5 - cy
            d = math.hypot(px, py)
            a = math.atan2(py, px)
            edge = r * (0.62 + 0.38 * abs(math.cos(a * 2.5)))
            if d <= edge:
                col = cc if d < r * 0.28 else mix(lighten(pc, 0.35), pc, min(1, d / max(0.1, edge)))
                _put(img, glow, x0 + i, y0 + j, col, glow_on)


def lightning(img, glow, rect, pal, face, color="spark", glow_on=True):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    pts = [(0.55, 0.05), (0.35, 0.5), (0.55, 0.5), (0.4, 0.95)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = int(max(abs(bx - ax) * fw, abs(by - ay) * fh)) + 1
        for k in range(n + 1):
            t = k / max(1, n)
            px = x0 + int((ax + (bx - ax) * t) * fw)
            py = y0 + int((ay + (by - ay) * t) * fh)
            for dx in (0, 1):
                if _in(rect, px + dx, py):
                    _put(img, glow, px + dx, py, col, glow_on)


def rainbow(img, glow, rect, pal, face, colors=("#FF9AA2", "#FFDAC1", "#FFF5BA", "#B5EAD7", "#C7CEEA", "#E2B6FF"),
            vertical=False, glow_on=False):
    x0, y0, fw, fh = rect
    n = len(colors)
    for j in range(fh):
        for i in range(fw):
            t = (i / max(1, fw)) if vertical else (j / max(1, fh))
            col = C(colors[min(n - 1, int(t * n))])
            _put(img, glow, x0 + i, y0 + j, shade(col, 1.0 + (hash01(x0 + i, y0 + j, 4) - 0.5) * 0.06), glow_on)


def stripes(img, glow, rect, pal, face, color="fur2", every=3, width=1, diagonal=False, vertical=False):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    for j in range(fh):
        for i in range(fw):
            k = (i + j) if diagonal else (i if vertical else j)
            if k % every < width:
                img.set(x0 + i, y0 + j, mix(col, img.get(x0 + i, y0 + j), 0.1))


def toe_beans(img, glow, rect, pal, face, color="pad"):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    img.ellipse(x0 + fw / 2, y0 + fh * 0.62, max(0.8, fw * 0.3), max(0.6, fh * 0.22), col)
    if fw >= 3:
        for tx in (0.22, 0.5, 0.78):
            img.set(x0 + int(fw * tx), y0 + max(0, int(fh * 0.2)), col)


def inner_ear(img, glow, rect, pal, face, color="inner", inset=0.25, top=0.15, bottom=0.05, glow_on=False):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    ix = max(1 if fw > 2 else 0, int(round(fw * inset)))
    for j in range(int(fh * top), fh - int(fh * bottom)):
        for i in range(ix, fw - ix):
            v = j / max(1, fh)
            _put(img, glow, x0 + i, y0 + j, shade(col, 0.95 + 0.1 * v), glow_on)


def feathers(img, glow, rect, pal, face, color="feather2", rows=3, tip=True):
    """Scalloped feather rows; tips darker."""
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    for j in range(fh):
        for i in range(fw):
            v = (j + 0.5) / fh
            row = int(v * rows)
            local = v * rows - row
            scallop = 0.5 + 0.5 * math.cos((i / 2.0) * math.pi)
            if local > 0.75 - 0.2 * scallop:
                img.set(x0 + i, y0 + j, mix(img.get(x0 + i, y0 + j), col, 0.45))
    if tip:
        for i in range(fw):
            img.set(x0 + i, y0 + fh - 1, mix(img.get(x0 + i, y0 + fh - 1), col, 0.8))


def knit_pattern(img, glow, rect, pal, face, color="knit2", every=4):
    x0, y0, fw, fh = rect
    col = resolve(pal, color)
    for j in range(fh):
        if (j // 2) % every == 0:
            for i in range(fw):
                img.set(x0 + i, y0 + j, mix(col, img.get(x0 + i, y0 + j), 0.2))


def whiskers(img, glow, rect, pal, face, color="whisker", lines=2, side="r"):
    """Whisker lines on an otherwise transparent plane."""
    x0, y0, fw, fh = rect
    for j in range(fh):
        for i in range(fw):
            img.set(x0 + i, y0 + j, (0, 0, 0, 0))
    col = resolve(pal, color)
    for k in range(lines):
        yy = y0 + int((k + 0.5) * fh / lines)
        for i in range(fw):
            t = i / max(1, fw - 1)
            if side == "r":
                px, py = x0 + i, yy + int((t - 0.2) * (k - (lines - 1) / 2) * 1.5)
            else:
                px, py = x0 + fw - 1 - i, yy + int((t - 0.2) * (k - (lines - 1) / 2) * 1.5)
            if _in(rect, px, py):
                img.set(px, py, col)


def wing_pattern(img, glow, rect, pal, face, kind="upper", mirror=False, glow_on=False, under=False):
    """Butterfly wing: colour bands radiating from the body, dark veins and a dark rim with dots."""
    x0, y0, fw, fh = rect
    bands = [resolve(pal, k) for k in ("wing1", "wing2", "wing3", "wing4")]
    rim = resolve(pal, "wingrim")
    dot = resolve(pal, "wingdot")
    for j in range(fh):
        for i in range(fw):
            u = (i + 0.5) / fw
            v = (j + 0.5) / fh
            if mirror:
                u = 1 - u
            # distance from the wing root (root is at u=0; upper wings root at the back edge)
            ru = u
            rv = (1 - v) if kind == "upper" else v
            d = math.hypot(ru * 1.0, rv * 0.6)
            k = min(len(bands) - 1, int(d * len(bands) * 0.95))
            col = mix(bands[k], bands[min(len(bands) - 1, k + 1)], (d * len(bands) * 0.95) % 1.0 * 0.5)
            if under:
                # undersides face down and get darker entity lighting, so paint them paler
                col = lighten(mix(col, bands[0], 0.3), 0.45)
            ang = math.atan2(rv, ru)
            if abs(math.sin(ang * 5.0)) < 0.09 and d > 0.15:
                col = darken(col, 0.2)
            inside = _wing_shape(u, v, kind)
            edge = inside and not _wing_shape(u + 0.07 * (1 if u > 0.5 else -1), v + (0.07 if v > 0.5 else -0.07), kind)
            if not inside:
                img.set(x0 + i, y0 + j, (0, 0, 0, 0))
                continue
            if edge or d > 0.98:
                col = rim
                if hash01(i, j, 77) > 0.72:
                    col = dot
            _put(img, glow, x0 + i, y0 + j, col, glow_on)


def _wing_shape(u, v, kind):
    if u < 0 or u > 1 or v < 0 or v > 1:
        return False
    if kind == "upper":
        # broad triangle-ish lobe, rounded tip at far front-outer corner
        cx, cy = 0.3, 0.55
        r = 0.62 + 0.25 * u
        return ((u - cx) / 0.75) ** 2 + ((v - cy) / (r * 0.85)) ** 2 <= 1.0 and not (u < 0.1 and v < 0.15)
    # lower wing: rounder, with a little tail
    if ((u - 0.35) / 0.68) ** 2 + ((v - 0.42) / 0.55) ** 2 <= 1.0:
        return True
    return 0.25 < u < 0.45 and v > 0.8


def antler_shape(u, v, mirror=False):
    """Branching antler silhouette for a plane; u across, v top->bottom."""
    if mirror:
        u = 1 - u
    t = 1 - v
    main_x = 0.3 + 0.25 * t
    if abs(u - main_x) < 0.09 + 0.04 * v:
        return True
    for bt, bx in ((0.35, 0.05), (0.62, 0.0), (0.85, 0.05)):
        if t > bt:
            k = (t - bt)
            tx = main_x + k * 1.6 * (1 if bx == 0.0 else -0.8)
            if abs(u - tx) < 0.07 and abs(t - bt - abs(tx - main_x) * 0.7) < 0.12:
                return True
    return False


DECALS = {
    "eyes": eyes, "closed_eyes": closed_eyes, "blush": blush, "nose": nose, "mouth": mouth,
    "patch": patch, "band": band, "gradient": gradient, "drip": drip, "spots": spots, "stars": stars,
    "crescent": crescent, "heart": heart, "flower": flower, "lightning": lightning, "rainbow": rainbow,
    "stripes": stripes, "toe_beans": toe_beans, "inner_ear": inner_ear, "feathers": feathers,
    "knit": knit_pattern, "whiskers": whiskers, "wing": wing_pattern,
}


def paint_model(model, pal, seed):
    """Paints every face of every cube. Returns (texture, glowmask or None)."""
    img = Img(model.tex_w, model.tex_h)
    glow = Img(model.tex_w, model.tex_h)
    for n, cube in enumerate(model.cubes()):
        for face, rect in cube.uv.items():
            mat = cube.face_mat(face)
            paint_material(img, rect, mat, pal, seed + n * 7, face)
            for name, kw in cube.decals.get(face, []):
                kw = dict(kw)
                if kw.pop("_skip", False):
                    continue
                DECALS[name](img, glow, rect, pal, face, **kw)
            x0, y0, w, h = rect
            if cube.mask is not None:
                for j in range(h):
                    for i in range(w):
                        if not cube.mask((i + 0.5) / w, (j + 0.5) / h, face):
                            img.set(x0 + i, y0 + j, (0, 0, 0, 0))
                            glow.set(x0 + i, y0 + j, (0, 0, 0, 0))
            if cube.glow:
                gc = resolve(pal, cube.glow)
                for j in range(h):
                    for i in range(w):
                        under = img.get(x0 + i, y0 + j)
                        if under[3]:
                            glow.set(x0 + i, y0 + j, mix(gc, under, 0.35))
    has_glow = any(glow.data[i + 3] for i in range(0, len(glow.data), 4))
    return img, (glow if has_glow else None)

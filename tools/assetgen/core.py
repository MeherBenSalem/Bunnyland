"""Core helpers for the Bunnyland asset generator: paths, JSON output, colours, deterministic
noise and a tiny RGBA image class that writes PNGs with nothing but the standard library."""
import colorsys
import json
import math
import struct
import zlib
from pathlib import Path

MODID = "bunnyland"
PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT / "src" / "main" / "resources"
ASSETS = ROOT / "assets" / MODID
DATA = ROOT / "data" / MODID


# --------------------------------------------------------------------------- output

def write_json(path, obj, compact=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    else:
        text = json.dumps(obj, indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- colours

def C(value, alpha=255):
    """Accepts '#RRGGBB', (r,g,b) or (r,g,b,a) and returns an RGBA tuple."""
    if isinstance(value, str):
        v = value.lstrip("#")
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16), alpha)
    if len(value) == 3:
        return (value[0], value[1], value[2], alpha)
    return tuple(value)


def clamp8(v):
    return max(0, min(255, int(round(v))))


def mix(a, b, t):
    a, b = C(a), C(b)
    return tuple(clamp8(a[i] + (b[i] - a[i]) * t) for i in range(4))


def lighten(c, t):
    c = C(c)
    return mix(c, (255, 255, 255, c[3]), t)


def darken(c, t):
    c = C(c)
    return mix(c, (0, 0, 0, c[3]), t)


def shade(c, f):
    """Multiplies brightness by f, nudging hue slightly warm when lightening and cool when darkening."""
    c = C(c)
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    if f < 1:
        h = (h + (0.66 - h) * 0.04 * (1 - f) * 4) % 1.0
        s = min(1.0, s + (1 - f) * 0.25)
    v = max(0.0, min(1.0, v * f))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (clamp8(r * 255), clamp8(g * 255), clamp8(b * 255), c[3])


def hue_shift(c, dh, ds=0.0, dv=0.0):
    c = C(c)
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    r, g, b = colorsys.hsv_to_rgb((h + dh) % 1.0, max(0, min(1, s + ds)), max(0, min(1, v + dv)))
    return (clamp8(r * 255), clamp8(g * 255), clamp8(b * 255), c[3])


def hsv(h, s, v, a=255):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    return (clamp8(r * 255), clamp8(g * 255), clamp8(b * 255), a)


def rgb_int(c):
    c = C(c)
    return (c[0] << 16) | (c[1] << 8) | c[2]


# --------------------------------------------------------------------------- noise

def hash01(*vals):
    """Deterministic pseudo-random float in [0, 1) from integer inputs."""
    h = 2166136261
    for v in vals:
        h ^= int(v) & 0xFFFFFFFF
        h = (h * 16777619) & 0xFFFFFFFF
        h ^= h >> 13
        h = (h * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return (h & 0xFFFFFF) / float(0x1000000)


def value_noise(x, y, seed, scale=4.0):
    """Smooth 2D value noise in [0, 1)."""
    fx, fy = x / scale, y / scale
    x0, y0 = math.floor(fx), math.floor(fy)
    tx, ty = fx - x0, fy - y0
    tx = tx * tx * (3 - 2 * tx)
    ty = ty * ty * (3 - 2 * ty)
    a = hash01(x0, y0, seed)
    b = hash01(x0 + 1, y0, seed)
    c = hash01(x0, y0 + 1, seed)
    d = hash01(x0 + 1, y0 + 1, seed)
    return (a + (b - a) * tx) + ((c + (d - c) * tx) - (a + (b - a) * tx)) * ty


def str_seed(s):
    return int(hash01(*[ord(ch) for ch in s]) * 1_000_000)


# --------------------------------------------------------------------------- images

class Img:
    def __init__(self, w, h, fill=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.data = bytearray(bytes(C(fill)) * (w * h))

    def inside(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def get(self, x, y):
        i = (int(y) * self.w + int(x)) * 4
        return tuple(self.data[i:i + 4])

    def set(self, x, y, c):
        x, y = int(x), int(y)
        if self.inside(x, y):
            i = (y * self.w + x) * 4
            self.data[i:i + 4] = bytes(C(c))

    def blend(self, x, y, c, alpha=None):
        x, y = int(x), int(y)
        if not self.inside(x, y):
            return
        c = C(c)
        a = (c[3] / 255) if alpha is None else alpha * (c[3] / 255)
        under = self.get(x, y)
        if under[3] == 0:
            self.set(x, y, (c[0], c[1], c[2], clamp8(255 * a)))
            return
        out = tuple(clamp8(under[i] + (c[i] - under[i]) * a) for i in range(3)) + (max(under[3], clamp8(255 * a)),)
        self.set(x, y, out)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, int(y0)), min(self.h, int(y1))):
            for x in range(max(0, int(x0)), min(self.w, int(x1))):
                self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, alpha=None):
        for y in range(int(math.floor(cy - ry)) - 1, int(math.ceil(cy + ry)) + 1):
            for x in range(int(math.floor(cx - rx)) - 1, int(math.ceil(cx + rx)) + 1):
                dx = (x + 0.5 - cx) / max(rx, 0.01)
                dy = (y + 0.5 - cy) / max(ry, 0.01)
                if dx * dx + dy * dy <= 1.0:
                    if alpha is None:
                        self.set(x, y, c)
                    else:
                        self.blend(x, y, c, alpha)

    def line(self, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(n, 1)
            self.set(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), c)

    def stamp(self, x0, y0, rows, palette):
        """Draws ASCII art: each character maps to a palette colour ('.' or ' ' = skip)."""
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch in ". " or ch not in palette:
                    continue
                col = palette[ch]
                if col is None:
                    self.set(x0 + dx, y0 + dy, (0, 0, 0, 0))
                else:
                    self.set(x0 + dx, y0 + dy, col)

    def outline(self, color, only_transparent_neighbours=True):
        """Adds a 1px outline around opaque pixels (used for item sprites)."""
        src = bytes(self.data)
        for y in range(self.h):
            for x in range(self.w):
                i = (y * self.w + x) * 4
                if src[i + 3] != 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[(ny * self.w + nx) * 4 + 3] > 0:
                        self.set(x, y, color)
                        break

    def scaled(self, factor):
        out = Img(self.w * factor, self.h * factor)
        for y in range(out.h):
            for x in range(out.w):
                out.set(x, y, self.get(x // factor, y // factor))
        return out

    def paste(self, other, x0, y0):
        for y in range(other.h):
            for x in range(other.w):
                c = other.get(x, y)
                if c[3]:
                    self.blend(x0 + x, y0 + y, c)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = bytearray()
        stride = self.w * 4
        for y in range(self.h):
            raw.append(0)
            raw.extend(self.data[y * stride:(y + 1) * stride])

        def chunk(tag, body):
            return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += chunk(b"IEND", b"")
        path.write_bytes(png)

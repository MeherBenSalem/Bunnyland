"""A small cuboid-model DSL that exports GeckoLib / Bedrock ``.geo.json`` geometry.

Coordinates are Bedrock model space in pixels: y up, the creature's FRONT faces -Z (the
"north" face of a cube is the side you see when the creature looks at you). Cube origins are
absolute (not relative to their bone), exactly like Blockbench.

Every cube face gets its own rectangle in the texture (per-face UV) at DENSITY texels per
model pixel, so the painter knows exactly which texels belong to which face. Faces can be
skipped (hidden faces and the edges of flat "planes"), which also keeps textures small.
"""
import math

DENSITY = 2
FACES = ("north", "south", "east", "west", "up", "down")
# Flat planes are given this much thickness: with no-cull rendering two coplanar faces z-fight and the
# back-facing (dark-lit) one wins, so each side needs its own face slightly in front.
PLANE = 0.04


def _tex(units):
    return max(1, int(round(units * DENSITY)))


class Cube:
    def __init__(self, bone, origin, size, mat, inflate=0.0, rotation=None, pivot=None,
                 faces=None, decals=None, mask=None, glow=None, name=None):
        self.bone = bone
        self.origin = [float(v) for v in origin]
        self.size = [float(v) for v in size]
        self.mat = mat
        self.inflate = inflate
        self.rotation = rotation
        self.pivot = pivot
        # face -> material name, or None to omit the face entirely
        self.faces = dict(faces or {})
        # face -> list of (decal_name, kwargs) painted on top of the material
        self.decals = {k: list(v) for k, v in (decals or {}).items()}
        # optional cut-out shape: callable(u, v, face) -> bool (u, v in 0..1); False = transparent
        self.mask = mask
        # material key of the emissive layer for this cube (None = no glow)
        self.glow = glow
        self.name = name
        self.uv = {}
        zero_area = {0: ("north", "south", "up", "down"), 1: ("north", "south", "east", "west"),
                     2: ("east", "west", "up", "down")}
        for axis, s in enumerate(self.size):
            if s == 0:
                # A flat plane: drop the edge faces and give it a sliver of thickness.
                for f in zero_area[axis]:
                    self.faces[f] = None
                self.size[axis] = PLANE

    def face_mat(self, face):
        return self.faces.get(face, self.mat)

    def face_units(self, face):
        w, h, d = self.size
        if face in ("north", "south"):
            return w, h
        if face in ("east", "west"):
            return d, h
        return w, d

    def face_texels(self, face):
        u, v = self.face_units(face)
        return _tex(u), _tex(v)

    def decal(self, face, name, **kw):
        self.decals.setdefault(face, []).append((name, kw))
        return self


class Bone:
    def __init__(self, model, name, pivot, parent=None, rotation=None):
        self.model = model
        self.name = name
        self.pivot = [float(v) for v in pivot]
        self.parent = parent
        self.rotation = rotation
        self.cubes = []

    def box(self, origin, size, mat, **kw):
        c = Cube(self, origin, size, mat, **kw)
        self.cubes.append(c)
        return c

    def cbox(self, center, size, mat, **kw):
        """Box by centre point."""
        o = [center[i] - size[i] / 2.0 for i in range(3)]
        return self.box(o, size, mat, **kw)

    def gbox(self, cx, y0, cz, size, mat, **kw):
        """Box centred on x/z standing on y0."""
        return self.box([cx - size[0] / 2.0, y0, cz - size[2] / 2.0], size, mat, **kw)


class Model:
    def __init__(self, name):
        self.name = name
        self.bones = []
        self.by_name = {}
        self.tex_w = self.tex_h = 0
        # anchors used by accessory builders and documentation
        self.anchors = {}

    def bone(self, name, pivot, parent=None, rotation=None):
        if name in self.by_name:
            raise ValueError(f"duplicate bone {name} in {self.name}")
        b = Bone(self, name, pivot, parent, rotation)
        self.bones.append(b)
        self.by_name[name] = b
        return b

    def __getitem__(self, name):
        return self.by_name[name]

    def cubes(self):
        for b in self.bones:
            for c in b.cubes:
                yield c

    # ------------------------------------------------------------------ UV packing
    def pack(self):
        rects = []
        for c in self.cubes():
            for f in FACES:
                if c.face_mat(f) is None:
                    continue
                w, h = c.face_texels(f)
                rects.append((h, w, c, f))
        rects.sort(key=lambda r: (-r[0], -r[1]))
        area = sum(r[0] * r[1] for r in rects)
        size = 32
        while size * size < area * 1.15:
            size *= 2
        while True:
            placed = self._shelf(rects, size)
            if placed is not None:
                height = 32
                while height < placed:
                    height *= 2
                self.tex_w, self.tex_h = size, max(height, size // 2)
                return
            size *= 2

    @staticmethod
    def _shelf(rects, width):
        x = y = shelf_h = 0
        for h, w, c, f in rects:
            if w > width:
                return None
            if x + w > width:
                x, y = 0, y + shelf_h
                shelf_h = 0
            c.uv[f] = (x, y, w, h)
            x += w
            shelf_h = max(shelf_h, h)
        return y + shelf_h

    # ------------------------------------------------------------------ export
    def to_json(self):
        bones = []
        lo = [1e9] * 3
        hi = [-1e9] * 3
        for b in self.bones:
            jb = {"name": b.name, "pivot": _r(b.pivot)}
            if b.parent:
                jb["parent"] = b.parent
            if b.rotation and any(b.rotation):
                jb["rotation"] = _r(b.rotation)
            cubes = []
            for c in b.cubes:
                jc = {"origin": _r(c.origin), "size": _r(c.size)}
                if c.inflate:
                    jc["inflate"] = c.inflate
                if c.rotation and any(c.rotation):
                    jc["rotation"] = _r(c.rotation)
                    jc["pivot"] = _r(c.pivot if c.pivot else [c.origin[i] + c.size[i] / 2 for i in range(3)])
                uv = {}
                for f in FACES:
                    if f in c.uv:
                        x, y, w, h = c.uv[f]
                        uv[f] = {"uv": [x, y], "uv_size": [w, h]}
                jc["uv"] = uv
                cubes.append(jc)
                for i in range(3):
                    lo[i] = min(lo[i], c.origin[i])
                    hi[i] = max(hi[i], c.origin[i] + c.size[i])
            if cubes:
                jb["cubes"] = cubes
            bones.append(jb)
        width = max(hi[0] - lo[0], hi[2] - lo[2]) / 16.0
        height = (hi[1] - lo[1]) / 16.0
        return {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": "geometry.bunnyland." + self.name,
                    "texture_width": self.tex_w,
                    "texture_height": self.tex_h,
                    "visible_bounds_width": round(width + 1.5, 2),
                    "visible_bounds_height": round(height + 1.5, 2),
                    "visible_bounds_offset": [0, round(height / 2, 2), 0],
                },
                "bones": bones,
            }],
        }

    def bounds(self):
        lo = [1e9] * 3
        hi = [-1e9] * 3
        for c in self.cubes():
            for i in range(3):
                lo[i] = min(lo[i], c.origin[i])
                hi[i] = max(hi[i], c.origin[i] + c.size[i])
        return lo, hi


def _r(v):
    out = []
    for x in v:
        x = round(float(x), 3)
        out.append(int(x) if x == int(x) else x)
    return out


# --------------------------------------------------------------------------- mask helpers

def mask_ellipse(u, v, face=None):
    return (u - 0.5) ** 2 / 0.25 + (v - 0.5) ** 2 / 0.25 <= 1.0


def mask_round_top(u, v, face=None):
    """Rounded top (ear tips): square bottom half, semicircle top."""
    if v >= 0.5:
        return True
    return (u - 0.5) ** 2 + ((v - 0.5) * 1.0) ** 2 <= 0.25


def mask_tear(u, v, face=None):
    """Teardrop / leaf: point at the top."""
    half = 0.5 * math.sin(math.pi * min(1.0, v * 1.05)) ** 0.8
    return abs(u - 0.5) <= half


def mask_petal(u, v, face=None):
    half = 0.5 * math.sin(math.pi * v) ** 0.6
    notch = v < 0.12 and abs(u - 0.5) < 0.08
    return abs(u - 0.5) <= half and not notch


def mask_triangle(u, v, face=None):
    return abs(u - 0.5) <= 0.5 * v + 0.04

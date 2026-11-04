"""Procedural GeckoLib animations.

Animations are written as functions of time and baked into dense (20-24 fps) keyframes.
Rotation conventions (Bedrock JSON, as GeckoLib reads it):
  rotation X  +  = nose / front goes DOWN (and the tip of a backward-pointing part goes UP;
                   a downward-pointing leg swings its foot BACKWARD)
  rotation Z     an upward part on side s (+1 = +X side) tilts OUTWARD with +s;
                 an outward-pointing part (wing) on side s RAISES with -s
  position       pixels; +Y up, +Z backward
Every loop animation's periods divide its length so loops are seamless; one-shot
animations return every channel to rest by their final frame.
"""
import math

TAU = math.pi * 2


def sn(t, period, phase=0.0):
    return math.sin(TAU * (t / period + phase))


def cs(t, period, phase=0.0):
    return math.cos(TAU * (t / period + phase))


def bump(t, a, b):
    """Smooth 0 -> 1 -> 0 over [a, b]."""
    if t <= a or t >= b:
        return 0.0
    return math.sin(math.pi * (t - a) / (b - a)) ** 2


def ramp(t, a, b):
    """Smooth 0 -> 1 over [a, b]."""
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    x = (t - a) / (b - a)
    return x * x * (3 - 2 * x)


def hold(t, a, b, fade=0.15):
    """0 -> 1 quickly at a, stays 1, back to 0 by b."""
    return ramp(t, a, a + fade) * (1 - ramp(t, b - fade, b))


def pulse(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


class Anim:
    def __init__(self, length, loop=True, step=None):
        self.length = length
        self.loop = loop
        self.step = step
        self.tracks = {}

    def _add(self, bone, ch, fn):
        old = self.tracks.get((bone, ch))
        if old is None:
            self.tracks[(bone, ch)] = fn
        elif ch == "scale":
            self.tracks[(bone, ch)] = lambda t, a=old, b=fn: tuple(x * y for x, y in zip(_v3(a(t), 1), _v3(b(t), 1)))
        else:
            self.tracks[(bone, ch)] = lambda t, a=old, b=fn: tuple(x + y for x, y in zip(_v3(a(t), 0), _v3(b(t), 0)))
        return self

    def rot(self, bone, fn):
        return self._add(bone, "rotation", fn)

    def pos(self, bone, fn):
        return self._add(bone, "position", fn)

    def scl(self, bone, fn):
        return self._add(bone, "scale", fn)

    def to_json(self, bones_present):
        step = self.step or (1 / 20 if self.loop else 1 / 24)
        n = max(4, int(round(self.length / step)))
        out = {}
        for (bone, ch), fn in self.tracks.items():
            if bone not in bones_present:
                raise KeyError(f"animation references missing bone '{bone}'")
            rest = 1 if ch == "scale" else 0
            vals = [_v3(fn(self.length * i / n), rest) for i in range(n + 1)]
            if all(abs(c - rest) < 1e-3 for v in vals for c in v):
                continue
            frames = {}
            for i, v in enumerate(vals):
                t = round(self.length * i / n, 4)
                frames[_num(t)] = [round(c, 2) for c in v]
            out.setdefault(bone, {})[ch] = frames
        data = {"animation_length": round(self.length, 4), "bones": out}
        data["loop"] = True if self.loop else False
        return data


def _v3(v, rest):
    if isinstance(v, (int, float)):
        return (rest, rest, rest) if v is None else (v, v, v) if rest == 1 else (0.0, float(v), 0.0)
    return tuple(float(x) for x in v)


def _num(t):
    s = f"{t:.4f}".rstrip("0").rstrip(".")
    return s if "." in s else s + ".0"


def breathe(a, bone, period, amount=0.025):
    a.scl(bone, lambda t: (1 + amount * 0.5 * sn(t, period), 1 + amount * sn(t, period), 1 + amount * 0.5 * sn(t, period)))


def X(deg):
    return (deg, 0, 0)


def Y(deg):
    return (0, deg, 0)


def Z(deg):
    return (0, 0, deg)


# =========================================================================== BUNNIES

def bunny(sp):
    lop = sp.get("lop", False)
    extra = sp.get("extra", ())
    A = {}

    def ears(a, fn_l, fn_r=None):
        a.rot("ear_l", fn_l)
        a.rot("ear_r", fn_r or (lambda t, f=fn_l: (f(t)[0], -f(t)[1], -f(t)[2])))

    def extras_idle(a, L):
        if "moon" in extra:
            a.pos("moon", lambda t: (0, 0.6 * sn(t, L), 0))
            a.rot("moon", lambda t: (0, 30 * sn(t, L, 0.25), 6 * sn(t, L / 2)))
        if "sprig" in extra:
            a.rot("sprig", lambda t: Z(3 * sn(t, L / 2)))
        if "calyx" in extra:
            a.rot("calyx", lambda t: Y(5 * sn(t, L)))

    # ---- idle: breathing, sniffing, ear twitches
    a = Anim(4.0)
    breathe(a, "body", 2.0, 0.03)
    a.rot("head", lambda t: (2 * sn(t, 4.0) + 1.5 * sn(t, 1 / 5) * (pulse(t, 1.0, 0.25) + pulse(t, 2.8, 0.25)),
                             0, 3 * sn(t, 4.0, 0.3)))
    if lop:
        ears(a, lambda t: (2 * sn(t, 2.0), 0, -4 * pulse(t, 1.7, 0.12) + 1.5 * sn(t, 4.0)))
    else:
        a.rot("ear_l", lambda t: (-3 + 3 * sn(t, 4.0), 0, 14 * pulse(t, 1.6, 0.1)))
        a.rot("ear_r", lambda t: (-3 + 3 * sn(t, 4.0, 0.1), 0, -14 * pulse(t, 3.1, 0.1)))
    a.rot("tail", lambda t: Y(12 * sn(t, 0.25) * pulse(t, 2.2, 0.2)))
    extras_idle(a, 4.0)
    A["idle"] = a

    # ---- walk / run: hop cycle
    for name, T, hop, pitch, feet, paws, ear_back in (("walk", 0.6, 1.6, 8, 28, 30, 8), ("run", 0.4, 2.8, 14, 45, 50, 28)):
        a = Anim(T * (2 if name == "walk" else 3))
        up = lambda t, T=T: max(0.0, sn(t, T))
        a.pos("body", lambda t, T=T, hop=hop: (0, hop * max(0.0, sn(t, T)) ** 0.8, 0))
        a.rot("body", lambda t, T=T, p=pitch: X(-p * sn(t, T, 0.05)))
        a.rot("foot_l", lambda t, T=T, f=feet: X(f * sn(t, T, -0.05)))
        a.rot("foot_r", lambda t, T=T, f=feet: X(f * sn(t, T, -0.05)))
        a.rot("paw_l", lambda t, T=T, p=paws: X(-p * sn(t, T, 0.2)))
        a.rot("paw_r", lambda t, T=T, p=paws: X(-p * sn(t, T, 0.25)))
        a.rot("head", lambda t, T=T, p=pitch: X(p * 0.6 * sn(t, T, 0.1)))
        if lop:
            ears(a, lambda t, T=T: (-10 * sn(t, T, 0.3), 0, -8 * max(0.0, sn(t, T, 0.35))))
        else:
            ears(a, lambda t, T=T, e=ear_back: (-e - 10 * sn(t, T, 0.3), 0, 4 * sn(t, T, 0.3)))
        a.rot("tail", lambda t, T=T: X(10 * sn(t, T, 0.2)))
        extras_idle(a, a.length)
        A[name] = a

    # ---- sit: cosy loaf
    a = Anim(4.0)
    a.pos("body", lambda t: (0, -0.9, 0))
    breathe(a, "body", 2.0, 0.03)
    a.rot("paw_l", lambda t: X(-28))
    a.rot("paw_r", lambda t: X(-28))
    a.pos("paw_l", lambda t: (0, 0.6, 0))
    a.pos("paw_r", lambda t: (0, 0.6, 0))
    a.rot("head", lambda t: (4 + 2 * sn(t, 4.0), 0, 2 * sn(t, 4.0, 0.25)))
    if lop:
        ears(a, lambda t: (2 * sn(t, 2.0), 0, 2))
    else:
        a.rot("ear_l", lambda t: (-14 + 2 * sn(t, 4.0), 0, 8 + 10 * pulse(t, 2.0, 0.1)))
        a.rot("ear_r", lambda t: (-14 + 2 * sn(t, 4.0, 0.2), 0, -8))
    extras_idle(a, 4.0)
    A["sit"] = a

    # ---- sleep: flat loaf, ears folded back, slow breathing
    a = Anim(5.0)
    a.pos("body", lambda t: (0, -1.5, 0))
    a.scl("body", lambda t: (1.04 + 0.015 * sn(t, 2.5), 0.95 + 0.04 * sn(t, 2.5), 1.03))
    a.rot("head", lambda t: (16 + 2 * sn(t, 5.0), 8, 6))
    a.pos("head", lambda t: (0, -0.8, 0.4))
    a.rot("paw_l", lambda t: X(-60))
    a.rot("paw_r", lambda t: X(-60))
    a.pos("paw_l", lambda t: (0, 1.0, 0))
    a.pos("paw_r", lambda t: (0, 1.0, 0))
    if lop:
        ears(a, lambda t: (6, 0, -6))
    else:
        a.rot("ear_l", lambda t: (-62 + 2 * sn(t, 5.0), 0, 12))
        a.rot("ear_r", lambda t: (-62 + 2 * sn(t, 5.0, 0.3), 0, -12))
    if "moon" in extra:
        a.pos("moon", lambda t: (0, -0.8 + 0.4 * sn(t, 5.0), 0))
        a.rot("moon", lambda t: (0, 10 * sn(t, 5.0), 0))
    A["sleep"] = a

    # ---- eat: nibble with the front paws held up
    a = Anim(1.6, loop=False)
    a.rot("head", lambda t: X(18 * hold(t, 0.0, 1.6, 0.25) + 3 * sn(t, 1 / 7) * hold(t, 0.25, 1.35)))
    a.rot("paw_l", lambda t: X(-55 * hold(t, 0.0, 1.6, 0.25)))
    a.rot("paw_r", lambda t: X(-55 * hold(t, 0.0, 1.6, 0.25)))
    a.pos("body", lambda t: (0, -0.4 * hold(t, 0, 1.6, 0.25), 0))
    if not lop:
        ears(a, lambda t: (-10 * hold(t, 0.0, 1.6, 0.3), 0, 0))
    A["eat"] = a

    # ---- happy: a binky (jump + twist) and a little bounce
    a = Anim(1.3, loop=False)
    a.pos("body", lambda t: (0, 4.0 * bump(t, 0.0, 0.62) + 1.4 * bump(t, 0.75, 1.1), 0))
    a.rot("body", lambda t: (0, 35 * math.sin(TAU * t / 0.62) * bump(t, 0.0, 0.62), 12 * math.sin(TAU * t / 0.31) * bump(t, 0.0, 0.62)))
    a.scl("body", lambda t: (1 + 0.08 * pulse(t, 0.66, 0.05), 1 - 0.12 * pulse(t, 0.66, 0.05), 1 + 0.08 * pulse(t, 0.66, 0.05)))
    if lop:
        ears(a, lambda t: (0, 0, -25 * bump(t, 0.05, 0.6)))
    else:
        a.rot("ear_l", lambda t: (-10 * bump(t, 0, 1.2), 0, 22 * math.sin(TAU * t / 0.4) * bump(t, 0.0, 1.1)))
        a.rot("ear_r", lambda t: (-10 * bump(t, 0, 1.2), 0, -22 * math.sin(TAU * t / 0.4) * bump(t, 0.0, 1.1)))
    a.rot("foot_l", lambda t: X(40 * bump(t, 0.05, 0.4)))
    a.rot("foot_r", lambda t: X(40 * bump(t, 0.05, 0.4)))
    A["happy"] = a

    # ---- play: a happy spin with hops
    a = Anim(1.5, loop=False)
    a.rot("body", lambda t: Y(360 * ramp(t, 0.1, 1.2)))
    a.pos("body", lambda t: (0, 1.5 * abs(math.sin(math.pi * ramp(t, 0.1, 1.2) * 3)), 0))
    if not lop:
        ears(a, lambda t: (-20 * bump(t, 0.1, 1.3), 0, 10 * bump(t, 0.1, 1.3)))
    A["play"] = a

    # ---- special: curious sniff
    a = Anim(1.8, loop=False)
    a.rot("head", lambda t: X(-14 * hold(t, 0.0, 1.8, 0.3) + 2.5 * sn(t, 1 / 8) * hold(t, 0.3, 1.5)))
    a.pos("body", lambda t: (0, 0.8 * hold(t, 0.0, 1.8, 0.3), 0))
    a.rot("paw_l", lambda t: X(-20 * hold(t, 0.0, 1.8, 0.3)))
    a.rot("paw_r", lambda t: X(-20 * hold(t, 0.0, 1.8, 0.3)))
    if not lop:
        ears(a, lambda t: (10 * hold(t, 0.0, 1.8, 0.3), 0, 6 * sn(t, 0.6) * hold(t, 0.2, 1.6)))
    A["special"] = a
    return A


# =========================================================================== QUADRUPEDS

LEGS = ("leg_fl", "leg_fr", "leg_bl", "leg_br")


def quad(sp):
    """sp: walk (cycle s), swing (deg), tail ('sway'|'curl'|'stub'), kind (species id), has neck/cheeks/bee..."""
    kind = sp["kind"]
    T = sp.get("walk", 0.8)
    sw = sp.get("swing", 32)
    tall = kind == "moon_deer"
    tiny = kind in ("strawberry_mouse", "dreamy_hamster")
    has_tip = kind in ("cloud_kitty", "strawberry_mouse")
    leg_h = sp.get("leg_h", 4.0)
    A = {}

    def tail_sway(a, L, amp=12, x=0.0):
        a.rot("tail", lambda t: (x, amp * sn(t, L), 0))
        if has_tip:
            a.rot("tail_tip", lambda t: (0, amp * 0.8 * sn(t, L, -0.15), 0))

    def bee(a, L):
        if kind == "honey_bear":
            a.rot("bee_orbit", lambda t: Y(-360 * t / L))
            a.pos("bee", lambda t: (0, 0.8 * sn(t, L / 2), 0))
            a.rot("bee", lambda t: Z(10 * sn(t, L / 4)))

    def ears_flick(a, at_l, at_r, amp=12):
        a.rot("ear_l", lambda t: Z(amp * pulse(t, at_l, 0.08)))
        a.rot("ear_r", lambda t: Z(-amp * pulse(t, at_r, 0.08)))

    # ---- idle
    a = Anim(4.0)
    breathe(a, "body", 2.0, 0.025)
    a.rot("head", lambda t: (2 * sn(t, 4.0), 10 * sn(t, 4.0, 0.1) * (0.4 if tiny else 1.0), 4 * sn(t, 4.0, 0.35)))
    ears_flick(a, 1.3, 2.9)
    tail_sway(a, 2.0, 14 if kind in ("blossom_fox", "cloud_kitty") else 6)
    if kind == "dreamy_hamster":
        for c in ("cheek_l", "cheek_r"):
            a.scl(c, lambda t: 1 + 0.04 * sn(t, 1.0))
    if kind == "moon_deer":
        a.rot("neck", lambda t: X(2 * sn(t, 4.0)))
    bee(a, 4.0)
    A["idle"] = a

    # ---- walk: diagonal gait; run: bounding gallop
    for name, cyc, amp, bob in (("walk", T, sw, 0.35), ("run", T * 0.62, sw * 1.35, 0.9)):
        L = cyc * (2 if name == "walk" else 3)
        a = Anim(L)
        if name == "walk":
            ph = {"leg_fl": 0.0, "leg_br": 0.0, "leg_fr": 0.5, "leg_bl": 0.5}
        else:
            ph = {"leg_fl": 0.0, "leg_fr": 0.08, "leg_bl": 0.5, "leg_br": 0.58}
        for lg in LEGS:
            a.rot(lg, lambda t, p=ph[lg], c=cyc, A_=amp: X(A_ * sn(t, c, p)))
        walking = name == "walk"
        a.pos("body", lambda t, c=cyc, b=bob, w=walking: (0, b * (0.5 + 0.5 * sn(t, c / 2)) if w else b * max(0.0, sn(t, c, 0.25)), 0))
        if name == "run":
            a.rot("body", lambda t, c=cyc: X(6 * sn(t, c, 0.1)))
            a.rot("ear_l", lambda t: (-22, 0, 4))
            a.rot("ear_r", lambda t: (-22, 0, -4))
        a.rot("head", lambda t, c=cyc: X(3 * sn(t, c / 2, 0.2)))
        tail_sway(a, cyc, 10, x=-12 if name == "run" else 0)
        if kind == "moon_deer":
            a.rot("neck", lambda t, c=cyc: X(4 * sn(t, c / 2)))
        if kind == "dreamy_hamster":
            a.rot("paw_l", lambda t, c=cyc: X(20 * sn(t, c)))
            a.rot("paw_r", lambda t, c=cyc: X(20 * sn(t, c, 0.5)))
        bee(a, L)
        A[name] = a

    # ---- sit
    a = Anim(4.0)
    breathe(a, "body", 2.0, 0.025)
    if tall:
        a.pos("body", lambda t: (0, -8.2, 0))
        for lg in LEGS:
            a.scl(lg, lambda t: (1, 0.22, 1))
        a.rot("neck", lambda t: X(-6 + 2 * sn(t, 4.0)))
    elif tiny:
        a.pos("body", lambda t: (0, -0.5, 0))
        a.rot("body", lambda t: X(-10))
        a.rot("head", lambda t: X(8))
        a.rot("leg_fl", lambda t: X(10))
        a.rot("leg_fr", lambda t: X(10))
    elif kind == "honey_bear":
        # bear sits up on its bottom like a teddy
        a.rot("body", lambda t: X(-38))
        a.pos("body", lambda t: (0, -0.6, 1.0))
        a.rot("leg_bl", lambda t: X(-50))
        a.rot("leg_br", lambda t: X(-50))
        a.rot("leg_fl", lambda t: X(-10))
        a.rot("leg_fr", lambda t: X(-10))
        a.rot("head", lambda t: (32 + 2 * sn(t, 4.0), 0, 4 * sn(t, 4.0, 0.3)))
    else:
        a.rot("body", lambda t: X(-20))
        a.pos("body", lambda t: (0, -1.4, 0.6))
        a.rot("leg_fl", lambda t: X(20))
        a.rot("leg_fr", lambda t: X(20))
        a.rot("leg_bl", lambda t: X(-62))
        a.rot("leg_br", lambda t: X(-62))
        a.pos("leg_bl", lambda t: (0, 0.6, 0))
        a.pos("leg_br", lambda t: (0, 0.6, 0))
        a.rot("head", lambda t: (16 + 2 * sn(t, 4.0), 0, 3 * sn(t, 4.0, 0.3)))
    tail_sway(a, 4.0, 6, x=-30 if kind in ("blossom_fox", "cloud_kitty") else 0)
    ears_flick(a, 2.2, 3.4)
    bee(a, 4.0)
    A["sit"] = a

    # ---- sleep: lying down, curled, head resting
    a = Anim(6.0)
    if tall:
        a.pos("body", lambda t: (0, -8.6, 0))
        for lg in LEGS:
            a.scl(lg, lambda t: (1, 0.15, 1))
        a.rot("neck", lambda t: (55 + 2 * sn(t, 6.0), 25, 0))
        a.rot("head", lambda t: X(20))
    else:
        drop = leg_h - (0.4 if tiny else 0.9)
        a.pos("body", lambda t: (0, -drop, 0))
        for lg in LEGS:
            a.scl(lg, lambda t: (1, 0.3, 1))
        a.rot("head", lambda t: (22 + 2 * sn(t, 6.0), 24, 10))
        a.pos("head", lambda t: (0, -0.8, 0))
    a.scl("body", lambda t: (1.02, 0.97 + 0.035 * sn(t, 3.0), 1.0))
    a.rot("ear_l", lambda t: (-20, 0, -10))
    a.rot("ear_r", lambda t: (-20, 0, 10))
    if kind in ("blossom_fox", "cloud_kitty"):
        a.rot("tail", lambda t: (-45, 70 + 3 * sn(t, 6.0), 0))
        if has_tip:
            a.rot("tail_tip", lambda t: (-25, 30, 0))
    elif kind == "strawberry_mouse":
        a.rot("tail", lambda t: (-10, 60, 0))
        a.rot("tail_tip", lambda t: (-30, 50, 0))
    if kind == "honey_bear":
        a.rot("bee_orbit", lambda t: Y(-60 * t / 6.0))
        a.pos("bee", lambda t: (-1.0, -4.0 + 0.3 * sn(t, 3.0), 0))
    A["sleep"] = a

    # ---- eat
    a = Anim(1.8, loop=False)
    e = lambda t: hold(t, 0.0, 1.8, 0.3)
    if tall:
        a.rot("neck", lambda t: X(48 * e(t)))
        a.rot("head", lambda t: X(22 * e(t) + 3 * sn(t, 1 / 6) * hold(t, 0.35, 1.45)))
    else:
        a.rot("head", lambda t: X((32 if not tiny else 18) * e(t) + 3.5 * sn(t, 1 / 6) * hold(t, 0.35, 1.45)))
    if kind == "dreamy_hamster":
        for c in ("cheek_l", "cheek_r"):
            a.scl(c, lambda t: 1 + 0.55 * ramp(t, 0.3, 1.2) * (1 - ramp(t, 1.5, 1.8)))
        a.rot("paw_l", lambda t: X(-50 * e(t)))
        a.rot("paw_r", lambda t: X(-50 * e(t)))
    tail_sway(a, 0.6, 14)
    A["eat"] = a

    # ---- happy (species flavour)
    a = Anim(1.4, loop=False)
    if kind == "honey_bear":
        a.length = 2.0
        up = lambda t: hold(t, 0.0, 2.0, 0.45)
        a.rot("body", lambda t: X(-62 * up(t)))
        a.pos("body", lambda t: (0, 3.2 * up(t), 2.0 * up(t)))
        a.rot("leg_bl", lambda t: X(60 * up(t)))
        a.rot("leg_br", lambda t: X(60 * up(t)))
        a.rot("leg_fl", lambda t: (-70 * up(t), 0, 25 * up(t) + 10 * sn(t, 0.5) * hold(t, 0.5, 1.6)))
        a.rot("leg_fr", lambda t: (-70 * up(t), 0, -25 * up(t) - 10 * sn(t, 0.5) * hold(t, 0.5, 1.6)))
        a.rot("head", lambda t: (52 * up(t), 0, 8 * sn(t, 1.0) * hold(t, 0.4, 1.6)))
    elif kind == "cloud_kitty":
        b = lambda t: hold(t, 0.0, 1.4, 0.3)
        a.rot("body", lambda t: X(14 * b(t)))
        a.rot("leg_fl", lambda t: X(-45 * b(t)))
        a.rot("leg_fr", lambda t: X(-45 * b(t)))
        a.rot("head", lambda t: (-18 * b(t), 0, 10 * sn(t, 0.7) * b(t)))
        a.rot("tail", lambda t: (25 * b(t), 15 * sn(t, 0.35) * b(t), 0))
        a.rot("tail_tip", lambda t: (20 * b(t), 0, 0))
    elif kind == "moon_deer":
        a.pos("body", lambda t: (0, 3.5 * bump(t, 0.05, 0.6) + 2.5 * bump(t, 0.7, 1.2), 0))
        for lg in LEGS:
            a.rot(lg, lambda t, s=(1 if lg in ("leg_fl", "leg_fr") else -1): X(-s * 35 * (bump(t, 0.05, 0.6) + bump(t, 0.7, 1.2))))
        a.rot("neck", lambda t: X(-10 * hold(t, 0, 1.4)))
        ears_flick(a, 0.4, 0.9, 20)
    elif kind == "dreamy_hamster":
        for c in ("cheek_l", "cheek_r"):
            a.scl(c, lambda t: 1 + 0.5 * bump(t, 0.0, 1.4))
        a.pos("body", lambda t: (0, 1.2 * abs(math.sin(math.pi * t / 0.35)) * hold(t, 0, 1.4), 0))
        a.rot("body", lambda t: Z(8 * sn(t, 0.7) * hold(t, 0, 1.4)))
        a.rot("paw_l", lambda t: X(-60 * hold(t, 0, 1.4)))
        a.rot("paw_r", lambda t: X(-60 * hold(t, 0, 1.4)))
    elif kind == "strawberry_mouse":
        a.pos("body", lambda t: (0, 1.6 * bump(t, 0.0, 0.45) + 1.6 * bump(t, 0.55, 1.0), 0))
        a.rot("body", lambda t: Y(20 * sn(t, 0.5) * hold(t, 0, 1.2)))
        ears_flick(a, 0.3, 0.75, 25)
        tail_sway(a, 0.35, 25)
    else:  # blossom fox: a spinning hop
        a.rot("body", lambda t: Y(360 * ramp(t, 0.05, 0.85)))
        a.pos("body", lambda t: (0, 3.0 * bump(t, 0.05, 0.85), 0))
        for lg in LEGS:
            a.rot(lg, lambda t, s=(1 if lg in ("leg_fl", "leg_fr") else -1): X(-s * 30 * bump(t, 0.05, 0.85)))
        a.rot("tail", lambda t: (20 * bump(t, 0.0, 1.2), 25 * sn(t, 0.3) * bump(t, 0.0, 1.3), 0))
    A["happy"] = a

    # ---- play
    a = Anim(1.6, loop=False)
    if kind in ("blossom_fox", "cloud_kitty"):
        crouch = lambda t: hold(t, 0.0, 0.75, 0.2)
        leap = lambda t: bump(t, 0.7, 1.35)
        a.pos("body", lambda t: (0, -1.2 * crouch(t) + 3.2 * leap(t), -3.0 * leap(t)))
        a.rot("body", lambda t: (8 * crouch(t) - 10 * math.sin(math.pi * ramp(t, 0.7, 1.35)), 6 * sn(t, 0.25) * crouch(t), 0))
        a.rot("leg_fl", lambda t: X(-40 * leap(t)))
        a.rot("leg_fr", lambda t: X(-40 * leap(t)))
        a.rot("leg_bl", lambda t: X(40 * leap(t) - 30 * crouch(t)))
        a.rot("leg_br", lambda t: X(40 * leap(t) - 30 * crouch(t)))
        a.rot("tail", lambda t: (10, 30 * sn(t, 0.2) * crouch(t), 0))
    elif kind == "honey_bear":
        a.rot("body", lambda t: Z(360 * ramp(t, 0.15, 1.3)))
        a.pos("body", lambda t: (0, 2.5 * bump(t, 0.15, 1.3), 0))
    elif kind == "dreamy_hamster":
        a.rot("body", lambda t: X(360 * ramp(t, 0.1, 1.2)))
        a.pos("body", lambda t: (0, 2.5 * bump(t, 0.1, 1.2), 0))
    elif kind == "moon_deer":
        a.pos("body", lambda t: (0, 5.0 * bump(t, 0.1, 1.0), -4.0 * bump(t, 0.1, 1.0)))
        a.rot("body", lambda t: X(-12 * math.sin(TAU * ramp(t, 0.1, 1.0))))
        for lg in LEGS:
            a.rot(lg, lambda t, s=(1 if lg in ("leg_fl", "leg_fr") else -1): X(-s * 45 * bump(t, 0.1, 1.0)))
    else:
        a.rot("body", lambda t: Y(720 * ramp(t, 0.05, 1.4)))
        a.pos("body", lambda t: (0, 0.8 * abs(math.sin(TAU * t / 0.4)) * hold(t, 0, 1.5), 0))
    A["play"] = a

    # ---- special
    a = Anim(2.0, loop=False)
    s = lambda t: hold(t, 0.0, 2.0, 0.35)
    if kind == "cloud_kitty":  # grooming: lick a paw
        a.rot("leg_fl", lambda t: X(-95 * s(t)))
        a.pos("leg_fl", lambda t: (0, 1.0 * s(t), -0.5 * s(t)))
        a.rot("head", lambda t: (22 * s(t) + 6 * sn(t, 0.25) * hold(t, 0.4, 1.6), -18 * s(t), 0))
        a.rot("body", lambda t: X(-12 * s(t)))
    elif kind == "strawberry_mouse":  # face wash
        a.rot("body", lambda t: X(-40 * s(t)))
        a.pos("body", lambda t: (0, 0.8 * s(t), 0.8 * s(t)))
        a.rot("leg_fl", lambda t: X(-110 * s(t) + 12 * sn(t, 0.2) * hold(t, 0.4, 1.6)))
        a.rot("leg_fr", lambda t: X(-110 * s(t) + 12 * sn(t, 0.2, 0.5) * hold(t, 0.4, 1.6)))
        a.rot("head", lambda t: (30 * s(t) + 5 * sn(t, 0.4) * hold(t, 0.4, 1.6), 0, 0))
    elif kind == "dreamy_hamster":  # stuff cheeks
        for c in ("cheek_l", "cheek_r"):
            a.scl(c, lambda t: 1 + 0.7 * ramp(t, 0.2, 1.0) * (1 - ramp(t, 1.6, 2.0)))
        a.rot("paw_l", lambda t: X(-60 * s(t) + 15 * sn(t, 0.2) * hold(t, 0.4, 1.5)))
        a.rot("paw_r", lambda t: X(-60 * s(t) + 15 * sn(t, 0.2, 0.5) * hold(t, 0.4, 1.5)))
    elif kind == "honey_bear":  # sniffs the air for honey
        a.rot("head", lambda t: (-24 * s(t) + 3 * sn(t, 0.15) * hold(t, 0.4, 1.6), 15 * sn(t, 1.0) * s(t), 0))
    elif kind == "moon_deer":  # shakes its antlers
        a.rot("head", lambda t: Z(14 * sn(t, 0.3) * hold(t, 0.3, 1.6)))
        ears_flick(a, 0.5, 1.1, 25)
    else:  # fox: listens, tilting its head
        a.rot("head", lambda t: (-6 * s(t), 0, 22 * s(t) * (1 if t < 1.0 else -1) * hold(t, 0, 2.0, 0.3)))
        ears_flick(a, 0.5, 1.4, 18)
    A["special"] = a
    return A


# =========================================================================== AXOLOTL

def axolotl(sp):
    A = {}

    def gills(a, L, amp=8, spread=0.0):
        a.rot("gills_l", lambda t: (0, 0, -(spread + amp * sn(t, L))))
        a.rot("gills_r", lambda t: (0, 0, spread + amp * sn(t, L)))
        a.rot("gills_t", lambda t: X(-amp * 0.6 * sn(t, L, 0.25)))

    a = Anim(3.0)
    breathe(a, "body", 1.5, 0.02)
    gills(a, 1.5, 7)
    a.rot("tail", lambda t: Y(8 * sn(t, 3.0)))
    a.rot("head", lambda t: (0, 4 * sn(t, 3.0, 0.2), 0))
    A["idle"] = a

    for name, T, amp in (("walk", 0.9, 35), ("run", 0.55, 45)):
        a = Anim(T * 2)
        for lg, p in (("leg_fl", 0.0), ("leg_br", 0.0), ("leg_fr", 0.5), ("leg_bl", 0.5)):
            a.rot(lg, lambda t, p=p, T=T, A_=amp: (A_ * sn(t, T, p), 0, 0))
        a.rot("body", lambda t, T=T: Y(10 * sn(t, T)))
        a.rot("head", lambda t, T=T: Y(-8 * sn(t, T)))
        a.rot("tail", lambda t, T=T: Y(-22 * sn(t, T, 0.1)))
        gills(a, T, 5)
        A[name] = a

    a = Anim(1.2)
    for lg in LEGS:
        a.rot(lg, lambda t: X(75))
    a.rot("body", lambda t: Y(9 * sn(t, 1.2)))
    a.rot("head", lambda t: Y(-7 * sn(t, 1.2, 0.05)))
    a.rot("tail", lambda t: Y(-30 * sn(t, 1.2, 0.18)))
    gills(a, 0.6, 4, spread=-12)
    A["swim"] = a

    a = Anim(3.0)
    a.pos("body", lambda t: (0, -0.5, 0))
    breathe(a, "body", 1.5, 0.02)
    gills(a, 1.5, 6)
    a.rot("tail", lambda t: Y(20 + 4 * sn(t, 3.0)))
    A["sit"] = a

    a = Anim(5.0)
    a.pos("body", lambda t: (0, -0.7, 0))
    a.scl("body", lambda t: (1.02, 0.96 + 0.03 * sn(t, 2.5), 1.0))
    gills(a, 5.0, 2, spread=-25)
    a.rot("tail", lambda t: Y(55))
    a.rot("head", lambda t: (6, -12, 0))
    A["sleep"] = a

    a = Anim(1.4, loop=False)
    lunge = lambda t: bump(t, 0.1, 0.7)
    a.pos("head", lambda t: (0, 0, -1.6 * lunge(t)))
    a.rot("head", lambda t: X(12 * lunge(t)))
    gills(a, 0.35, 6)
    a.scl("head", lambda t: 1 + 0.06 * pulse(t, 0.7, 0.08))
    A["eat"] = a

    a = Anim(1.4, loop=False)
    w = lambda t: hold(t, 0.0, 1.4, 0.2)
    a.rot("body", lambda t: Z(16 * sn(t, 0.25) * w(t)))
    a.rot("tail", lambda t: Y(30 * sn(t, 0.25, 0.2) * w(t)))
    a.rot("gills_l", lambda t: Z(-(18 + 10 * sn(t, 0.2)) * w(t)))
    a.rot("gills_r", lambda t: Z((18 + 10 * sn(t, 0.2)) * w(t)))
    A["happy"] = a

    a = Anim(1.5, loop=False)
    a.rot("body", lambda t: Z(360 * ramp(t, 0.15, 1.2)))
    a.pos("body", lambda t: (0, 2.0 * bump(t, 0.15, 1.2), 0))
    A["play"] = a

    a = Anim(1.6, loop=False)
    f = lambda t: hold(t, 0.0, 1.6, 0.25)
    a.rot("gills_l", lambda t: Z(-34 * f(t)))
    a.rot("gills_r", lambda t: Z(34 * f(t)))
    a.rot("gills_t", lambda t: X(-30 * f(t)))
    a.rot("head", lambda t: X(-10 * f(t)))
    A["special"] = a
    return A


# =========================================================================== SWAN

def swan(sp):
    A = {}

    def wings(a, fn_l):
        a.rot("wing_l", fn_l)
        a.rot("wing_r", lambda t, f=fn_l: (f(t)[0], -f(t)[1], -f(t)[2]))

    a = Anim(4.0)
    breathe(a, "body", 2.0, 0.02)
    a.rot("neck_low", lambda t: X(3 * sn(t, 4.0)))
    a.rot("neck_up", lambda t: X(-4 * sn(t, 4.0, 0.1)))
    a.rot("head", lambda t: (2 * sn(t, 2.0), 6 * sn(t, 4.0, 0.3), 0))
    a.rot("tail", lambda t: Y(14 * sn(t, 0.2) * pulse(t, 2.5, 0.25)))
    A["idle"] = a

    for name, T, amp in (("walk", 0.7, 28), ("run", 0.45, 38)):
        a = Anim(T * 2)
        a.rot("body", lambda t, T=T: (0, 4 * sn(t, T), 7 * sn(t, T)))
        a.rot("foot_l", lambda t, T=T, A_=amp: X(A_ * sn(t, T)))
        a.rot("foot_r", lambda t, T=T, A_=amp: X(A_ * sn(t, T, 0.5)))
        a.rot("neck_low", lambda t, T=T: X(6 * sn(t, T / 2)))
        a.rot("neck_up", lambda t, T=T: X(-5 * sn(t, T / 2, 0.1)))
        if name == "run":
            wings(a, lambda t, T=T: (0, 0, -(18 + 12 * sn(t, T / 2))))
        A[name] = a

    a = Anim(3.0)
    a.pos("body", lambda t: (0, 0.3 * sn(t, 3.0), 0))
    a.rot("body", lambda t: Z(1.5 * sn(t, 3.0, 0.2)))
    a.rot("foot_l", lambda t: X(30 * sn(t, 1.0)))
    a.rot("foot_r", lambda t: X(30 * sn(t, 1.0, 0.5)))
    a.rot("neck_low", lambda t: X(4 * sn(t, 3.0)))
    a.rot("neck_up", lambda t: X(-5 * sn(t, 3.0, 0.15)))
    a.rot("tail", lambda t: Y(6 * sn(t, 1.5)))
    A["swim"] = a

    a = Anim(4.0)
    a.pos("body", lambda t: (0, -1.3, 0))
    breathe(a, "body", 2.0, 0.02)
    a.rot("neck_low", lambda t: X(-6 + 2 * sn(t, 4.0)))
    a.rot("neck_up", lambda t: X(6 - 2 * sn(t, 4.0, 0.1)))
    A["sit"] = a

    a = Anim(5.0)
    a.pos("body", lambda t: (0, -1.3, 0))
    a.scl("body", lambda t: (1.02, 0.97 + 0.03 * sn(t, 2.5), 1.0))
    a.rot("neck_low", lambda t: X(-42))
    a.rot("neck_up", lambda t: (-95, 0, 0))
    a.rot("head", lambda t: (40 + 2 * sn(t, 5.0), 0, 0))
    A["sleep"] = a

    a = Anim(1.8, loop=False)
    d = lambda t: hold(t, 0.0, 1.8, 0.3)
    a.rot("neck_low", lambda t: X(45 * d(t)))
    a.rot("neck_up", lambda t: X(40 * d(t)))
    a.rot("head", lambda t: X(15 * d(t) + 6 * sn(t, 0.2) * hold(t, 0.4, 1.4)))
    A["eat"] = a

    a = Anim(1.8, loop=False)
    h = lambda t: hold(t, 0.0, 1.8, 0.35)
    wings(a, lambda t: (-15 * h(t), 0, -(75 * h(t) + 6 * sn(t, 0.3) * hold(t, 0.4, 1.4))))
    a.rot("neck_low", lambda t: X(-10 * h(t)))
    a.rot("tail", lambda t: X(20 * h(t)))
    A["happy"] = a

    a = Anim(1.4, loop=False)
    wings(a, lambda t: (0, 0, -(40 + 40 * sn(t, 0.2)) * hold(t, 0.0, 1.4, 0.2)))
    a.pos("body", lambda t: (0, 0.8 * bump(t, 0.1, 1.2), 0))
    A["play"] = a

    a = Anim(2.2, loop=False)
    p = lambda t: hold(t, 0.0, 2.2, 0.4)
    a.rot("neck_low", lambda t: (-10 * p(t), 30 * p(t), 0))
    a.rot("neck_up", lambda t: (-40 * p(t), 90 * p(t), 0))
    a.rot("head", lambda t: (30 * p(t) + 6 * sn(t, 0.25) * hold(t, 0.5, 1.7), 0, 0))
    wings(a, lambda t: (0, 0, -12 * p(t)))
    A["special"] = a
    return A


# =========================================================================== BIRD

def bird(sp):
    A = {}

    def wings(a, fn_l):
        a.rot("wing_l", fn_l)
        a.rot("wing_r", lambda t, f=fn_l: (f(t)[0], -f(t)[1], -f(t)[2]))

    a = Anim(3.0)
    breathe(a, "body", 1.5, 0.03)
    a.rot("head", lambda t: (0, 18 * (pulse(t, 0.8, 0.12) - pulse(t, 2.1, 0.12)), 14 * (pulse(t, 1.4, 0.15) - pulse(t, 2.6, 0.12))))
    a.rot("tail", lambda t: X(8 * pulse(t, 1.0, 0.1) + 8 * pulse(t, 2.3, 0.1)))
    a.rot("crest", lambda t: X(-4 * sn(t, 1.5)))
    A["idle"] = a

    for name, T, hop in (("walk", 0.4, 1.0), ("run", 0.28, 1.4)):
        a = Anim(T * 3)
        a.pos("body", lambda t, T=T, h=hop: (0, h * abs(math.sin(math.pi * t / T)), 0))
        a.rot("body", lambda t, T=T: X(4 * sn(t, T)))
        a.rot("tail", lambda t, T=T: X(-10 * sn(t, T, 0.2)))
        a.rot("foot_l", lambda t, T=T: X(-20 * sn(t, T)))
        a.rot("foot_r", lambda t, T=T: X(-20 * sn(t, T)))
        A[name] = a

    a = Anim(0.6)
    wings(a, lambda t: (0, 0, -(25 + 55 * sn(t, 0.2))))
    a.rot("body", lambda t: X(12 + 3 * sn(t, 0.6)))
    a.pos("body", lambda t: (0, 0.6 * sn(t, 0.6), 0))
    a.rot("head", lambda t: X(-10))
    a.rot("foot_l", lambda t: X(70))
    a.rot("foot_r", lambda t: X(70))
    a.rot("tail", lambda t: X(-8 + 4 * sn(t, 0.2)))
    A["fly"] = a

    a = Anim(4.0)
    a.pos("body", lambda t: (0, -0.6, 0))
    a.scl("body", lambda t: (1.08 + 0.02 * sn(t, 2.0), 1.06 + 0.03 * sn(t, 2.0), 1.06))
    a.rot("head", lambda t: (6, 10 * sn(t, 4.0), 0))
    A["sit"] = a

    a = Anim(5.0)
    a.pos("body", lambda t: (0, -0.7, 0))
    a.scl("body", lambda t: (1.12, 1.08 + 0.03 * sn(t, 2.5), 1.1))
    a.pos("head", lambda t: (0, -1.1, 0.8))
    a.rot("head", lambda t: (24, 30, 0))
    a.rot("crest", lambda t: X(-12))
    A["sleep"] = a

    a = Anim(1.4, loop=False)
    a.rot("head", lambda t: X(38 * (bump(t, 0.1, 0.35) + bump(t, 0.5, 0.75) + bump(t, 0.9, 1.15))))
    a.rot("body", lambda t: X(10 * hold(t, 0.0, 1.4, 0.2)))
    A["eat"] = a

    a = Anim(1.4, loop=False)
    a.pos("body", lambda t: (0, 1.8 * bump(t, 0.0, 0.45) + 1.8 * bump(t, 0.6, 1.05), 0))
    wings(a, lambda t: (0, 0, -(30 + 30 * sn(t, 0.15)) * hold(t, 0.0, 1.2, 0.15)))
    a.rot("tail", lambda t: X(15 * hold(t, 0, 1.3)))
    A["happy"] = a

    a = Anim(1.4, loop=False)
    a.rot("body", lambda t: Y(360 * ramp(t, 0.1, 1.1)))
    wings(a, lambda t: (0, 0, -60 * bump(t, 0.05, 1.2)))
    a.pos("body", lambda t: (0, 1.5 * bump(t, 0.1, 1.1), 0))
    A["play"] = a

    a = Anim(2.4, loop=False)
    s = lambda t: hold(t, 0.0, 2.4, 0.3)
    a.rot("head", lambda t: (-22 * s(t) + 5 * sn(t, 0.3) * hold(t, 0.3, 2.1), 0, 10 * sn(t, 0.6) * hold(t, 0.3, 2.1)))
    a.pos("body", lambda t: (0, 0.5 * abs(math.sin(TAU * t / 0.6)) * s(t), 0))
    a.rot("tail", lambda t: X(10 * sn(t, 0.3) * s(t)))
    a.rot("crest", lambda t: X(-15 * s(t)))
    A["special"] = a

    a = Anim(1.0)
    a.rot("body", lambda t: Z(14 * sn(t, 1.0)))
    a.pos("body", lambda t: (0, 0.8 * abs(sn(t, 1.0)), 0))
    a.rot("head", lambda t: (14 * abs(sn(t, 0.5)) - 6, 0, -10 * sn(t, 1.0)))
    wings(a, lambda t: (0, 0, -(15 + 15 * sn(t, 0.5))))
    a.rot("tail", lambda t: Y(20 * sn(t, 1.0)))
    A["dance"] = a
    return A


# =========================================================================== BUTTERFLY

def butterfly(sp):
    A = {}

    def wings(a, fn_up, lag=0.04, low=0.8):
        a.rot("wing_l", lambda t: Z(-fn_up(t)))
        a.rot("wing_r", lambda t: Z(fn_up(t)))
        a.rot("wing_l2", lambda t: Z(-fn_up(t - lag) * low))
        a.rot("wing_r2", lambda t: Z(fn_up(t - lag) * low))

    def antennae(a, L, amp=6):
        a.rot("antenna_l", lambda t: (amp * sn(t, L), 0, 3 * sn(t, L, 0.3)))
        a.rot("antenna_r", lambda t: (amp * sn(t, L, 0.1), 0, -3 * sn(t, L, 0.3)))

    a = Anim(3.0)
    wings(a, lambda t: 50 + 32 * sn(t, 3.0), lag=0.15, low=0.9)
    antennae(a, 3.0)
    A["idle"] = a

    for name, T in (("fly", 0.3), ("walk", 0.3), ("run", 0.2)):
        a = Anim(T * 4)
        wings(a, lambda t, T=T: 12 + 62 * sn(t, T))
        a.pos("body", lambda t, T=T: (0, 0.7 * sn(t, T * 2), 0))
        a.rot("body", lambda t, T=T: X(-5 * sn(t, T * 2, 0.25)))
        antennae(a, T * 2, 10)
        A[name] = a

    a = Anim(4.0)
    wings(a, lambda t: 84 + 4 * sn(t, 4.0), lag=0.2, low=1.0)
    antennae(a, 4.0, 3)
    A["sit"] = a

    a = Anim(5.0)
    wings(a, lambda t: 88, lag=0.0, low=1.0)
    a.rot("antenna_l", lambda t: X(25))
    a.rot("antenna_r", lambda t: X(25))
    a.scl("body", lambda t: (1, 1 + 0.02 * sn(t, 2.5), 1))
    A["sleep"] = a

    a = Anim(1.6, loop=False)
    a.rot("head", lambda t: X(24 * hold(t, 0.0, 1.6, 0.3)))
    wings(a, lambda t: 60 + 20 * sn(max(t, 0.0), 0.8))
    A["eat"] = a

    a = Anim(1.4, loop=False)
    wings(a, lambda t: 10 + 70 * sn(t, 0.14) * hold(t, 0.0, 1.4, 0.1))
    a.rot("body", lambda t: X(-360 * ramp(t, 0.2, 1.1)))
    a.pos("body", lambda t: (0, 3.0 * bump(t, 0.1, 1.2), 0))
    A["happy"] = a

    a = Anim(1.6, loop=False)
    wings(a, lambda t: 12 + 60 * sn(t, 0.2) * hold(t, 0.0, 1.6, 0.1))
    a.rot("body", lambda t: (0, 360 * ramp(t, 0.1, 1.4), 18 * bump(t, 0.1, 1.4)))
    a.pos("body", lambda t: (0, 2.0 * bump(t, 0.1, 1.4), 0))
    A["play"] = a

    a = Anim(2.4, loop=False)
    sh = lambda t: hold(t, 0.0, 2.4, 0.4)
    wings(a, lambda t: 50 * (1 - sh(t)) + (-4 + 3 * sn(t, 0.8)) * sh(t), lag=0.05, low=1.0)
    a.rot("body", lambda t: Z(10 * sn(t, 1.2) * sh(t)))
    antennae(a, 0.6, 8)
    A["special"] = a
    return A


RIGS = {"bunny": bunny, "quad": quad, "axolotl": axolotl, "swan": swan, "bird": bird, "butterfly": butterfly}


def build(rig, params, bones_present, species):
    anims = RIGS[rig](params)
    return {
        "format_version": "1.8.0",
        "animations": {name: a.to_json(bones_present) for name, a in anims.items()},
    }

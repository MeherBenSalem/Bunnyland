#!/usr/bin/env python3
"""Procedurally synthesise every Bunnyland sound effect and write sounds.json.

All sounds are ORIGINAL: they are built from oscillators, filters and noise in pure Python
(standard library only -- no samples, no downloads). Each variant is rendered to a temporary
16-bit WAV (in the system temp dir) and encoded to mono Ogg Vorbis with ffmpeg/libvorbis.
Every event/variant gets its own RNG seed and the encoder/muxer run in bitexact mode, so reruns
produce byte-identical files.

Usage (paths are resolved from this file, so any working directory works):
    python tools/generate_sounds.py

Inputs : tools/assetgen/sound_events.py   SOUND_EVENTS: event -> (subtitle, variants, brief)
Outputs: src/main/resources/assets/bunnyland/sounds/**.ogg   (folder wiped + regenerated)
         src/main/resources/assets/bunnyland/sounds.json

Art direction: adorable / fairytale -- everything soft, sweet and pleasant, never harsh.
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from array import array
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# --------------------------------------------------------------------------------- settings

SR = 44100
TAU = 2.0 * math.pi
NYQ_SAFE = 0.45 * SR
NAMESPACE = "bunnyland"

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent
ASSETS = ROOT / "src" / "main" / "resources" / "assets" / NAMESPACE
SOUNDS_DIR = ASSETS / "sounds"
SOUNDS_JSON = ASSETS / "sounds.json"
EVENTS_FILE = TOOLS_DIR / "assetgen" / "sound_events.py"

PEAK_DB = -3.0          # normal peak level
QUIET_PEAK_DB = -9.0    # butterflies and snores are meant to be barely-there
QUIET_EVENTS = ("entity.rainbow_butterfly.", "entity.pet.snore")
# Pure-tone squeaks at 2-4 kHz (where hearing is most sensitive) sound much louder than noisy
# sounds at the same peak. Anything whose approximate K-weighted loudness exceeds this ceiling
# is turned down -- by at most MAX_CEILING_CUT_DB, so its peak stays within ~-6.5 dBFS.
LOUDNESS_CEILING_DB = -8.0
MAX_CEILING_CUT_DB = 3.5

# (min, max) duration in seconds by the last part of the event path
DURATION_LIMITS = {
    "ambient": (0.15, 0.9), "hurt": (0.15, 0.9), "death": (0.15, 1.2),
    "purr": (0.15, 1.8), "sing": (0.15, 1.8), "snore": (0.15, 1.8),
}
DEFAULT_LIMITS = (0.15, 1.2)


def load_events():
    """Load SOUND_EVENTS straight from its file (no package import side effects)."""
    spec = importlib.util.spec_from_file_location("bunnyland_sound_events", EVENTS_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SOUND_EVENTS


# ================================================================================ toolkit
# Signals are plain Python lists of floats at SR. Times are in seconds.

def ns(sec):
    """Seconds -> sample count (at least 1)."""
    return max(1, int(round(sec * SR)))


def _curve(value, n):
    """Scalar -> constant list, (a, b) tuple -> linear ramp, list -> itself."""
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return ramp([(0.0, value[0]), (n / SR, value[1])], n, smooth=False)
    return [float(value)] * n


def ramp(points, n, log=False, smooth=True):
    """Sample a piecewise curve through (time, value) points n times.

    Values are held flat before the first and after the last point. log=True interpolates
    geometrically (right for frequencies); smooth=True eases every segment (smoothstep).
    Points must be in non-decreasing time order.
    """
    if len(points) == 1:
        return [float(points[0][1])] * n
    ts = [p[0] * SR for p in points]
    vs = [math.log(p[1]) if log else float(p[1]) for p in points]
    out = [0.0] * n
    exp = math.exp
    j, last = 0, len(points) - 2
    for i in range(n):
        while j < last and i >= ts[j + 1]:
            j += 1
        t0, t1 = ts[j], ts[j + 1]
        if i <= t0:
            u = 0.0
        elif i >= t1:
            u = 1.0
        else:
            u = (i - t0) / (t1 - t0)
            if smooth:
                u = u * u * (3.0 - 2.0 * u)
        v = vs[j] + (vs[j + 1] - vs[j]) * u
        out[i] = exp(v) if log else v
    return out


def white(n, rng):
    r = rng.random
    return [2.0 * r() - 1.0 for _ in range(n)]


def smooth_rand(n, rng, rate):
    """Smooth random curve in [-1, 1]: cosine-interpolated random points, `rate` per second."""
    step = max(1, int(SR / rate))
    pts = [rng.uniform(-1.0, 1.0) for _ in range(n // step + 2)]
    cos, pi = math.cos, math.pi
    out = [0.0] * n
    for i in range(n):
        k, r = divmod(i, step)
        u = 0.5 - 0.5 * cos(pi * r / step)
        out[i] = pts[k] + (pts[k + 1] - pts[k]) * u
    return out


def osc(freq, n=None, shape="sine", phase=0.0):
    """Phase-accumulating oscillator. freq: Hz (scalar + n, or per-sample list).
    'saw' is PolyBLEP band-limited; 'tri' starts at zero like 'sine'."""
    f = freq if isinstance(freq, list) else [float(freq)] * n
    n = len(f)
    out = [0.0] * n
    inv = 1.0 / SR
    p = phase % 1.0
    if shape == "sine":
        sin = math.sin
        for i in range(n):
            out[i] = sin(TAU * p)
            p += f[i] * inv
            if p >= 1.0:
                p -= 1.0
    elif shape == "tri":
        for i in range(n):
            q = p + 0.25
            if q >= 1.0:
                q -= 1.0
            out[i] = 1.0 - 4.0 * abs(q - 0.5)
            p += f[i] * inv
            if p >= 1.0:
                p -= 1.0
    elif shape == "saw":
        for i in range(n):
            dt = f[i] * inv
            v = 2.0 * p - 1.0
            if p < dt:
                x = p / dt
                v -= x + x - x * x - 1.0
            elif p > 1.0 - dt:
                x = (p - 1.0) / dt
                v -= x * x + x + x + 1.0
            out[i] = v
            p += dt
            if p >= 1.0:
                p -= 1.0
    else:
        raise ValueError(shape)
    return out


def tone(freq, amp, harmonics=(1.0,)):
    """Additive tone: sum of integer harmonics (gains in `harmonics`), times amp.
    Harmonics above ~0.45*SR are skipped so nothing aliases."""
    n = len(amp)
    f = freq if isinstance(freq, list) else [float(freq)] * n
    hs = [(h + 1, g) for h, g in enumerate(harmonics) if g]
    out = [0.0] * n
    sin = math.sin
    inv = 1.0 / SR
    p = 0.0
    for i in range(n):
        fi = f[i]
        th = TAU * p
        s = 0.0
        for h, g in hs:
            if h * fi < NYQ_SAFE:
                s += g * sin(h * th)
        out[i] = s * amp[i]
        p += fi * inv
        if p >= 1.0:
            p -= 1.0
    return out


def lfo(n, rate, rng=None, phase=None):
    """Sine LFO in [-1, 1]; rate may be a per-sample list. Random start phase if rng given."""
    r = _curve(rate, n)
    p = phase if phase is not None else (rng.random() if rng else 0.0)
    sin = math.sin
    out = [0.0] * n
    inv = 1.0 / SR
    for i in range(n):
        out[i] = sin(TAU * p)
        p += r[i] * inv
        if p >= 1.0:
            p -= 1.0
    return out


def bend(freq, mod, depth_semi):
    """freq * 2**(depth * mod / 12) per sample (depth scalar / tuple / list)."""
    d = _curve(depth_semi, len(freq))
    c = math.log(2.0) / 12.0
    exp = math.exp
    return [f * exp(c * dd * m) for f, m, dd in zip(freq, mod, d)]


def vibrato(freq, rate, depth_semi, rng, onset=0.0):
    """Sine vibrato (depth in semitones) that fades in over `onset` seconds."""
    n = len(freq)
    m = lfo(n, rate, rng)
    if onset > 0.0:
        depth = ramp([(0.0, 0.0), (onset, depth_semi)], n)
    else:
        depth = depth_semi
    return bend(freq, m, depth)


def svf(x, fc, q=0.707, mode="bp"):
    """Zero-delay-feedback state-variable filter (A. Simper's trapezoidal SVF).

    fc: Hz, scalar or per-sample list (stable under fast modulation). mode: 'lp', 'hp' or
    'bp' (band-pass normalised to unity gain at the centre, i.e. a constant-peak biquad BP).
    """
    n = len(x)
    out = [0.0] * n
    k = 1.0 / q
    w = math.pi / SR
    tan = math.tan
    varying = isinstance(fc, list)
    if not varying:
        g = tan(w * min(fc, NYQ_SAFE))
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
    m = {"lp": 0, "bp": 1, "hp": 2}[mode]
    ic1 = ic2 = 0.0
    for i in range(n):
        if varying:
            g = tan(w * min(fc[i], NYQ_SAFE))
            a1 = 1.0 / (1.0 + g * (g + k))
            a2 = g * a1
            a3 = g * a2
        v0 = x[i]
        v3 = v0 - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if m == 1:
            out[i] = k * v1
        elif m == 0:
            out[i] = v2
        else:
            out[i] = v0 - k * v1 - v2
    return out


def dc_block(x, fc=25.0):
    """First-order DC / rumble blocker."""
    r = math.exp(-TAU * fc / SR)
    y = xp = 0.0
    out = [0.0] * len(x)
    for i, v in enumerate(x):
        y = v - xp + r * y
        xp = v
        out[i] = y
    return out


def env_perc(n, attack, tau, end=0.15):
    """Percussive envelope: smooth rise over `attack`, exponential decay (time constant tau),
    then a raised-cosine taper over the last `end` fraction so it always lands on zero."""
    out = [0.0] * n
    na = min(n, max(1, int(attack * SR)))
    for i in range(na):
        s = math.sin(0.5 * math.pi * i / na)
        out[i] = s * s
    k = math.exp(-1.0 / (tau * SR))
    e = 1.0
    for i in range(na, n):
        out[i] = e
        e *= k
    return taper(out, end)


def taper(x, frac=0.2):
    """Raised-cosine fade over the last `frac` of x (in place)."""
    n = len(x)
    m = max(1, int(n * frac))
    for i in range(m):
        x[n - 1 - i] *= 0.5 - 0.5 * math.cos(math.pi * i / m)
    return x


def mul(a, b):
    return [x * y for x, y in zip(a, b)]


def scaled(a, g):
    return [x * g for x in a]


def addsig(a, b, gb=1.0):
    """a + gb*b, padding the shorter with zeros."""
    if len(b) > len(a):
        a = a + [0.0] * (len(b) - len(a))
    else:
        a = list(a)
    for i, v in enumerate(b):
        a[i] += gb * v
    return a


def pad(x, sec):
    return x + [0.0] * ns(sec)


class Buf:
    """Auto-growing mix buffer: add(signal, at_seconds, gain)."""

    def __init__(self):
        self.x = []

    def add(self, sig, at=0.0, g=1.0):
        o = max(0, int(round(at * SR)))
        need = o + len(sig)
        x = self.x
        if need > len(x):
            x.extend([0.0] * (need - len(x)))
        for i, v in enumerate(sig):
            x[o + i] += g * v
        return self


def rms(x):
    return math.sqrt(sum(v * v for v in x) / max(1, len(x)))


def reverb(x, wet=0.2, room=0.78, damp=0.35, tail=0.3):
    """Tiny Freeverb-style room (4 damped combs + 2 all-passes) for a soft fairytale tail.
    `wet` is the RMS ratio of the reverb signal to the dry signal."""
    n = len(x) + ns(tail)
    src = x + [0.0] * (n - len(x))
    acc = [0.0] * n
    d1 = 1.0 - damp
    for length in (1116, 1188, 1277, 1356):
        buf = [0.0] * length
        idx = 0
        filt = 0.0
        for i in range(n):
            y = buf[idx]
            filt = y * d1 + filt * damp
            buf[idx] = src[i] + filt * room
            acc[i] += y
            idx += 1
            if idx == length:
                idx = 0
    for length in (556, 441):
        buf = [0.0] * length
        idx = 0
        for i in range(n):
            b = buf[idx]
            a = acc[i]
            buf[idx] = a + b * 0.5
            acc[i] = b - a
            idx += 1
            if idx == length:
                idx = 0
    rw = rms(acc)
    g = wet * rms(x) / rw if rw > 0 else 0.0
    out = [s + g * r for s, r in zip(src, acc)]
    return taper(out, min(0.5, 0.6 * ns(tail) / n))


# ------------------------------------------------------------------ voices & instruments

# Formant centres (F1, F2, F3) in Hz for an adult-sized tract; `scale` shrinks it for
# small creatures (> 1 = smaller / cuter).
VOWELS = {
    "a": (800.0, 1250.0, 2600.0),
    "e": (520.0, 1850.0, 2600.0),
    "i": (330.0, 2300.0, 3000.0),
    "o": (520.0, 880.0, 2450.0),
    "u": (360.0, 760.0, 2300.0),
    "m": (270.0, 1100.0, 2300.0),
}


def voice(f0, amp, keys, rng, scale=1.0, bright=0.7, breath=0.35, q=(5.0, 7.0, 9.0),
          gains=(1.0, 0.55, 0.22), body=0.35, lowpass=None):
    """Simple formant voice: (saw + sine + breath noise) through three band-passes whose
    centres glide between the vowels in `keys` = [(time, vowel), ...].
    `body` mixes in the bare fundamental for warmth; breath may be a scalar, (a, b) or list."""
    n = len(f0)
    saw = osc(f0, shape="saw", phase=0.5)
    sine = osc(f0, shape="sine")
    nz = white(n, rng)
    br = _curve(breath, n)
    nb = 1.0 - bright
    src = [(bright * s + nb * t + b * z) * a for s, t, z, b, a in zip(saw, sine, nz, br, amp)]
    out = [body * t * a for t, a in zip(sine, amp)]
    for k in range(3):
        g = gains[k]
        if g <= 0.0:
            continue
        track = ramp([(t, VOWELS[vw][k] * scale) for t, vw in keys], n, log=True)
        bp = svf(src, track, q[k], "bp")
        for i in range(n):
            out[i] += g * bp[i]
    if lowpass:
        out = svf(out, lowpass, 0.707, "lp")
    return out


def air(n, rng, amp, fc=4500.0, q=0.8, level=0.06):
    """Airy band of noise that follows an amplitude envelope."""
    s = svf(white(n, rng), fc, q, "bp")
    return [v * a * level for v, a in zip(s, amp)]


def squeak(rng, dur, pts, vib_rate=30.0, vib_depth=0.3, harm=(1.0, 0.14, 0.04),
           attack=0.008, hold=0.6, vib_onset=0.0):
    """Mostly-sine squeak gliding through frequency points, with optional fast vibrato."""
    n = ns(dur)
    f = ramp(pts, n, log=True)
    if vib_depth:
        f = vibrato(f, vib_rate, vib_depth, rng, onset=vib_onset)
    amp = ramp([(0.0, 0.0), (attack, 1.0), (dur * hold, 0.75), (dur, 0.0)], n)
    return tone(f, amp, harm)


def bell(freq, dur, decay, bright=1.0):
    """Soft FM bell: carrier f with a 2f modulator whose index decays quickly (a bright strike
    that mellows), plus two faint inharmonic partials for a glassy shimmer."""
    n = ns(dur)
    out = [0.0] * n
    w = TAU * freq / SR
    sin = math.sin
    e = 1.0
    de = math.exp(-1.0 / (decay * SR))
    ix = 1.5 * bright
    dix = math.exp(-1.0 / (decay * 0.3 * SR))
    e2 = 0.2 * bright if freq * 2.756 < 12000.0 else 0.0
    de2 = math.exp(-1.0 / (decay * 0.4 * SR))
    e3 = 0.06 * bright if freq * 5.404 < 12000.0 else 0.0
    de3 = math.exp(-1.0 / (decay * 0.15 * SR))
    for i in range(n):
        ph = w * i
        out[i] = e * sin(ph + ix * sin(2.0 * ph)) + e2 * sin(2.756 * ph) + e3 * sin(5.404 * ph)
        e *= de
        ix *= dix
        e2 *= de2
        e3 *= de3
    na = ns(0.0015)
    for i in range(min(na, n)):
        out[i] *= i / na
    return taper(out, 0.3)


def twinkle(f, tau, max_dur=0.3, partial=0.0):
    """A single high sparkle: a pure sine ping with exponential decay."""
    dur = min(max_dur, tau * 5.0)
    n = ns(dur)
    return tone(f, env_perc(n, 0.003, tau, end=0.25), (1.0, partial))


def flutter(rng, dur, beats_per_sec, level_pts, fc=1200.0):
    """Soft wing-flutter: band-passed noise gated by |sin| wing beats."""
    n = ns(dur)
    s = svf(white(n, rng), fc, 0.6, "bp")
    s = svf(s, 2600.0, 0.707, "lp")
    wing = lfo(n, beats_per_sec * 0.5, rng)
    env = ramp(level_pts, n)
    return [x * e * abs(w) ** 3 for x, e, w in zip(s, env, wing)]


def sniff(rng, dur, fc, q=1.3, rise=1.25):
    """One soft nose sniff: a short band of noise whose centre rises slightly."""
    n = ns(dur)
    f = ramp([(0.0, fc), (dur, fc * rise)], n, log=True)
    s = svf(white(n, rng), f, q, "bp")
    s = svf(s, 900.0, 0.7, "hp")
    s = svf(s, 5200.0, 0.707, "lp")   # keep it soft, not hissy
    e = ramp([(0.0, 0.0), (dur * 0.3, 1.0), (dur * 0.6, 0.65), (dur, 0.0)], n)
    return mul(s, e)


def bloop(rng, dur, f0, f1, tau, p2=0.12):
    """Bubble 'bloop': a resonant sine whose pitch sweeps upward as it decays."""
    n = ns(dur)
    f = ramp([(0.0, f0), (dur * 0.55, f1), (dur, f1 * 1.04)], n, log=True, smooth=False)
    amp = env_perc(n, 0.004, tau, end=0.3)
    s = tone(f, amp, (1.0, p2))
    # tiny watery 'plip' at the start of the bubble
    m = ns(0.004)
    plip = svf(pad(mul(white(m, rng), env_perc(m, 0.0005, 0.0012)), 0.004), min(f1 * 1.5, 6000.0), 3.0, "bp")
    return addsig(s, plip, 0.08)


def pop(rng, dur, f0, f1, tau):
    """Soft cork-like pop: a sine with a fast pitch sweep and a quick decay."""
    n = ns(dur)
    f = ramp([(0.0, f0), (dur * 0.5, f1), (dur, f1)], n, log=True)
    return tone(f, env_perc(n, 0.003, tau, end=0.3), (1.0, 0.12))


def rustle(rng, dur, fc=2600.0):
    """Fabric rustle: band-passed noise with an irregular, crinkly amplitude."""
    n = ns(dur)
    s = svf(white(n, rng), fc, 0.7, "bp")
    s = svf(s, 5500.0, 0.707, "lp")
    r = smooth_rand(n, rng, 40.0)
    env = ramp([(0.0, 0.0), (dur * 0.3, 1.0), (dur, 0.0)], n)
    return [x * e * max(0.0, 0.35 + y) ** 2 for x, e, y in zip(s, env, r)]


def j(rng, spread=0.05):
    """Random multiplier around 1 for organic jitter."""
    return rng.uniform(1.0 - spread, 1.0 + spread)


# ================================================================================ bunnies

def bunny_ambient(rng, v):
    layouts = [
        ([0.0, 0.095, 0.19], 0.30, "rise"),
        ([0.0, 0.085, 0.29, 0.375], 0.185, "arch"),
        ([0.0, 0.075, 0.15, 0.225], 0.33, "dip"),
    ]
    times, chirp_at, shape = layouts[v % 3]
    b = Buf()
    base = rng.uniform(2600.0, 3300.0)
    for k, t in enumerate(times):
        t += rng.uniform(-0.006, 0.006) if k else 0.0
        b.add(sniff(rng, rng.uniform(0.045, 0.07), base * j(rng, 0.15), rise=rng.uniform(1.1, 1.4)),
              t, rng.uniform(0.65, 1.0))
    f = rng.uniform(2200.0, 2700.0)
    d = rng.uniform(0.05, 0.07)
    pts = {
        "rise": [(0.0, f), (d, f * 1.35)],
        "arch": [(0.0, f), (d * 0.5, f * 1.3), (d, f * 1.1)],
        "dip": [(0.0, f * 1.2), (d * 0.4, f), (d, f * 1.3)],
    }[shape]
    b.add(squeak(rng, d, pts, 0.0, 0.0, harm=(1.0, 0.08), attack=0.006, hold=0.5), chirp_at, 0.22)
    return b.x


def bunny_hurt(rng, v):
    f = rng.uniform(1900.0, 2300.0)
    if v % 2 == 0:
        d = rng.uniform(0.2, 0.24)
        pts = [(0.0, f), (0.035, f * 1.32), (d * 0.6, f * 1.18), (d, f)]
    else:
        d = rng.uniform(0.26, 0.3)
        pts = [(0.0, f * 1.1), (0.03, f * 1.45), (0.09, f * 1.2), (0.14, f * 1.38), (d, f * 0.95)]
    n = ns(d)
    s = squeak(rng, d, pts, rng.uniform(24.0, 32.0), 0.25, attack=0.006)
    breath = mul(svf(white(n, rng), 3800.0, 1.0, "bp"), ramp([(0.0, 0.0), (0.01, 1.0), (d, 0.0)], n))
    return svf(addsig(s, breath, 0.12), 7000.0, 0.707, "lp")


def bunny_death(rng, v):
    b = Buf()
    f = rng.uniform(2300.0, 2600.0)
    b.add(squeak(rng, 0.11, [(0.0, f), (0.04, f * 1.15), (0.11, f * 1.05)], 28.0, 0.2), 0.0, 0.7)
    d = 0.9
    n = ns(d)
    fr = ramp([(0.0, f * 1.08), (0.12, f * 1.12), (d, f * 0.36)], n, log=True)
    fr = bend(fr, lfo(n, ramp([(0.0, 9.0), (d, 4.5)], n), rng), ramp([(0.0, 0.15), (d, 0.8)], n))
    amp = ramp([(0.0, 0.0), (0.02, 1.0), (0.3, 0.7), (d, 0.0)], n)
    b.add(tone(fr, amp, (1.0, 0.12, 0.03)), 0.14)
    return svf(b.x, 6500.0, 0.707, "lp")


def grunt(rng, dur, f0, flutter_hz=42.0):
    """One soft rabbit 'honk' grunt-purr."""
    n = ns(dur)
    f = ramp([(0.0, f0 * 1.06), (dur, f0 * 0.92)], n, log=True)
    amp = ramp([(0.0, 0.0), (0.008, 1.0), (dur * 0.5, 0.6), (dur, 0.0)], n)
    fl = lfo(n, flutter_hz, rng)
    amp = [a * (0.6 + 0.4 * m) for a, m in zip(amp, fl)]
    return voice(f, amp, [(0.0, "u"), (dur, "o")], rng, scale=1.3, bright=0.5, breath=0.6,
                 body=0.5, lowpass=1800.0)


def bunny_happy(rng, v):
    count, step, base = [(6, 0.105, 165.0), (8, 0.085, 185.0)][v % 2]
    base *= j(rng)
    b = Buf()
    t = 0.0
    for k in range(count):
        f = base * (1.0 + 0.12 * math.sin(math.pi * k / (count - 1))) * j(rng)
        g = (1.0 if k % 2 == 0 else 0.75) * rng.uniform(0.85, 1.0) * (1.0 - 0.25 * k / count)
        b.add(grunt(rng, rng.uniform(0.05, 0.075), f, rng.uniform(38.0, 46.0)), t, g)
        t += step * j(rng, 0.1)
    return b.x


# ============================================================================ blossom fox

def yip(rng, dur, lo, hi, end=None, keys=None, breath=0.35, attack=0.01):
    n = ns(dur)
    end = lo * 1.05 if end is None else end
    f = ramp([(0.0, lo), (dur * 0.3, hi), (dur, end)], n, log=True)
    amp = ramp([(0.0, 0.0), (attack, 1.0), (dur * 0.5, 0.8), (dur, 0.0)], n)
    keys = keys or [(0.0, "i"), (dur * 0.4, "e"), (dur, "i")]
    return voice(f, amp, keys, rng, scale=1.35, bright=0.75, breath=breath, body=0.3, lowpass=6500.0)


def fox_ambient(rng, v):
    b = Buf()
    lo = rng.uniform(650.0, 760.0)
    if v % 3 == 0:
        b.add(yip(rng, rng.uniform(0.16, 0.19), lo, lo * 1.55))
    elif v % 3 == 1:
        b.add(yip(rng, 0.14, lo, lo * 1.45), 0.0, 0.85)
        b.add(yip(rng, 0.16, lo * 1.1, lo * 1.7), rng.uniform(0.17, 0.2))
    else:
        for k in range(3):
            b.add(yip(rng, rng.uniform(0.075, 0.09), lo * (1.0 + 0.08 * k), lo * (1.4 + 0.1 * k)),
                  k * rng.uniform(0.11, 0.125), 1.0 - 0.15 * k)
    return b.x


def fox_hurt(rng, v):
    lo = rng.uniform(880.0, 1000.0)
    if v % 2 == 0:
        d = rng.uniform(0.22, 0.26)
        return yip(rng, d, lo, lo * 1.5, end=lo * 0.75, keys=[(0.0, "e"), (d * 0.3, "a"), (d, "o")],
                   breath=0.5, attack=0.006)
    b = Buf()
    b.add(yip(rng, 0.08, lo, lo * 1.35, keys=[(0.0, "i"), (0.08, "e")], attack=0.005), 0.0, 0.7)
    d = rng.uniform(0.19, 0.22)
    b.add(yip(rng, d, lo * 1.05, lo * 1.45, end=lo * 0.7, keys=[(0.0, "e"), (d * 0.35, "a"), (d, "o")],
              breath=0.5, attack=0.006), 0.095)
    return b.x


def whimper(rng, dur, pts, breath=0.7):
    n = ns(dur)
    f = vibrato(ramp(pts, n, log=True), rng.uniform(5.5, 7.0), 0.45, rng, onset=dur * 0.3)
    amp = ramp([(0.0, 0.0), (dur * 0.15, 1.0), (dur * 0.55, 0.7), (dur, 0.0)], n)
    return voice(f, amp, [(0.0, "u"), (dur * 0.3, "i"), (dur, "u")], rng, scale=1.3, bright=0.55,
                 breath=breath, body=0.45, lowpass=3000.0)


def fox_death(rng, v):
    b = Buf()
    f = rng.uniform(780.0, 860.0)
    b.add(whimper(rng, 0.42, [(0.0, f * 0.95), (0.12, f * 1.1), (0.42, f * 0.78)]))
    b.add(whimper(rng, 0.62, [(0.0, f * 0.9), (0.1, f * 0.95), (0.62, f * 0.5)], breath=1.0), 0.48, 0.75)
    return b.x


def chatter(rng, starts, lens, freqs, gains, vowel="e", scale=1.35, breath=0.35):
    """A run of short voiced chirps rendered as one continuous voice with gated amplitude."""
    total = starts[-1] + lens[-1] + 0.02
    n = ns(total)
    fpts, apts = [], [(0.0, 0.0)]
    for t, d, f, g in zip(starts, lens, freqs, gains):
        fpts += [(t, f * 0.9), (t + d * 0.35, f * 1.12), (t + d, f * 0.95)]
        apts += [(t, 0.0), (t + d * 0.2, g), (t + d * 0.55, g * 0.7), (t + d, 0.0)]
    f0 = ramp(fpts, n, log=True)
    amp = ramp(apts, n)
    return voice(f0, amp, [(0.0, vowel)], rng, scale=scale, bright=0.7, breath=breath, body=0.3,
                 lowpass=6500.0)


def fox_happy(rng, v):
    if v % 2 == 0:
        count = rng.randint(8, 10)
        step = rng.uniform(0.068, 0.078)
        base = rng.uniform(950.0, 1050.0)
        freqs = [base * (1.18 - 0.035 * k) * j(rng, 0.04) for k in range(count)]
    else:
        count = rng.randint(7, 8)
        step = rng.uniform(0.08, 0.09)
        base = rng.uniform(880.0, 960.0)
        freqs = [base * (1.0 + 0.25 * math.sin(math.pi * k / (count - 1))) * j(rng, 0.04)
                 for k in range(count)]
    starts = [k * step + (rng.uniform(-0.006, 0.006) if k else 0.0) for k in range(count)]
    lens = [step * rng.uniform(0.55, 0.7) for _ in range(count)]
    gains = [(1.0 - 0.45 * k / count) * (1.0 if k % 2 == 0 else 0.8) for k in range(count)]
    return chatter(rng, starts, lens, freqs, gains, "e")


# ============================================================================ cloud kitty

def mew(rng, dur, f_start, f_peak, f_end, peak_at=0.35, breath=0.4, attack_frac=0.12,
        vib=0.25, trill=False, scale=1.55):
    """Kitten mew: formant glide m-e-a-o-u over a rise-and-fall pitch contour, plus air."""
    n = ns(dur)
    f0 = ramp([(0.0, f_start), (dur * peak_at, f_peak), (dur, f_end)], n, log=True)
    if vib:
        f0 = vibrato(f0, rng.uniform(5.0, 6.5), vib, rng, onset=dur * 0.5)
    amp = ramp([(0.0, 0.0), (dur * attack_frac, 0.55), (dur * 0.35, 1.0), (dur * 0.7, 0.7), (dur, 0.0)], n)
    if trill:  # a little rolled 'mrrp' onset
        m = lfo(n, rng.uniform(26.0, 30.0), rng)
        w = ramp([(0.0, 1.0), (0.1, 1.0), (0.17, 0.0)], n)
        amp = [a * (1.0 - ww * 0.5 * (1.0 - mm)) for a, ww, mm in zip(amp, w, m)]
    keys = [(0.0, "m"), (dur * 0.18, "e"), (dur * 0.45, "a"), (dur * 0.8, "o"), (dur, "u")]
    s = voice(f0, amp, keys, rng, scale=scale, bright=0.65, breath=breath, body=0.3, lowpass=7000.0)
    return addsig(s, air(n, rng, amp, 5200.0, 0.9, 0.06))


def kitty_ambient(rng, v):
    if v % 3 == 0:
        return mew(rng, rng.uniform(0.42, 0.48), 620 * j(rng), 880 * j(rng), 700 * j(rng))
    if v % 3 == 1:
        return mew(rng, rng.uniform(0.32, 0.36), 760 * j(rng), 980 * j(rng), 820 * j(rng), peak_at=0.3)
    return mew(rng, rng.uniform(0.56, 0.62), 660 * j(rng), 860 * j(rng), 600 * j(rng), peak_at=0.45,
               trill=True)


def kitty_hurt(rng, v):
    if v % 2 == 0:
        return mew(rng, 0.22, 950 * j(rng), 1300 * j(rng), 1050 * j(rng), peak_at=0.25,
                   attack_frac=0.05, vib=0.0, breath=0.5)
    return mew(rng, 0.27, 1000 * j(rng), 1400 * j(rng), 900 * j(rng), peak_at=0.3,
               attack_frac=0.05, vib=0.3, breath=0.5)


def kitty_death(rng, v):
    return mew(rng, 1.1, 820 * j(rng), 870 * j(rng), 470 * j(rng), peak_at=0.18,
               breath=(0.4, 1.2), vib=0.35, attack_frac=0.06)


def kitty_purr(rng, v):
    """~25 Hz pulsed low buzz with breathy noise, over exhale/inhale phases."""
    if v % 2 == 0:
        dur, f0, rate = 1.5, rng.uniform(105.0, 118.0), rng.uniform(24.5, 26.5)
        phases = [(0.0, 0.7, 1.0, 1.0), (0.78, 1.5, 0.7, 1.08)]   # (start, end, level, rate factor)
    else:
        dur, f0, rate = 1.65, rng.uniform(92.0, 102.0), rng.uniform(22.5, 24.0)
        phases = [(0.0, 0.5, 0.65, 1.1), (0.56, 1.12, 1.0, 1.0), (1.18, 1.65, 0.6, 1.1)]
    n = ns(dur)
    bpts, rpts = [], []
    for s, e, lvl, rf in phases:
        bpts += [(s, 0.0), (s + 0.12, lvl), (e - 0.12, lvl * 0.9), (e, 0.0)]
        rpts += [(s + 0.05, rate * rf), (e - 0.05, rate * rf)]
    breath_env = ramp(bpts, n)
    rate_c = ramp(rpts, n)
    jit = smooth_rand(n, rng, 6.0)
    pulse = [0.0] * n
    p = 0.0
    cos = math.cos
    for i in range(n):
        c = 0.5 - 0.5 * cos(TAU * p)
        pulse[i] = c * c
        p += rate_c[i] * (1.0 + 0.04 * jit[i]) / SR
        if p >= 1.0:
            p -= 1.0
    buzz = osc([f0 * (1.0 + 0.02 * x) for x in jit], shape="saw", phase=0.5)
    low = svf(buzz, 520.0, 0.8, "lp")
    nasal = svf(buzz, 380.0, 2.0, "bp")
    hiss = svf(white(n, rng), 950.0, 0.7, "bp")
    out = [((lo + 0.8 * na) * (0.15 + 0.85 * pu) + 0.6 * h * (0.3 + 0.7 * pu)) * be
           for lo, na, h, pu, be in zip(low, nasal, hiss, pulse, breath_env)]
    return svf(out, 2800.0, 0.707, "lp")


# ======================================================================= strawberry mouse

def _squeak_pts(rng, f, d):
    shape = rng.choice(("arch", "rise", "fall"))
    if shape == "arch":
        return [(0.0, f * 0.9), (d * 0.4, f * 1.12), (d, f * 0.98)]
    if shape == "rise":
        return [(0.0, f * 0.88), (d, f * 1.12)]
    return [(0.0, f * 1.12), (d, f * 0.9)]


def mouse_ambient(rng, v):
    count = v % 3 + 1
    b = Buf()
    t = 0.0
    for _ in range(count):
        f = rng.uniform(3000.0, 3900.0)
        d = rng.uniform(0.15, 0.18) if count == 1 else rng.uniform(0.05, 0.085)
        b.add(squeak(rng, d, _squeak_pts(rng, f, d), rng.uniform(38.0, 52.0), 0.3,
                     harm=(1.0, 0.1, 0.03), attack=0.005, hold=0.55), t, rng.uniform(0.75, 1.0))
        t += d + rng.uniform(0.04, 0.07)
    return svf(b.x, 8000.0, 0.707, "lp")


def mouse_hurt(rng, v):
    f = rng.uniform(3200.0, 3500.0)
    if v % 2 == 0:
        d = 0.15
        return squeak(rng, d, [(0.0, f), (0.025, f * 1.3), (d, f * 1.15)], 45.0, 0.25,
                      attack=0.003, hold=0.5)
    b = Buf()
    b.add(squeak(rng, 0.055, [(0.0, f * 1.05), (0.02, f * 1.25), (0.055, f * 1.15)], 45.0, 0.2,
                 attack=0.003, hold=0.5), 0.0, 0.7)
    b.add(squeak(rng, 0.12, [(0.0, f * 1.1), (0.02, f * 1.38), (0.12, f * 1.2)], 48.0, 0.25,
                 attack=0.003, hold=0.5), 0.075)
    return b.x


def mouse_death(rng, v):
    d = 0.85
    n = ns(d)
    f = rng.uniform(4000.0, 4400.0)
    fr = ramp([(0.0, f), (0.06, f * 1.08), (d, f * 0.42)], n, log=True)
    fr = bend(fr, lfo(n, ramp([(0.0, 14.0), (d, 6.0)], n), rng), ramp([(0.0, 0.2), (d, 0.6)], n))
    amp = ramp([(0.0, 0.0), (0.01, 1.0), (0.25, 0.75), (d, 0.0)], n)
    return svf(tone(fr, amp, (1.0, 0.1, 0.02)), 8000.0, 0.707, "lp")


# ============================================================================== honey bear

def bear_voice(rng, dur, fpts, keys, amp_pts, rough=0.0, breath=0.45, scale=0.95,
               lowpass=1600.0, vib=(4.5, 0.15)):
    n = ns(dur)
    f0 = ramp(fpts, n, log=True)
    if vib:
        f0 = vibrato(f0, vib[0], vib[1], rng, onset=dur * 0.3)
    amp = ramp(amp_pts, n)
    if rough:  # cuddly grumble: irregular amplitude rumble
        g = lfo(n, rng.uniform(19.0, 24.0), rng)
        r = smooth_rand(n, rng, 40.0)
        amp = [a * (1.0 - rough * (0.5 - 0.5 * (0.6 * x + 0.4 * y))) for a, x, y in zip(amp, g, r)]
    return voice(f0, amp, keys, rng, scale=scale, bright=0.55, breath=breath, body=0.6, lowpass=lowpass)


def bear_ambient(rng, v):
    if v % 3 == 0:  # 'hmm-mm' hum with a rise
        d = 0.7
        f = 115.0 * j(rng)
        return bear_voice(rng, d, [(0.0, f), (0.45, f * 1.2), (d, f * 1.1)], [(0.0, "m"), (d, "m")],
                          [(0.0, 0.0), (0.08, 0.8), (0.4, 1.0), (d, 0.0)], lowpass=1500.0)
    if v % 3 == 1:  # 'grr-umm' grumble
        d = 0.75
        f = 108.0 * j(rng)
        return bear_voice(rng, d, [(0.0, f), (0.3, f * 1.13), (d, f * 0.92)],
                          [(0.0, "o"), (0.35, "u"), (d, "m")],
                          [(0.0, 0.0), (0.05, 1.0), (0.5, 0.75), (d, 0.0)], rough=0.5, lowpass=1500.0)
    b = Buf()  # two little 'mrr mrr'
    f = 130.0 * j(rng)
    for k, (t, rise) in enumerate(((0.0, 1.12), (0.36, 1.08))):
        d = 0.28 * j(rng)
        b.add(bear_voice(rng, d, [(0.0, f * (1 - 0.04 * k)), (d * 0.4, f * rise), (d, f * 0.95)],
                         [(0.0, "m"), (d * 0.35, "o"), (d, "u")],
                         [(0.0, 0.0), (0.03, 1.0), (d * 0.5, 0.7), (d, 0.0)], rough=0.35,
                         lowpass=1500.0), t, 1.0 - 0.15 * k)
    return b.x


def bear_hurt(rng, v):
    """'hrmf': breathy h, a short voiced 'rm', and a soft f puff."""
    b = Buf()
    n = ns(0.07)
    b.add(mul(svf(white(n, rng), 1100.0, 0.8, "bp"), ramp([(0.0, 0.0), (0.015, 1.0), (0.07, 0.0)], n)),
          0.0, 0.35)
    f = rng.uniform(140.0, 155.0)
    if v % 2 == 0:
        d = 0.2
        fpts = [(0.0, f), (0.05, f * 1.04), (d, f * 0.78)]
    else:
        d = 0.24
        fpts = [(0.0, f * 0.95), (0.09, f * 1.12), (d, f * 0.8)]
    b.add(bear_voice(rng, d, fpts, [(0.0, "o"), (d * 0.5, "u"), (d, "m")],
                     [(0.0, 0.0), (0.012, 1.0), (d * 0.45, 0.8), (d, 0.0)], vib=None, breath=0.5), 0.035)
    n = ns(0.09)
    b.add(mul(svf(white(n, rng), 2400.0, 0.7, "bp"), ramp([(0.0, 0.0), (0.02, 1.0), (0.09, 0.0)], n)),
          0.035 + d - 0.03, 0.18)
    return b.x


def bear_death(rng, v):
    d = 1.15
    f = rng.uniform(148.0, 160.0)
    return bear_voice(rng, d, [(0.0, f), (0.2, f * 1.07), (d, f * 0.55)],
                      [(0.0, "o"), (0.4, "o"), (0.85, "u"), (d, "m")],
                      [(0.0, 0.0), (0.06, 1.0), (0.45, 0.75), (d, 0.0)], breath=(0.4, 0.9),
                      vib=(4.0, 0.2), lowpass=1400.0)


def bear_happy(rng, v):
    f = rng.uniform(118.0, 126.0)
    if v % 2 == 0:  # 'mmm-MMM' with a little rise
        d = 1.0
        return bear_voice(rng, d, [(0.0, f), (0.4, f), (0.72, f * 1.22), (d, f * 1.15)],
                          [(0.0, "m"), (d, "m")],
                          [(0.0, 0.0), (0.1, 0.75), (0.5, 0.85), (0.75, 1.0), (d, 0.0)],
                          vib=(5.0, 0.2), lowpass=1500.0, breath=0.3)
    b = Buf()  # 'mm-mmm'
    b.add(bear_voice(rng, 0.3, [(0.0, f), (0.3, f * 1.04)], [(0.0, "m"), (0.3, "m")],
                     [(0.0, 0.0), (0.05, 0.8), (0.3, 0.0)], vib=None, lowpass=1500.0, breath=0.3), 0.0, 0.8)
    b.add(bear_voice(rng, 0.62, [(0.0, f * 1.02), (0.35, f * 1.25), (0.62, f * 1.18)],
                     [(0.0, "m"), (0.62, "m")], [(0.0, 0.0), (0.06, 0.8), (0.35, 1.0), (0.62, 0.0)],
                     vib=(5.2, 0.2), lowpass=1500.0, breath=0.3), 0.36)
    return b.x


# =============================================================================== moon deer

def bleat(rng, dur, fpts, vib_rate, vib_depth, breath=0.5, keys=None, attack=0.02, amp_pts=None):
    """Fawn bleat: voice with 7-9 Hz vibrato (and matching tremolo) plus airy noise."""
    n = ns(dur)
    m = lfo(n, vib_rate, rng)
    if isinstance(vib_depth, list):
        depth = vib_depth
    else:
        depth = ramp([(0.0, vib_depth * 0.3), (0.06, vib_depth), (dur, vib_depth)], n)
    f0 = bend(ramp(fpts, n, log=True), m, depth)
    amp = ramp(amp_pts or [(0.0, 0.0), (attack, 0.8), (dur * 0.3, 1.0), (dur * 0.75, 0.65), (dur, 0.0)], n)
    amp = [a * (0.82 + 0.18 * x) for a, x in zip(amp, m)]
    keys = keys or [(0.0, "e"), (dur * 0.4, "a"), (dur, "e")]
    s = voice(f0, amp, keys, rng, scale=1.15, bright=0.6, breath=breath, body=0.35, lowpass=5000.0)
    return addsig(s, air(n, rng, amp, 3400.0, 0.9, 0.06))


def deer_ambient(rng, v):
    if v % 3 == 0:
        d = rng.uniform(0.52, 0.58)
        f = 400.0 * j(rng)
        return bleat(rng, d, [(0.0, f), (0.08, f * 1.16), (d * 0.6, f * 1.2), (d, f * 1.07)],
                     rng.uniform(7.5, 8.5), 0.6)
    if v % 3 == 1:
        d = rng.uniform(0.42, 0.47)
        f = 450.0 * j(rng)
        return bleat(rng, d, [(0.0, f), (0.06, f * 1.15), (d, f * 1.04)], rng.uniform(7.0, 7.8), 0.7,
                     keys=[(0.0, "i"), (d * 0.3, "e"), (d, "a")])
    d = rng.uniform(0.66, 0.72)  # two-part 'meh-eh'
    f = 410.0 * j(rng)
    return bleat(rng, d, [(0.0, f), (0.08, f * 1.15), (0.33, f * 1.11), (0.4, f * 1.07), (d, f * 0.96)],
                 8.5, 0.5, amp_pts=[(0.0, 0.0), (0.025, 0.85), (0.3, 1.0), (0.36, 0.45), (0.42, 0.9), (d, 0.0)])


def deer_hurt(rng, v):
    if v % 2 == 0:
        d = 0.25
        f = 540.0 * j(rng)
        return bleat(rng, d, [(0.0, f), (0.05, f * 1.23), (d, f * 1.1)], 9.0, 0.8, breath=0.6, attack=0.008)
    d = 0.3
    f = 600.0 * j(rng)
    return bleat(rng, d, [(0.0, f), (0.06, f * 1.17), (0.15, f * 1.08), (d, f * 0.93)], 9.5, 0.7,
                 breath=0.6, attack=0.008, keys=[(0.0, "e"), (0.1, "a"), (d, "a")])


def deer_death(rng, v):
    d = 1.15
    n = ns(d)
    f = 500.0 * j(rng)
    return bleat(rng, d, [(0.0, f), (0.15, f * 1.08), (d, f * 0.6)], ramp([(0.0, 8.0), (d, 4.0)], n),
                 ramp([(0.0, 0.3), (0.1, 0.6), (d, 0.95)], n), breath=(0.5, 1.4),
                 amp_pts=[(0.0, 0.0), (0.03, 0.85), (0.3, 1.0), (0.6, 0.6), (d, 0.0)])


# ========================================================================= pastel axolotl

def axolotl_ambient(rng, v):
    b = Buf()
    if v % 3 == 0:
        b.add(bloop(rng, 0.17, 380 * j(rng), 1150 * j(rng), 0.05))
        b.add(bloop(rng, 0.1, 620 * j(rng), 1500 * j(rng), 0.03), 0.15, 0.45)
    elif v % 3 == 1:
        b.add(bloop(rng, 0.15, 420 * j(rng), 1050 * j(rng), 0.045))
        b.add(bloop(rng, 0.17, 500 * j(rng), 1350 * j(rng), 0.05), 0.16, 0.9)
    else:
        for t, g in ((0.0, 0.8), (0.075, 1.0), (0.165, 0.7)):
            base = rng.uniform(450.0, 800.0)
            b.add(bloop(rng, 0.09, base, base * 2.4, 0.028), t, g)
    return reverb(b.x, 0.12, tail=0.2)


def axolotl_hurt(rng, v):
    b = Buf()
    if v % 2 == 0:
        b.add(bloop(rng, 0.09, 700 * j(rng), 2300 * j(rng), 0.035))
        b.add(squeak(rng, 0.1, [(0.0, 2250.0), (0.1, 1900.0)], 32.0, 0.4, harm=(1.0, 0.1)), 0.06, 0.55)
    else:
        b.add(bloop(rng, 0.07, 900 * j(rng), 2600 * j(rng), 0.025))
        b.add(bloop(rng, 0.09, 800 * j(rng), 2000 * j(rng), 0.03), 0.085, 0.85)
    return reverb(b.x, 0.1, tail=0.18)


def axolotl_death(rng, v):
    b = Buf()
    base = rng.uniform(860.0, 940.0)
    for k, t in enumerate((0.0, 0.13, 0.28, 0.44, 0.61, 0.79)):
        f = base * 0.8 ** k
        b.add(bloop(rng, 0.12 + 0.015 * k, f, f * (2.3 - 0.12 * k), 0.035 + 0.006 * k),
              t + (rng.uniform(-0.01, 0.01) if k else 0.0), 1.0 - 0.11 * k)
    return reverb(b.x, 0.15, tail=0.2)


# ============================================================================== tiny swan

def honk(rng, dur, fpts, nasal=1050.0, rough=0.0, vib=(6.0, 0.25), attack=0.015):
    """Small nasal honk: saw through a ~1 kHz 'nose' band-pass, with a soft low body."""
    n = ns(dur)
    f0 = vibrato(ramp(fpts, n, log=True), vib[0], vib[1], rng, onset=0.03)
    amp = ramp([(0.0, 0.0), (attack, 1.0), (dur * 0.6, 0.85), (dur, 0.0)], n)
    if rough:
        r = smooth_rand(n, rng, 45.0)
        amp = [a * (1.0 - rough * 0.5 * (1.0 + x)) for a, x in zip(amp, r)]
    saw = osc(f0, shape="saw", phase=0.5)
    nz = white(n, rng)
    src = [(s + 0.25 * z) * a for s, z, a in zip(saw, nz, amp)]
    nose = svf(src, nasal, 4.0, "bp")
    f2 = svf(src, nasal * 2.2, 6.0, "bp")
    low = svf(src, 500.0, 0.7, "lp")
    out = [a + 0.35 * b + 0.3 * c for a, b, c in zip(nose, f2, low)]
    return svf(out, 3600.0, 0.707, "lp")


def swan_ambient(rng, v):
    if v % 3 == 0:
        d = 0.3
        f = 340.0 * j(rng)
        return honk(rng, d, [(0.0, f), (0.08, f * 1.18), (d, f * 1.06)])
    if v % 3 == 1:
        b = Buf()
        f = 380.0 * j(rng)
        b.add(honk(rng, 0.16, [(0.0, f), (0.05, f * 1.1), (0.16, f * 1.03)]))
        b.add(honk(rng, 0.16, [(0.0, f * 0.95), (0.05, f * 1.05), (0.16, f * 0.92)]), 0.21, 0.85)
        return b.x
    d = 0.35  # questioning 'hon-k?'
    f = 330.0 * j(rng)
    return honk(rng, d, [(0.0, f), (0.12, f * 1.08), (d, f * 1.3)], nasal=1150.0)


def swan_hurt(rng, v):
    if v % 2 == 0:
        d = 0.22
        f = 470.0 * j(rng)
        return honk(rng, d, [(0.0, f), (0.05, f * 1.28), (d, f * 0.92)], rough=0.3, attack=0.008)
    d = 0.26
    f = 520.0 * j(rng)
    return honk(rng, d, [(0.0, f), (0.06, f * 1.23), (d, f * 0.92)], nasal=1300.0, rough=0.25, attack=0.008)


def swan_death(rng, v):
    d = 0.95
    f = 430.0 * j(rng)
    return honk(rng, d, [(0.0, f), (0.12, f * 1.06), (d, f * 0.53)], vib=(5.0, 0.3))


# ====================================================================== rainbow butterfly

def butterfly_ambient(rng, v):
    b = Buf()
    count = 10 if v % 2 == 0 else 13
    for k in range(count):
        if v % 2 == 0:
            t = rng.uniform(0.0, 0.5)
            f = rng.uniform(6000.0, 9000.0)
        else:  # a gentle upward shimmer
            t = 0.5 * k / (count - 1) + rng.uniform(-0.015, 0.015)
            f = (6000.0 + 3000.0 * k / (count - 1)) * rng.uniform(0.97, 1.02)
        b.add(twinkle(f, rng.uniform(0.04, 0.11), 0.28), max(0.0, t), rng.uniform(0.35, 1.0))
    d = 0.75
    beat = 12.0 if v % 2 == 0 else 9.0
    b.add(flutter(rng, d, beat * j(rng), [(0.0, 0.0), (0.15, 1.0), (0.55, 0.8), (d, 0.0)]), 0.0, 0.6)
    return reverb(b.x, 0.25, tail=0.12)


def butterfly_hurt(rng, v):
    b = Buf()
    for k, f in enumerate((5200.0, 6300.0, 7500.0, 8700.0)):
        b.add(twinkle(f * j(rng, 0.03), 0.045, 0.2), k * 0.035 * j(rng, 0.1), 0.7 + 0.1 * k)
    b.add(flutter(rng, 0.14, 18.0, [(0.0, 0.0), (0.03, 1.0), (0.14, 0.0)]), 0.0, 0.5)
    return reverb(b.x, 0.2, tail=0.12)


def butterfly_death(rng, v):
    b = Buf()
    ladder = (8372.0, 7040.0, 6272.0, 5274.0, 4699.0, 4186.0, 3520.0, 3136.0, 2637.0)
    for k, f in enumerate(ladder):
        b.add(twinkle(f * j(rng, 0.01), 0.09 + 0.008 * k, 0.25), k * 0.085 * j(rng, 0.05) if k else 0.0,
              1.0 - 0.07 * k)
    b.add(flutter(rng, 0.4, 10.0, [(0.0, 0.0), (0.05, 1.0), (0.4, 0.0)]), 0.0, 0.4)
    return reverb(b.x, 0.3, tail=0.2)


# ===================================================================== cherry blossom bird

def bird_chirp(rng, dur, pts, vib=None, harm=(1.0, 0.07, 0.02), attack=0.006):
    n = ns(dur)
    f = ramp(pts, n, log=True)
    if vib:
        f = vibrato(f, vib[0], vib[1], rng)
    amp = ramp([(0.0, 0.0), (attack, 1.0), (dur * 0.55, 0.8), (dur, 0.0)], n)
    return tone(f, amp, harm)


CHIRP_SHAPES = {
    "up": lambda f, d: [(0.0, f * 0.75), (d, f * 1.15)],
    "down": lambda f, d: [(0.0, f * 1.25), (d, f * 0.8)],
    "tweet": lambda f, d: [(0.0, f * 0.85), (d * 0.45, f * 1.2), (d, f * 0.95)],
    "chee": lambda f, d: [(0.0, f * 0.95), (d * 0.2, f * 1.05), (d, f)],
}


def bird_ambient(rng, v):
    count = v % 3 + 1
    b = Buf()
    t = 0.0
    for k in range(count):
        shape = "tweet" if count == 1 else rng.choice(list(CHIRP_SHAPES))
        f = rng.uniform(3000.0, 4000.0)
        d = rng.uniform(0.14, 0.17) if count == 1 else rng.uniform(0.08, 0.13)
        vib = (rng.uniform(30.0, 45.0), 0.35) if shape == "chee" else None
        b.add(bird_chirp(rng, d, CHIRP_SHAPES[shape](f, d), vib), t, rng.uniform(0.75, 1.0))
        t += d + rng.uniform(0.05, 0.09)
    return reverb(b.x, 0.15, tail=0.15)


def bird_hurt(rng, v):
    if v % 2 == 0:
        x = bird_chirp(rng, 0.09, [(0.0, 5000.0 * j(rng)), (0.09, 3200.0 * j(rng))], attack=0.003)
    else:
        x = bird_chirp(rng, 0.11, [(0.0, 4400.0 * j(rng)), (0.03, 5200.0 * j(rng)), (0.11, 3600.0 * j(rng))],
                       attack=0.003)
    return reverb(x, 0.12, tail=0.12)


def bird_death(rng, v):
    b = Buf()
    b.add(bird_chirp(rng, 0.08, [(0.0, 4800.0), (0.08, 4000.0)]), 0.0, 0.7)
    d = 0.62
    n = ns(d)
    f = 4600.0 * j(rng)
    fr = ramp([(0.0, f), (0.05, f * 1.04), (d, f * 0.41)], n, log=True)
    fr = bend(fr, lfo(n, ramp([(0.0, 22.0), (d, 14.0)], n), rng), ramp([(0.0, 0.5), (d, 0.25)], n))
    amp = ramp([(0.0, 0.0), (0.008, 1.0), (0.2, 0.75), (d, 0.0)], n)
    b.add(tone(fr, amp, (1.0, 0.07, 0.02)), 0.11)
    return reverb(b.x, 0.15, tail=0.15)


PENTA_HZ = (2093.0, 2349.3, 2637.0, 3136.0, 3520.0, 4186.0, 4698.6)   # C7 D7 E7 G7 A7 C8 D8


def song_note(rng, d, fa, fb, vib=0.0, attack=0.006):
    n = ns(d)
    f = ramp([(0.0, fa * 0.96), (min(0.012, d * 0.25), fa), (d, fb)], n, log=True)
    if vib:
        f = vibrato(f, rng.uniform(24.0, 30.0), vib, rng, onset=d * 0.3)
    amp = ramp([(0.0, 0.0), (attack, 1.0), (d * 0.6, 0.8), (d, 0.0)], n)
    return tone(f, amp, (1.0, 0.06, 0.02))


def bird_sing(rng, v):
    """Short melodic phrase on a major-pentatonic scale between ~2 and ~4.7 kHz."""
    scale = PENTA_HZ
    top = len(scale) - 1
    b = Buf()
    t = 0.0

    def clamp(i):
        return max(0, min(top, i))

    def note(i, d, gain=1.0, to=None, vib=0.0, gap=0.025):
        nonlocal t
        i = clamp(i)
        fa = scale[i] * j(rng, 0.012)
        fb = scale[clamp(to)] * j(rng, 0.012) if to is not None else fa * rng.uniform(0.98, 1.03)
        b.add(song_note(rng, d, fa, fb, vib), t, gain * rng.uniform(0.85, 1.0))
        t += d + gap

    def trill(i, k, count, d=0.028, gain=0.85):
        for c in range(count):
            note(i if c % 2 == 0 else k, d, gain, gap=0.006)

    style = v % 3
    if style == 0:  # rising run, trill, cascade, long sung note
        i = rng.randint(0, 2)
        for k in range(3):
            note(i + k, 0.07)
        trill(i + 3, i + 4, rng.randint(7, 9))
        t += 0.04
        for k in (3, 2, 1):
            note(i + k, 0.085)
        note(i + 1, 0.28, to=i, vib=0.35)
    elif style == 1:  # trill opener, wandering notes, sliding 'tweee-oo'
        trill(top - 1, top, rng.randint(8, 10))
        t += 0.06
        i = rng.randint(2, 4)
        for _ in range(5):
            note(i, rng.choice((0.07, 0.09, 0.11)))
            i = clamp(i + rng.choice((-2, -1, 1, 2)))
        note(max(i, 3), 0.24, to=max(i, 3) - 3)
    else:  # call and answer, then 'chee-chew'
        i = rng.randint(1, 3)
        motif = [0, rng.choice((1, 2)), rng.choice((-1, 1)), 0]
        durs = (0.06, 0.06, 0.07, 0.12)
        for rep in range(2):
            for m, d in zip(motif, durs):
                note(i + m + rep, d)
            t += 0.07
        note(top, 0.1)
        note(top - 2, 0.16, to=top - 4)
    return reverb(b.x, 0.18, tail=0.28)


# ========================================================================= dreamy hamster

def hamster_ambient(rng, v):
    count = (7, 9, 6)[v % 3]
    b = Buf()
    t = 0.0
    base = rng.uniform(2100.0, 2600.0)
    for k in range(count):
        d = rng.uniform(0.025, 0.04)
        f = base * (1.0 - 0.15 * k / count) * j(rng, 0.06)
        g = (1.0 - 0.5 * k / count) * rng.uniform(0.7, 1.0)
        b.add(squeak(rng, d, [(0.0, f * 0.92), (d * 0.4, f * 1.08), (d, f * 0.96)], 0.0, 0.0,
                     harm=(1.0, 0.15, 0.04), attack=0.004, hold=0.5), t, g)
        m = ns(0.003)
        click = svf(pad(mul(white(m, rng), env_perc(m, 0.0003, 0.001)), 0.004), 4500.0, 1.5, "bp")
        b.add(click, t, 0.15 * g)
        t += rng.uniform(0.06, 0.075) * (1.0 + 0.8 * (k / count) ** 2)   # sleepily slowing down
    if v % 3 == 2:  # little yawn-squeak to finish
        f = rng.uniform(2400.0, 2600.0)
        b.add(squeak(rng, 0.22, [(0.0, f), (0.05, f * 1.06), (0.22, f * 0.68)], 9.0, 0.3), t + 0.04, 0.6)
    return svf(b.x, 7000.0, 0.707, "lp")


def hamster_hurt(rng, v):
    f = rng.uniform(2250.0, 2400.0)
    if v % 2 == 0:
        d = 0.18
        return squeak(rng, d, [(0.0, f), (0.04, f * 1.35), (d, f * 1.17)], 35.0, 0.3, attack=0.005)
    d = 0.21
    return squeak(rng, d, [(0.0, f * 1.1), (0.04, f * 1.4), (0.1, f * 1.2), (0.14, f * 1.36), (d, f * 1.08)],
                  33.0, 0.3, attack=0.005)


def hamster_death(rng, v):
    d = 0.85
    n = ns(d)
    f = rng.uniform(2900.0, 3100.0)
    fr = ramp([(0.0, f), (0.07, f * 1.07), (d, f * 0.43)], n, log=True)
    fr = bend(fr, lfo(n, ramp([(0.0, 12.0), (d, 6.0)], n), rng), ramp([(0.0, 0.25), (d, 0.6)], n))
    amp = ramp([(0.0, 0.0), (0.01, 1.0), (0.25, 0.75), (d, 0.0)], n)
    return svf(tone(fr, amp, (1.0, 0.15, 0.04)), 7000.0, 0.707, "lp")


# ============================================================================= pet shared

def pet_happy(rng, v):
    """Magical rising bell arpeggio."""
    b = Buf()
    if v % 2 == 0:
        seq, step = (1046.5, 1318.5, 1568.0, 2093.0), 0.085      # C6 E6 G6 C7
    else:
        seq, step = (784.0, 1046.5, 1318.5, 1568.0, 2093.0), 0.07  # G5 C6 E6 G6 C7
    last = len(seq) - 1
    for k, f in enumerate(seq):
        dur, decay = (0.6, 0.3) if k == last else (0.45, 0.22)
        b.add(bell(f * j(rng, 0.002), dur, decay, bright=rng.uniform(0.8, 1.0)),
              k * step * (j(rng, 0.03) if k else 1.0), 0.65 + 0.35 * k / last)
    t_end = last * step
    if v % 2 == 0:  # two tiny sparkles on top
        b.add(twinkle(5274.0, 0.08, 0.3), t_end + 0.06, 0.12)
        b.add(twinkle(6272.0, 0.07, 0.3), t_end + 0.12, 0.1)
    else:           # soft high shimmer chord
        b.add(bell(2093.0 * 2, 0.45, 0.2, bright=0.4), t_end + 0.08, 0.18)
        b.add(bell(2637.0 * 2, 0.45, 0.2, bright=0.4), t_end + 0.1, 0.14)
    return reverb(b.x, 0.22, tail=0.22)


def bite(rng, strength=1.0):
    """One cute crunchy bite: a cluster of tiny crackle grains plus a soft chewy body."""
    dur = rng.uniform(0.07, 0.1)
    b = Buf()
    for _ in range(rng.randint(9, 15)):
        t = dur * 0.8 * rng.random() ** 1.6
        gl = rng.uniform(0.002, 0.006)
        m = ns(gl)
        grain = pad(mul(white(m, rng), env_perc(m, 0.0004, gl * 0.35)), 0.004)
        b.add(svf(grain, rng.uniform(1800.0, 4500.0), rng.uniform(1.2, 2.5), "bp"), t, rng.uniform(0.4, 1.0))
    n = ns(dur)
    b.add(mul(svf(white(n, rng), 520.0, 0.9, "bp"), env_perc(n, 0.004, 0.03)), 0.0, 0.6)
    m = ns(0.05)
    b.add(tone(ramp([(0.0, 210.0), (0.05, 130.0)], m, log=True), env_perc(m, 0.002, 0.015)), 0.0, 0.25)
    return scaled(svf(b.x, 6500.0, 0.707, "lp"), strength)


def pet_eat(rng, v):
    plans = ((0.0, 0.2), (0.0, 0.16, 0.34), (0.0, 0.13, 0.36))
    gains = (1.0, 0.85, 0.95)
    b = Buf()
    for k, t in enumerate(plans[v % 3]):
        b.add(bite(rng), t + (rng.uniform(-0.01, 0.01) if k else 0.0), gains[k] * rng.uniform(0.85, 1.0))
    if v % 3 == 2:
        b.add(bite(rng, 0.4), 0.47)   # one last tiny nibble
    return b.x


def pet_snore(rng, v):
    """Tiny snore: a soft fluttery inhale, then a breathy exhale (with a whistle or a lip puff)."""
    b = Buf()
    di = rng.uniform(0.5, 0.56)
    n = ns(di)
    env = ramp([(0.0, 0.0), (di * 0.45, 0.8), (di * 0.8, 1.0), (di, 0.0)], n)
    buzz = svf(osc(ramp([(0.0, 92.0), (di, 108.0)], n, log=True), shape="saw", phase=0.5), 420.0, 0.8, "lp")
    fl = lfo(n, rng.uniform(28.0, 34.0), rng)
    breath = svf(white(n, rng), 650.0, 0.8, "bp")
    b.add([(bz * (0.5 + 0.5 * m) * 0.9 + br * 0.5) * e for bz, m, br, e in zip(buzz, fl, breath, env)])
    t = di + rng.uniform(0.08, 0.12)
    de = rng.uniform(0.52, 0.58)
    n = ns(de)
    env = ramp([(0.0, 0.0), (de * 0.25, 1.0), (de * 0.6, 0.7), (de, 0.0)], n)
    if v % 2 == 0:  # 'hhh' with a tiny sleepy whistle
        ex = [h * e * 0.45 for h, e in zip(svf(white(n, rng), 1300.0, 1.0, "bp"), env)]
        w = 1500.0 * j(rng)
        whistle = tone(ramp([(0.0, w), (de * 0.3, w * 1.1), (de, w * 0.87)], n, log=True), scaled(env, 0.22))
        ex = addsig(ex, whistle)
    else:           # soft 'pfff' lip puff
        hiss = svf(svf(white(n, rng), 1200.0, 0.7, "hp"), 4000.0, 0.707, "lp")
        lip = lfo(n, rng.uniform(16.0, 20.0), rng)
        ex = [h * e * 0.5 * (0.55 + 0.45 * m) for h, e, m in zip(hiss, env, lip)]
    b.add(ex, t)
    return svf(b.x, 4000.0, 0.707, "lp")


# ========================================================================= items & blocks

def rubber_squeak(rng, dur, fpts, vib_rate=30.0, vib_depth=0.7):
    """Rubber toy squeal: saw/sine blend with fast vibrato and a resonance on the 2nd harmonic."""
    n = ns(dur)
    f0 = vibrato(ramp(fpts, n, log=True), vib_rate, vib_depth, rng)
    amp = ramp([(0.0, 0.0), (0.012, 1.0), (dur * 0.7, 0.85), (dur, 0.0)], n)
    saw = osc(f0, shape="saw", phase=0.5)
    sine = osc(f0)
    src = [(0.6 * s + 0.4 * q) * a for s, q, a in zip(saw, sine, amp)]
    res = svf(src, [f * 2.0 for f in f0], 3.0, "bp")
    hiss = svf(white(n, rng), 3200.0, 1.0, "bp")
    out = [0.45 * s + 0.9 * r + 0.04 * h * a for s, r, h, a in zip(src, res, hiss, amp)]
    return svf(out, 5000.0, 0.707, "lp")


def squeaky_carrot(rng, v):
    b = Buf()
    if v % 3 == 0:  # squeeze + release, two tones
        f = 950.0 * j(rng)
        b.add(rubber_squeak(rng, 0.17, [(0.0, f), (0.08, f * 1.58), (0.17, f * 1.53)], rng.uniform(28, 34)))
        b.add(rubber_squeak(rng, 0.18, [(0.0, f * 1.37), (0.06, f * 1.32), (0.18, f * 1.05)],
                            rng.uniform(26, 32)), 0.2, 0.85)
    elif v % 3 == 1:  # one long squeeze
        f = 1100.0 * j(rng)
        b.add(rubber_squeak(rng, 0.32, [(0.0, f), (0.1, f * 1.45), (0.32, f * 1.23)], rng.uniform(24, 30), 0.8))
    else:  # two quick squeaks
        f = 1400.0 * j(rng)
        b.add(rubber_squeak(rng, 0.11, [(0.0, f), (0.05, f * 1.18), (0.11, f * 1.1)], rng.uniform(32, 36)))
        b.add(rubber_squeak(rng, 0.12, [(0.0, f * 0.96), (0.05, f * 1.1), (0.12, f * 1.03)],
                            rng.uniform(32, 36)), 0.16, 0.9)
    return b.x


JINGLE_PARTIALS = ((1.0, 1.0, 0.2), (1.49, 0.6, 0.15), (2.12, 0.45, 0.1), (2.63, 0.3, 0.075),
                   (3.31, 0.2, 0.055))  # (ratio, amplitude, decay)


def jingle_strike(rng, base, dur=0.3):
    """One small bell strike: detuned pairs of inharmonic partials (they beat gently)."""
    n = ns(dur)
    out = [0.0] * n
    sin = math.sin
    for ratio, a, tau in JINGLE_PARTIALS:
        for det in (1.0, 1.0035):
            f = base * ratio * det * j(rng, 0.005)
            if f > 11000.0:
                continue
            w = TAU * f / SR
            ph = rng.random() * TAU
            e = 0.5 * a * rng.uniform(0.7, 1.0)
            k = math.exp(-1.0 / (tau * SR))
            for i in range(n):
                out[i] += e * sin(w * i + ph)
                e *= k
    m = ns(0.002)
    click = svf(pad(mul(white(m, rng), env_perc(m, 0.0002, 0.0006)), 0.003), 7000.0, 1.5, "bp")
    out = addsig(out, click, 0.12)
    na = ns(0.001)
    for i in range(na):
        out[i] *= i / na
    return taper(out, 0.3)


def collar_jingle(rng, v):
    b = Buf()
    if v % 2 == 0:
        times = (0.0, 0.06, 0.13, 0.2, 0.31, 0.44)
        bells = (3150.0 * j(rng, 0.02), 3550.0 * j(rng, 0.02))
    else:
        times = (0.0, 0.045, 0.09, 0.17, 0.23, 0.36, 0.5)
        bells = (2900.0 * j(rng, 0.02), 3400.0 * j(rng, 0.02), 3900.0 * j(rng, 0.02))
    for k, t in enumerate(times):
        base = bells[k % len(bells)] if v % 2 == 0 else rng.choice(bells)
        g = (1.0 - 0.55 * k / len(times)) * rng.uniform(0.75, 1.0)
        b.add(jingle_strike(rng, base), t + (rng.uniform(-0.008, 0.008) if k else 0.0), g)
    return reverb(svf(b.x, 9000.0, 0.707, "lp"), 0.12, tail=0.15)


def carrier_capture(rng, v):
    b = Buf()
    b.add(rustle(rng, 0.3, 2600.0 * j(rng)), 0.0, 0.5)
    b.add(pop(rng, 0.12, 260.0 * j(rng), 820.0 * j(rng), 0.045), 0.15)
    b.add(pop(rng, 0.08, 520.0 * j(rng), 1300.0 * j(rng), 0.025), 0.23, 0.3)
    return b.x


def carrier_release(rng, v):
    b = Buf()
    b.add(pop(rng, 0.14, 820.0 * j(rng), 250.0 * j(rng), 0.05), 0.0)
    b.add(rustle(rng, 0.3, 2400.0 * j(rng)), 0.06, 0.45)
    return b.x


BOWL_MODES = ((1.0, 0.35, 0.06), (2.32, 0.22, 0.04), (3.88, 0.12, 0.025))  # (ratio, amp, decay)


def kibble_tick(rng, base, g):
    """A tiny clicky kibble tick that sets the ceramic bowl ringing."""
    n = ns(0.12)
    out = [0.0] * n
    m = ns(0.0025)
    click = svf(pad(mul(white(m, rng), env_perc(m, 0.0003, 0.0007)), 0.004), rng.uniform(3000.0, 6000.0),
                2.0, "bp")
    for i, x in enumerate(click):
        out[i] += x
    sin = math.sin
    for ratio, a, tau in BOWL_MODES:
        w = TAU * base * ratio * j(rng, 0.01) / SR
        e = a * rng.uniform(0.4, 1.0)
        k = math.exp(-1.0 / (tau * SR))
        for i in range(n):
            out[i] += e * sin(w * i)
            e *= k
    return scaled(taper(out, 0.25), g)


def bowl_fill(rng, v):
    count = 15 if v % 2 == 0 else 19
    base = rng.uniform(1900.0, 2150.0) if v % 2 == 0 else rng.uniform(2250.0, 2500.0)
    span = 0.6
    times = sorted(span * rng.betavariate(1.6, 2.4) for _ in range(count))
    for k in range(1, count):  # keep ticks at least 8 ms apart
        times[k] = max(times[k], times[k - 1] + 0.008)
    b = Buf()
    for t in times:
        b.add(kibble_tick(rng, base, rng.uniform(0.5, 1.0) * (1.0 - 0.4 * min(1.0, t / span))), t)
    n = ns(span + 0.1)
    hiss = mul(svf(white(n, rng), 3500.0, 0.8, "bp"),
               ramp([(0.0, 0.0), (0.15, 1.0), (span, 0.3), (span + 0.1, 0.0)], n))
    b.add(hiss, 0.0, 0.05)
    return svf(b.x, 9000.0, 0.707, "lp")


# =============================================================================== registry

GENERATORS = {
    "entity.bunny.ambient": bunny_ambient,
    "entity.bunny.hurt": bunny_hurt,
    "entity.bunny.death": bunny_death,
    "entity.bunny.happy": bunny_happy,
    "entity.blossom_fox.ambient": fox_ambient,
    "entity.blossom_fox.hurt": fox_hurt,
    "entity.blossom_fox.death": fox_death,
    "entity.blossom_fox.happy": fox_happy,
    "entity.cloud_kitty.ambient": kitty_ambient,
    "entity.cloud_kitty.hurt": kitty_hurt,
    "entity.cloud_kitty.death": kitty_death,
    "entity.cloud_kitty.purr": kitty_purr,
    "entity.strawberry_mouse.ambient": mouse_ambient,
    "entity.strawberry_mouse.hurt": mouse_hurt,
    "entity.strawberry_mouse.death": mouse_death,
    "entity.honey_bear.ambient": bear_ambient,
    "entity.honey_bear.hurt": bear_hurt,
    "entity.honey_bear.death": bear_death,
    "entity.honey_bear.happy": bear_happy,
    "entity.moon_deer.ambient": deer_ambient,
    "entity.moon_deer.hurt": deer_hurt,
    "entity.moon_deer.death": deer_death,
    "entity.pastel_axolotl.ambient": axolotl_ambient,
    "entity.pastel_axolotl.hurt": axolotl_hurt,
    "entity.pastel_axolotl.death": axolotl_death,
    "entity.tiny_swan.ambient": swan_ambient,
    "entity.tiny_swan.hurt": swan_hurt,
    "entity.tiny_swan.death": swan_death,
    "entity.rainbow_butterfly.ambient": butterfly_ambient,
    "entity.rainbow_butterfly.hurt": butterfly_hurt,
    "entity.rainbow_butterfly.death": butterfly_death,
    "entity.cherry_blossom_bird.ambient": bird_ambient,
    "entity.cherry_blossom_bird.hurt": bird_hurt,
    "entity.cherry_blossom_bird.death": bird_death,
    "entity.cherry_blossom_bird.sing": bird_sing,
    "entity.dreamy_hamster.ambient": hamster_ambient,
    "entity.dreamy_hamster.hurt": hamster_hurt,
    "entity.dreamy_hamster.death": hamster_death,
    "entity.pet.happy": pet_happy,
    "entity.pet.eat": pet_eat,
    "entity.pet.snore": pet_snore,
    "item.squeaky_carrot.squeak": squeaky_carrot,
    "item.pet_collar.jingle": collar_jingle,
    "item.pet_carrier.capture": carrier_capture,
    "item.pet_carrier.release": carrier_release,
    "block.feeding_bowl.fill": bowl_fill,
}


# ================================================================================ output

def finalize(x, peak_db, limits):
    """DC-block, trim silence, enforce the duration limit, fade the edges, normalise the peak."""
    x = dc_block(x)
    peak = max(abs(s) for s in x)
    if not peak > 0.0 or math.isnan(peak):
        raise ValueError("silent or invalid signal")
    thr = peak * 10 ** (-66.0 / 20.0)
    n = len(x)
    first = next(i for i, s in enumerate(x) if abs(s) > thr)
    last = n - 1 - next(i for i, s in enumerate(reversed(x)) if abs(s) > thr)
    x = x[max(0, first - ns(0.002)):min(n, last + ns(0.01))]
    truncated = len(x) > int(limits[1] * SR)
    if truncated:
        x = x[:int(limits[1] * SR)]
    n = len(x)
    na = min(ns(0.003), n // 4)
    nr = min(ns(0.08 if truncated else 0.03), n // 4)
    for i in range(na):
        x[i] *= 0.5 - 0.5 * math.cos(math.pi * i / na)
    for i in range(nr):
        x[n - 1 - i] *= 0.5 - 0.5 * math.cos(math.pi * i / nr)
    g = 10 ** (peak_db / 20.0) / max(abs(s) for s in x)
    x = [s * g for s in x]
    over = loudness_db(x) - LOUDNESS_CEILING_DB
    if over > 0.0:
        x = scaled(x, 10 ** (-min(over, MAX_CEILING_CUT_DB) / 20.0))
    return x, truncated


def loudness_db(x):
    """Rough K-weighted loudness (dB): +4 dB high shelf above ~1.5 kHz, low-cut at 60 Hz,
    mean square over the active 50 ms blocks (blocks within 40 dB of the loudest)."""
    hp = svf(x, 1500.0, 0.707, "hp")
    y = svf([a + 0.585 * b for a, b in zip(x, hp)], 60.0, 0.5, "hp")
    blk = ns(0.05)
    ms = [sum(v * v for v in y[i:i + blk]) / blk for i in range(0, max(1, len(y) - blk + 1), blk)]
    top = max(ms)
    active = [m for m in ms if m > top * 1e-4]
    return 10.0 * math.log10(max(1e-12, sum(active) / len(active)))


def write_wav(path, x):
    pcm = array("h", (max(-32767, min(32767, int(round(s * 32767.0)))) for s in x))
    if sys.byteorder == "big":
        pcm.byteswap()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def encode(ffmpeg, wav, ogg):
    # bitexact flags keep the Ogg serial number / encoder tag stable -> byte-identical reruns
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-c:a", "libvorbis",
           "-q:a", "4", "-fflags", "+bitexact", "-flags:a", "+bitexact", str(ogg)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not ogg.is_file() or ogg.stat().st_size == 0:
        raise RuntimeError(f"ffmpeg failed for {ogg.name}: {r.stderr.strip()}")
    return ogg.stat().st_size


def main():
    started = time.perf_counter()
    events = load_events()
    missing = [e for e in events if e not in GENERATORS]
    if missing:
        sys.exit("No synthesiser for sound event(s): " + ", ".join(missing))
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg not found on PATH")

    if SOUNDS_DIR.exists():
        shutil.rmtree(SOUNDS_DIR)
    SOUNDS_DIR.mkdir(parents=True)

    results = []   # (event, file name, duration, future)
    warnings = []
    with tempfile.TemporaryDirectory(prefix="bunnyland_sounds_") as tmp, \
            ThreadPoolExecutor(max_workers=4) as pool:
        for event, (_subtitle, count, _brief) in events.items():
            rel = event.replace(".", "/")
            kind = event.rsplit(".", 1)[-1]
            limits = DURATION_LIMITS.get(kind, DEFAULT_LIMITS)
            peak_db = QUIET_PEAK_DB if event.startswith(QUIET_EVENTS) else PEAK_DB
            for v in range(count):
                rng = random.Random(f"{NAMESPACE}:{event}#{v + 1}")
                x, truncated = finalize(GENERATORS[event](rng, v), peak_db, limits)
                dur = len(x) / SR
                if truncated:
                    warnings.append(f"{rel}{v + 1}: trimmed to {limits[1]:.2f}s")
                if dur < limits[0]:
                    warnings.append(f"{rel}{v + 1}: only {dur:.2f}s long")
                wav = Path(tmp) / f"{rel.replace('/', '_')}{v + 1}.wav"
                ogg = SOUNDS_DIR / f"{rel}{v + 1}.ogg"
                ogg.parent.mkdir(parents=True, exist_ok=True)
                write_wav(wav, x)
                results.append((event, ogg, dur, pool.submit(encode, ffmpeg, wav, ogg)))
        sizes = {ogg: fut.result() for _e, ogg, _d, fut in results}

    data = {}
    for event, (_subtitle, count, _brief) in events.items():
        rel = event.replace(".", "/")
        data[event] = {
            "subtitle": f"subtitles.{NAMESPACE}.{event}",
            "sounds": [f"{NAMESPACE}:{rel}{i}" for i in range(1, count + 1)],
        }
    SOUNDS_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")

    current = None
    for event, ogg, dur, _fut in results:
        if event != current:
            current = event
            print(event)
        print(f"    {ogg.relative_to(SOUNDS_DIR).as_posix():<44} {dur:5.2f}s {sizes[ogg] / 1024:6.1f} KB")
    for w in warnings:
        print("warning:", w)
    total = sum(sizes.values())
    print(f"{len(sizes)} sounds for {len(events)} events, {total / 1024:.0f} KB total, "
          f"{time.perf_counter() - started:.1f}s")


if __name__ == "__main__":
    main()

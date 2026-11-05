"""Helpers for staging the listing screenshots: ground heights, frozen creatures, camera placement."""
from __future__ import annotations

import math
import time
from pathlib import Path

from session import PLAYER, Session

OUT = Path(__file__).resolve().parents[1] / 'images' / 'screenshots'
s: Session = None  # set by connect()


def connect():
    global s
    s = Session()
    return s


def c(*commands):
    return s.cmd(*commands)


def ground(x, z, top):
    """The y a creature standing at x z would have: an invisible armor stand dropped from `top` falls through grass,
    flowers and petals and lands on the first solid block."""
    c(f'summon minecraft:armor_stand {x} {top} {z} {{Invisible:1b,Tags:["probe"]}}')
    time.sleep(1.2)
    out = c('data get entity @e[tag=probe,limit=1] Pos')
    c('kill @e[tag=probe]')
    return float(out.split('[')[1].split(',')[1].strip().rstrip('d'))


def grounds(points, top):
    """ground() for many (x, z) points at once."""
    for i, (x, z) in enumerate(points):
        c(f'summon minecraft:armor_stand {x} {top} {z} {{Invisible:1b,Tags:["probe","p{i}"]}}')
    time.sleep(1.5)
    ys = []
    for i in range(len(points)):
        out = c(f'data get entity @e[tag=p{i},limit=1] Pos')
        ys.append(float(out.split('[')[1].split(',')[1].strip().rstrip('d')))
    c('kill @e[tag=probe]')
    return ys


def heightmap(px, pz, yaw, top, forward=range(1, 11), right=range(-6, 7)):
    """Prints the ground heights in front of a camera at (px, pz) facing yaw: rows are blocks ahead, columns blocks to
    the right. Used to pick flat spots."""
    pts = [ahead(px, pz, yaw, f, r) for f in forward for r in right]
    ys = grounds(pts, top)
    grid = {}
    i = 0
    for f in forward:
        row = []
        for r in right:
            grid[(f, r)] = ys[i]
            row.append(f'{int(ys[i]) % 100:3d}')
            i += 1
        print(f'{f:3d} |' + ''.join(row))
    print('     ' + ''.join(f'{r:3d}' for r in right))
    return grid


def top(x, z):
    """The y on top of the highest block at x z, plants included (for placing the camera roughly)."""
    c(f'summon minecraft:marker {x} 320 {z} {{Tags:["probe"]}}')
    c(f'spreadplayers {x} {z} 0 1 false @e[tag=probe,limit=1]')
    out = c('data get entity @e[tag=probe,limit=1] Pos')
    c('kill @e[tag=probe]')
    return float(out.split('[')[1].split(',')[1].strip().rstrip('d'))


PLANTS = ('minecraft:grass', 'minecraft:tall_grass', 'minecraft:fern', 'minecraft:large_fern')


def mow(x1, y1, z1, x2, y2, z2, plants=PLANTS):
    """Clears grass (not flowers or petals) from a box, so it does not hide the creatures."""
    for p in plants:
        c(f'fill {math.floor(x1)} {math.floor(y1)} {math.floor(z1)} {math.floor(x2)} {math.floor(y2)} {math.floor(z2)} minecraft:air replace {p}')


def camera(x, y, z, yaw=0.0, pitch=0.0, facing=None):
    """A spectator camera with its eye exactly at x y z."""
    return s.tp(x, y - 1.62, z, yaw=yaw, pitch=pitch,
                facing=(facing[0], facing[1], facing[2]) if facing else None)


def ahead(px, pz, yaw, forward, right=0.0):
    """The point `forward` blocks ahead of (px, pz) when facing yaw, and `right` blocks to its right."""
    rad = math.radians(yaw)
    fx, fz = -math.sin(rad), math.cos(rad)
    rx, rz = -fz, fx
    return round(px + fx * forward + rx * right, 2), round(pz + fz * forward + rz * right, 2)


def creature(kind, x, y, z, yaw=0.0, nbt='', tag='shot'):
    """A Bunnyland creature that holds still (NoAI), facing yaw."""
    extra = (',' + nbt) if nbt else ''
    c(f'summon bunnyland:{kind} {x} {y} {z} {{NoAI:1b,PersistenceRequired:1b,Rotation:[{yaw}f,0f],Tags:["{tag}"]{extra}}}')


def clear():
    c('kill @e[type=!minecraft:player,type=!minecraft:armor_stand]', 'kill @e[type=minecraft:armor_stand]')
    time.sleep(0.3)
    c('kill @e[type=minecraft:item]', 'kill @e[type=minecraft:experience_orb]')


def save(name, quality=90):
    """Captures the screen as a JPEG in screenshots/."""
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f'.{name}.png'
    s.shot(png)
    Image.open(png).convert('RGB').save(OUT / f'{name}.jpg', quality=quality, optimize=True)
    png.unlink()
    print('captured', name)
    return OUT / f'{name}.jpg'


def keep(png, name, quality=90):
    """Saves a scratch capture (a burst frame) as screenshots/<name>.jpg."""
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    Image.open(png).convert('RGB').save(OUT / f'{name}.jpg', quality=quality, optimize=True)
    print('kept', name)


def burst(name, count=4, gap=0.5):
    """A few frames in a row (wings and blinks move), as /tmp/bunnyland-shots/<name>-<i>.png."""
    frames = []
    for i in range(count):
        frames.append(peek(f'{name}-{i}'))
        time.sleep(gap)
    return frames


def peek(name='peek'):
    """A scratch capture for checking a framing."""
    return s.shot(Path('/tmp/bunnyland-shots') / f'{name}.png')


def setup():
    for rule in ('doMobSpawning false', 'doDaylightCycle false', 'doWeatherCycle false', 'showDeathMessages false',
                 'sendCommandFeedback false', 'announceAdvancements false', 'doFireTick false', 'randomTickSpeed 0'):
        c(f'gamerule {rule}')
    c('weather clear', 'difficulty peaceful', f'gamemode creative {PLAYER}')


def lineup(mobs, px, pz, yaw, g, forward=3.5, spacing=1.2, turn=6.0):
    """Creatures in a row across the view of a camera at (px, pz) facing yaw, on flat ground at height g, all facing
    the camera. mobs: (kind, nbt) pairs, left to right."""
    n = len(mobs)
    for i, (kind, nbt) in enumerate(mobs):
        r = (i - (n - 1) / 2) * spacing
        x, z = ahead(px, pz, yaw, forward, r)
        creature(kind, x, g, z, yaw=yaw + 180 + r * turn, nbt=nbt)

# The offline-mode UUID of "Sugarplum" as an NBT int array, for pets the player owns.
OWNER = 'Owner:[I;-1707750500,64241069,-1360204317,24406500]'

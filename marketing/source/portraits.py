"""One portrait per creature on the same patch of the cherry grove, for the "meet the creatures" card."""
import sys
import time
from stage import *

SPECIES = ['cotton_bunny', 'strawberry_bunny', 'moon_bunny', 'lavender_bunny', 'snowball_bunny', 'blossom_fox', 'cloud_kitty',
           'strawberry_mouse', 'honey_bear', 'moon_deer', 'pastel_axolotl', 'tiny_swan', 'rainbow_butterfly',
           'cherry_blossom_bird', 'dreamy_hamster']
# camera distance, eye height above the ground, aim height
SIZE = {'moon_deer': (2.7, 1.15, 0.95), 'honey_bear': (2.05, 0.85, 0.62), 'rainbow_butterfly': (0.75, 1.55, 0.42),
        'strawberry_mouse': (1.05, 0.36, 0.16), 'cherry_blossom_bird': (1.15, 0.45, 0.26), 'dreamy_hamster': (1.15, 0.44, 0.24),
        'pastel_axolotl': (1.3, 0.48, 0.18), 'tiny_swan': (1.6, 0.68, 0.45), 'cloud_kitty': (1.55, 0.62, 0.45),
        'blossom_fox': (1.65, 0.62, 0.45)}
GRID = (-80.7, -1061.3, 112.0)  # a flat, petal-covered patch in the grove, looking north at the big cherry tree


def portrait(i, sp, yaw=180.0):
    px, pz, g = GRID
    d, h, a = SIZE.get(sp, (1.5, 0.58, 0.46))
    c('kill @e[tag=shot]')
    time.sleep(0.3)
    c('kill @e[type=minecraft:item]')
    if sp == 'rainbow_butterfly':
        c(f'summon bunnyland:{sp} {px} {g + 0.42} {pz} {{NoAI:1b,NoGravity:1b,PersistenceRequired:1b,Rotation:[{yaw+180}f,0f],Tags:["shot"]}}')
    else:
        creature(sp, px, g, pz, yaw=yaw + 180 + 28)
    cam = ahead(px, pz, yaw, -d)
    camera(cam[0], g + h, cam[1], facing=(px, g + a, pz))
    time.sleep(4.5)
    return burst(f'p{i:02d}-{sp}', 3, 0.5)


if __name__ == '__main__':
    connect()
    c('kill @e[type=!minecraft:player]')
    wanted = sys.argv[1:] or SPECIES
    for i, sp in enumerate(SPECIES):
        if sp in wanted:
            portrait(i, sp)

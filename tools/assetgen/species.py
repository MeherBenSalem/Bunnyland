"""Species order and animation rigs. The order here is the Species enum order in Java."""

SPECIES = [
    # id, rig, rig params
    ("cotton_bunny", "bunny", {}),
    ("strawberry_bunny", "bunny", {"extra": ("calyx",)}),
    ("moon_bunny", "bunny", {"extra": ("moon",)}),
    ("lavender_bunny", "bunny", {"lop": True, "extra": ("sprig",)}),
    ("snowball_bunny", "bunny", {}),
    ("blossom_fox", "quad", {"kind": "blossom_fox", "walk": 0.7, "swing": 34, "leg_h": 5.0}),
    ("cloud_kitty", "quad", {"kind": "cloud_kitty", "walk": 0.75, "swing": 32, "leg_h": 4.2}),
    ("strawberry_mouse", "quad", {"kind": "strawberry_mouse", "walk": 0.36, "swing": 40, "leg_h": 1.1}),
    ("honey_bear", "quad", {"kind": "honey_bear", "walk": 1.0, "swing": 26, "leg_h": 4.2}),
    ("moon_deer", "quad", {"kind": "moon_deer", "walk": 0.95, "swing": 28, "leg_h": 10.4}),
    ("pastel_axolotl", "axolotl", {}),
    ("tiny_swan", "swan", {}),
    ("rainbow_butterfly", "butterfly", {}),
    ("cherry_blossom_bird", "bird", {}),
    ("dreamy_hamster", "quad", {"kind": "dreamy_hamster", "walk": 0.4, "swing": 40, "leg_h": 0.9}),
]

IDS = [s[0] for s in SPECIES]

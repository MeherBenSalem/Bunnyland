"""Colour variants for every creature. The first COMMON variant is the default.
Rare variants only appear through breeding (see Species.java / the rareOffspringChance config).

Order matters: the variant index stored on the entity is the position in COMMON + RARE.
"""
from .core import C, darken, lighten, mix
from .rig import ACCESSORY_PALETTE

BASE = {
    "pupil": "#2A2140", "mouth": "#B45C7C", "blush": "#FF9AB4", "whisker": "#FFFFFF",
    "inner": "#FFC4D6", "nose": "#FF8DAA", "pad": "#FFB0C4", "eye": "#7C6BD6",
    "gold": "#F5C542", "star": "#FFF3B0", "glitter": "#FFF6C9", "dark": "#5A4320",
    "beeyellow": "#FFD54A", "beestripe": "#3A2A2E", "beewing": "#F2FAFF",
}


def _fill(p):
    """Derive the optional palette keys from the main fur colour."""
    fur = C(p["fur"])
    p.setdefault("fur2", darken(fur, 0.18))
    p.setdefault("fur3", lighten(fur, 0.25))
    p.setdefault("belly", lighten(fur, 0.6))
    p.setdefault("muzzle", p["belly"])
    p.setdefault("fluff", lighten(fur, 0.5))
    p.setdefault("sock", p["fur2"])
    return p


VARIANTS = {
    # ------------------------------------------------------------------ bunnies
    "cotton_bunny": {
        "common": {
            "classic": {"fur": "#FFF9F5", "fluff": "#FFFFFF", "muzzle": "#FFF1EF", "belly": "#FFFFFF", "eye": "#7C6BD6"},
            "cocoa": {"fur": "#CFA383", "fluff": "#F7E8DB", "muzzle": "#F1DCC9", "belly": "#F4E4D6", "nose": "#D97A92", "eye": "#5A3A2A"},
            "cream": {"fur": "#FBE6B4", "fluff": "#FFF8E3", "muzzle": "#FFF4DC", "belly": "#FFF8E8", "eye": "#9A6E3C"},
        },
        "rare": {
            "sugar_star": {"fur": "#FFF2FA", "fluff": "#FFFFFF", "muzzle": "#FFF7FB", "glitter": "#FFD86B", "eye": "#B57CFF"},
            "cotton_candy": {"fur": "#FFC6E3", "fluff": "#BDE7FF", "muzzle": "#FFE6F3", "belly": "#FFE6F3", "eye": "#5FA8E8",
                             "glitter": "#FFFFFF"},
        },
    },
    "strawberry_bunny": {
        "common": {
            "classic": {"fur": "#FF8FA4", "belly": "#FFF1F0", "muzzle": "#FFF1F0", "fluff": "#FFFFFF", "inner": "#FFD6DE",
                        "nose": "#E94F6E", "seed": "#FFE58C", "leaf": "#79C76F", "stem": "#5C9E52", "berry": "#FF6F88",
                        "eye": "#6B3D2E"},
            "pineberry": {"fur": "#FFF6F3", "belly": "#FFFFFF", "muzzle": "#FFFFFF", "fluff": "#FFFFFF", "inner": "#FFC9D6",
                          "nose": "#FF8DAA", "seed": "#FF6F8D", "leaf": "#79C76F", "stem": "#5C9E52", "berry": "#FFF0EE",
                          "eye": "#E0587A"},
            "chocolate_dipped": {"fur": "#FFA2B4", "fur2": "#80503D", "belly": "#FFF1F0", "muzzle": "#FFF1F0", "fluff": "#FFFFFF",
                                 "nose": "#E94F6E", "seed": "#FFEAB0", "leaf": "#79C76F", "stem": "#5C9E52", "berry": "#7A4A38",
                                 "eye": "#4A2C22"},
        },
        "rare": {
            "golden_berry": {"fur": "#FFD36B", "belly": "#FFF7DC", "muzzle": "#FFF7DC", "fluff": "#FFFDF2", "nose": "#F08A5D",
                             "seed": "#FFFBE0", "leaf": "#8EDC7A", "stem": "#6DB05E", "berry": "#FFC24A", "eye": "#C57A1E",
                             "glitter": "#FFFFFF"},
        },
    },
    "moon_bunny": {
        "common": {
            "midnight": {"fur": "#5E5CAB", "fur2": "#8F8CD8", "fluff": "#C9C7F5", "muzzle": "#B4B1EB", "belly": "#9E9BE3",
                         "inner": "#E2C8FF", "nose": "#FFB3D9", "moon": "#FFF0A6", "star": "#FFF6C9", "eye": "#FFD86B",
                         "pupil": "#231C3A"},
            "dusk": {"fur": "#D79DCA", "fluff": "#F7DFF1", "muzzle": "#F7E4F2", "inner": "#FFD9EC", "moon": "#FFD27A",
                     "star": "#FFE8B0", "eye": "#7D4FA8"},
            "silver": {"fur": "#C9D3E6", "fluff": "#F1F5FF", "muzzle": "#EEF2FA", "moon": "#BFE6FF", "star": "#E6F6FF",
                       "eye": "#5A6FB5"},
        },
        "rare": {
            "eclipse": {"fur": "#2E2839", "fur2": "#4B4260", "fluff": "#4E4565", "muzzle": "#5A5070", "belly": "#433A58",
                        "inner": "#7A5D86", "nose": "#FF8C7A", "moon": "#FF7A59", "star": "#FFB067", "eye": "#FF6F61",
                        "pupil": "#120E18"},
            "starlight": {"fur": "#2F3B8E", "fur2": "#4A57B8", "fluff": "#6E7FE0", "muzzle": "#5B6AD0", "belly": "#4E5DC2",
                          "inner": "#B9C4FF", "moon": "#E8F3FF", "star": "#FFFFFF", "eye": "#9FE6FF", "pupil": "#151A40"},
        },
    },
    "lavender_bunny": {
        "common": {
            "lavender": {"fur": "#C9B6F0", "fluff": "#EFE7FF", "muzzle": "#F2ECFF", "inner": "#FFD3EA", "nose": "#F59AC6",
                         "petal": "#9B7FE0", "stem": "#77B06A", "leaf": "#86C479", "eye": "#6A4BB3"},
            "lilac": {"fur": "#E8B9E9", "fluff": "#FBEAFB", "muzzle": "#FDF0FD", "petal": "#C27CD8", "stem": "#77B06A",
                      "leaf": "#86C479", "eye": "#9B4FA5"},
            "periwinkle": {"fur": "#AAB7F2", "fluff": "#E6EBFF", "muzzle": "#EEF1FF", "petal": "#7E86E8", "stem": "#77B06A",
                           "leaf": "#86C479", "eye": "#4559B8"},
        },
        "rare": {
            "wisteria": {"fur": "#B89DF0", "fur3": "#86AEF2", "fluff": "#F0E8FF", "muzzle": "#F4EEFF", "petal": "#E9C9FF",
                         "sprig_glow": "#E7C8FF", "stem": "#77B06A", "leaf": "#86C479", "eye": "#D5A6FF", "glitter": "#FFFFFF"},
        },
    },
    "snowball_bunny": {
        "common": {
            "snow": {"fur": "#FFFFFF", "fluff": "#F3F9FF", "muzzle": "#FFFFFF", "belly": "#FFFFFF", "inner": "#FFD6E2",
                     "nose": "#FFA3B8", "eye": "#7FB8F0", "flake": "#D6ECFF", "blush": "#FF9DB6"},
            "frost": {"fur": "#E3F1FF", "fluff": "#F7FBFF", "muzzle": "#F4F9FF", "belly": "#F7FBFF", "eye": "#5C8FD6",
                      "flake": "#FFFFFF"},
            "peppermint": {"fur": "#FFFFFF", "fur2": "#FF7C8E", "fluff": "#FFF5F6", "muzzle": "#FFFFFF", "belly": "#FFFFFF",
                           "eye": "#E05469", "flake": "#FFD6DC"},
        },
        "rare": {
            "aurora": {"fur": "#F0FFFB", "fluff": "#F8FFFD", "muzzle": "#FFFFFF", "belly": "#FFFFFF", "eye": "#6FE3C5",
                       "flake": "#C9FFF0", "aurora1": "#9CFFD9", "aurora2": "#FFB3F0"},
        },
    },
    # ------------------------------------------------------------------ others
    "blossom_fox": {
        "common": {
            "sakura": {"fur": "#FFB4CA", "fur2": "#FFFFFF", "belly": "#FFF5F8", "sock": "#EA8CA8", "inner": "#FFE1EB",
                       "nose": "#8A3D5C", "petal": "#FFC7DA", "eye": "#C04E7A"},
            "peach": {"fur": "#FFC59C", "fur2": "#FFFFFF", "belly": "#FFF6EC", "sock": "#E59A6E", "inner": "#FFE3D2",
                      "nose": "#7A3D2A", "petal": "#FFD9C2", "eye": "#A0522D"},
            "snow_blossom": {"fur": "#FFFFFF", "fur2": "#FFB4CA", "belly": "#FFF8FA", "sock": "#FFC2D5", "inner": "#FFD6E3",
                             "nose": "#C76A8C", "petal": "#FFB4CA", "eye": "#E06C93"},
        },
        "rare": {
            "twilight_blossom": {"fur": "#9C8BE1", "fur2": "#FFD6F4", "belly": "#E6DFFF", "sock": "#6E5FBF", "inner": "#E8D9FF",
                                 "nose": "#3B2E6B", "petal": "#FFC2F2", "eye": "#FFD86B", "glitter": "#FFE6FA"},
            "golden_hour": {"fur": "#FFD36E", "fur2": "#FFF8E6", "belly": "#FFF6DA", "sock": "#E8A63E", "inner": "#FFEBC2",
                            "nose": "#7A4A12", "petal": "#FFF0A6", "eye": "#D2691E", "glitter": "#FFFFFF"},
        },
    },
    "cloud_kitty": {
        "common": {
            "sky": {"fur": "#FFFFFF", "fur2": "#C4E5FF", "cloud": "#F5FBFF", "belly": "#FFFFFF", "inner": "#FFD0DD",
                    "nose": "#FFA0B8", "eye": "#6EB6FF"},
            "sunset": {"fur": "#FFE1C9", "fur2": "#FFB5A2", "cloud": "#FFF1E8", "belly": "#FFF6EE", "eye": "#FF8C69"},
            "lilac_mist": {"fur": "#EEE6FF", "fur2": "#CBB9F6", "cloud": "#FBF8FF", "belly": "#FFFFFF", "eye": "#9B7FE0"},
        },
        "rare": {
            "storm": {"fur": "#8F96A9", "fur2": "#6D748A", "cloud": "#BAC0CE", "belly": "#C3C8D4", "inner": "#C9B6C6",
                      "nose": "#E0A2B6", "spark": "#FFE45C", "eye": "#FFE45C", "glitter": "#FFF3A6"},
            "rainbow": {"fur": "#FFFFFF", "fur2": "#FFD6EC", "cloud": "#FFFFFF", "belly": "#FFFFFF", "eye": "#FF8FD8",
                        "glitter": "#FFFFFF"},
        },
    },
    "strawberry_mouse": {
        "common": {
            "classic": {"fur": "#FFD7DF", "belly": "#FFF4F6", "inner": "#FFB3C3", "nose": "#FF7A99", "berry": "#FF5C7A",
                        "seed": "#FFE58A", "leaf": "#76C26C", "stem": "#5C9E52", "tailskin": "#FFC2CD", "eye": "#3A2A3A"},
            "white_chocolate": {"fur": "#FFF7EE", "belly": "#FFFFFF", "inner": "#FFC9D1", "nose": "#FF8FA8", "berry": "#FFF3F3",
                                "seed": "#FF7A99", "leaf": "#76C26C", "stem": "#5C9E52", "tailskin": "#FFE2E6", "eye": "#5A3A2A"},
            "blueberry": {"fur": "#E2E6FF", "belly": "#F7F8FF", "inner": "#C9D1FF", "nose": "#8E9BF2", "berry": "#7D8CF0",
                          "seed": "#C9D1FF", "leaf": "#76C26C", "stem": "#5C9E52", "tailskin": "#D3D8FF", "eye": "#2E3270"},
        },
        "rare": {
            "golden_berry": {"fur": "#FFF1C2", "belly": "#FFFBEA", "inner": "#FFD9A0", "nose": "#F2A65A", "berry": "#FFC93C",
                             "seed": "#FFF8D6", "leaf": "#8EDC7A", "stem": "#6DB05E", "tailskin": "#FFE7A8", "eye": "#8A5A12"},
        },
    },
    "honey_bear": {
        "common": {
            "honey": {"fur": "#F2B45B", "belly": "#FFE3B0", "muzzle": "#FFEBC4", "inner": "#FFD08A", "nose": "#6B4226",
                      "honey": "#FFC93C", "eye": "#5A3A1A", "pad": "#E59B5A", "mouth": "#6B4226"},
            "cinnamon": {"fur": "#C77E4F", "belly": "#F2C9A0", "muzzle": "#F6D9B8", "inner": "#F2B27E", "nose": "#3E2414",
                         "honey": "#FFB830", "eye": "#3E2414", "pad": "#A85E36", "mouth": "#3E2414"},
            "vanilla": {"fur": "#FFF1D6", "belly": "#FFFFFF", "muzzle": "#FFFFFF", "inner": "#FFDDC4", "nose": "#8A5A3A",
                        "honey": "#FFD86B", "eye": "#7A5230", "pad": "#F2C9A0", "mouth": "#8A5A3A"},
        },
        "rare": {
            "royal_jelly": {"fur": "#FFFCF2", "belly": "#FFF6D2", "muzzle": "#FFF8E0", "inner": "#FFE8A8", "nose": "#B57A2A",
                            "honey": "#FFE27A", "eye": "#C08A1E", "pad": "#FFE0A0", "mouth": "#B57A2A", "glitter": "#FFD54A"},
            "midnight_honey": {"fur": "#3F3651", "belly": "#6C5E86", "muzzle": "#7A6C96", "inner": "#8A7AA8", "nose": "#1E1828",
                               "honey": "#FFB84D", "eye": "#FFC857", "pad": "#5A4C72", "mouth": "#1E1828", "glitter": "#FFD580",
                               "pupil": "#120E18"},
        },
    },
    "moon_deer": {
        "common": {
            "midnight": {"fur": "#6B6DB8", "belly": "#B9B6EE", "fur2": "#E8E6FF", "muzzle": "#C9C6F2", "antler": "#CFEAFF",
                         "antler_glow": "#AEE2FF", "hoof": "#3B3566", "inner": "#FFD1EC", "nose": "#3B3566", "star": "#FFF6C9",
                         "eye": "#FFE07A", "pupil": "#211A3A"},
            "dawn": {"fur": "#F2B9C7", "belly": "#FFE9EF", "fur2": "#FFFFFF", "muzzle": "#FFF0F4", "antler": "#FFE9A8",
                     "antler_glow": "#FFE08A", "hoof": "#B5677E", "nose": "#8A4A62", "star": "#FFFFFF", "eye": "#8A4A9C"},
            "frost": {"fur": "#E6EEF8", "belly": "#FFFFFF", "fur2": "#C9DDF5", "muzzle": "#FFFFFF", "antler": "#BDEBFF",
                      "antler_glow": "#9FDFFF", "hoof": "#7E8FB0", "nose": "#5C6C90", "star": "#FFFFFF", "eye": "#5C8FD6"},
        },
        "rare": {
            "aurora": {"fur": "#4FA3A6", "belly": "#A8E6DA", "fur2": "#B5FFE9", "muzzle": "#C2F2E8", "antler": "#FFD6FA",
                       "antler_glow": "#FFB3F7", "hoof": "#2C5A5C", "nose": "#1E4446", "star": "#E8FFFA", "eye": "#E8FFFA",
                       "spots_glow": True},
            "solar": {"fur": "#FFC96B", "belly": "#FFF1C9", "fur2": "#FFF6D0", "muzzle": "#FFF4D6", "antler": "#FFF6C2",
                      "antler_glow": "#FFF2A6", "hoof": "#B5701E", "nose": "#6B3E0E", "star": "#FFFFFF", "eye": "#D2691E",
                      "spots_glow": True},
        },
    },
    "pastel_axolotl": {
        "common": {
            "bubblegum": {"fur": "#FFB9DA", "belly": "#FFE6F2", "gill": "#FF7FB6", "fin": "#FFD0E7", "heart": "#FF6FA5",
                          "eye": "#3A2A4A", "mouth": "#B04A78", "blush": "#FF8DBE", "glitter": "#FFFFFF"},
            "mint": {"fur": "#B9F2DA", "belly": "#E9FFF5", "gill": "#6FD8B0", "fin": "#D8FFF0", "heart": "#FF9EC4",
                     "eye": "#24463A", "mouth": "#3E8A6E", "glitter": "#FFFFFF"},
            "lavender": {"fur": "#D7C9FF", "belly": "#F2EDFF", "gill": "#A88BF5", "fin": "#EDE6FF", "heart": "#FF9EC4",
                         "eye": "#3A2A5A", "mouth": "#7A5AB8", "glitter": "#FFFFFF"},
            "peach": {"fur": "#FFD4B9", "belly": "#FFF0E6", "gill": "#FF9E7A", "fin": "#FFE6D6", "heart": "#FF8FA8",
                      "eye": "#4A2A1A", "mouth": "#C0604A", "glitter": "#FFFFFF"},
        },
        "rare": {
            "opal": {"fur": "#F5F7FF", "belly": "#FFFFFF", "gill": "#C9F0FF", "gill_glow": "#FFD1F5", "fin": "#F0E6FF",
                     "fin_glow": "#C9F0FF", "heart": "#FFB3E6", "eye": "#9F7FFF", "mouth": "#9F7FFF", "glitter": "#FFD1F5"},
            "galaxy": {"fur": "#3A316D", "belly": "#5A4F99", "gill": "#7F6FFF", "gill_glow": "#C7B8FF", "fin": "#5A4F99",
                       "fin_glow": "#9F8FFF", "heart": "#FFB3E6", "eye": "#FFE07A", "mouth": "#C7B8FF", "glitter": "#FFFFFF",
                       "pupil": "#120E28", "blush": "#C77DFF"},
        },
    },
    "tiny_swan": {
        "common": {
            "white": {"fur": "#FFFFFF", "feather": "#FAFCFF", "feather2": "#E6EDF5", "beak": "#FF9E5E", "knob": "#3A3A48",
                      "eye": "#2A2140", "blush": "#FFC1D0"},
            "blush": {"fur": "#FFE7EF", "feather": "#FFEDF3", "feather2": "#FFD0DE", "beak": "#FF8F7A", "knob": "#5A3A48",
                      "eye": "#2A2140"},
            "dove": {"fur": "#DADDE7", "feather": "#E2E5EE", "feather2": "#C2C6D4", "beak": "#7A7F92", "knob": "#3A3A48",
                     "eye": "#2A2140"},
        },
        "rare": {
            "midnight": {"fur": "#302B3B", "feather": "#3A3448", "feather2": "#4D4659", "beak": "#FF5C6A", "knob": "#FFFFFF",
                         "eye": "#FF8FA0", "pupil": "#FFFFFF", "glitter": "#FFF3B0", "blush": "#FF8FA0"},
            "golden": {"fur": "#FFE08A", "feather": "#FFE7A3", "feather2": "#FFD15C", "beak": "#FF9E3D", "knob": "#7A4A12",
                       "eye": "#7A4A12", "glitter": "#FFFFFF"},
        },
    },
    "rainbow_butterfly": {
        "common": {
            "rainbow": {"fur": "#5B4D80", "fur2": "#8A7AB8", "wing1": "#FF9AA2", "wing2": "#FFDAC1", "wing3": "#B5EAD7",
                        "wing4": "#C7CEEA", "wingrim": "#6E5F9E", "wingdot": "#FFFFFF", "eye": "#FFFFFF", "wing": "#FFFFFF"},
            "sunset": {"fur": "#5A2D4A", "fur2": "#8A4A6E", "wing1": "#FFE08A", "wing2": "#FFB86B", "wing3": "#FF8F8F",
                       "wing4": "#FF6FA8", "wingrim": "#5A2D4A", "wingdot": "#FFF3D6", "eye": "#FFFFFF", "wing": "#FFFFFF"},
            "ocean": {"fur": "#2E3A6B", "fur2": "#4A5A9C", "wing1": "#B8FFF6", "wing2": "#7FDFFF", "wing3": "#6FA8FF",
                      "wing4": "#A98CFF", "wingrim": "#2E3A6B", "wingdot": "#FFFFFF", "eye": "#FFFFFF", "wing": "#FFFFFF"},
            "candy": {"fur": "#A05A8C", "fur2": "#C77DB0", "wing1": "#FFFFFF", "wing2": "#FFC2E2", "wing3": "#B3E5FF",
                      "wing4": "#E0B8FF", "wingrim": "#C76AA6", "wingdot": "#FFFFFF", "eye": "#FFFFFF", "wing": "#FFFFFF"},
            "meadow": {"fur": "#4A6A4A", "fur2": "#6E9A6A", "wing1": "#FFFBD0", "wing2": "#FFF09A", "wing3": "#C9F2A6",
                       "wing4": "#8FE3B8", "wingrim": "#4A7A5A", "wingdot": "#FFFFFF", "eye": "#FFFFFF", "wing": "#FFFFFF"},
        },
        "rare": {
            "aurora": {"fur": "#2C2650", "fur2": "#4A3F7A", "wing1": "#9CFFD9", "wing2": "#7FE0FF", "wing3": "#C9A6FF",
                       "wing4": "#FFB3F0", "wingrim": "#2C2650", "wingdot": "#E8FFFA", "eye": "#E8FFFA", "wing": "#FFFFFF"},
            "prism": {"fur": "#8A5A1E", "fur2": "#B5822E", "wing1": "#FFFBE0", "wing2": "#FFE9A8", "wing3": "#FFD36B",
                      "wing4": "#FFB347", "wingrim": "#9A6A22", "wingdot": "#FFFFFF", "eye": "#FFFFFF", "wing": "#FFFFFF"},
        },
    },
    "cherry_blossom_bird": {
        "common": {
            "blossom": {"fur": "#FFFFFF", "fur2": "#FFCADB", "belly": "#FFF2F6", "beak": "#E8A0A8", "petal": "#FF9EC0",
                        "wingtip": "#F08AAE", "eye": "#2A2140", "blush": "#FF9EB5"},
            "snow": {"fur": "#FFFFFF", "fur2": "#F1F3F9", "belly": "#FFFFFF", "beak": "#C9A0A8", "petal": "#FFC2D6",
                     "wingtip": "#C9CEDB", "eye": "#2A2140", "blush": "#FFB3C6"},
            "plum": {"fur": "#F4E5FF", "fur2": "#C8A3E8", "belly": "#FBF5FF", "beak": "#D69AC0", "petal": "#E07AB8",
                     "wingtip": "#9B6FC4", "eye": "#2A2140"},
        },
        "rare": {
            "golden_sakura": {"fur": "#FFF7D6", "fur2": "#FFD46B", "belly": "#FFFCEA", "beak": "#E89A5A", "petal": "#FFB3D1",
                              "wingtip": "#E8A63E", "eye": "#7A4A12", "glitter": "#FFFFFF"},
        },
    },
    "dreamy_hamster": {
        "common": {
            "cream": {"fur": "#FFE9C8", "fur2": "#FFD39E", "belly": "#FFFFFF", "inner": "#FFC9D1", "nose": "#FF9EAE",
                      "felt2": "#B9A6F2", "capstar": "#FFF3A6", "pom": "#FFFFFF", "eye": "#3A2A3A"},
            "caramel": {"fur": "#E8B17B", "fur2": "#C98A52", "belly": "#FFF6EA", "inner": "#FFC9C4", "nose": "#E0848E",
                        "felt2": "#8FB8F2", "capstar": "#FFF3A6", "pom": "#FFFFFF", "eye": "#3A2414"},
            "lavender_dream": {"fur": "#E7D9FF", "fur2": "#CDB8F5", "belly": "#FFFFFF", "inner": "#FFD1E8", "nose": "#F59AC6",
                               "felt2": "#FFB3D1", "capstar": "#FFFFFF", "pom": "#FFFFFF", "eye": "#3A2A5A"},
        },
        "rare": {
            "starry_night": {"fur": "#3B407B", "fur2": "#2C3066", "belly": "#7076BA", "inner": "#9FA6E8", "nose": "#FFB3D1",
                             "felt2": "#1F2251", "capstar": "#FFF0A6", "pom": "#FFF6C9", "eye": "#FFE07A", "glitter": "#FFF6C9",
                             "pupil": "#14163A"},
            "cotton_candy": {"fur": "#FFD2E9", "fur2": "#BDE7FF", "belly": "#E3F5FF", "inner": "#FFC2DE", "nose": "#FF8DBE",
                             "felt2": "#B3E5FF", "capstar": "#FFFFFF", "pom": "#FFB3D9", "eye": "#5A3A6A", "glitter": "#FFFFFF"},
        },
    },
}


def variant_list(species):
    spec = VARIANTS[species]
    return [(n, False) for n in spec["common"]] + [(n, True) for n in spec["rare"]]


def palette(species, name):
    spec = VARIANTS[species]
    rare = name in spec["rare"]
    raw = dict(spec["rare" if rare else "common"][name])
    flags = {k: raw.pop(k) for k in [k for k, v in raw.items() if isinstance(v, bool)]}
    p = {}
    p.update(ACCESSORY_PALETTE)
    p.update(BASE)
    p.update(raw)
    _fill(p)
    p.update(flags)
    p["_species"] = species
    p["_variant"] = name
    p["_rare"] = rare
    return p

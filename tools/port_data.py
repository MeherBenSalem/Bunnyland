#!/usr/bin/env python3
"""Derives a newer Minecraft version's common resources from the 1.20.1 ones.

tools/generate_assets.py writes 1.20.1/common/src/main/resources. This script copies that tree into another workspace
and rewrites the data (and, for 26.x, the item model definitions) into that version's formats:

    python3 tools/port_data.py 1.21.1
    python3 tools/port_data.py 26.2
    python3 tools/port_data.py 26.3

Standard library only. The target's common/src/main/resources/{assets,data} are replaced; pack.mcmeta is rewritten.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "1.20.1" / "common" / "src" / "main" / "resources"
MODID = "bunnyland"

# (pack_format, min, max) for the mod's pack.mcmeta.
PACK = {"1.21.1": (34, 34, 48), "26.2": (None, 88, 107), "26.3": (None, 97, 121)}
# Data folders renamed in 1.21.
RENAMED = {"loot_tables": "loot_table", "recipes": "recipe", "structures": "structure", "advancements": "advancement"}
RENAMED_TAGS = {"items": "item", "blocks": "block", "entity_types": "entity_type", "fluids": "fluid", "game_events": "game_event"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def is_26(version):
    return version.startswith("26.")


# ----------------------------------------------------------------------- recipes

def ingredient_26(ing):
    """1.21.2+: an ingredient is an item id, a #tag, or a list of those."""
    if isinstance(ing, list):
        return [ingredient_26(i) for i in ing]
    if "item" in ing:
        return ing["item"]
    if "tag" in ing:
        return "#" + ing["tag"]
    return ing


def recipe(obj, version):
    if "result" in obj and isinstance(obj["result"], dict) and "item" in obj["result"]:
        obj["result"]["id"] = obj["result"].pop("item")
    if is_26(version):
        if "ingredients" in obj:
            obj["ingredients"] = [ingredient_26(i) for i in obj["ingredients"]]
        if "key" in obj:
            obj["key"] = {k: ingredient_26(v) for k, v in obj["key"].items()}
    return obj


# ----------------------------------------------------------------------- advancements

def item_predicate(pred):
    """1.20.5+: {"items": [...]} / {"tag": t} become {"items": ids-or-#tag}."""
    if "tag" in pred:
        pred["items"] = "#" + pred.pop("tag")
    elif isinstance(pred.get("items"), list) and len(pred["items"]) == 1:
        pred["items"] = pred["items"][0]
    return pred


ENTITY_SUB = {"type": "minecraft:entity_type", "nbt": "minecraft:nbt"}


def advancement(obj, version):
    icon = obj.get("display", {}).get("icon")
    if icon and "item" in icon:
        icon["id"] = icon.pop("item")
    for criterion in obj.get("criteria", {}).values():
        conditions = criterion.get("conditions", {})
        if criterion.get("trigger") == "minecraft:inventory_changed":
            conditions["items"] = [item_predicate(p) for p in conditions.get("items", [])]
    if is_26(version):
        # 1.21.5+: an entity predicate is a map of namespaced sub-predicates.
        for criterion in obj.get("criteria", {}).values():
            for conditions in criterion.get("conditions", {}).values():
                for cond in conditions if isinstance(conditions, list) else []:
                    if isinstance(cond, dict) and isinstance(cond.get("predicate"), dict):
                        cond["predicate"] = {ENTITY_SUB.get(k, k): v for k, v in cond["predicate"].items()}
    if is_26(version) and "background" in obj.get("display", {}):
        # 1.21.5+: the background is a texture id without the textures/ prefix and .png suffix.
        bg = obj["display"]["background"]
        if bg.endswith(".png") and "textures/" in bg:
            ns, path = bg.split(":", 1)
            obj["display"]["background"] = ns + ":" + path[len("textures/"):-len(".png")]
    return obj


# ----------------------------------------------------------------------- loot tables

def loot_function(fn):
    if fn.get("function") == "minecraft:looting_enchant":
        fn["function"] = "minecraft:enchanted_count_increase"
        fn["enchantment"] = "minecraft:looting"
    return fn


def loot_table(obj, version):
    for pool in obj.get("pools", []):
        for entry in pool.get("entries", []):
            entry["functions"] = [loot_function(f) for f in entry.get("functions", [])]
            if not entry["functions"]:
                del entry["functions"]
        pool["functions"] = [loot_function(f) for f in pool.get("functions", [])]
        if not pool["functions"]:
            del pool["functions"]
    return obj


# ----------------------------------------------------------------------- item model definitions (26.x)

def item_definitions(assets, version):
    """1.21.4+: every item needs assets/<ns>/items/<id>.json pointing at its model (with tints and properties)."""
    models = assets / "models" / "item"
    out = assets / "items"
    dyed = {"pet_collar": 0xF7A8C8, "pet_bow": 0xFF8FB8}
    for model in sorted(models.glob("*.json")):
        name = model.stem
        if name == "pet_carrier_full":
            continue
        ref = f"{MODID}:item/{name}"
        if name in dyed:
            definition = {"type": "minecraft:model", "model": ref,
                          "tints": [{"type": "minecraft:dye", "default": dyed[name]}]}
        elif name == "pet_carrier":
            definition = {"type": "minecraft:condition", "property": "minecraft:has_component", "component": "minecraft:custom_data",
                          "on_true": {"type": "minecraft:model", "model": f"{MODID}:item/pet_carrier_full"},
                          "on_false": {"type": "minecraft:model", "model": ref}}
        else:
            definition = {"type": "minecraft:model", "model": ref}
        dump(out / f"{name}.json", {"model": definition})


# ----------------------------------------------------------------------- spawn eggs (26.x)

# Base and spot colours, as in 1.20.1's ModItems#eggColors (spawn eggs lost their tint colours in 1.21.5).
EGG_COLORS = {
    "cotton_bunny": (0xFFF9F5, 0xFFB3C9), "strawberry_bunny": (0xFF8FA4, 0x7CC46E), "moon_bunny": (0x5E5CAB, 0xFFF0A6),
    "lavender_bunny": (0xC9B6F0, 0x9B7FE0), "snowball_bunny": (0xFFFFFF, 0xA9D8FF), "blossom_fox": (0xFFB4CA, 0xFFFFFF),
    "cloud_kitty": (0xFFFFFF, 0xC4E5FF), "strawberry_mouse": (0xFFD7DF, 0xFF5C7A), "honey_bear": (0xF2B45B, 0xFFE3B0),
    "moon_deer": (0x6B6DB8, 0xCFEAFF), "pastel_axolotl": (0xFFB9DA, 0xFF7FB6), "tiny_swan": (0xFFFFFF, 0xFF9E5E),
    "rainbow_butterfly": (0xC7CEEA, 0xFF9AA2), "cherry_blossom_bird": (0xFFCADB, 0xFFFFFF), "dreamy_hamster": (0xFFE9C8, 0xB9A6F2),
}
# A 16x16 egg: '#' outline, 'o' base, 'h' highlight, 's' shade, 'x' spot.
EGG = [
    "................",
    "......####......",
    ".....#ohoo#.....",
    "....#ohhoxo#....",
    "....#ohoxxo#....",
    "...#ooooooxo#...",
    "...#oxxoooos#...",
    "..#ooxxooxxos#..",
    "..#ooooooxxos#..",
    "..#oooxooooos#..",
    "..#ooxxxoooss#..",
    "..#soooooxoss#..",
    "...#ssooooss#...",
    "....#sssss##....",
    ".....######.....",
    "................",
]


def egg_textures(assets):
    sys.path.insert(0, str(ROOT / "tools"))
    from assetgen.core import Img as Image

    def rgb(c, k=1.0):
        return tuple(max(0, min(255, round(((c >> s) & 0xFF) * k))) for s in (16, 8, 0)) + (255,)

    for sid, (base, spot) in EGG_COLORS.items():
        img = Image(16, 16)
        for y, row in enumerate(EGG):
            for x, ch in enumerate(row):
                colour = {"#": rgb(base, 0.45), "o": rgb(base), "h": rgb(base, 1.12), "s": rgb(base, 0.82), "x": rgb(spot)}.get(ch)
                if colour:
                    img.set(x, y, colour)
        img.save(assets / "textures" / "item" / f"{sid}_spawn_egg.png")
        dump(assets / "models" / "item" / f"{sid}_spawn_egg.json",
             {"parent": "minecraft:item/generated", "textures": {"layer0": f"{MODID}:item/{sid}_spawn_egg"}})


# ----------------------------------------------------------------------- driver

def port(version):
    target = ROOT / version / "common" / "src" / "main" / "resources"
    for sub in ("assets", "data"):
        shutil.rmtree(target / sub, ignore_errors=True)
        shutil.copytree(SOURCE / sub, target / sub)
    for extra in ("bunnyland_logo.png",):
        shutil.copy2(SOURCE / extra, target / extra)

    for ns_dir in (target / "data").iterdir():
        for old, new in RENAMED.items():
            if (ns_dir / old).exists():
                (ns_dir / old).rename(ns_dir / new)
        tags = ns_dir / "tags"
        if tags.exists():
            for old, new in RENAMED_TAGS.items():
                if (tags / old).exists():
                    (tags / old).rename(tags / new)

    data = target / "data"
    for path in data.glob("*/recipe/**/*.json"):
        dump(path, recipe(load(path), version))
    for path in data.glob("*/advancement/**/*.json"):
        dump(path, advancement(load(path), version))
    for path in data.glob("*/loot_table/**/*.json"):
        dump(path, loot_table(load(path), version))

    # 1.20.5+: the vanilla dye recipe colours anything in #minecraft:dyeable.
    dump(data / "minecraft" / "tags" / "item" / "dyeable.json",
         {"replace": False, "values": [f"{MODID}:pet_collar", f"{MODID}:pet_bow"]})

    # 1.21+: breathing under water is an entity tag (LivingEntity#canBreatheUnderwater can no longer be overridden).
    dump(data / "minecraft" / "tags" / "entity_type" / "can_breathe_under_water.json",
         {"replace": False, "values": [f"{MODID}:pastel_axolotl"]})

    if is_26(version):
        assets = target / "assets" / MODID
        egg_textures(assets)
        item_definitions(assets, version)
        # GeckoLib 5 reads geckolib/models/... and geckolib/animations/... (ids without folder or suffix).
        (assets / "geckolib").mkdir(exist_ok=True)
        (assets / "geo").rename(assets / "geckolib" / "models")
        (assets / "animations").rename(assets / "geckolib" / "animations")

    fmt, lo, hi = PACK[version]
    pack = {"pack": {"description": {"text": "${mod_id} resources"}}}
    if fmt is not None:
        pack["pack"]["pack_format"] = fmt
        pack["pack"]["supported_formats"] = {"min_inclusive": lo, "max_inclusive": hi}
    else:
        # 1.21.9+: a format range instead of pack_format.
        pack["pack"]["min_format"] = lo
        pack["pack"]["max_format"] = hi
    dump(target / "pack.mcmeta", pack)
    print(f"ported resources to {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in PACK:
        sys.exit(f"usage: {sys.argv[0]} {{{','.join(PACK)}}}")
    port(sys.argv[1])

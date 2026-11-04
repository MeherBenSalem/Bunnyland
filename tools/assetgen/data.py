"""Data-pack content (recipes, loot, tags, biome tags, biome modifier, advancements, the GameTest
arena) and the English lang file."""
import gzip
import struct

from .content import (ACCESSORY_ITEMS, BED_WOOL, BLOCK_NAMES, ITEM_NAMES, ITEM_TOOLTIPS, SPECIES, TOYS, TREATS,
                      VARIANT_NAMES)
from .core import ASSETS, DATA, MODID, ROOT, write_json
from .sound_events import SOUND_EVENTS
from .species import IDS
from .variants import variant_list

M = MODID + ":"
MC_TAGS = ROOT / "data" / "minecraft" / "tags"
BUNNIES = ["cotton_bunny", "strawberry_bunny", "moon_bunny", "lavender_bunny", "snowball_bunny"]


def ing(x):
    if x.startswith("#"):
        return {"tag": x[1:]}
    return {"item": x if ":" in x else "minecraft:" + x}


def shaped(name, pattern, key, result, count=1, group=None):
    r = {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
         "key": {k: ing(v) for k, v in key.items()}, "result": {"item": result if ":" in result else M + result, "count": count}}
    if group:
        r["group"] = group
    write_json(DATA / "recipes" / f"{name}.json", r)


def shapeless(name, ingredients, result, count=1, group=None):
    r = {"type": "minecraft:crafting_shapeless", "category": "misc", "ingredients": [ing(i) for i in ingredients],
         "result": {"item": result if ":" in result else M + result, "count": count}}
    if group:
        r["group"] = group
    write_json(DATA / "recipes" / f"{name}.json", r)


def recipes():
    shapeless("bunny_biscuit", ["carrot", "wheat", "sugar"], "bunny_biscuit", 4, "bunnyland:treats")
    shapeless("strawberry_tart", ["sweet_berries", "sweet_berries", "wheat", "sugar", "egg"], "strawberry_tart", 3, "bunnyland:treats")
    shapeless("moon_cookie", ["glow_berries", "wheat", "sugar"], "moon_cookie", 4, "bunnyland:treats")
    shapeless("blossom_mochi", ["pink_petals", "wheat", "sugar"], "blossom_mochi", 4, "bunnyland:treats")
    shapeless("fish_cracker", ["#minecraft:fishes", "wheat"], "fish_cracker", 4, "bunnyland:treats")
    shapeless("honey_cake", ["honey_bottle", "wheat", "sugar", "egg"], "honey_cake", 2, "bunnyland:treats")
    shapeless("seed_medley", ["wheat_seeds", "#forge:seeds", "#forge:seeds"], "seed_medley", 2, "bunnyland:treats")
    shapeless("flower_nectar", ["honey_bottle", "#minecraft:small_flowers", "#minecraft:small_flowers"], "flower_nectar", 2,
              "bunnyland:treats")
    shapeless("pet_kibble", ["wheat", "wheat", "#bunnyland:kibble_bits"], "pet_kibble", 6)
    shaped("pet_collar", ["SLS", " G "], {"S": "string", "L": "leather", "G": "gold_nugget"}, "pet_collar")
    shapeless("pet_bow", ["#minecraft:wool", "string"], "pet_bow", 2)
    shaped("flower_crown", ["FFF", "F F"], {"F": "#minecraft:small_flowers"}, "flower_crown")
    shaped("tiny_top_hat", [" B ", "BPB"], {"B": "black_wool", "P": "pink_dye"}, "tiny_top_hat")
    shaped("party_hat", [" S ", "PDP"], {"S": "string", "P": "paper", "D": "pink_dye"}, "party_hat")
    shaped("star_clip", [" G ", "GSG", " I "], {"G": "gold_nugget", "S": "glowstone_dust", "I": "iron_nugget"}, "star_clip", 2)
    shaped("heart_glasses", ["PIP"], {"P": "pink_stained_glass_pane", "I": "iron_nugget"}, "heart_glasses")
    shaped("cozy_scarf", ["WWW", "W  "], {"W": "#minecraft:wool"}, "cozy_scarf")
    shapeless("yarn_ball", ["#minecraft:wool", "string", "string"], "yarn_ball")
    shapeless("squeaky_carrot", ["carrot", "slime_ball"], "squeaky_carrot")
    shaped("feather_wand", ["  F", " S ", "S  "], {"F": "feather", "S": "stick"}, "feather_wand")
    shaped("pet_carrier", [" L ", "PIP", "PPP"], {"L": "leather", "P": "#minecraft:planks", "I": "iron_bars"}, "pet_carrier")
    shapeless("pet_journal", ["book", "feather", "#minecraft:small_flowers"], "pet_journal")
    shaped("feeding_bowl", ["T T", " T "], {"T": "#minecraft:terracotta"}, "feeding_bowl")
    for color, wool in BED_WOOL.items():
        shaped(f"{color}_pet_bed", ["WFW", "PPP"], {"W": wool, "F": "#bunnyland:stuffing", "P": "#minecraft:wooden_slabs"},
               f"{color}_pet_bed", group="bunnyland:pet_beds")
    shapeless("string_from_cotton_fluff", [M + "cotton_fluff", M + "cotton_fluff"], "minecraft:string")
    shaped("white_wool_from_cotton_fluff", ["FF", "FF"], {"F": M + "cotton_fluff"}, "minecraft:white_wool")


def loot():
    drops = {"cotton_bunny": ("bunnyland:cotton_fluff", 0, 2), "strawberry_bunny": ("minecraft:sweet_berries", 0, 1),
             "moon_bunny": ("minecraft:glow_berries", 0, 1), "lavender_bunny": ("minecraft:allium", 0, 1),
             "snowball_bunny": ("minecraft:snowball", 0, 2), "blossom_fox": ("minecraft:pink_petals", 0, 1),
             "cloud_kitty": ("minecraft:string", 0, 1), "strawberry_mouse": ("minecraft:wheat_seeds", 0, 1),
             "honey_bear": ("minecraft:honeycomb", 0, 1), "moon_deer": ("minecraft:leather", 0, 1),
             "tiny_swan": ("minecraft:feather", 0, 2), "cherry_blossom_bird": ("minecraft:feather", 0, 1),
             "dreamy_hamster": ("minecraft:wheat_seeds", 0, 1)}
    for sid in IDS:
        pools = []
        if sid in drops:
            item, lo, hi = drops[sid]
            pools.append({"rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": item, "functions": [
                {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}},
                {"function": "minecraft:looting_enchant", "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]})
        write_json(DATA / "loot_tables" / "entities" / f"{sid}.json", {"type": "minecraft:entity", "pools": pools})
    for block in BLOCK_NAMES:
        write_json(DATA / "loot_tables" / "blocks" / f"{block}.json", {"type": "minecraft:block", "pools": [{
            "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": M + block}],
            "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


def tag(path, values, registry="items", base=None):
    write_json((base or DATA / "tags") / registry / f"{path}.json", {"replace": False, "values": values})


def tags():
    for sid, s in SPECIES.items():
        treats = [M + t for t in s["treats"]]
        food = [f if f.startswith("#") else "minecraft:" + f for f in s["food"]]
        tag(f"taming_treats/{sid}", treats)
        tag(f"breeding_food/{sid}", food + treats)
        tag(f"tempting/{sid}", ["#bunnyland:taming_treats/" + sid, "#bunnyland:breeding_food/" + sid, M + "feather_wand"])
        tag(f"spawns/{sid}", ["minecraft:" + b for b in s["biomes"]], registry="worldgen/biome")
    tag("bowl_food", [M + "pet_kibble"] + [M + t for t in TREATS])
    tag("pet_treats", [M + t for t in TREATS])
    tag("accessories", [M + a for a in ACCESSORY_ITEMS])
    tag("pet_toys", [M + t for t in TOYS])
    tag("stuffing", [M + "cotton_fluff", "minecraft:feather", "minecraft:white_wool"])
    tag("kibble_bits", ["minecraft:carrot", "minecraft:potato", "minecraft:beetroot", "minecraft:apple",
                        "minecraft:sweet_berries", "minecraft:melon_slice"])
    tag("pet_beds", [M + f"{c}_pet_bed" for c in BED_WOOL], registry="blocks")
    tag("pet_beds", [M + f"{c}_pet_bed" for c in BED_WOOL])
    tag("creatures_spawnable_on", ["#minecraft:animals_spawnable_on", "minecraft:snow", "minecraft:snow_block",
                                   "minecraft:podzol", "minecraft:coarse_dirt", "minecraft:moss_block", "minecraft:sand",
                                   "minecraft:dirt", "minecraft:rooted_dirt", "minecraft:mud"], registry="blocks")
    tag("flyers_perch_on", ["#bunnyland:creatures_spawnable_on", "#minecraft:leaves", "#minecraft:logs"], registry="blocks")
    tag("creatures", [M + s for s in IDS], registry="entity_types")
    tag("bunnies", [M + s for s in BUNNIES], registry="entity_types")
    tag("mouse_predators", ["minecraft:cat", "minecraft:ocelot", M + "cloud_kitty"], registry="entity_types")
    tag("powder_snow_walkable_mobs", [M + "snowball_bunny", M + "moon_bunny"], registry="entity_types", base=MC_TAGS)
    tag("freeze_immune_entity_types", [M + "snowball_bunny"], registry="entity_types", base=MC_TAGS)


def biome_modifier():
    write_json(DATA / "forge" / "biome_modifier" / "creature_spawns.json", {"type": M + "creature_spawns"})


def advancements():
    def adv(name, parent, icon, frame, criteria, requirements=None, hidden=False):
        a = {"display": {"icon": {"item": icon}, "title": {"translate": f"advancements.bunnyland.{name}.title"},
                         "description": {"translate": f"advancements.bunnyland.{name}.description"},
                         "frame": frame, "show_toast": True, "announce_to_chat": True, "hidden": hidden},
             "criteria": criteria}
        if parent:
            a["parent"] = M + parent
        else:
            a["display"]["background"] = "minecraft:textures/block/cherry_planks.png"
        if requirements:
            a["requirements"] = requirements
        write_json(DATA / "advancements" / f"{name}.json", a)

    def tame(types):
        return {"trigger": "minecraft:tame_animal", "conditions": {"entity": [{"condition": "minecraft:entity_properties",
                                                                                   "entity": "this", "predicate": {"type": types}}]}}

    adv("root", None, M + "pet_journal", "task", {"journal": {"trigger": "minecraft:inventory_changed", "conditions": {
        "items": [{"items": [M + "pet_journal"]}]}}, "treat": {"trigger": "minecraft:inventory_changed", "conditions": {
        "items": [{"tag": "bunnyland:pet_treats"}]}}}, requirements=[["journal", "treat"]])
    adv("first_friend", "root", M + "bunny_biscuit", "task", {"tamed": tame("#bunnyland:creatures")})
    adv("fluffle", "first_friend", M + "cotton_bunny_spawn_egg", "goal", {b: tame(M + b) for b in BUNNIES})
    adv("best_friends_forever", "fluffle", M + "flower_crown", "challenge", {s: tame(M + s) for s in IDS})
    adv("rare_find", "first_friend", M + "star_clip", "goal", {"bred": {"trigger": "minecraft:bred_animals", "conditions": {
        "child": [{"condition": "minecraft:entity_properties", "entity": "this",
                   "predicate": {"type": "#bunnyland:creatures", "nbt": "{Rare:1b}"}}]}}})
    beds = {c: {"trigger": "minecraft:placed_block", "conditions": {"location": [{"condition": "minecraft:block_state_property",
                                                                                   "block": M + f"{c}_pet_bed"}]}} for c in BED_WOOL}
    adv("snug_as_a_bunny", "first_friend", M + "pink_pet_bed", "task", beds, requirements=[list(beds)])


def arena():
    """A 9x6x9 GameTest structure with no blocks. The GameTest framework lays a grass floor at relative
    y=0 itself (relative coordinates start at the structure block, one layer below the template), so
    creatures spawned at relative y=1 stand on it."""
    def name(s):
        b = s.encode()
        return struct.pack(">H", len(b)) + b

    size = (9, 6, 9)
    out = b"\x0a" + name("")
    out += b"\x03" + name("DataVersion") + struct.pack(">i", 3465)
    out += b"\x09" + name("size") + b"\x03" + struct.pack(">i", 3) + b"".join(struct.pack(">i", v) for v in size)
    for key in ("palette", "blocks", "entities"):
        out += b"\x09" + name(key) + b"\x00" + struct.pack(">i", 0)
    out += b"\x00"
    p = DATA / "structures" / "arena.nbt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(gzip.compress(out, mtime=0))


def lang():
    L = {"itemGroup.bunnyland": "Bunnyland"}
    for sid, s in SPECIES.items():
        L[f"entity.bunnyland.{sid}"] = s["name"]
        L[f"item.bunnyland.{sid}_spawn_egg"] = s["name"] + " Spawn Egg"
        L[f"journal.bunnyland.{sid}.description"] = s["desc"]
        L[f"journal.bunnyland.{sid}.habitat"] = s["habitat"]
        L[f"journal.bunnyland.{sid}.tip"] = s["tip"]
        for v, rare in variant_list(sid):
            L[f"variant.bunnyland.{sid}.{v}"] = VARIANT_NAMES[v]
    for k, v in ITEM_NAMES.items():
        L[f"item.bunnyland.{k}"] = v
    for k, v in BLOCK_NAMES.items():
        L[f"block.bunnyland.{k}"] = v
    for k, v in ITEM_TOOLTIPS.items():
        L[f"tooltip.bunnyland.{k}"] = v
    L.update({
        "tooltip.bunnyland.carrier.empty": "Empty. Use on one of your pets to pick it up",
        "tooltip.bunnyland.carrier.holding": "Holding %s",
        "tooltip.bunnyland.carrier.details": "%s · %s",
        "tooltip.bunnyland.carrier.release": "Use on a block to let your pet out",
        "tooltip.bunnyland.food_for": "Favourite of: %s",
        "gui.bunnyland.journal.title": "Pet Journal",
        "gui.bunnyland.journal.index": "My Creatures",
        "gui.bunnyland.journal.discovered_count": "Discovered %s / %s",
        "gui.bunnyland.journal.tamed_count": "Befriended %s / %s",
        "gui.bunnyland.journal.rare_count": "Rare variants %s / %s",
        "gui.bunnyland.journal.unknown": "???",
        "gui.bunnyland.journal.unknown_hint": "You haven't met this creature yet. Explore its habitat to find it!",
        "gui.bunnyland.journal.habitat": "Habitat",
        "gui.bunnyland.journal.taming": "Taming treat",
        "gui.bunnyland.journal.food": "Favourite food",
        "gui.bunnyland.journal.variants": "Variants",
        "gui.bunnyland.journal.rare": "rare",
        "gui.bunnyland.journal.tamed": "Befriended",
        "gui.bunnyland.journal.discovered": "Discovered",
        "gui.bunnyland.journal.not_tamed": "Not befriended yet",
        "gui.bunnyland.journal.rare_hint": "Rare variants are born through breeding, twice as often to overjoyed parents.",
        "gui.bunnyland.journal.click_variant": "Click a variant to preview it",
        "gui.bunnyland.journal.back": "Back to index",
        "toast.bunnyland.discovered": "New creature discovered!",
        "toast.bunnyland.tamed": "A new friend!",
        "toast.bunnyland.rare": "Rare variant found!",
        "message.bunnyland.sitting": "%s will wait here",
        "message.bunnyland.following": "%s is following you",
        "message.bunnyland.mood": "%s feels %s  ❤ %s%%",
        "mood.bunnyland.sad": "a little lonely",
        "mood.bunnyland.content": "content",
        "mood.bunnyland.happy": "happy",
        "mood.bunnyland.overjoyed": "overjoyed",
        "message.bunnyland.status": "%s · %s · %s · ❤ %s%%",
        "message.bunnyland.status_wild": "%s · %s (wild)",
        "message.bunnyland.not_your_pet": "%s belongs to someone else",
        "message.bunnyland.tamed": "%s is your friend now!",
        "message.bunnyland.too_sad": "%s is too lonely to think about babies. Give it some love first!",
        "message.bunnyland.gift": "%s left you a little gift",
        "message.bunnyland.bowl_full": "The bowl is full",
        "message.bunnyland.bowl_level": "Bowl: %s / %s portions",
        "message.bunnyland.journal_given": "You received a Pet Journal! Discover cute creatures to fill its pages.",
        "message.bunnyland.dressed": "%s looks adorable!",
        "message.bunnyland.undressed": "You took off %s's %s",
        "message.bunnyland.toy_tired": "%s needs a little rest before playing again",
        "message.bunnyland.carrier_wrong_pet": "You can only carry your own pets",
        "message.bunnyland.carrier_busy": "That pet is too busy to be picked up",
        "accessory.bunnyland.collar": "collar",
        "accessory.bunnyland.bow": "bow",
    })
    for a in ACCESSORY_ITEMS:
        L[f"accessory.bunnyland.{a}"] = ITEM_NAMES[a].lower()
    texts = {
        "root": ("Bunnyland", "Get a Pet Journal or a pet treat and start your cute creature adventure"),
        "first_friend": ("A Furry Friend", "Befriend any Bunnyland creature with its favourite treat"),
        "fluffle": ("A Whole Fluffle", "Befriend all five kinds of bunny"),
        "best_friends_forever": ("Best Friends Forever", "Befriend every kind of Bunnyland creature"),
        "rare_find": ("Once in a Blue Moon", "Breed a rare variant"),
        "snug_as_a_bunny": ("Snug as a Bunny", "Place a cosy pet bed"),
    }
    for k, (t, d) in texts.items():
        L[f"advancements.bunnyland.{k}.title"] = t
        L[f"advancements.bunnyland.{k}.description"] = d
    for event, (subtitle, _n, _brief) in SOUND_EVENTS.items():
        L[f"subtitles.bunnyland.{event}"] = subtitle
    write_json(ASSETS / "lang" / "en_us.json", dict(sorted(L.items())))
    return L


def generate():
    recipes()
    loot()
    tags()
    biome_modifier()
    advancements()
    arena()
    L = lang()
    print(f"  recipes, loot tables, tags, biome modifier, advancements, arena, {len(L)} lang entries")

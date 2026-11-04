"""Game content shared by the data and lang generators: species texts, foods, habitats and
spawn defaults, item names. Mirrors Species.java / ModItems.java (ids must match)."""

TREATS = ["bunny_biscuit", "strawberry_tart", "moon_cookie", "blossom_mochi", "fish_cracker", "honey_cake",
          "seed_medley", "flower_nectar"]
ACCESSORY_ITEMS = ["flower_crown", "tiny_top_hat", "party_hat", "star_clip", "heart_glasses", "cozy_scarf"]
TOYS = ["yarn_ball", "squeaky_carrot", "feather_wand"]
BED_WOOL = {"pink": "pink_wool", "lavender": "purple_wool", "mint": "lime_wool", "sky": "light_blue_wool"}

# id: name, treat(s), breeding food, biomes, (weight, min, max), category, tame odds, description, habitat, tip
SPECIES = {
    "cotton_bunny": dict(
        name="Cotton Bunny", treats=["bunny_biscuit"], food=["carrot", "golden_carrot", "dandelion"],
        biomes=["meadow", "flower_forest", "plains", "sunflower_plains", "cherry_grove"], spawn=(8, 2, 4),
        desc="A round little puff of a bunny with a cotton-ball tail. Every so often it sheds a tuft of soft Cotton Fluff, "
             "which makes wonderful stuffing for pet beds.",
        habitat="Meadows, flower forests, plains and cherry groves.",
        tip="Wild bunnies are shy: sneak to get close, then offer a Bunny Biscuit."),
    "strawberry_bunny": dict(
        name="Strawberry Bunny", treats=["strawberry_tart"], food=["sweet_berries", "carrot"],
        biomes=["flower_forest", "meadow", "sunflower_plains", "birch_forest"], spawn=(6, 2, 3),
        desc="Speckled with golden seeds and crowned with a leafy calyx, this berry-sweet bunny can't resist ripe berry "
             "bushes and will happily nibble any it finds.",
        habitat="Flower forests, meadows and sunny birch woods.",
        tip="Tame it with a Strawberry Tart. It loves sweet berries."),
    "moon_bunny": dict(
        name="Moon Bunny", treats=["moon_cookie"], food=["glow_berries", "carrot"],
        biomes=["meadow", "grove", "snowy_slopes", "snowy_plains"], spawn=(4, 1, 3),
        desc="A night-loving bunny whose markings glow like moonlight. A tiny crescent moon follows it everywhere. It "
             "floats down gently from great heights and never takes fall damage.",
        habitat="High meadows, groves and snowy slopes, close to the sky.",
        tip="Moon Bunnies nap during the day; look for them awake at night with a Moon Cookie."),
    "lavender_bunny": dict(
        name="Lavender Bunny", treats=["bunny_biscuit"], food=["carrot", "allium", "lilac"],
        biomes=["flower_forest", "meadow", "cherry_grove"], spawn=(6, 2, 3),
        desc="A floppy-eared lop who smells faintly of lavender and keeps a sprig tucked behind one ear. Cuddling a happy "
             "Lavender Bunny is so calming that it soothes your wounds.",
        habitat="Flower forests, meadows and cherry groves.",
        tip="Pet a happy Lavender Bunny (sneak + use) to receive a few seconds of Regeneration."),
    "snowball_bunny": dict(
        name="Snowball Bunny", treats=["bunny_biscuit"], food=["carrot", "beetroot"],
        biomes=["snowy_plains", "snowy_taiga", "ice_spikes", "grove", "snowy_slopes"], spawn=(8, 2, 4),
        desc="So round and so fluffy it is mostly snowball. Snowball Bunnies never feel the cold, can't freeze, and hop "
             "across powder snow without sinking.",
        habitat="Snowy plains, snowy taigas, ice spikes and groves.",
        tip="Their white fur hides them well in the snow. Look for rosy cheeks!"),
    "blossom_fox": dict(
        name="Blossom Fox", treats=["blossom_mochi"], food=["sweet_berries", "glow_berries"],
        biomes=["cherry_grove", "flower_forest", "birch_forest", "old_growth_birch_forest"], spawn=(5, 1, 3),
        desc="A playful fox with a cherry blossom behind its ear and a tail so fluffy it sheds petals as it runs. It loves "
             "to pounce and spin when it's happy.",
        habitat="Cherry groves, flower forests and birch woods.",
        tip="Blossom Foxes sleep through the day and wake at dusk."),
    "cloud_kitty": dict(
        name="Cloud Kitty", treats=["fish_cracker"], food=["cod", "salmon"],
        biomes=["meadow", "cherry_grove", "plains", "windswept_hills"], spawn=(4, 1, 2),
        desc="A kitten wrapped in a ruff of cloud with a cloud-puff on the tip of its tail. It drifts down softly instead "
             "of falling, purrs when petted, and sometimes leaves gifts when its owner wakes up.",
        habitat="Meadows, plains, cherry groves and windswept hills.",
        tip="Sleep in a bed near your Cloud Kitty to find a little present in the morning."),
    "strawberry_mouse": dict(
        name="Strawberry Mouse", treats=["strawberry_tart"], food=["wheat", "sweet_berries"],
        biomes=["plains", "meadow", "flower_forest", "forest"], spawn=(6, 2, 4),
        desc="A tiny mouse who wears a strawberry as a hood. It scampers away from cats, including Cloud Kitties, but "
             "once tamed it is the bravest little friend.",
        habitat="Plains, meadows, forests and flower forests.",
        tip="Mice are quick! Sneak and hold a Strawberry Tart so they come to you."),
    "honey_bear": dict(
        name="Honey Bear", treats=["honey_cake"], food=["honeycomb", "sweet_berries"],
        biomes=["forest", "birch_forest", "flower_forest", "old_growth_birch_forest"], spawn=(3, 1, 2),
        desc="A cuddly cub with honey-dipped ears and a best friend: a little bee that orbits its head. It sniffs out "
             "full beehives and licks them clean, and stands up for a hug when happy.",
        habitat="Forests, birch forests and flower forests, anywhere bees buzz.",
        tip="Honey Bears are sturdy friends. Tame one with a Honey Cake."),
    "moon_deer": dict(
        name="Moon Deer", treats=["moon_cookie"], food=["apple", "glow_berries", "wheat"],
        biomes=["taiga", "snowy_taiga", "old_growth_pine_taiga", "old_growth_spruce_taiga", "grove", "meadow", "forest"],
        spawn=(4, 1, 3),
        desc="A graceful night deer with starry spots and softly glowing antlers. It is very shy and bounds away from "
             "anyone who isn't sneaking.",
        habitat="Taigas, groves, forests and meadows.",
        tip="Moon Deer sleep during the day. Approach slowly while sneaking."),
    "pastel_axolotl": dict(
        name="Pastel Axolotl", treats=["fish_cracker"], food=["tropical_fish", "kelp"],
        biomes=["river", "swamp"], spawn=(6, 1, 3),
        desc="A smiley axolotl with frilly gradient gills and a heart on its back. It swims gracefully and is just as "
             "happy waddling on land beside you.",
        habitat="Rivers and swamps.",
        tip="Pastel Axolotls never dry out, so you can take them anywhere."),
    "tiny_swan": dict(
        name="Tiny Swan", treats=["seed_medley"], food=["wheat_seeds", "beetroot_seeds", "bread"],
        biomes=["river", "swamp"], spawn=(6, 2, 4),
        desc="An elegant little swan who glides along rivers. Cygnets follow their parents in a neat little line, and a "
             "happy swan raises its wings into a heart.",
        habitat="Rivers and swamps.",
        tip="Swans love water. They float, and they paddle after you through rivers."),
    "rainbow_butterfly": dict(
        name="Rainbow Butterfly", treats=["flower_nectar"], food=["#minecraft:small_flowers"],
        biomes=["flower_forest", "meadow", "cherry_grove", "sunflower_plains", "plains"], spawn=(14, 2, 4),
        category="ambient",
        desc="A butterfly with wings painted in rainbow bands. It flutters from flower to flower, rests to show off its "
             "wings, and sometimes helps new flowers bloom.",
        habitat="Flower forests, meadows, cherry groves and plains, on sunny days.",
        tip="Offer Flower Nectar to befriend one. Tamed butterflies flutter after you."),
    "cherry_blossom_bird": dict(
        name="Cherry Blossom Bird", treats=["blossom_mochi"], food=["wheat_seeds", "melon_seeds", "pink_petals"],
        biomes=["cherry_grove", "flower_forest"], spawn=(8, 2, 4),
        desc="A round songbird with a crest of cherry petals. It sings sweet melodies in the morning and can't help "
             "dancing whenever music plays nearby.",
        habitat="Cherry groves and flower forests.",
        tip="Play a music disc near a Cherry Blossom Bird."),
    "dreamy_hamster": dict(
        name="Dreamy Hamster", treats=["seed_medley"], food=["wheat_seeds", "pumpkin_seeds", "carrot"],
        biomes=["plains", "sunflower_plains", "meadow", "savanna"], spawn=(5, 1, 3),
        desc="A sleepy hamster in a starry nightcap. It naps all day, stuffs its cheeks until they're round when it "
             "eats, and blows little dream bubbles in its sleep.",
        habitat="Plains, sunflower plains, meadows and savannas.",
        tip="Dreamy Hamsters are night owls. They nap during the day and get busy at night."),
}

TAME_ODDS = {"cotton_bunny": 3, "strawberry_bunny": 3, "moon_bunny": 4, "lavender_bunny": 3, "snowball_bunny": 3,
             "blossom_fox": 4, "cloud_kitty": 3, "strawberry_mouse": 3, "honey_bear": 4, "moon_deer": 5,
             "pastel_axolotl": 3, "tiny_swan": 3, "rainbow_butterfly": 2, "cherry_blossom_bird": 3, "dreamy_hamster": 2}

VARIANT_NAMES = {
    "classic": "Classic", "cocoa": "Cocoa", "cream": "Cream", "sugar_star": "Sugar Star", "cotton_candy": "Cotton Candy",
    "pineberry": "Pineberry", "chocolate_dipped": "Chocolate Dipped", "golden_berry": "Golden Berry",
    "midnight": "Midnight", "dusk": "Dusk", "silver": "Silver", "eclipse": "Eclipse", "starlight": "Starlight",
    "lavender": "Lavender", "lilac": "Lilac", "periwinkle": "Periwinkle", "wisteria": "Wisteria",
    "snow": "Snow", "frost": "Frost", "peppermint": "Peppermint", "aurora": "Aurora",
    "sakura": "Sakura", "peach": "Peach", "snow_blossom": "Snow Blossom", "twilight_blossom": "Twilight Blossom",
    "golden_hour": "Golden Hour", "sky": "Sky", "sunset": "Sunset", "lilac_mist": "Lilac Mist", "storm": "Storm",
    "rainbow": "Rainbow", "white_chocolate": "White Chocolate", "blueberry": "Blueberry", "honey": "Honey",
    "cinnamon": "Cinnamon", "vanilla": "Vanilla", "royal_jelly": "Royal Jelly", "midnight_honey": "Midnight Honey",
    "dawn": "Dawn", "solar": "Solar", "bubblegum": "Bubblegum", "mint": "Mint", "opal": "Opal", "galaxy": "Galaxy",
    "white": "White", "blush": "Blush", "dove": "Dove", "golden": "Golden", "ocean": "Ocean", "candy": "Candy",
    "meadow": "Meadow", "prism": "Prism", "blossom": "Blossom", "plum": "Plum", "golden_sakura": "Golden Sakura",
    "caramel": "Caramel", "lavender_dream": "Lavender Dream", "starry_night": "Starry Night",
}

ITEM_NAMES = {
    "bunny_biscuit": "Bunny Biscuit", "strawberry_tart": "Strawberry Tart", "moon_cookie": "Moon Cookie",
    "blossom_mochi": "Blossom Mochi", "fish_cracker": "Fish Cracker", "honey_cake": "Honey Cake",
    "seed_medley": "Seed Medley", "flower_nectar": "Flower Nectar", "pet_kibble": "Pet Kibble",
    "pet_collar": "Pet Collar", "pet_bow": "Pet Bow", "flower_crown": "Flower Crown", "tiny_top_hat": "Tiny Top Hat",
    "party_hat": "Party Hat", "star_clip": "Star Clip", "heart_glasses": "Heart Glasses", "cozy_scarf": "Cozy Scarf",
    "yarn_ball": "Yarn Ball", "squeaky_carrot": "Squeaky Carrot", "feather_wand": "Feather Wand",
    "pet_carrier": "Pet Carrier", "pet_journal": "Pet Journal", "cotton_fluff": "Cotton Fluff",
}
BLOCK_NAMES = {"feeding_bowl": "Feeding Bowl", "pink_pet_bed": "Pink Pet Bed", "lavender_pet_bed": "Lavender Pet Bed",
               "mint_pet_bed": "Mint Pet Bed", "sky_pet_bed": "Sky Pet Bed"}

ITEM_TOOLTIPS = {
    "bunny_biscuit": "Tames Cotton, Lavender and Snowball Bunnies",
    "strawberry_tart": "Tames Strawberry Bunnies and Strawberry Mice",
    "moon_cookie": "Tames Moon Bunnies and Moon Deer",
    "blossom_mochi": "Tames Blossom Foxes and Cherry Blossom Birds",
    "fish_cracker": "Tames Cloud Kitties and Pastel Axolotls",
    "honey_cake": "Tames Honey Bears",
    "seed_medley": "Tames Tiny Swans and Dreamy Hamsters",
    "flower_nectar": "Tames Rainbow Butterflies",
    "pet_kibble": "Feeds any pet. Fill a Feeding Bowl with it",
    "pet_collar": "Use on your pet. Dye it in a crafting grid",
    "pet_bow": "Use on your pet. Dye it in a crafting grid",
    "yarn_ball": "Play with your pet. Cloud Kitties adore it",
    "squeaky_carrot": "Play with your pet. Bunnies adore it",
    "feather_wand": "Play with your pet. Pets follow it",
    "pet_journal": "Records every creature you discover",
    "cotton_fluff": "Soft stuffing shed by Cotton Bunnies",
}
for _a in ACCESSORY_ITEMS:
    ITEM_TOOLTIPS[_a] = "Use on your pet to dress it up"

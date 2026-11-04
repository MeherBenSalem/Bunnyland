"""The single list of Bunnyland sound events.

Shared by tools/generate_sounds.py (which synthesises the .ogg files and writes sounds.json),
tools/generate_assets.py (which writes the subtitle lang entries) and mirrored by
ModSounds.java. Keys are sound event paths under the ``bunnyland`` namespace.

Each entry: (subtitle, number of variant files, character brief for the synthesiser).
Files are written to assets/bunnyland/sounds/<event path with '.' -> '/'><n>.ogg, e.g.
entity.bunny.ambient -> sounds/entity/bunny/ambient1.ogg ... ambient3.ogg
"""

SOUND_EVENTS = {
    # --- Bunnies (shared by all five; each species plays them at its own pitch)
    "entity.bunny.ambient": ("Bunny sniffs", 3, "soft quick nose sniffs and a tiny chirp; very gentle"),
    "entity.bunny.hurt": ("Bunny squeaks", 2, "short startled squeak, high and soft, not harsh"),
    "entity.bunny.death": ("Bunny faints", 1, "small descending squeak that fades out"),
    "entity.bunny.happy": ("Bunny honks happily", 2, "rabbit 'honking': a run of soft low grunt-purrs"),

    # --- Blossom Fox
    "entity.blossom_fox.ambient": ("Blossom Fox yips", 3, "playful little fox yip / chirp, bright"),
    "entity.blossom_fox.hurt": ("Blossom Fox yelps", 2, "short yelp"),
    "entity.blossom_fox.death": ("Blossom Fox whimpers", 1, "soft descending whimper"),
    "entity.blossom_fox.happy": ("Blossom Fox giggles", 2, "rapid chattering 'giggle' of short chirps"),

    # --- Cloud Kitty
    "entity.cloud_kitty.ambient": ("Cloud Kitty mews", 3, "small kitten mew, sweet and airy"),
    "entity.cloud_kitty.hurt": ("Cloud Kitty hisses", 2, "short surprised mew (not a scary hiss)"),
    "entity.cloud_kitty.death": ("Cloud Kitty sighs", 1, "long soft falling mew"),
    "entity.cloud_kitty.purr": ("Cloud Kitty purrs", 2, "warm rhythmic purr about 1.5 s"),

    # --- Strawberry Mouse
    "entity.strawberry_mouse.ambient": ("Strawberry Mouse squeaks", 3, "tiny high squeaks, one to three"),
    "entity.strawberry_mouse.hurt": ("Strawberry Mouse eeps", 2, "sharp tiny eep"),
    "entity.strawberry_mouse.death": ("Strawberry Mouse squeals", 1, "falling tiny squeal"),

    # --- Honey Bear
    "entity.honey_bear.ambient": ("Honey Bear grumbles", 3, "cuddly low grumble / hum, cub-like"),
    "entity.honey_bear.hurt": ("Honey Bear groans", 2, "short low 'hrmf'"),
    "entity.honey_bear.death": ("Honey Bear moans", 1, "long low falling moan"),
    "entity.honey_bear.happy": ("Honey Bear hums", 2, "contented 'mmm' hum with a little rise"),

    # --- Moon Deer
    "entity.moon_deer.ambient": ("Moon Deer bleats", 3, "soft fawn bleat with light vibrato, airy"),
    "entity.moon_deer.hurt": ("Moon Deer bleats", 2, "short startled bleat"),
    "entity.moon_deer.death": ("Moon Deer sighs", 1, "falling breathy bleat"),

    # --- Pastel Axolotl
    "entity.pastel_axolotl.ambient": ("Pastel Axolotl bloops", 3, "bubbly 'bloop' chirps, watery resonance"),
    "entity.pastel_axolotl.hurt": ("Pastel Axolotl squeaks", 2, "squeaky bubbly blip"),
    "entity.pastel_axolotl.death": ("Pastel Axolotl fades", 1, "descending bubble blips"),

    # --- Tiny Swan
    "entity.tiny_swan.ambient": ("Tiny Swan honks", 3, "small, soft, nasal honk (cygnet-sized, not loud)"),
    "entity.tiny_swan.hurt": ("Tiny Swan squawks", 2, "short squawk"),
    "entity.tiny_swan.death": ("Tiny Swan cries", 1, "falling honk"),

    # --- Rainbow Butterfly
    "entity.rainbow_butterfly.ambient": ("Rainbow Butterfly flutters", 2, "very quiet sparkly shimmer with soft wing flutter"),
    "entity.rainbow_butterfly.hurt": ("Rainbow Butterfly flutters", 1, "quick sparkle blip"),
    "entity.rainbow_butterfly.death": ("Rainbow Butterfly fades", 1, "descending twinkle"),

    # --- Cherry Blossom Bird
    "entity.cherry_blossom_bird.ambient": ("Cherry Blossom Bird chirps", 3, "one to three cheerful songbird chirps"),
    "entity.cherry_blossom_bird.hurt": ("Cherry Blossom Bird cheeps", 2, "sharp cheep"),
    "entity.cherry_blossom_bird.death": ("Cherry Blossom Bird falls quiet", 1, "falling chirp"),
    "entity.cherry_blossom_bird.sing": ("Cherry Blossom Bird sings", 3, "short melodic songbird phrase ~1.5 s, pentatonic"),

    # --- Dreamy Hamster
    "entity.dreamy_hamster.ambient": ("Dreamy Hamster chitters", 3, "soft chittering, sleepy little squeaks"),
    "entity.dreamy_hamster.hurt": ("Dreamy Hamster squeaks", 2, "short squeak"),
    "entity.dreamy_hamster.death": ("Dreamy Hamster squeals", 1, "falling squeak"),

    # --- Shared pet sounds
    "entity.pet.happy": ("Pet sparkles with joy", 2, "magical rising bell chime arpeggio, ~0.8 s"),
    "entity.pet.eat": ("Pet munches", 3, "cute crunchy nibbling, 2-3 small bites"),
    "entity.pet.snore": ("Pet snores softly", 2, "tiny gentle snore / sleepy breath, ~1.2 s, quiet"),

    # --- Items & blocks
    "item.squeaky_carrot.squeak": ("Toy squeaks", 3, "rubber squeaky toy squeeze"),
    "item.pet_collar.jingle": ("Collar bell jingles", 2, "little bell jingle"),
    "item.pet_carrier.capture": ("Pet hops into carrier", 1, "soft rising 'pop' with a fabric rustle"),
    "item.pet_carrier.release": ("Pet hops out of carrier", 1, "soft falling 'pop'"),
    "block.feeding_bowl.fill": ("Kibble clinks into bowl", 2, "light kibble rattling into a ceramic bowl"),
}

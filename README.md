# Bunnyland 🐰

*A Sugarplum Studios mod for Minecraft Java 1.20.1, 1.21.1, 26.2 and 26.3, on Fabric, Forge and NeoForge (with GeckoLib)*

A world full of cute animals. Fifteen fairytale creatures live in Minecraft's meadows, flower forests, cherry
groves, snowy biomes, forests and rivers. Discover them, befriend them with their favourite treats, dress them up,
care for them, and breed them for rare cosmetic variants. A Pet Journal records everything you find.

Every creature has its own 3D GeckoLib model, a unique silhouette, painted textures with expressive blinking faces,
idle / walk / run / sit / sleep / eat animations plus happy, play and signature animations, original synthesised
sounds, natural spawning and its own behaviour.

---

## Installing

| Minecraft | Loaders | Java | Also install |
|---|---|---|---|
| 1.20.1 | Fabric, Forge (47.1+) | 17+ | GeckoLib 4 (4.4.9+); Fabric API on Fabric |
| 1.21.1 | Fabric, NeoForge | 21+ | GeckoLib 4 (4.8.4+); Fabric API on Fabric |
| 26.2 | Fabric, NeoForge | 25+ | GeckoLib 5 (5.5.5+); Fabric API on Fabric |
| 26.3 | Fabric, NeoForge | 25+ | GeckoLib 5 (5.5.7+); Fabric API on Fabric |

Put the jar for your loader and version (`bunnyland-<loader>-<minecraft>-1.0.0.jar`) and GeckoLib in your `mods`
folder.

The mod is needed on both the server and every client. On your first join you are given a **Pet Journal**.

---

## The creatures

| Creature | Lives in | Befriend with | Breed with | Special behaviour |
|---|---|---|---|---|
| **Cotton Bunny** | meadows, flower forests, plains, cherry groves | Bunny Biscuit | carrot, golden carrot, dandelion | Sheds **Cotton Fluff** every few minutes; lands softly |
| **Strawberry Bunny** | flower forests, meadows, sunflower plains, birch forests | Strawberry Tart | sweet berries, carrot | Hops over to ripe sweet berry bushes and nibbles them |
| **Moon Bunny** | meadows, groves, snowy slopes, snowy plains | Moon Cookie | glow berries, carrot | Night creature; glowing markings and a floating crescent moon; jumps high, never takes fall damage, walks on powder snow |
| **Lavender Bunny** | flower forests, meadows, cherry groves | Bunny Biscuit | carrot, allium, lilac | Lop-eared; sniffs flowers; petting a happy one gives you **Regeneration** for 5 s |
| **Snowball Bunny** | snowy plains, snowy taigas, ice spikes, groves, snowy slopes | Bunny Biscuit | carrot, beetroot | Can't freeze, walks on powder snow, kicks up snowflakes |
| **Blossom Fox** | cherry groves, flower forests, birch forests | Blossom Mochi | sweet berries, glow berries | Night creature; sheds cherry petals as it runs; spins and pounces |
| **Cloud Kitty** | meadows, cherry groves, plains, windswept hills | Fish Cracker | cod, salmon | Floats down instead of falling; purrs; **leaves a gift** when you wake up nearby |
| **Strawberry Mouse** | plains, meadows, flower forests, forests | Strawberry Tart | wheat, sweet berries | Tiny and quick; wild ones flee from cats and Cloud Kitties |
| **Honey Bear** | forests, birch forests, flower forests | Honey Cake | honeycomb, sweet berries | Sturdy (20 ❤); licks full beehives clean; a bee buddy orbits its head; stands up for hugs |
| **Moon Deer** | taigas, groves, forests, meadows | Moon Cookie | apple, glow berries, wheat | Night creature; glowing antlers and starry spots; steps up full blocks; very shy |
| **Pastel Axolotl** | rivers, swamps | Fish Cracker | tropical fish, kelp | Swims and walks; never dries out |
| **Tiny Swan** | rivers, swamps | Seed Medley | wheat seeds, beetroot seeds, bread | Floats and paddles; prefers water; cygnets follow their parents; heart-wing display |
| **Rainbow Butterfly** | flower forests, meadows, cherry groves, plains (daytime) | Flower Nectar | any small flower | Flies flower to flower and rests on them; sometimes **plants a new flower** |
| **Cherry Blossom Bird** | cherry groves, flower forests | Blossom Mochi | wheat seeds, melon seeds, pink petals | Flies and perches; sings in the daytime; **dances** next to a playing jukebox |
| **Dreamy Hamster** | plains, sunflower plains, meadows, savannas | Seed Medley | wheat seeds, pumpkin seeds, carrot | Night owl in a starry nightcap; stuffs its cheeks when it eats; blows dream bubbles while asleep |

The treat's tooltip tells you which creatures it tames, and the Pet Journal shows each creature's treat and foods.

### Variants

Every creature comes in 3–5 common colourways and 1–2 **rare variants**: 73 in all, 25 of them rare. Rare variants (Sugar Star,
Eclipse, Starlight, Golden Berry, Wisteria, Aurora, Twilight Blossom, Golden Hour, Storm, Rainbow, Royal Jelly,
Midnight Honey, Solar, Opal, Galaxy, Midnight, Golden, Prism, Golden Sakura, Starry Night, Cotton Candy...) never
spawn in the wild by default. They're only **born through breeding** (8 % chance, doubled when both parents are
overjoyed). Rare creatures sparkle, and most of them glow in the dark.

---

## How to...

### Find creatures
Each creature spawns in the biomes listed above. **Day creatures sleep at night, and night creatures (Moon Bunny,
Blossom Fox, Moon Deer, Dreamy Hamster) nap during the day.** You'll find them curled up with their eyes closed and
little Zzz's floating up.

Wild bunnies, mice, foxes and deer are **shy**: they run from players who aren't sneaking. **Sneak** to get close.
A sleeping wild creature wakes up if you walk right up to it without sneaking.

Any creature you can see within 16 blocks is written into your **Pet Journal** automatically.

### Befriend (tame) a creature
1. Craft its favourite treat (see the table and the recipes below).
2. Hold the treat. Wild creatures are tempted by it and come closer.
3. Use the treat on the creature. Each treat has a chance to work (1 in 2 for butterflies and hamsters, up to
   1 in 5 for the shy Moon Deer). Hearts mean success, smoke means "try again".

The wrong treat never works: a Bunny Biscuit won't tame a Honey Bear.

### Commands for your pet
| Action | What happens |
|---|---|
| Use with an **empty hand** | Toggle **sit / follow**. A sitting pet waits where it is |
| **Sneak** + use with an empty hand | **Pet** it: a happy animation and sound, hearts, more happiness. Shows its mood |
| Use a **Name Tag** | Name it (vanilla name tags) |
| Use a **Lead** | Leash it |
| Use its **food or a treat** | Feed it: heals, cheers it up, and grows babies up faster |
| Use **Shears** | Takes off one cosmetic at a time (accessory, then bow, then collar). You get the item back |
| Use the **Pet Journal** | Shows its species, variant and happiness |

Following pets teleport to you if left far behind (configurable). Like vanilla wolves and cats, pets sit and wait
while their owner is offline.

### Breed
Feed two adults of the same kind their **breeding food** (or their taming treat) while they are healthy. Tamed pets
need at least **40 % happiness** to breed; a lonely pet tells you it isn't in the mood. Babies inherit a parent's
colour (or are born rare!), belong to the parents' owner, and grow up faster when fed. Swan cygnets follow their
parents in a line.

### Care for your pet
Care is light. No pet ever dies or runs away from neglect.

- **Happiness (0–100 %)** goes up when you pet it (once every 30 s), feed it, play with it, dress it up, and when it
  eats from a bowl or sleeps in a pet bed. It drops slowly over time (1 point every 3 minutes, never below 10) and when
  the pet gets hurt.
- **Moods**: *a little lonely* (under 25, shows little rain drops), *content*, *happy* (60+), *overjoyed* (85+,
  floating hearts and the occasional **zoomies**).
- **Happy and overjoyed pets slowly regenerate health.**
- **Feeding Bowl**: fill it with Pet Kibble or any treat (up to 8 portions, shown in the bowl). A tamed pet that is
  hurt or a little sad walks over by itself and eats a portion. Comparators read how full it is.
- **Pet Beds**: at bedtime, a tamed pet that isn't sitting finds a free bed within 12 blocks and curls up in it.
  Pets also fall asleep wherever they are when **you** go to sleep nearby.
- **Toys**: use a toy on your pet, or use it in the air to play with every pet of yours within 8 blocks.
  - *Yarn Ball*: favourite of Cloud Kitties, Blossom Foxes and Honey Bears
  - *Squeaky Carrot*: favourite of bunnies, mice and hamsters
  - *Feather Wand*: favourite of kitties, birds, butterflies, swans, deer and axolotls. Pets also follow it like a treat.
  A favourite toy cheers a pet up almost twice as much (+18 instead of +10). Toys wear out slowly (64 uses), and a
  pet needs a 10 s rest between games.

### Dress up
Use a cosmetic item on **your own** pet. Every creature has its own fitted version of each accessory.

- **Pet Collar** with a little gold bell, and **Pet Bow**. Both can be **dyed any colour**: put one in a crafting
  grid with dyes, like leather armour. Swapping returns the old one with its colour.
- One **accessory** at a time: **Flower Crown, Tiny Top Hat, Party Hat, Star Clip, Heart Glasses, Cozy Scarf**.
  (Hats replace the Dreamy Hamster's nightcap while worn.)

### Carry a pet
Use a **Pet Carrier** on your pet to pick it up. Its name, variant, happiness and outfit are all kept, and the
tooltip shows who's inside. Use the carrier on a block to let it out again.

### Pet Journal
Use it to open the journal:
- **Index page**: how many creatures you've discovered and befriended, and how many rare variants you've seen. Click
  a name to jump to its page.
- **Creature pages**: a live animated model (drag to turn it), its variants (rare ones starred; click one you've
  seen to preview it), description, habitat, taming treat, favourite foods and a tip. Undiscovered creatures appear
  as silhouettes with a hint about where to look.
- Toasts pop up when you discover a creature, befriend a new kind, or find a rare variant.

Use the arrow keys or the page arrows to turn pages.

---

## Recipes

| Item | Recipe |
|---|---|
| Bunny Biscuit ×4 | carrot + wheat + sugar (shapeless) |
| Strawberry Tart ×3 | 2 sweet berries + wheat + sugar + egg |
| Moon Cookie ×4 | glow berries + wheat + sugar |
| Blossom Mochi ×4 | pink petals + wheat + sugar |
| Fish Cracker ×4 | any fish + wheat |
| Honey Cake ×2 | honey bottle + wheat + sugar + egg |
| Seed Medley ×2 | wheat seeds + 2 any seeds |
| Flower Nectar ×2 | honey bottle + 2 small flowers |
| Pet Kibble ×6 | 2 wheat + carrot, potato, beetroot, apple, sweet berries or melon slice |
| Pet Collar | `S L S` / ` G ` (string, leather, gold nugget) |
| Pet Bow ×2 | any wool + string |
| Flower Crown | `F F F` / `F _ F` (small flowers) |
| Tiny Top Hat | ` B ` / `B P B` (black wool, pink dye) |
| Party Hat | ` S ` / `P D P` (string, paper, pink dye) |
| Star Clip ×2 | ` G ` / `G S G` / ` I ` (gold nugget, glowstone dust, iron nugget) |
| Heart Glasses | `P I P` (pink stained glass pane, iron nugget) |
| Cozy Scarf | `W W W` / `W _ _` (any wool) |
| Yarn Ball | any wool + 2 string |
| Squeaky Carrot | carrot + slime ball |
| Feather Wand | feather on top of a diagonal of 2 sticks |
| Pet Carrier | ` L ` / `P I P` / `P P P` (leather, planks, iron bars) |
| Pet Journal | book + feather + small flower |
| Feeding Bowl | `T _ T` / ` T ` (any terracotta) |
| Pet Bed (pink / lavender / mint / sky) | `W F W` / `S S S`: pink / purple / lime / light blue wool, stuffing (Cotton Fluff, feather or white wool), wooden slabs |
| String | 2 Cotton Fluff |
| White Wool | 4 Cotton Fluff (2×2) |

The treats are snacks for you too.

---

## Commands & spawn eggs

All creatures have spawn eggs in the **Bunnyland** creative tab. With commands:

```
/summon bunnyland:cotton_bunny ~ ~ ~
/summon bunnyland:moon_bunny ~ ~ ~ {Variant:4}
/summon bunnyland:honey_bear ~ ~ ~ {Accessory:"party_hat",CollarColor:16748491}
```

Entity ids: `cotton_bunny, strawberry_bunny, moon_bunny, lavender_bunny, snowball_bunny, blossom_fox, cloud_kitty,
strawberry_mouse, honey_bear, moon_deer, pastel_axolotl, tiny_swan, rainbow_butterfly, cherry_blossom_bird,
dreamy_hamster`.

Useful NBT: `Variant` (index, common variants first), `Happiness` (0–100), `CollarColor` / `BowColor` (RGB int),
`Accessory` (`flower_crown`, `tiny_top_hat`, `party_hat`, `star_clip`, `heart_glasses`, `cozy_scarf`), `Napping`.

## Advancements

*Bunnyland* → *A Furry Friend* (befriend anything) → *A Whole Fluffle* (all five bunnies) →
*Best Friends Forever* (all fifteen). Also *Once in a Blue Moon* (breed a rare variant) and *Snug as a Bunny*
(place a pet bed).

---

## Configuration

`config/bunnyland-common.toml` (server rules):
- **spawning**: global `spawnWeightMultiplier`, and per creature `enabled`, `weight`, `minGroup`, `maxGroup`.
  Spawn biomes come from the biome tags `bunnyland:spawns/<creature>`, which data packs can override.
- **breeding**: `rareOffspringChance` (0.08), `naturalRareChance` (0 = rare variants only from breeding),
  `breedingHappiness` (40).
- **care**: `happinessDecay`, `happinessDecayMinutes` (3), `petsTeleport`.
- **behaviour**: `wildCreaturesAreShy`, `cottonFluffMinutes`, `butterfliesSpreadFlowers`, `honeyBearsLickHives`,
  `berryBunniesEatBerries` (block changes also respect the `mobGriefing` game rule).
- **journal**: `discoveryRange` (16), `starterJournal`.

`config/bunnyland-client.toml`: `ambientParticles`, `journalToasts`.

---

## For developers

The repository holds one MultiLoader workspace per Minecraft version, laid out like the other Sugarplum/NightBeam
mods: `1.20.1/` (common, fabric, forge), `1.21.1/`, `26.2/` and `26.3/` (common, fabric, neoforge). `common` holds all
gameplay, rendering and data; the loader modules are thin layers (registration, networking, events, spawn rules,
biome spawns, client registration) behind `platform.IPlatform`.

```
cd 1.20.1 && ./gradlew build              # fabric/build/libs and forge/build/libs (Java 17)
cd 1.21.1 && ./gradlew build              # Java 21
cd 26.2 && ./gradlew build                # Java 25 (26.3 likewise)
./gradlew :fabric:runClient               # play in a dev client (also :forge: / :neoforge:)
./gradlew :forge:runGameTestServer        # 1.20.1: 17 headless GameTests (also :neoforge: on 1.21.1)
./gradlew :forge:runSnapshots             # 1.20.1: builds a showcase world, saves screenshots and quits
python tools/generate_assets.py           # regenerates models, textures, animations, item art, data and lang
python tools/generate_sounds.py           # re-synthesises every sound (needs ffmpeg on PATH)
python tools/port_data.py 1.21.1          # derives 1.21.1/26.2/26.3 resources from the 1.20.1 ones
```

The Python tools write `1.20.1/common/src/main/resources` (standard library only). Models are written as
GeckoLib/Bedrock `.geo.json` with per-face UVs. Textures are painted procedurally per material, with decals for faces
and markings. Animations are baked from code into keyframes. Sounds are synthesised from scratch and encoded to OGG
Vorbis with ffmpeg. `tools/port_data.py` then rewrites that data for newer versions (1.21 folder names, recipe and
advancement formats, item model definitions, GeckoLib 5 asset folders, spawn egg textures).

Code layout (`com.sugarplumstudios.bunnyland`): `creature` (species table, accessories, moods), `entity` (the shared
`BunnylandAnimal` base, `FlyingCreature`, one class per creature) and `entity.ai` (napping, owner-following for any
movement type, pet beds, bowls, zoomies, block visits), `item`, `block`, `journal` (world-saved per-player journal +
discovery), `network`, `world` (spawn placement rules), `config` (a small TOML config shared by every loader),
`platform` (the loader interface), `client` (GeckoLib model and renderer with dye tinting and a glow layer, journal
screen, toasts, particles). The Forge module also holds `gametest` and the snapshot harness.

# Marketing assets: 1.0 "First Bloom"

Listing copy and artwork for CurseForge and Modrinth. Nothing here ships in the mod JAR.

## Listing

| File | Use |
| --- | --- |
| [`curseforge/description.md`](curseforge/description.md) | Full project description (Markdown; also works on Modrinth) |
| [`curseforge/summary.txt`](curseforge/summary.txt) | Short project summary (226 characters) |
| `images/icon.png` | Project avatar |

Image links in the description point at `raw.githubusercontent.com/MeherBenSalem/Bunnyland/main/marketing/images/...`, so they work once this folder is on `main`. To host on CurseForge instead, upload the images to the project gallery and replace each URL.

The description leads with the pitch, then the creatures, where to find them (with the night creatures), befriending, variants and breeding, dress-up, pet care, personalities, the Pet Journal, recipes, configuration, everything else, downloads and compatibility, the FAQ and a gallery.

## Adding a Minecraft version

The supported versions are listed in exactly two places:

1. `VERSIONS` at the top of [`source/render.cjs`](source/render.cjs). Add one line, for example `{ minecraft: '1.21.1', loaders: ['NeoForge'] },`. The banner's loader pills and version line are built from it. Then rerun the script for `banner`.
2. The table under **Downloads & Compatibility** in `curseforge/description.md`. Add one row.

No other copy or artwork names a Minecraft version. A new release name or number goes in `RELEASE` in `render.cjs` and in the banner's alt text on the first line of the description.

## Images

| File | Size | Use |
| --- | --- | --- |
| `images/banner.png` | 1800×600, 1159 KB | Description header: the cherry grove scene, the logo, "1.0 · First Bloom", the loader, GeckoLib and version pills |
| `images/icon.png` | 512×512, 95 KB | Project avatar: the mod logo (`bunnyland_logo.png`) in a pink and lavender ring |
| `images/card-creatures.png` | 1600×900, 1353 KB | All fifteen creatures, one portrait each; night creatures marked with a moon |
| `images/card-habitats.png` | 1600×900, 1371 KB | Cherry grove, snowy taiga, river and forest |
| `images/card-night.png` | 1600×900, 1020 KB | Moon Bunnies and Moon Deer glowing at midnight |
| `images/card-befriend.png` | 1600×900, 1377 KB | A Bunny Biscuit taming a bunny and a pat with its mood readout, plus the eight treats |
| `images/card-variants.png` | 1600×900, 1310 KB | Every Cotton Bunny colourway and a rare line-up; 73 variants, 25 rare, 8%, ×2 |
| `images/card-dress-up.png` | 1600×900, 1292 KB | Seven dressed-up pets, plus the collar, bow and six accessories |
| `images/card-care.png` | 1600×900, 1345 KB | Napping pets in the four pet beds next to feeding bowls, plus the four moods |
| `images/card-personality.png` | 1600×900, 1323 KB | The forest (Honey Bear and beehive, Strawberry Bunny, Strawberry Mouse) and a swan family |
| `images/card-journal.png` | 1600×900, 1008 KB | The Pet Journal index and the Honey Bear page |
| `images/card-config.png` | 1600×900, 696 KB | Excerpts of `bunnyland-common.toml` and a spawn biome tag |
| `images/header-*.png` | 1400×120, transparent, 30–54 KB | 14 section headings for the description |
| `images/divider.png` | 1400×40, transparent | Section divider |
| `images/screenshots/*.jpg` | 1920×1080, 209–593 KB | 15 captures: gallery uploads and card art |
| `images/screenshots/portraits/*.jpg` | 720×720, about 140 KB | One portrait per creature for `card-creatures` |

### How the screenshots were captured

Every screenshot is an unedited capture of the **1.20.1 Forge development client** (`./gradlew runClient`, Bunnyland 1.0.0, GeckoLib 4.8.4, default configuration) with software rendering (Mesa llvmpipe) at 1920×1080, GUI scale 3 and Fancy graphics. The client joined a dev server (`./gradlew runServer`) and was driven over RCON and xdotool; [`source/devrun.sh`](source/devrun.sh) starts both under Xvfb, [`source/session.py`](source/session.py) talks to them, and [`source/stage.py`](source/stage.py) holds the staging helpers (ground probes, frozen creatures, camera placement, bursts).

- **World:** a fresh world, "showcase", seed `sugarplum-meadows` (`server.properties`), in Peaceful with the day cycle and weather off. The scenes are in the world's own generated terrain: a cherry grove at about −80 −1056, the snowy taiga and frozen lake at spawn, and the river and forest at about 240 −150.
- **Changes for the shots:** grass in front of the camera was cleared so it does not hide the creatures. The care shot places the four pet beds and three feeding bowls; the forest shot places a beehive, two berry bushes and a few flowers.
- **Creatures** are spawned with `/summon` and frozen with `NoAI` so they hold still; variants, outfits, naps and ages are their NBT (`Variant`, `Accessory`, `CollarColor`, `BowColor`, `Napping`, `Age`). Butterflies and the bird in flight also have `NoGravity`. Everything they show (models, animations, glow, sparkles, faces) comes from the mod as it runs.
- **Camera:** a spectator camera placed with `/tp`, with the HUD hidden (F1), except for `befriend`, `petting` and the three journal shots. Bursts of three or four frames were taken and the frame with open eyes and spread wings kept.
- **Lighting:** the daytime scenes use Night Vision, which evens out the light under the cherry canopy; `moonlit-night` does not, so the glow reads as it does in play. `rare-variants` and `beds-and-bowls` are at sunset.
- **Befriend and petting:** real interactions. A Bunny Biscuit was used on a wild, frozen Cotton Bunny named Mochi until it was tamed; then it was given a flower crown and a collar with `/data merge` and petted while sneaking.
- **Journal:** the player had discovered all fifteen kinds (and nine rare variants) and befriended six, each with its own treat, before the journal was opened.
- **Portraits:** [`source/portraits.py`](source/portraits.py) takes one portrait per creature on the same patch of the grove; each kept frame is cropped to a square around the creature and scaled to 720×720.

## Regenerating the artwork

The cards, banner, icon and headers are HTML rendered with Playwright from the screenshots, the mod's own logo and item textures, and the bundled fonts:

```bash
NODE_PATH="$(npm root -g)" node marketing/source/render.cjs            # everything
NODE_PATH="$(npm root -g)" node marketing/source/render.cjs banner icon  # selected assets
```

- `source/backdrop.jpg` is the blurred background scene, a 1280×720 copy of `screenshots/cherry-grove.jpg`.
- `source/logo.png` is the mod logo (`src/main/resources/bunnyland_logo.png`).
- The treat, cosmetic and toy icons are read straight from `src/main/resources/assets/bunnyland/textures/item/`. The collar and bow textures are greyscale, so the cards tint them with the items' default colours, the way the game does.
- `source/fonts/` holds Fredoka and Nunito with their SIL Open Font License 1.1 texts. The script uses only these files.

Creature names, treats, cosmetics and moods on the cards are written at the top of `render.cjs`, copied from `creature/Species.java`, `creature/Mood.java`, `item/DyeableCosmeticItem.java` and the lang file. Update them when those change. Card crops are pixel regions of the 1920×1080 captures (`region()` calls), so new captures may need their crops adjusted.

To retake screenshots:

```bash
JAVA_HOME=/path/to/jdk-17 marketing/source/devrun.sh prepare
```

```bash
marketing/source/devrun.sh display
```

```bash
JAVA_HOME=/path/to/jdk-17 marketing/source/devrun.sh server
```

```bash
JAVA_HOME=/path/to/jdk-17 marketing/source/devrun.sh client
```

Then stage a scene from Python with `from stage import *; connect()` (run from `marketing/source/`), and save it with `save('name')` or keep a burst frame with `keep(frame, 'name')`.

## Wording

Every number in the copy and on the cards is a 1.0.0 default from the generated config (`config/bunnyland-common.toml`), a recipe, a tag, or the code. Update the copy when those defaults change. Call the tamed creatures **pets** and the act of taming **befriending**; the rare colourways are **rare variants**.

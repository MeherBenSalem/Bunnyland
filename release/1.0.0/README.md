# Bunnyland 1.0.0 "First Bloom": release files

Each jar targets one Minecraft version and one loader. On CurseForge, upload each file separately and tick the matching game version, loader and Java version. Add GeckoLib (and Fabric API on Fabric) as required dependencies. Paste `patchnotes/1.0.0.md` as the changelog.

| File | Minecraft | Loader | Java | Required dependencies |
|---|---|---|---|---|
| `bunnyland-forge-1.20.1-1.0.0.jar` | 1.20.1 | Forge | 17 | GeckoLib 4 (4.4.9+) |
| `bunnyland-fabric-1.20.1-1.0.0.jar` | 1.20.1 | Fabric | 17 | Fabric API, GeckoLib 4 (4.4.9+) |
| `bunnyland-neoforge-1.21.1-1.0.0.jar` | 1.21.1 | NeoForge | 21 | GeckoLib 4 (4.8.4+) |
| `bunnyland-fabric-1.21.1-1.0.0.jar` | 1.21.1 | Fabric | 21 | Fabric API, GeckoLib 4 (4.8.4+) |
| `bunnyland-neoforge-26.2-1.0.0.jar` | 26.2 | NeoForge | 25 | GeckoLib 5 (5.5.5+) |
| `bunnyland-fabric-26.2-1.0.0.jar` | 26.2 | Fabric | 25 | Fabric API, GeckoLib 5 (5.5.5+) |
| `bunnyland-neoforge-26.3-1.0.0.jar` | 26.3 | NeoForge | 25 | GeckoLib 5 (5.5.7+) |
| `bunnyland-fabric-26.3-1.0.0.jar` | 26.3 | Fabric | 25 | Fabric API, GeckoLib 5 (5.5.7+) |

Built from this commit with `./gradlew build` in each version folder. Every jar passed a dedicated-server and client smoke test (all 15 creatures summoned, rendered and saved; recipes, advancements, biome tags and items loaded).

package com.sugarplumstudios.bunnyland.config;

import com.sugarplumstudios.bunnyland.platform.Services;
import com.sugarplumstudios.bunnyland.creature.Species;
import java.util.EnumMap;
import java.util.Map;

public final class BunnylandConfig {
    private static final TomlConfig.Builder COMMON_BUILDER = new TomlConfig.Builder();
    public static final Common COMMON = new Common(COMMON_BUILDER);
    private static final TomlConfig COMMON_FILE = COMMON_BUILDER.build("bunnyland-common.toml");
    private static final TomlConfig.Builder CLIENT_BUILDER = new TomlConfig.Builder();
    public static final Client CLIENT = new Client(CLIENT_BUILDER);
    private static final TomlConfig CLIENT_FILE = CLIENT_BUILDER.build("bunnyland-client.toml");

    /** Server rules; read at mod start. */
    public static void loadCommon() {
        COMMON_FILE.load(Services.PLATFORM.configDir());
    }

    /** Client options; read when the client starts. */
    public static void loadClient() {
        CLIENT_FILE.load(Services.PLATFORM.configDir());
    }

    private BunnylandConfig() {
    }

    public static final class SpawnSettings {
        public final TomlConfig.BooleanValue enabled;
        public final TomlConfig.IntValue weight;
        public final TomlConfig.IntValue minGroup;
        public final TomlConfig.IntValue maxGroup;

        SpawnSettings(TomlConfig.Builder builder, Species species) {
            builder.push(species.id);
            enabled = builder.comment("Whether " + species.id + " spawns naturally.").define("enabled", true);
            weight = builder.comment("Spawn weight (vanilla sheep use 12, cows 8).")
                    .defineInRange("weight", species.defaultWeight, 0, 100);
            minGroup = builder.defineInRange("minGroup", species.defaultMinGroup, 1, 8);
            maxGroup = builder.defineInRange("maxGroup", species.defaultMaxGroup, 1, 8);
            builder.pop();
        }
    }

    public static final class Common {
        public final Map<Species, SpawnSettings> spawns = new EnumMap<>(Species.class);
        public final TomlConfig.DoubleValue spawnWeightMultiplier;
        public final TomlConfig.DoubleValue rareOffspringChance;
        public final TomlConfig.DoubleValue naturalRareChance;
        public final TomlConfig.BooleanValue happinessDecay;
        public final TomlConfig.IntValue happinessDecayMinutes;
        public final TomlConfig.IntValue breedingHappiness;
        public final TomlConfig.BooleanValue petsTeleport;
        public final TomlConfig.BooleanValue wildCreaturesAreShy;
        public final TomlConfig.IntValue cottonFluffMinutes;
        public final TomlConfig.BooleanValue butterfliesSpreadFlowers;
        public final TomlConfig.BooleanValue honeyBearsLickHives;
        public final TomlConfig.BooleanValue berryBunniesEatBerries;
        public final TomlConfig.IntValue discoveryRange;
        public final TomlConfig.BooleanValue starterJournal;

        Common(TomlConfig.Builder builder) {
            builder.comment("Natural spawning. Biomes are chosen by the biome tags bunnyland:spawns/<creature>,",
                    "which data packs can override.").push("spawning");
            spawnWeightMultiplier = builder.comment("Multiplies every creature's spawn weight.")
                    .defineInRange("spawnWeightMultiplier", 1.0D, 0.0D, 10.0D);
            for (Species s : Species.values()) {
                spawns.put(s, new SpawnSettings(builder, s));
            }
            builder.pop();

            builder.comment("Breeding and rare variants").push("breeding");
            rareOffspringChance = builder.comment("Chance that a baby is born as a rare variant (doubled when both parents are overjoyed).")
                    .defineInRange("rareOffspringChance", 0.08D, 0.0D, 1.0D);
            naturalRareChance = builder.comment("Chance that a naturally spawned creature is a rare variant (0 = breeding only).")
                    .defineInRange("naturalRareChance", 0.0D, 0.0D, 1.0D);
            breedingHappiness = builder.comment("Minimum happiness a tamed pet needs before it will breed.")
                    .defineInRange("breedingHappiness", 40, 0, 100);
            builder.pop();

            builder.comment("Pet care").push("care");
            happinessDecay = builder.comment("Pets slowly get lonely when nobody plays with them (never below 10).")
                    .define("happinessDecay", true);
            happinessDecayMinutes = builder.comment("Minutes between each point of happiness lost.")
                    .defineInRange("happinessDecayMinutes", 3, 1, 120);
            petsTeleport = builder.comment("Following pets teleport to their owner when left far behind.")
                    .define("petsTeleport", true);
            builder.pop();

            builder.comment("Creature behaviour").push("behaviour");
            wildCreaturesAreShy = builder.comment("Wild bunnies, mice, foxes and deer run from players who aren't sneaking.")
                    .define("wildCreaturesAreShy", true);
            cottonFluffMinutes = builder.comment("Average minutes between Cotton Fluff drops from an adult Cotton Bunny.")
                    .defineInRange("cottonFluffMinutes", 8, 1, 120);
            butterfliesSpreadFlowers = builder.comment("Resting butterflies sometimes plant a matching flower nearby.")
                    .define("butterfliesSpreadFlowers", true);
            honeyBearsLickHives = builder.comment("Honey Bears empty full beehives and bee nests by licking the honey.")
                    .define("honeyBearsLickHives", true);
            berryBunniesEatBerries = builder.comment("Strawberry Bunnies nibble ripe sweet berry bushes.")
                    .define("berryBunniesEatBerries", true);
            builder.pop();

            builder.comment("Pet Journal").push("journal");
            discoveryRange = builder.comment("Blocks within which a visible creature counts as discovered.")
                    .defineInRange("discoveryRange", 16, 4, 64);
            starterJournal = builder.comment("Give every player a Pet Journal the first time they join.")
                    .define("starterJournal", true);
            builder.pop();
        }
    }

    public static final class Client {
        public final TomlConfig.BooleanValue ambientParticles;
        public final TomlConfig.BooleanValue journalToasts;

        Client(TomlConfig.Builder builder) {
            ambientParticles = builder.comment("Mood hearts, sleepy Zzz's, sparkles and petals around creatures.")
                    .define("ambientParticles", true);
            journalToasts = builder.comment("Show a toast when you discover or befriend a creature.")
                    .define("journalToasts", true);
        }
    }
}

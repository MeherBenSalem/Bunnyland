package com.sugarplumstudios.bunnyland.creature;

import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.biome.Biome;

import java.util.List;

/**
 * Every Bunnyland creature and its fixed traits. The variant lists mirror tools/assetgen/variants.py:
 * the variant index stored on an entity is its position in {@code common} followed by {@code rare}.
 */
public enum Species {
    COTTON_BUNNY("cotton_bunny", Schedule.DAY, 3, 1.15F, 0.35F,
            List.of("classic", "cocoa", "cream"), List.of("sugar_star", "cotton_candy"), 8, 2, 4),
    STRAWBERRY_BUNNY("strawberry_bunny", Schedule.DAY, 3, 1.1F, 0.35F,
            List.of("classic", "pineberry", "chocolate_dipped"), List.of("golden_berry"), 6, 2, 3),
    MOON_BUNNY("moon_bunny", Schedule.NIGHT, 4, 1.25F, 0.32F,
            List.of("midnight", "dusk", "silver"), List.of("eclipse", "starlight"), 4, 1, 3),
    LAVENDER_BUNNY("lavender_bunny", Schedule.DAY, 3, 1.05F, 0.35F,
            List.of("lavender", "lilac", "periwinkle"), List.of("wisteria"), 6, 2, 3),
    SNOWBALL_BUNNY("snowball_bunny", Schedule.DAY, 3, 1.2F, 0.38F,
            List.of("snow", "frost", "peppermint"), List.of("aurora"), 8, 2, 4),
    BLOSSOM_FOX("blossom_fox", Schedule.NIGHT, 4, 1.05F, 0.4F,
            List.of("sakura", "peach", "snow_blossom"), List.of("twilight_blossom", "golden_hour"), 5, 1, 3),
    CLOUD_KITTY("cloud_kitty", Schedule.DAY, 3, 1.15F, 0.35F,
            List.of("sky", "sunset", "lilac_mist"), List.of("storm", "rainbow"), 4, 1, 2),
    STRAWBERRY_MOUSE("strawberry_mouse", Schedule.DAY, 3, 1.5F, 0.2F,
            List.of("classic", "white_chocolate", "blueberry"), List.of("golden_berry"), 6, 2, 4),
    HONEY_BEAR("honey_bear", Schedule.DAY, 4, 0.8F, 0.6F,
            List.of("honey", "cinnamon", "vanilla"), List.of("royal_jelly", "midnight_honey"), 3, 1, 2),
    MOON_DEER("moon_deer", Schedule.NIGHT, 5, 1.0F, 0.6F,
            List.of("midnight", "dawn", "frost"), List.of("aurora", "solar"), 4, 1, 3),
    PASTEL_AXOLOTL("pastel_axolotl", Schedule.DAY, 3, 1.2F, 0.35F,
            List.of("bubblegum", "mint", "lavender", "peach"), List.of("opal", "galaxy"), 6, 1, 3),
    TINY_SWAN("tiny_swan", Schedule.DAY, 3, 1.15F, 0.35F,
            List.of("white", "blush", "dove"), List.of("midnight", "golden"), 6, 2, 4),
    RAINBOW_BUTTERFLY("rainbow_butterfly", Schedule.DAY, 2, 1.4F, 0.15F,
            List.of("rainbow", "sunset", "ocean", "candy", "meadow"), List.of("aurora", "prism"), 14, 2, 4),
    CHERRY_BLOSSOM_BIRD("cherry_blossom_bird", Schedule.DAY, 3, 1.3F, 0.22F,
            List.of("blossom", "snow", "plum"), List.of("golden_sakura"), 8, 2, 4),
    DREAMY_HAMSTER("dreamy_hamster", Schedule.NIGHT, 2, 1.35F, 0.28F,
            List.of("cream", "caramel", "lavender_dream"), List.of("starry_night", "cotton_candy"), 5, 1, 3);

    public enum Schedule {
        /** Awake by day, sleeps at night. */
        DAY,
        /** Awake at night, naps through the day. */
        NIGHT
    }

    public final String id;
    public final Schedule schedule;
    /** One in this many treats tames a wild creature. */
    public final int tameOdds;
    public final float voicePitch;
    public final float shadowRadius;
    public final List<String> common;
    public final List<String> rare;
    public final int defaultWeight;
    public final int defaultMinGroup;
    public final int defaultMaxGroup;
    public final TagKey<Item> tamingTreats;
    public final TagKey<Item> breedingFood;
    public final TagKey<Item> tempting;
    public final TagKey<Biome> spawnBiomes;
    private final ResourceLocation model;
    private final ResourceLocation animation;
    private final ResourceLocation[] textures;
    private final ResourceLocation[] glowTextures;

    Species(String id, Schedule schedule, int tameOdds, float voicePitch, float shadowRadius,
            List<String> common, List<String> rare, int weight, int minGroup, int maxGroup) {
        this.id = id;
        this.schedule = schedule;
        this.tameOdds = tameOdds;
        this.voicePitch = voicePitch;
        this.shadowRadius = shadowRadius;
        this.common = common;
        this.rare = rare;
        this.defaultWeight = weight;
        this.defaultMinGroup = minGroup;
        this.defaultMaxGroup = maxGroup;
        this.tamingTreats = TagKey.create(Registries.ITEM, Bunnyland.id("taming_treats/" + id));
        this.breedingFood = TagKey.create(Registries.ITEM, Bunnyland.id("breeding_food/" + id));
        this.tempting = TagKey.create(Registries.ITEM, Bunnyland.id("tempting/" + id));
        this.spawnBiomes = TagKey.create(Registries.BIOME, Bunnyland.id("spawns/" + id));
        this.model = Bunnyland.id("geo/entity/" + id + ".geo.json");
        this.animation = Bunnyland.id("animations/entity/" + id + ".animation.json");
        int n = common.size() + rare.size();
        this.textures = new ResourceLocation[n];
        this.glowTextures = new ResourceLocation[n];
        for (int i = 0; i < n; i++) {
            textures[i] = Bunnyland.id("textures/entity/" + id + "/" + variantName(i) + ".png");
            glowTextures[i] = Bunnyland.id("textures/entity/" + id + "/" + variantName(i) + "_glow.png");
        }
    }

    public MobCategory category() {
        return this == RAINBOW_BUTTERFLY ? MobCategory.AMBIENT : MobCategory.CREATURE;
    }

    public boolean isBunny() {
        return ordinal() <= SNOWBALL_BUNNY.ordinal();
    }

    public int variantCount() {
        return common.size() + rare.size();
    }

    public boolean isRare(int variant) {
        return variant >= common.size();
    }

    public int clampVariant(int variant) {
        return variant < 0 || variant >= variantCount() ? 0 : variant;
    }

    public String variantName(int variant) {
        variant = clampVariant(variant);
        return variant < common.size() ? common.get(variant) : rare.get(variant - common.size());
    }

    public int variantByName(String name) {
        for (int i = 0; i < variantCount(); i++) {
            if (variantName(i).equals(name)) return i;
        }
        return -1;
    }

    public int randomCommonVariant(RandomSource random) {
        return random.nextInt(common.size());
    }

    public int randomRareVariant(RandomSource random) {
        return common.size() + random.nextInt(rare.size());
    }

    /** Babies take after one parent; with {@code rareChance} they are born a rare variant instead. */
    public int rollOffspringVariant(RandomSource random, int parentA, int parentB, double rareChance) {
        if (random.nextDouble() < rareChance) return randomRareVariant(random);
        return clampVariant(random.nextBoolean() ? parentA : parentB);
    }

    public ResourceLocation model() {
        return model;
    }

    public ResourceLocation animation() {
        return animation;
    }

    public ResourceLocation texture(int variant) {
        return textures[clampVariant(variant)];
    }

    public ResourceLocation glowTexture(int variant) {
        return glowTextures[clampVariant(variant)];
    }

    public String translationKey() {
        return "entity." + Bunnyland.MOD_ID + "." + id;
    }

    public Component displayName() {
        return Component.translatable(translationKey());
    }

    public Component variantDisplayName(int variant) {
        return Component.translatable("variant." + Bunnyland.MOD_ID + "." + id + "." + variantName(variant));
    }

    public Component journalText(String field) {
        return Component.translatable("journal." + Bunnyland.MOD_ID + "." + id + "." + field);
    }

    public static Species byId(String id) {
        for (Species s : values()) {
            if (s.id.equals(id)) return s;
        }
        return null;
    }

    public static Species byOrdinal(int ordinal) {
        Species[] all = values();
        return ordinal >= 0 && ordinal < all.length ? all[ordinal] : null;
    }
}

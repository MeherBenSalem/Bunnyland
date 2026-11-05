package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.platform.Services;
import net.minecraft.core.registries.Registries;
import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.creature.Accessory;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.item.AccessoryItem;
import com.sugarplumstudios.bunnyland.item.DyeableCosmeticItem;
import com.sugarplumstudios.bunnyland.item.PetCarrierItem;
import com.sugarplumstudios.bunnyland.item.PetJournalItem;
import com.sugarplumstudios.bunnyland.item.PetToyItem;
import com.sugarplumstudios.bunnyland.item.TooltipItem;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import com.sugarplumstudios.bunnyland.platform.RegistryEntry;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public final class ModItems {
    /** Everything in creative-tab order. */
    public static final List<RegistryEntry<? extends Item>> TAB_ORDER = new ArrayList<>();
    public static final Map<Species, RegistryEntry<Item>> SPAWN_EGGS = new EnumMap<>(Species.class);

    // Treats (players can snack on them too)
    public static final RegistryEntry<Item> BUNNY_BISCUIT = treat("bunny_biscuit", 2, 0.3F);
    public static final RegistryEntry<Item> STRAWBERRY_TART = treat("strawberry_tart", 3, 0.4F);
    public static final RegistryEntry<Item> MOON_COOKIE = treat("moon_cookie", 2, 0.3F);
    public static final RegistryEntry<Item> BLOSSOM_MOCHI = treat("blossom_mochi", 3, 0.4F);
    public static final RegistryEntry<Item> FISH_CRACKER = treat("fish_cracker", 2, 0.4F);
    public static final RegistryEntry<Item> HONEY_CAKE = treat("honey_cake", 4, 0.5F);
    public static final RegistryEntry<Item> SEED_MEDLEY = register("seed_medley", () -> new TooltipItem(new Item.Properties()));
    public static final RegistryEntry<Item> FLOWER_NECTAR = register("flower_nectar", () -> new TooltipItem(new Item.Properties().stacksTo(16)));
    public static final RegistryEntry<Item> PET_KIBBLE = register("pet_kibble", () -> new TooltipItem(new Item.Properties()));

    // Cosmetics
    public static final RegistryEntry<Item> PET_COLLAR = register("pet_collar", () -> new DyeableCosmeticItem(
            DyeableCosmeticItem.Slot.COLLAR, 0xF7A8C8, new Item.Properties().stacksTo(16)));
    public static final RegistryEntry<Item> PET_BOW = register("pet_bow", () -> new DyeableCosmeticItem(
            DyeableCosmeticItem.Slot.BOW, 0xFF8FB8, new Item.Properties().stacksTo(16)));
    public static final RegistryEntry<Item> FLOWER_CROWN = accessory(Accessory.FLOWER_CROWN);
    public static final RegistryEntry<Item> TINY_TOP_HAT = accessory(Accessory.TINY_TOP_HAT);
    public static final RegistryEntry<Item> PARTY_HAT = accessory(Accessory.PARTY_HAT);
    public static final RegistryEntry<Item> STAR_CLIP = accessory(Accessory.STAR_CLIP);
    public static final RegistryEntry<Item> HEART_GLASSES = accessory(Accessory.HEART_GLASSES);
    public static final RegistryEntry<Item> COZY_SCARF = accessory(Accessory.COZY_SCARF);

    // Toys
    public static final RegistryEntry<Item> YARN_BALL = toy("yarn_ball", PetToyItem.Kind.YARN_BALL);
    public static final RegistryEntry<Item> SQUEAKY_CARROT = toy("squeaky_carrot", PetToyItem.Kind.SQUEAKY_CARROT);
    public static final RegistryEntry<Item> FEATHER_WAND = toy("feather_wand", PetToyItem.Kind.FEATHER_WAND);

    // Care
    public static final RegistryEntry<Item> FEEDING_BOWL = block("feeding_bowl", ModBlocks.FEEDING_BOWL);
    public static final RegistryEntry<Item> PINK_PET_BED = block("pink_pet_bed", ModBlocks.PINK_PET_BED);
    public static final RegistryEntry<Item> LAVENDER_PET_BED = block("lavender_pet_bed", ModBlocks.LAVENDER_PET_BED);
    public static final RegistryEntry<Item> MINT_PET_BED = block("mint_pet_bed", ModBlocks.MINT_PET_BED);
    public static final RegistryEntry<Item> SKY_PET_BED = block("sky_pet_bed", ModBlocks.SKY_PET_BED);
    public static final RegistryEntry<Item> PET_CARRIER = register("pet_carrier", () -> new PetCarrierItem(new Item.Properties().stacksTo(1)));
    public static final RegistryEntry<Item> PET_JOURNAL = register("pet_journal", () -> new PetJournalItem(
            new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));
    public static final RegistryEntry<Item> COTTON_FLUFF = register("cotton_fluff", () -> new TooltipItem(new Item.Properties()));

    static {
        for (Species species : Species.values()) {
            int[] colors = eggColors(species);
            SPAWN_EGGS.put(species, register(species.id + "_spawn_egg",
                    () -> Services.PLATFORM.spawnEgg(() -> ModEntities.get(species), colors[0], colors[1], new Item.Properties())));
        }
    }

    private ModItems() {
    }

    private static <T extends Item> RegistryEntry<T> register(String name, java.util.function.Supplier<T> item) {
        RegistryEntry<T> ro = Services.PLATFORM.register(Registries.ITEM, name, item);
        TAB_ORDER.add(ro);
        return ro;
    }

    private static RegistryEntry<Item> treat(String name, int nutrition, float saturation) {
        return register(name, () -> new TooltipItem(new Item.Properties()
                .food(new FoodProperties.Builder().nutrition(nutrition).saturationModifier(saturation).fast().build())));
    }

    private static RegistryEntry<Item> accessory(Accessory accessory) {
        return register(accessory.id, () -> new AccessoryItem(accessory, new Item.Properties().stacksTo(16)));
    }

    private static RegistryEntry<Item> toy(String name, PetToyItem.Kind kind) {
        return register(name, () -> new PetToyItem(kind, new Item.Properties().durability(64)));
    }

    private static RegistryEntry<Item> block(String name, RegistryEntry<? extends net.minecraft.world.level.block.Block> block) {
        return register(name, () -> new BlockItem(block.get(), new Item.Properties()));
    }

    private static int[] eggColors(Species species) {
        return switch (species) {
            case COTTON_BUNNY -> new int[]{0xFFF9F5, 0xFFB3C9};
            case STRAWBERRY_BUNNY -> new int[]{0xFF8FA4, 0x7CC46E};
            case MOON_BUNNY -> new int[]{0x5E5CAB, 0xFFF0A6};
            case LAVENDER_BUNNY -> new int[]{0xC9B6F0, 0x9B7FE0};
            case SNOWBALL_BUNNY -> new int[]{0xFFFFFF, 0xA9D8FF};
            case BLOSSOM_FOX -> new int[]{0xFFB4CA, 0xFFFFFF};
            case CLOUD_KITTY -> new int[]{0xFFFFFF, 0xC4E5FF};
            case STRAWBERRY_MOUSE -> new int[]{0xFFD7DF, 0xFF5C7A};
            case HONEY_BEAR -> new int[]{0xF2B45B, 0xFFE3B0};
            case MOON_DEER -> new int[]{0x6B6DB8, 0xCFEAFF};
            case PASTEL_AXOLOTL -> new int[]{0xFFB9DA, 0xFF7FB6};
            case TINY_SWAN -> new int[]{0xFFFFFF, 0xFF9E5E};
            case RAINBOW_BUTTERFLY -> new int[]{0xC7CEEA, 0xFF9AA2};
            case CHERRY_BLOSSOM_BIRD -> new int[]{0xFFCADB, 0xFFFFFF};
            case DREAMY_HAMSTER -> new int[]{0xFFE9C8, 0xB9A6F2};
        };
    }
}

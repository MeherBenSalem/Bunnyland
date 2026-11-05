package com.sugarplumstudios.bunnyland.registry;

import net.minecraft.world.item.component.Consumables;
import net.minecraft.resources.ResourceKey;
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
    public static final RegistryEntry<Item> SEED_MEDLEY = register("seed_medley", () -> new TooltipItem(props("seed_medley")));
    public static final RegistryEntry<Item> FLOWER_NECTAR = register("flower_nectar", () -> new TooltipItem(props("flower_nectar").stacksTo(16)));
    public static final RegistryEntry<Item> PET_KIBBLE = register("pet_kibble", () -> new TooltipItem(props("pet_kibble")));

    // Cosmetics
    public static final RegistryEntry<Item> PET_COLLAR = register("pet_collar", () -> new DyeableCosmeticItem(
            DyeableCosmeticItem.Slot.COLLAR, 0xF7A8C8, props("pet_collar").stacksTo(16)));
    public static final RegistryEntry<Item> PET_BOW = register("pet_bow", () -> new DyeableCosmeticItem(
            DyeableCosmeticItem.Slot.BOW, 0xFF8FB8, props("pet_bow").stacksTo(16)));
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
    public static final RegistryEntry<Item> PET_CARRIER = register("pet_carrier", () -> new PetCarrierItem(props("pet_carrier").stacksTo(1)));
    public static final RegistryEntry<Item> PET_JOURNAL = register("pet_journal", () -> new PetJournalItem(
            props("pet_journal").stacksTo(1).rarity(Rarity.UNCOMMON)));
    public static final RegistryEntry<Item> COTTON_FLUFF = register("cotton_fluff", () -> new TooltipItem(props("cotton_fluff")));

    static {
        for (Species species : Species.values()) {
            SPAWN_EGGS.put(species, register(species.id + "_spawn_egg", () -> Services.PLATFORM.spawnEgg(() -> ModEntities.get(species), props(species.id + "_spawn_egg"))));
        }
    }

    private ModItems() {
    }

    /** Item properties carrying the item's registry id (required since 1.21.2). */
    private static Item.Properties props(String name) {
        return new Item.Properties().setId(ResourceKey.create(Registries.ITEM, Bunnyland.id(name)));
    }

    private static <T extends Item> RegistryEntry<T> register(String name, java.util.function.Supplier<T> item) {
        RegistryEntry<T> ro = Services.PLATFORM.register(Registries.ITEM, name, item);
        TAB_ORDER.add(ro);
        return ro;
    }

    private static RegistryEntry<Item> treat(String name, int nutrition, float saturation) {
        return register(name, () -> new TooltipItem(props(name)
                .food(new FoodProperties.Builder().nutrition(nutrition).saturationModifier(saturation).build(),
                        Consumables.defaultFood().consumeSeconds(0.8F).build())));
    }

    private static RegistryEntry<Item> accessory(Accessory accessory) {
        return register(accessory.id, () -> new AccessoryItem(accessory, props(accessory.id).stacksTo(16)));
    }

    private static RegistryEntry<Item> toy(String name, PetToyItem.Kind kind) {
        return register(name, () -> new PetToyItem(kind, props(name).durability(64)));
    }

    private static RegistryEntry<Item> block(String name, RegistryEntry<? extends net.minecraft.world.level.block.Block> block) {
        return register(name, () -> new BlockItem(block.get(), props(name).useBlockDescriptionPrefix()));
    }

}

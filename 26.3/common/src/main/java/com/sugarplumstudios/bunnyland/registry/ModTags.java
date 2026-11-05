package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;

public final class ModTags {
    public static final TagKey<Item> BOWL_FOOD = item("bowl_food");
    public static final TagKey<Item> PET_TREATS = item("pet_treats");
    public static final TagKey<Block> PET_BEDS = block("pet_beds");
    public static final TagKey<Block> CREATURES_SPAWNABLE_ON = block("creatures_spawnable_on");
    public static final TagKey<Block> FLYERS_PERCH_ON = block("flyers_perch_on");
    public static final TagKey<EntityType<?>> CREATURES = entity("creatures");
    public static final TagKey<EntityType<?>> MOUSE_PREDATORS = entity("mouse_predators");

    private ModTags() {
    }

    private static TagKey<Item> item(String name) {
        return TagKey.create(Registries.ITEM, Bunnyland.id(name));
    }

    private static TagKey<Block> block(String name) {
        return TagKey.create(Registries.BLOCK, Bunnyland.id(name));
    }

    private static TagKey<EntityType<?>> entity(String name) {
        return TagKey.create(Registries.ENTITY_TYPE, Bunnyland.id(name));
    }
}

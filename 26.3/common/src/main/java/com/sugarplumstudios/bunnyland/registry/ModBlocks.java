package com.sugarplumstudios.bunnyland.registry;

import net.minecraft.resources.ResourceKey;
import com.sugarplumstudios.bunnyland.platform.Services;
import net.minecraft.core.registries.Registries;
import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.block.FeedingBowlBlock;
import com.sugarplumstudios.bunnyland.block.PetBedBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import com.sugarplumstudios.bunnyland.platform.RegistryEntry;

import java.util.List;

public final class ModBlocks {

    public static final RegistryEntry<Block> FEEDING_BOWL = Services.PLATFORM.register(Registries.BLOCK, "feeding_bowl", () -> new FeedingBowlBlock(
            props("feeding_bowl").mapColor(MapColor.COLOR_PINK).strength(0.6F).sound(SoundType.DECORATED_POT)
                    .noOcclusion().pushReaction(PushReaction.POPPED)));
    public static final RegistryEntry<Block> PINK_PET_BED = bed("pink", MapColor.COLOR_PINK);
    public static final RegistryEntry<Block> LAVENDER_PET_BED = bed("lavender", MapColor.COLOR_PURPLE);
    public static final RegistryEntry<Block> MINT_PET_BED = bed("mint", MapColor.COLOR_LIGHT_GREEN);
    public static final RegistryEntry<Block> SKY_PET_BED = bed("sky", MapColor.COLOR_LIGHT_BLUE);
    public static final List<RegistryEntry<Block>> PET_BEDS = List.of(PINK_PET_BED, LAVENDER_PET_BED, MINT_PET_BED, SKY_PET_BED);

    private ModBlocks() {
    }

    /** Block properties carrying the block's registry id (required since 1.21.2). */
    private static BlockBehaviour.Properties props(String name) {
        return BlockBehaviour.Properties.of().setId(ResourceKey.create(Registries.BLOCK, Bunnyland.id(name)));
    }

    private static RegistryEntry<Block> bed(String color, MapColor mapColor) {
        return Services.PLATFORM.register(Registries.BLOCK, color + "_pet_bed", () -> new PetBedBlock(props(color + "_pet_bed").mapColor(mapColor)
                .strength(0.4F).sound(SoundType.WOOL).noOcclusion().ignitedByLava()));
    }
}

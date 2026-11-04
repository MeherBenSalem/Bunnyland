package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.block.FeedingBowlBlock;
import com.sugarplumstudios.bunnyland.block.PetBedBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.List;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, Bunnyland.MOD_ID);

    public static final RegistryObject<Block> FEEDING_BOWL = BLOCKS.register("feeding_bowl", () -> new FeedingBowlBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PINK).strength(0.6F).sound(SoundType.DECORATED_POT)
                    .noOcclusion().pushReaction(PushReaction.DESTROY)));
    public static final RegistryObject<Block> PINK_PET_BED = bed("pink", MapColor.COLOR_PINK);
    public static final RegistryObject<Block> LAVENDER_PET_BED = bed("lavender", MapColor.COLOR_PURPLE);
    public static final RegistryObject<Block> MINT_PET_BED = bed("mint", MapColor.COLOR_LIGHT_GREEN);
    public static final RegistryObject<Block> SKY_PET_BED = bed("sky", MapColor.COLOR_LIGHT_BLUE);
    public static final List<RegistryObject<Block>> PET_BEDS = List.of(PINK_PET_BED, LAVENDER_PET_BED, MINT_PET_BED, SKY_PET_BED);

    private ModBlocks() {
    }

    private static RegistryObject<Block> bed(String color, MapColor mapColor) {
        return BLOCKS.register(color + "_pet_bed", () -> new PetBedBlock(BlockBehaviour.Properties.of().mapColor(mapColor)
                .strength(0.4F).sound(SoundType.WOOL).noOcclusion().ignitedByLava()));
    }
}

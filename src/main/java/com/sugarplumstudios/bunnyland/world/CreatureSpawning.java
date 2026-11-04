package com.sugarplumstudios.bunnyland.world;

import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;

/** Where each creature may appear when it spawns naturally. Which biomes is decided by biome tags. */
public final class CreatureSpawning {
    private CreatureSpawning() {
    }

    @SuppressWarnings("unchecked")
    public static void register(SpawnPlacementRegisterEvent event) {
        for (Species species : Species.values()) {
            EntityType<BunnylandAnimal> type = (EntityType<BunnylandAnimal>) ModEntities.get(species);
            switch (species) {
                case PASTEL_AXOLOTL -> event.register(type, SpawnPlacements.Type.IN_WATER, Heightmap.Types.OCEAN_FLOOR,
                        CreatureSpawning::checkAquatic, SpawnPlacementRegisterEvent.Operation.REPLACE);
                case TINY_SWAN -> event.register(type, SpawnPlacements.Type.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING,
                        CreatureSpawning::checkSwan, SpawnPlacementRegisterEvent.Operation.REPLACE);
                case RAINBOW_BUTTERFLY, CHERRY_BLOSSOM_BIRD -> event.register(type, SpawnPlacements.Type.ON_GROUND,
                        Heightmap.Types.MOTION_BLOCKING, CreatureSpawning::checkFlyer, SpawnPlacementRegisterEvent.Operation.REPLACE);
                default -> event.register(type, SpawnPlacements.Type.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                        CreatureSpawning::checkGround, SpawnPlacementRegisterEvent.Operation.REPLACE);
            }
        }
    }

    private static boolean bright(ServerLevelAccessor level, BlockPos pos) {
        return level.getRawBrightness(pos, 0) > 8;
    }

    public static boolean checkGround(EntityType<BunnylandAnimal> type, ServerLevelAccessor level, MobSpawnType reason,
                                      BlockPos pos, RandomSource random) {
        return level.getBlockState(pos.below()).is(ModTags.CREATURES_SPAWNABLE_ON) && bright(level, pos);
    }

    public static boolean checkFlyer(EntityType<BunnylandAnimal> type, ServerLevelAccessor level, MobSpawnType reason,
                                     BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos.below()).is(ModTags.FLYERS_PERCH_ON) || !bright(level, pos)) return false;
        // Butterflies are ambient and spawn continuously, so only while the sun is up.
        return (EntityType<?>) type != ModEntities.RAINBOW_BUTTERFLY.get() || reason != MobSpawnType.NATURAL || level.getLevel().isDay();
    }

    public static boolean checkAquatic(EntityType<BunnylandAnimal> type, ServerLevelAccessor level, MobSpawnType reason,
                                       BlockPos pos, RandomSource random) {
        int sea = level.getSeaLevel();
        return level.getFluidState(pos).is(FluidTags.WATER) && pos.getY() >= sea - 12 && pos.getY() <= sea + 1;
    }

    public static boolean checkSwan(EntityType<BunnylandAnimal> type, ServerLevelAccessor level, MobSpawnType reason,
                                    BlockPos pos, RandomSource random) {
        if (!level.getBlockState(pos).isAir()) return false;
        if (level.getFluidState(pos.below()).is(FluidTags.WATER)) return true;
        return level.getBlockState(pos.below()).is(ModTags.CREATURES_SPAWNABLE_ON) && bright(level, pos);
    }
}

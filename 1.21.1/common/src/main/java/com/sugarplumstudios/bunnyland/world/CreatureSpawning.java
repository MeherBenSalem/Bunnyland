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
import net.minecraft.world.entity.SpawnPlacementType;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;

/** Where each creature may appear when it spawns naturally. Which biomes is decided by biome tags. */
public final class CreatureSpawning {
    private CreatureSpawning() {
    }

    /** Receives a spawn rule; each loader registers it its own way. */
    public interface Sink {
        void register(EntityType<BunnylandAnimal> type, SpawnPlacementType placement, Heightmap.Types heightmap,
                      SpawnPlacements.SpawnPredicate<BunnylandAnimal> predicate);
    }

    @SuppressWarnings("unchecked")
    public static void register(Sink event) {
        for (Species species : Species.values()) {
            EntityType<BunnylandAnimal> type = (EntityType<BunnylandAnimal>) ModEntities.get(species);
            switch (species) {
                case PASTEL_AXOLOTL -> event.register(type, SpawnPlacementTypes.IN_WATER, Heightmap.Types.OCEAN_FLOOR,
                        CreatureSpawning::checkAquatic);
                case TINY_SWAN -> event.register(type, SpawnPlacementTypes.NO_RESTRICTIONS, Heightmap.Types.MOTION_BLOCKING,
                        CreatureSpawning::checkSwan);
                case RAINBOW_BUTTERFLY, CHERRY_BLOSSOM_BIRD -> event.register(type, SpawnPlacementTypes.ON_GROUND,
                        Heightmap.Types.MOTION_BLOCKING, CreatureSpawning::checkFlyer);
                default -> event.register(type, SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                        CreatureSpawning::checkGround);
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

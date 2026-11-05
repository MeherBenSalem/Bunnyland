package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.ai.BlockVisitGoal;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import com.sugarplumstudios.bunnyland.registry.ModParticles;

/** Flutters from flower to flower, rests to show off its wings and sometimes helps a new flower bloom. */
public class RainbowButterfly extends FlyingCreature {
    public RainbowButterfly(EntityType<? extends RainbowButterfly> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.RAINBOW_BUTTERFLY;
    }

    @Override
    protected void addSpeciesGoals() {
        goalSelector.addGoal(9, new BlockVisitGoal(this, 1.0D, 10, 400, () -> true,
                s -> s.is(BlockTags.SMALL_FLOWERS), (mob, pos) -> {
                    mob.playAction("special");
                    if (mob.isTame()) mob.addHappiness(2);
                    if (mob.level() instanceof ServerLevel server && BunnylandConfig.COMMON.butterfliesSpreadFlowers.get()
                            && mob.getRandom().nextInt(8) == 0) {
                        spreadFlower(server, pos);
                    }
                }));
    }

    private static void spreadFlower(ServerLevel level, BlockPos flowerPos) {
        BlockState flower = level.getBlockState(flowerPos);
        for (int i = 0; i < 8; i++) {
            BlockPos pos = flowerPos.offset(level.random.nextInt(7) - 3, level.random.nextInt(3) - 1, level.random.nextInt(7) - 3);
            if (level.isEmptyBlock(pos) && level.getBlockState(pos.below()).is(Blocks.GRASS_BLOCK) && flower.canSurvive(level, pos)) {
                level.setBlock(pos, flower, Block.UPDATE_ALL);
                level.sendParticles(ModParticles.SPARKLE.get(), pos.getX() + 0.5D, pos.getY() + 0.4D, pos.getZ() + 0.5D, 6,
                        0.25D, 0.2D, 0.25D, 0.0D);
                return;
            }
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return !isTame() && !hasCustomName() && !isLeashed();
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    protected void doPush(Entity entity) {
    }

    @Override
    protected void pushEntities() {
    }
}

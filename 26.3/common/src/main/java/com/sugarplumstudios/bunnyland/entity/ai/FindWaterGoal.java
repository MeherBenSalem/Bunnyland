package com.sugarplumstudios.bunnyland.entity.ai;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;

/** Walks a stranded water creature back to water nearby (vanilla's TryFindWaterGoal, removed in 26.3). */
public class FindWaterGoal extends Goal {
    private final PathfinderMob mob;

    public FindWaterGoal(PathfinderMob mob) {
        this.mob = mob;
    }

    @Override
    public boolean canUse() {
        return mob.onGround() && !mob.level().getFluidState(mob.blockPosition()).is(FluidTags.WATER);
    }

    @Override
    public void start() {
        for (BlockPos pos : BlockPos.betweenClosed(Mth.floor(mob.getX() - 2.0D), Mth.floor(mob.getY() - 2.0D), Mth.floor(mob.getZ() - 2.0D),
                Mth.floor(mob.getX() + 2.0D), mob.getBlockY(), Mth.floor(mob.getZ() + 2.0D))) {
            if (mob.level().getFluidState(pos).is(FluidTags.WATER)) {
                mob.getMoveControl().setWantedPosition(pos.getX(), pos.getY(), pos.getZ(), 1.0D);
                return;
            }
        }
    }
}

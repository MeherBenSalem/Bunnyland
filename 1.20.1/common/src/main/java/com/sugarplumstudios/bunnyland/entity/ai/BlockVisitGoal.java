package com.sugarplumstudios.bunnyland.entity.ai;

import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.MoveToBlockGoal;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.state.BlockState;

import java.util.function.BiConsumer;
import java.util.function.BooleanSupplier;
import java.util.function.Predicate;

/**
 * Walks up to a matching block nearby and does something there once (nibble berries, lick honey, sniff a
 * flower...). Waits {@code cooldown} ticks before looking for another.
 */
public class BlockVisitGoal extends MoveToBlockGoal {
    private final BunnylandAnimal mob;
    private final Predicate<BlockState> target;
    private final BooleanSupplier enabled;
    private final BiConsumer<BunnylandAnimal, BlockPos> action;
    private final int cooldown;
    private boolean done;

    public BlockVisitGoal(BunnylandAnimal mob, double speed, int range, int cooldown, BooleanSupplier enabled,
                          Predicate<BlockState> target, BiConsumer<BunnylandAnimal, BlockPos> action) {
        super(mob, speed, range, 2);
        this.mob = mob;
        this.target = target;
        this.enabled = enabled;
        this.action = action;
        this.cooldown = cooldown;
    }

    private boolean free() {
        return !mob.isOrderedToSit() && !mob.isNapping() && !mob.isLeashed() && !mob.isInLove() && enabled.getAsBoolean();
    }

    @Override
    public boolean canUse() {
        return free() && super.canUse();
    }

    @Override
    public boolean canContinueToUse() {
        return !done && free() && super.canContinueToUse();
    }

    @Override
    protected int nextStartTick(PathfinderMob mob) {
        return reducedTickDelay(cooldown / 2 + mob.getRandom().nextInt(Math.max(1, cooldown)));
    }

    @Override
    public void start() {
        super.start();
        done = false;
    }

    @Override
    protected BlockPos getMoveToTarget() {
        return blockPos;
    }

    @Override
    public double acceptedDistance() {
        return 1.3D + mob.getBbWidth() * 0.5D;
    }

    @Override
    protected boolean isValidTarget(LevelReader level, BlockPos pos) {
        return target.test(level.getBlockState(pos));
    }

    @Override
    public void tick() {
        super.tick();
        if (isReachedTarget() && !done) {
            mob.getLookControl().setLookAt(blockPos.getX() + 0.5D, blockPos.getY() + 0.5D, blockPos.getZ() + 0.5D);
            if (target.test(mob.level().getBlockState(blockPos))) action.accept(mob, blockPos);
            done = true;
        }
    }
}

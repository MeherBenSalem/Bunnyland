package com.sugarplumstudios.bunnyland.entity.ai;

import com.sugarplumstudios.bunnyland.block.FeedingBowlBlock;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.MoveToBlockGoal;
import net.minecraft.world.level.LevelReader;

/** A hungry or lonely pet trots to a Feeding Bowl with food in it and eats a portion. */
public class EatFromBowlGoal extends MoveToBlockGoal {
    private final BunnylandAnimal pet;
    private int eatTicks;

    public EatFromBowlGoal(BunnylandAnimal pet) {
        super(pet, 1.05D, 12, 3);
        this.pet = pet;
    }

    private boolean eligible() {
        return pet.isTame() && !pet.isOrderedToSit() && !pet.isNapping() && !pet.isLeashed() && pet.isReadyToEat();
    }

    @Override
    public boolean canUse() {
        return eligible() && super.canUse();
    }

    @Override
    public boolean canContinueToUse() {
        return eatTicks < 40 && (eligible() || eatTicks > 0) && super.canContinueToUse();
    }

    @Override
    protected int nextStartTick(PathfinderMob mob) {
        return reducedTickDelay(60 + mob.getRandom().nextInt(80));
    }

    @Override
    public void start() {
        super.start();
        eatTicks = 0;
    }

    @Override
    protected BlockPos getMoveToTarget() {
        return blockPos;
    }

    @Override
    public double acceptedDistance() {
        return 1.4D + pet.getBbWidth() * 0.5D;
    }

    @Override
    protected boolean isValidTarget(LevelReader level, BlockPos pos) {
        return FeedingBowlBlock.hasFood(level.getBlockState(pos));
    }

    @Override
    public void tick() {
        super.tick();
        if (!isReachedTarget()) return;
        pet.getLookControl().setLookAt(blockPos.getX() + 0.5D, blockPos.getY() + 0.2D, blockPos.getZ() + 0.5D);
        if (eatTicks++ == 0) {
            if (FeedingBowlBlock.eatPortion(pet.level(), blockPos)) pet.eatFromBowl();
            else eatTicks = 40;
        }
    }
}

package com.sugarplumstudios.bunnyland.entity.ai;

import com.sugarplumstudios.bunnyland.block.PetBedBlock;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.MoveToBlockGoal;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;

/** At bedtime a pet that isn't busy walks to a free pet bed nearby and curls up in it. */
public class SeekPetBedGoal extends MoveToBlockGoal {
    private final BunnylandAnimal pet;

    public SeekPetBedGoal(BunnylandAnimal pet) {
        super(pet, 1.0D, 12, 3);
        this.pet = pet;
    }

    private boolean eligible() {
        if (!pet.isTame() || pet.isOrderedToSit() || pet.isNapping() || pet.isLeashed() || !pet.isSleepTime()) return false;
        LivingEntity owner = pet.getOwner();
        return owner == null || pet.distanceToSqr(owner) < 20.0D * 20.0D;
    }

    @Override
    public boolean canUse() {
        return eligible() && super.canUse();
    }

    @Override
    public boolean canContinueToUse() {
        return eligible() && super.canContinueToUse();
    }

    @Override
    protected int nextStartTick(net.minecraft.world.entity.PathfinderMob mob) {
        return reducedTickDelay(100 + mob.getRandom().nextInt(100));
    }

    @Override
    protected BlockPos getMoveToTarget() {
        return blockPos;
    }

    @Override
    public double acceptedDistance() {
        return 1.1D;
    }

    @Override
    protected boolean isValidTarget(LevelReader level, BlockPos pos) {
        return level.getBlockState(pos).is(ModTags.PET_BEDS) && level.getBlockState(pos.above()).getCollisionShape(level, pos.above()).isEmpty()
                && !(level instanceof Level l && PetBedBlock.isOccupied(l, pos, pet));
    }

    @Override
    public void tick() {
        super.tick();
        if (isReachedTarget()) {
            pet.snapTo(blockPos.getX() + 0.5D, blockPos.getY() + PetBedBlock.CUSHION_HEIGHT, blockPos.getZ() + 0.5D,
                    pet.getYRot(), pet.getXRot());
            pet.getNavigation().stop();
            pet.setBedPos(blockPos.immutable());
        }
    }
}

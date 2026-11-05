package com.sugarplumstudios.bunnyland.entity.ai;

import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.level.pathfinder.WalkNodeEvaluator;

import java.util.EnumSet;

/**
 * Follows the owner like the vanilla wolf goal, but works with any navigation (walking, flying,
 * swimming), never interrupts a nap, hurries when far behind and can teleport (configurable).
 */
public class PetFollowOwnerGoal extends Goal {
    private final BunnylandAnimal pet;
    private final double speed;
    private final float startDistance;
    private final float stopDistance;
    private final boolean canFly;
    private LivingEntity owner;
    private int recalcTimer;
    private float oldWaterCost;

    public PetFollowOwnerGoal(BunnylandAnimal pet, double speed, float startDistance, float stopDistance, boolean canFly) {
        this.pet = pet;
        this.speed = speed;
        this.startDistance = startDistance;
        this.stopDistance = stopDistance;
        this.canFly = canFly;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean unableToMove() {
        return pet.isOrderedToSit() || pet.isPassenger() || pet.isLeashed() || pet.isNapping();
    }

    @Override
    public boolean canUse() {
        LivingEntity o = pet.getOwner();
        if (o == null || o.isSpectator() || unableToMove()) return false;
        if (pet.distanceToSqr(o) < startDistance * startDistance) return false;
        owner = o;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return owner != null && !pet.getNavigation().isDone() && !unableToMove()
                && pet.distanceToSqr(owner) > stopDistance * stopDistance;
    }

    @Override
    public void start() {
        recalcTimer = 0;
        oldWaterCost = pet.getPathfindingMalus(PathType.WATER);
        pet.setPathfindingMalus(PathType.WATER, 0.0F);
    }

    @Override
    public void stop() {
        owner = null;
        pet.getNavigation().stop();
        pet.setPathfindingMalus(PathType.WATER, oldWaterCost);
    }

    @Override
    public void tick() {
        pet.getLookControl().setLookAt(owner, 10.0F, pet.getMaxHeadXRot());
        if (--recalcTimer > 0) return;
        recalcTimer = adjustedTickDelay(10);
        double dist = pet.distanceToSqr(owner);
        if (dist >= 144.0D && BunnylandConfig.COMMON.petsTeleport.get()) {
            teleportToOwner();
        } else {
            PathNavigation nav = pet.getNavigation();
            nav.moveTo(owner, dist > 64.0D ? speed * 1.35D : speed);
        }
    }

    private void teleportToOwner() {
        BlockPos base = owner.blockPosition();
        for (int i = 0; i < 10; i++) {
            int dx = pet.getRandom().nextIntBetweenInclusive(-3, 3);
            int dy = pet.getRandom().nextIntBetweenInclusive(-1, 1);
            int dz = pet.getRandom().nextIntBetweenInclusive(-3, 3);
            if (Math.abs(dx) < 2 && Math.abs(dz) < 2) continue;
            BlockPos pos = base.offset(dx, dy, dz);
            if (canTeleportTo(pos)) {
                pet.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, pet.getYRot(), pet.getXRot());
                pet.getNavigation().stop();
                return;
            }
        }
    }

    private boolean canTeleportTo(BlockPos pos) {
        PathType type = WalkNodeEvaluator.getPathTypeStatic(pet, pos.mutable());
        boolean water = pet.likesWater() && pet.level().getFluidState(pos).isSource();
        if (type != PathType.WALKABLE && !water && !canFly) return false;
        BlockState below = pet.level().getBlockState(pos.below());
        if (!canFly && below.getBlock() instanceof LeavesBlock) return false;
        BlockPos offset = pos.subtract(pet.blockPosition());
        return pet.level().noCollision(pet, pet.getBoundingBox().move(offset));
    }
}

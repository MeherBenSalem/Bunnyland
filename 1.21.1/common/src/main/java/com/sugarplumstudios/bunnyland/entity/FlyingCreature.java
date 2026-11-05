package com.sugarplumstudios.bunnyland.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomFlyingGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.RawAnimation;

/** Creatures that fly like parrots: they flutter around, glide down gently and land to rest. */
public abstract class FlyingCreature extends BunnylandAnimal {
    protected FlyingCreature(EntityType<? extends FlyingCreature> type, Level level) {
        super(type, level);
        this.moveControl = new FlyingMoveControl(this, 10, false);
        setPathfindingMalus(PathType.DANGER_FIRE, -1.0F);
        setPathfindingMalus(PathType.DAMAGE_FIRE, -1.0F);
        setPathfindingMalus(PathType.COCOA, -1.0F);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        FlyingPathNavigation nav = new FlyingPathNavigation(this, level);
        nav.setCanOpenDoors(false);
        nav.setCanFloat(true);
        nav.setCanPassDoors(true);
        return nav;
    }

    @Override
    public boolean isFlyer() {
        return true;
    }

    @Override
    protected void addWanderGoals() {
        goalSelector.addGoal(12, new WaterAvoidingRandomFlyingGoal(this, 1.0D));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        Vec3 motion = getDeltaMovement();
        if (!onGround() && motion.y < 0.0D) setDeltaMovement(motion.multiply(1.0D, 0.6D, 1.0D));
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {
    }

    public boolean isFlying() {
        return !onGround();
    }

    @Override
    protected RawAnimation baseAnimation(boolean moving) {
        if (isNapping()) return SLEEP;
        if (isFlying() && !isInSittingPose()) return FLY;
        return super.baseAnimation(moving);
    }
}

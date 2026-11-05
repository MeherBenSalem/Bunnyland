package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.TryFindWaterGoal;
import net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.RawAnimation;

/** Swims gracefully and waddles just as happily on land. It never dries out. */
public class PastelAxolotl extends BunnylandAnimal {
    public PastelAxolotl(EntityType<? extends PastelAxolotl> type, Level level) {
        super(type, level);
        setPathfindingMalus(PathType.WATER, 0.0F);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.1F, 0.3F, false);
        this.lookControl = new SmoothSwimmingLookControl(this, 20);
    }

    @Override
    public Species species() {
        return Species.PASTEL_AXOLOTL;
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new AmphibiousPathNavigation(this, level);
    }

    @Override
    protected boolean floatsInWater() {
        return false;
    }

    @Override
    public boolean likesWater() {
        return true;
    }

    @Override
    protected void addWanderGoals() {
        goalSelector.addGoal(12, new TryFindWaterGoal(this) {
            @Override
            public boolean canUse() {
                return !isTame() && super.canUse();
            }
        });
        goalSelector.addGoal(12, new RandomSwimmingGoal(this, 1.0D, 40));
        goalSelector.addGoal(12, new RandomStrollGoal(this, 0.8D, 100));
    }

    // Breathing under water comes from the #minecraft:can_breathe_under_water entity tag (1.21+).

    @Override
    public boolean isPushedByFluid() {
        return false;
    }

    @Override
    public void travel(Vec3 input) {
        if (isControlledByLocalInstance() && isInWater()) {
            moveRelative(getSpeed(), input);
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.9D));
        } else {
            super.travel(input);
        }
    }

    @Override
    protected RawAnimation baseAnimation(boolean moving) {
        if (!isNapping() && isInWater() && !isInSittingPose()) return SWIM;
        return super.baseAnimation(moving);
    }
}

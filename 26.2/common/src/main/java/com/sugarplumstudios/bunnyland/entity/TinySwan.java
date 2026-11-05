package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import com.geckolib.animation.RawAnimation;

/** Glides along rivers, prefers to wander towards water, and cygnets follow their parents in a line. */
public class TinySwan extends BunnylandAnimal {
    public TinySwan(EntityType<? extends TinySwan> type, Level level) {
        super(type, level);
        setPathfindingMalus(PathType.WATER, 0.0F);
    }

    @Override
    public Species species() {
        return Species.TINY_SWAN;
    }

    @Override
    public boolean likesWater() {
        return true;
    }

    @Override
    protected void addWanderGoals() {
        goalSelector.addGoal(12, new RandomStrollGoal(this, 0.8D) {
            @Nullable
            @Override
            protected Vec3 getPosition() {
                Vec3 fallback = null;
                for (int i = 0; i < 6; i++) {
                    Vec3 pos = DefaultRandomPos.getPos(mob, 10, 4);
                    if (pos == null) continue;
                    if (mob.level().getFluidState(BlockPos.containing(pos)).is(FluidTags.WATER)
                            || mob.level().getFluidState(BlockPos.containing(pos).below()).is(FluidTags.WATER)) {
                        return pos;
                    }
                    if (fallback == null) fallback = pos;
                }
                return fallback;
            }
        });
    }

    @Override
    public void aiStep() {
        super.aiStep();
        // Gentle buoyancy so swans ride on the surface instead of bobbing under it.
        if (isInWater() && getFluidHeight(FluidTags.WATER) > 0.3D) {
            setDeltaMovement(getDeltaMovement().add(0.0D, 0.03D, 0.0D));
        }
    }

    @Override
    protected RawAnimation baseAnimation(boolean moving) {
        if (!isNapping() && isInWater()) return SWIM;
        return super.baseAnimation(moving);
    }
}

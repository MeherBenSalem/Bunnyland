package com.sugarplumstudios.bunnyland.entity.ai;

import com.sugarplumstudios.bunnyland.creature.Mood;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/** An overjoyed pet sometimes gets the zoomies and dashes happily around its owner. */
public class ZoomiesGoal extends Goal {
    private final BunnylandAnimal pet;
    private int dashes;
    private int timeout;

    public ZoomiesGoal(BunnylandAnimal pet) {
        this.pet = pet;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (!pet.isTame() || pet.isOrderedToSit() || pet.isNapping() || pet.isLeashed() || pet.getMood() != Mood.OVERJOYED) return false;
        LivingEntity owner = pet.getOwner();
        return owner != null && pet.distanceToSqr(owner) < 100.0D && pet.getRandom().nextInt(reducedTickDelay(1600)) == 0;
    }

    @Override
    public void start() {
        dashes = 3 + pet.getRandom().nextInt(3);
        timeout = 200;
        pet.playAction("play");
        dash();
    }

    private void dash() {
        Vec3 target = DefaultRandomPos.getPos(pet, 6, 2);
        if (target != null) pet.getNavigation().moveTo(target.x, target.y, target.z, 1.6D);
        dashes--;
    }

    @Override
    public boolean canContinueToUse() {
        return timeout > 0 && (dashes > 0 || !pet.getNavigation().isDone()) && !pet.isOrderedToSit();
    }

    @Override
    public void tick() {
        timeout--;
        if (pet.getNavigation().isDone() && dashes > 0) dash();
    }
}

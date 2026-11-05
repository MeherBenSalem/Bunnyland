package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.level.Level;

/** A tiny, quick mouse. Wild ones scamper away from cats, Cloud Kitties included. */
public class StrawberryMouse extends BunnylandAnimal {
    public StrawberryMouse(EntityType<? extends StrawberryMouse> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.STRAWBERRY_MOUSE;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    @Override
    protected void addSpeciesGoals() {
        goalSelector.addGoal(6, new AvoidEntityGoal<>(this, LivingEntity.class, 6.0F, 1.2D, 1.6D,
                e -> !isTame() && e.is(ModTags.MOUSE_PREDATORS)));
    }
}

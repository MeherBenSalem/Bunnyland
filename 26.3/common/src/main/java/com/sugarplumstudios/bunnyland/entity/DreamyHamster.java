package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;

/** A sleepy night owl in a starry nightcap. It naps all day and blows dream bubbles in its sleep. */
public class DreamyHamster extends BunnylandAnimal {
    public DreamyHamster(EntityType<? extends DreamyHamster> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.DREAMY_HAMSTER;
    }

    @Override
    protected void clientParticles() {
        super.clientParticles();
        if (isNapping() && random.nextInt(30) == 0) particle(ParticleTypes.BUBBLE_POP, 0.3D, getBbHeight() + 0.1D);
    }
}

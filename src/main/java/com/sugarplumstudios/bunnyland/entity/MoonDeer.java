package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;

/** A shy, graceful night deer with glowing antlers. It steps lightly over whole blocks. */
public class MoonDeer extends BunnylandAnimal {
    public MoonDeer(EntityType<? extends MoonDeer> type, Level level) {
        super(type, level);
        setMaxUpStep(1.0F);
    }

    @Override
    public Species species() {
        return Species.MOON_DEER;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    @Override
    protected double followSpeed() {
        return 1.25D;
    }

    @Override
    protected void clientParticles() {
        super.clientParticles();
        if (!level().isDay() && random.nextInt(40) == 0) particle(ModParticles.SPARKLE.get(), 0.6D, getBbHeight() + 0.3D);
    }
}

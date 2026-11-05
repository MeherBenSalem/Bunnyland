package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;

/**
 * Never cold: immune to freezing and walks on powder snow (via the vanilla entity type tags), and
 * kicks up little snowflakes as it hops.
 */
public class SnowballBunny extends BunnylandAnimal {
    public SnowballBunny(EntityType<? extends SnowballBunny> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.SNOWBALL_BUNNY;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    @Override
    protected void clientParticles() {
        super.clientParticles();
        if (getDeltaMovement().horizontalDistanceSqr() > 1.0E-4D && random.nextInt(6) == 0) {
            particle(ParticleTypes.SNOWFLAKE, getBbWidth(), 0.1D);
        }
    }
}

package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;

/** A playful night fox whose fluffy tail sheds cherry petals as it runs. */
public class BlossomFox extends BunnylandAnimal {
    public BlossomFox(EntityType<? extends BlossomFox> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.BLOSSOM_FOX;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    @Override
    protected void clientParticles() {
        super.clientParticles();
        boolean moving = getDeltaMovement().horizontalDistanceSqr() > 2.5E-3D;
        if (random.nextInt(moving ? 5 : 240) == 0) particle(ParticleTypes.CHERRY_LEAVES, getBbWidth(), getBbHeight() * 0.7D);
    }
}

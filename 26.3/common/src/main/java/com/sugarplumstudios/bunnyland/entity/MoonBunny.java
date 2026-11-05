package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/** A night bunny with moon-low gravity: it jumps high, floats down gently and never takes fall damage. */
public class MoonBunny extends BunnylandAnimal {
    public MoonBunny(EntityType<? extends MoonBunny> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.MOON_BUNNY;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    @Override
    protected float getJumpPower() {
        return super.getJumpPower() * 1.3F;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        Vec3 motion = getDeltaMovement();
        if (!onGround() && motion.y < 0.0D) setDeltaMovement(motion.multiply(1.0D, 0.75D, 1.0D));
    }

    @Override
    protected void clientParticles() {
        super.clientParticles();
        if (!level().isBrightOutside() && random.nextInt(60) == 0) particle(ModParticles.SPARKLE.get(), 0.6D, getBbHeight() + 0.4D);
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {
    }
}

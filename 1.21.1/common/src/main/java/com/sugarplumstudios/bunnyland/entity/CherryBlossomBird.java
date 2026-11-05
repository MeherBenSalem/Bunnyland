package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animation.RawAnimation;

/** A round songbird: it sings through the day and dances whenever a jukebox plays nearby. */
public class CherryBlossomBird extends FlyingCreature {
    @Nullable
    private BlockPos jukebox;
    private boolean partying;

    public CherryBlossomBird(EntityType<? extends CherryBlossomBird> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.CHERRY_BLOSSOM_BIRD;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (!isNapping() && level().isDay() && random.nextInt(900) == 0) sing();
    }

    @Override
    protected void onIdleSpecial() {
        sing();
    }

    public void sing() {
        playAction("special");
        playSound(ModSounds.BIRD_SING.get(), getSoundVolume(), getVoicePitch());
        if (level() instanceof ServerLevel server) {
            for (int i = 0; i < 3; i++) {
                server.sendParticles(ParticleTypes.NOTE, getX(), getY() + getBbHeight() + 0.2D, getZ(), 0,
                        random.nextInt(25) / 24.0D, 0.0D, 0.0D, 1.0D);
            }
        }
    }

    @Override
    public void aiStep() {
        if (jukebox == null || !jukebox.closerToCenterThan(position(), 3.46D) || !level().getBlockState(jukebox).is(Blocks.JUKEBOX)) {
            partying = false;
            jukebox = null;
        }
        super.aiStep();
    }

    @Override
    public void setRecordPlayingNearby(BlockPos pos, boolean playing) {
        this.jukebox = pos;
        this.partying = playing;
    }

    public boolean isPartying() {
        return partying;
    }

    @Override
    protected RawAnimation baseAnimation(boolean moving) {
        if (partying && !isNapping() && onGround()) return DANCE;
        return super.baseAnimation(moving);
    }
}

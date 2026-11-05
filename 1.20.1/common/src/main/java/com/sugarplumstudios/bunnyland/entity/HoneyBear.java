package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.ai.BlockVisitGoal;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BeehiveBlock;
import net.minecraft.world.level.block.Block;
import com.sugarplumstudios.bunnyland.platform.Services;

/** A cuddly cub that sniffs out full beehives and licks them clean. Its bee buddy never leaves its side. */
public class HoneyBear extends BunnylandAnimal {
    public HoneyBear(EntityType<? extends HoneyBear> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.HONEY_BEAR;
    }

    @Override
    protected double followSpeed() {
        return 1.3D;
    }

    @Override
    protected void addSpeciesGoals() {
        goalSelector.addGoal(9, new BlockVisitGoal(this, 1.0D, 12, 1200,
                () -> BunnylandConfig.COMMON.honeyBearsLickHives.get() && Services.PLATFORM.mobGriefing(level(), this),
                s -> s.is(BlockTags.BEEHIVES) && s.hasProperty(BeehiveBlock.HONEY_LEVEL)
                        && s.getValue(BeehiveBlock.HONEY_LEVEL) >= BeehiveBlock.MAX_HONEY_LEVELS,
                (mob, pos) -> {
                    mob.level().setBlock(pos, mob.level().getBlockState(pos).setValue(BeehiveBlock.HONEY_LEVEL, 0), Block.UPDATE_ALL);
                    mob.level().playSound(null, pos, SoundEvents.HONEY_DRINK, SoundSource.NEUTRAL, 1.0F, 0.9F);
                    if (mob.level() instanceof ServerLevel server) {
                        server.sendParticles(ParticleTypes.DRIPPING_HONEY, pos.getX() + 0.5D, pos.getY() + 0.6D, pos.getZ() + 0.5D,
                                8, 0.3D, 0.3D, 0.3D, 0.0D);
                    }
                    mob.playAction("eat");
                    mob.heal(2.0F);
                    if (mob.isTame()) mob.addHappiness(6);
                }));
    }
}

package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.creature.Mood;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.ai.BlockVisitGoal;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/** Sniffs flowers, and cuddling a happy one is so calming it heals you a little. */
public class LavenderBunny extends BunnylandAnimal {
    public LavenderBunny(EntityType<? extends LavenderBunny> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.LAVENDER_BUNNY;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    @Override
    protected void addSpeciesGoals() {
        goalSelector.addGoal(9, new BlockVisitGoal(this, 0.9D, 8, 1200, () -> true,
                s -> s.is(BlockTags.SMALL_FLOWERS), (mob, pos) -> mob.playAction("special")));
    }

    @Override
    protected void onPetted(Player player) {
        if (getMood().ordinal() >= Mood.HAPPY.ordinal()) {
            player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0));
        }
    }
}

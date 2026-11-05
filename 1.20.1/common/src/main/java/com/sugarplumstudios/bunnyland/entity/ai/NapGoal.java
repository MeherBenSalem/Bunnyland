package com.sugarplumstudios.bunnyland.entity.ai;

import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;

import java.util.EnumSet;

/**
 * Curls up for a nap at bedtime. Wild creatures wake when a player comes close without sneaking;
 * pets sleep when sitting at bedtime, when tucked into a pet bed, or whenever their owner sleeps.
 */
public class NapGoal extends Goal {
    private final BunnylandAnimal mob;

    public NapGoal(BunnylandAnimal mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        if (mob.isNapping()) return mob.wantsToNap();
        return mob.getRandom().nextInt(reducedTickDelay(mob.isTame() ? 20 : 80)) == 0 && mob.wantsToNap() && !disturbed();
    }

    @Override
    public boolean canContinueToUse() {
        return mob.wantsToNap() && !disturbed();
    }

    private boolean disturbed() {
        if (mob.isTame()) return false;
        Player near = mob.level().getNearestPlayer(mob, 3.0D);
        return near != null && !near.isDiscrete() && !near.isSpectator();
    }

    @Override
    public void start() {
        mob.setNapping(true);
        mob.getNavigation().stop();
    }

    @Override
    public void stop() {
        mob.setNapping(false);
    }

    @Override
    public void tick() {
        mob.getNavigation().stop();
    }
}

package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.ai.BlockVisitGoal;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraftforge.event.ForgeEventFactory;

/** Can't resist ripe sweet berry bushes: it hops over and nibbles them. */
public class StrawberryBunny extends BunnylandAnimal {
    public StrawberryBunny(EntityType<? extends StrawberryBunny> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.STRAWBERRY_BUNNY;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    @Override
    protected void addSpeciesGoals() {
        goalSelector.addGoal(9, new BlockVisitGoal(this, 1.0D, 10, 800,
                () -> BunnylandConfig.COMMON.berryBunniesEatBerries.get() && ForgeEventFactory.getMobGriefingEvent(level(), this),
                s -> s.is(Blocks.SWEET_BERRY_BUSH) && s.getValue(SweetBerryBushBlock.AGE) >= 2,
                (mob, pos) -> {
                    mob.level().setBlock(pos, mob.level().getBlockState(pos).setValue(SweetBerryBushBlock.AGE, 1), Block.UPDATE_CLIENTS);
                    mob.level().playSound(null, pos, SoundEvents.SWEET_BERRY_BUSH_PICK_BERRIES, SoundSource.BLOCKS, 1.0F, 1.2F);
                    mob.playAction("eat");
                    mob.heal(1.0F);
                    if (mob.isTame()) mob.addHappiness(4);
                }));
    }
}

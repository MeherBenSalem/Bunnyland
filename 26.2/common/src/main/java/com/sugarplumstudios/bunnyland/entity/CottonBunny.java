package com.sugarplumstudios.bunnyland.entity;

import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.server.level.ServerLevel;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.gameevent.GameEvent;

/** Sheds a tuft of Cotton Fluff every few minutes and lands softly on its fluffy bottom. */
public class CottonBunny extends BunnylandAnimal {
    private int fluffTime = 6000;

    public CottonBunny(EntityType<? extends CottonBunny> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.COTTON_BUNNY;
    }

    @Override
    protected boolean isShy() {
        return true;
    }

    private int nextFluffTime() {
        int base = BunnylandConfig.COMMON.cottonFluffMinutes.get() * 1200;
        return base / 2 + random.nextInt(Math.max(1, base));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (!level().isClientSide() && isAlive() && !isBaby() && --fluffTime <= 0) {
            playSound(SoundEvents.WOOL_PLACE, 0.8F, 1.4F);
            spawnAtLocation((ServerLevel) level(), ModItems.COTTON_FLUFF.get());
            gameEvent(GameEvent.ENTITY_PLACE);
            fluffTime = nextFluffTime();
        }
    }

    @Override
    protected int calculateFallDamage(double distance, float multiplier) {
        return Math.max(0, super.calculateFallDamage(distance, multiplier) - 2);
    }

    @Override
    public void addAdditionalSaveData(ValueOutput tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("FluffTime", fluffTime);
    }

    @Override
    public void readAdditionalSaveData(ValueInput tag) {
        super.readAdditionalSaveData(tag);
        fluffTime = tag.getIntOr("FluffTime", nextFluffTime());
    }
}

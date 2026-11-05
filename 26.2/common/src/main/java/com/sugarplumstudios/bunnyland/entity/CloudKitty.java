package com.sugarplumstudios.bunnyland.entity;

import net.minecraft.server.level.ServerLevel;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * A kitten on a cloud: it drifts down instead of falling, purrs when petted and leaves its owner a little
 * gift after they sleep nearby.
 */
public class CloudKitty extends BunnylandAnimal {
    private boolean ownerWasSleeping;

    public CloudKitty(EntityType<? extends CloudKitty> type, Level level) {
        super(type, level);
    }

    @Override
    public Species species() {
        return Species.CLOUD_KITTY;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        Vec3 motion = getDeltaMovement();
        if (!onGround() && motion.y < 0.0D) setDeltaMovement(motion.multiply(1.0D, 0.7D, 1.0D));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (!isTame() || tickCount % 10 != 0) return;
        if (getOwner() instanceof Player owner) {
            boolean sleeping = owner.isSleeping() && distanceToSqr(owner) < 400.0D;
            if (sleeping) {
                ownerWasSleeping = true;
            } else if (ownerWasSleeping) {
                ownerWasSleeping = false;
                if (random.nextFloat() < 0.7F) leaveGift(owner);
            }
        }
    }

    private void leaveGift(Player owner) {
        ItemLike[] gifts = {Items.STRING, Items.FEATHER, ModItems.COTTON_FLUFF.get(), Items.PINK_PETALS, Items.SWEET_BERRIES,
                ModItems.PET_KIBBLE.get(), Items.DANDELION, Items.ALLIUM};
        ItemStack gift = random.nextFloat() < 0.05F ? new ItemStack(Items.PHANTOM_MEMBRANE)
                : new ItemStack(gifts[random.nextInt(gifts.length)], 1 + random.nextInt(2));
        spawnAtLocation((ServerLevel) level(), gift);
        playAction("happy");
        owner.sendOverlayMessage(Component.translatable("message.bunnyland.gift", getName()));
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {
    }
}

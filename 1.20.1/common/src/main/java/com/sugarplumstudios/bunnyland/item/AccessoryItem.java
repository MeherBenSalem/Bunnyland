package com.sugarplumstudios.bunnyland.item;

import com.sugarplumstudios.bunnyland.creature.Accessory;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/** A wearable cosmetic. A pet wears one accessory at a time; the previous one is handed back. */
public class AccessoryItem extends TooltipItem implements PetInteractable {
    private final Accessory accessory;

    public AccessoryItem(Accessory accessory, Properties properties) {
        super(properties);
        this.accessory = accessory;
    }

    public Accessory accessory() {
        return accessory;
    }

    @Override
    public InteractionResult interactWithPet(BunnylandAnimal pet, Player player, InteractionHand hand, ItemStack stack) {
        if (!pet.isTame()) return InteractionResult.PASS;
        if (!pet.isOwnedBy(player)) {
            if (!player.level().isClientSide) {
                player.displayClientMessage(Component.translatable("message.bunnyland.not_your_pet", pet.getName()), true);
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        if (pet.getAccessory() == accessory) return InteractionResult.PASS;
        if (!player.level().isClientSide) {
            Accessory old = pet.getAccessory();
            if (old != Accessory.NONE && old.item() != null) pet.spawnAtLocation(old.item());
            pet.setAccessory(accessory);
            pet.level().playSound(null, pet, SoundEvents.ARMOR_EQUIP_GENERIC, SoundSource.NEUTRAL, 0.8F, 1.4F);
            if (!player.getAbilities().instabuild) stack.shrink(1);
            pet.onDressedUp(player);
        }
        return InteractionResult.sidedSuccess(player.level().isClientSide);
    }
}

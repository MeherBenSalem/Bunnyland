package com.sugarplumstudios.bunnyland.item;

import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.DyeableLeatherItem;
import net.minecraft.world.item.ItemStack;

/**
 * Pet Collar and Pet Bow. Dye them like leather armour (any dyes in a crafting grid), then use them on
 * your pet. Putting on a new one gives the old one back with its colour.
 */
public class DyeableCosmeticItem extends TooltipItem implements DyeableLeatherItem, PetInteractable {
    public enum Slot {
        COLLAR, BOW
    }

    private final Slot slot;
    private final int defaultColor;

    public DyeableCosmeticItem(Slot slot, int defaultColor, Properties properties) {
        super(properties);
        this.slot = slot;
        this.defaultColor = defaultColor;
    }

    public Slot slot() {
        return slot;
    }

    @Override
    public int getColor(ItemStack stack) {
        return hasCustomColor(stack) ? DyeableLeatherItem.super.getColor(stack) : defaultColor;
    }

    public ItemStack withColor(int color) {
        ItemStack stack = new ItemStack(this);
        if (color != defaultColor) setColor(stack, color);
        return stack;
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
        if (!player.level().isClientSide) {
            int color = getColor(stack);
            int old = slot == Slot.COLLAR ? pet.getCollarColor() : pet.getBowColor();
            if (old == color) return InteractionResult.PASS;
            if (old >= 0) pet.spawnAtLocation(withColor(old));
            if (slot == Slot.COLLAR) {
                pet.setCollarColor(color);
                pet.playSound(ModSounds.COLLAR_JINGLE.get(), 0.8F, 1.0F);
            } else {
                pet.setBowColor(color);
                pet.level().playSound(null, pet, SoundEvents.ARMOR_EQUIP_LEATHER, SoundSource.NEUTRAL, 0.8F, 1.3F);
            }
            if (!player.getAbilities().instabuild) stack.shrink(1);
            pet.onDressedUp(player);
        }
        return InteractionResult.sidedSuccess(player.level().isClientSide);
    }
}

package com.sugarplumstudios.bunnyland.item;

import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/**
 * Items that do something special when used on a Bunnyland creature. The creature calls this before its
 * own interactions; return {@link InteractionResult#PASS} to let the creature handle the click normally.
 */
public interface PetInteractable {
    InteractionResult interactWithPet(BunnylandAnimal pet, Player player, InteractionHand hand, ItemStack stack);
}

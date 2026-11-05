package com.sugarplumstudios.bunnyland.item;

import com.sugarplumstudios.bunnyland.client.ClientAccess;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.journal.JournalEvents;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Opens the Pet Journal. Used on a creature it tells you about it (species, variant, owner and mood)
 * and writes it into the journal.
 */
public class PetJournalItem extends TooltipItem implements PetInteractable {
    public PetJournalItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide()) {
            ClientAccess.openJournal();
        } else if (player instanceof ServerPlayer sp) {
            JournalEvents.sync(sp);
        }
        player.playSound(SoundEvents.BOOK_PAGE_TURN, 1.0F, 1.0F);
        player.awardStat(Stats.ITEM_USED.get(this));
        return InteractionResult.SUCCESS;
    }

    @Override
    public InteractionResult interactWithPet(BunnylandAnimal pet, Player player, InteractionHand hand, ItemStack stack) {
        if (!player.level().isClientSide() && player instanceof ServerPlayer sp) {
            pet.showStatus(sp);
            JournalEvents.discover(sp, pet);
        }
        return InteractionResult.SUCCESS;
    }
}

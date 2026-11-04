package com.sugarplumstudios.bunnyland.journal;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.network.JournalToastPacket;
import com.sugarplumstudios.bunnyland.network.ModNetwork;
import com.sugarplumstudios.bunnyland.network.SyncJournalPacket;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Fills in Pet Journals: creatures a player can see nearby are discovered automatically. */
@Mod.EventBusSubscriber(modid = Bunnyland.MOD_ID)
public final class JournalEvents {
    private JournalEvents() {
    }

    public static PlayerJournal journal(ServerPlayer player) {
        return JournalData.get(player.server).of(player.getUUID());
    }

    private static void changed(ServerPlayer player) {
        JournalData.get(player.server).setDirty();
        sync(player);
    }

    public static void sync(ServerPlayer player) {
        ModNetwork.sendTo(player, new SyncJournalPacket(journal(player)));
    }

    /** Records that the player has seen this creature (and its variant). */
    public static void discover(ServerPlayer player, BunnylandAnimal animal) {
        int changes = journal(player).see(animal.species(), animal.getVariant());
        if (changes == 0) return;
        changed(player);
        if ((changes & PlayerJournal.NEW_SPECIES) != 0) toast(player, JournalToastPacket.DISCOVERED, animal.species(), animal.getVariant());
        else if ((changes & PlayerJournal.NEW_RARE) != 0) toast(player, JournalToastPacket.RARE, animal.species(), animal.getVariant());
    }

    public static void tamed(ServerPlayer player, BunnylandAnimal animal) {
        int changes = journal(player).tame(animal.species(), animal.getVariant());
        if (changes == 0) return;
        changed(player);
        if ((changes & PlayerJournal.NEW_TAMED) != 0) toast(player, JournalToastPacket.TAMED, animal.species(), animal.getVariant());
    }

    public static void seeVariant(ServerPlayer player, Species species, int variant) {
        int changes = journal(player).see(species, variant);
        if (changes == 0) return;
        changed(player);
        if ((changes & PlayerJournal.NEW_RARE) != 0) toast(player, JournalToastPacket.RARE, species, variant);
    }

    private static void toast(ServerPlayer player, int kind, Species species, int variant) {
        ModNetwork.sendTo(player, new JournalToastPacket(kind, species.ordinal(), variant));
    }

    /** Looks for creatures the player can see. Cheap: runs every two seconds per player. */
    public static void scan(ServerPlayer player) {
        double range = BunnylandConfig.COMMON.discoveryRange.get();
        for (BunnylandAnimal animal : player.level().getEntitiesOfClass(BunnylandAnimal.class, player.getBoundingBox().inflate(range),
                a -> a.isAlive() && !a.isInvisible())) {
            if (player.hasLineOfSight(animal)) discover(player, animal);
        }
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        PlayerJournal journal = journal(player);
        if (BunnylandConfig.COMMON.starterJournal.get() && !journal.starterGiven()) {
            journal.setStarterGiven();
            JournalData.get(player.server).setDirty();
            ItemStack book = new ItemStack(ModItems.PET_JOURNAL.get());
            if (!player.getInventory().add(book)) player.drop(book, false);
            player.sendSystemMessage(Component.translatable("message.bunnyland.journal_given"));
        }
        sync(player);
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase == TickEvent.Phase.END && event.player instanceof ServerPlayer player
                && !player.isSpectator() && player.tickCount % 40 == 0) {
            scan(player);
        }
    }
}

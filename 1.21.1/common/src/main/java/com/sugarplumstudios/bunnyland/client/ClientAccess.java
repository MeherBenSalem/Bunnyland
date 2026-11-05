package com.sugarplumstudios.bunnyland.client;

import com.sugarplumstudios.bunnyland.client.screen.PetJournalScreen;
import com.sugarplumstudios.bunnyland.client.toast.JournalToast;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.journal.PlayerJournal;
import net.minecraft.client.Minecraft;

/** Client-only entry points, called from common code and packets only on the client. */
public final class ClientAccess {
    private static PlayerJournal journal = new PlayerJournal();

    private ClientAccess() {
    }

    public static PlayerJournal journal() {
        return journal;
    }

    public static void receiveJournal(PlayerJournal received) {
        journal = received;
    }

    public static void openJournal() {
        Minecraft.getInstance().setScreen(new PetJournalScreen());
    }

    public static void showToast(int kind, int species, int variant) {
        Species s = Species.byOrdinal(species);
        if (s == null || !BunnylandConfig.CLIENT.journalToasts.get()) return;
        Minecraft.getInstance().getToasts().addToast(new JournalToast(kind, s, variant));
    }
}

package com.sugarplumstudios.bunnyland.network;

import com.sugarplumstudios.bunnyland.client.ClientAccess;
import com.sugarplumstudios.bunnyland.journal.PlayerJournal;
import net.minecraft.network.FriendlyByteBuf;

/** Server -> client: the player's whole Pet Journal (a few dozen bytes). */
public record SyncJournalPacket(PlayerJournal journal) implements ClientboundMessage {
    @Override
    public void write(FriendlyByteBuf buf) {
        journal.write(buf);
    }

    public static SyncJournalPacket decode(FriendlyByteBuf buf) {
        return new SyncJournalPacket(PlayerJournal.read(buf));
    }

    @Override
    public void handleOnClient() {
        ClientAccess.receiveJournal(journal);
    }
}

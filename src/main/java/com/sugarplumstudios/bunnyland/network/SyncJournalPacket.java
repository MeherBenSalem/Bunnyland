package com.sugarplumstudios.bunnyland.network;

import com.sugarplumstudios.bunnyland.client.ClientAccess;
import com.sugarplumstudios.bunnyland.journal.PlayerJournal;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Server -> client: the player's whole Pet Journal (a few dozen bytes). */
public record SyncJournalPacket(PlayerJournal journal) {
    public static void encode(SyncJournalPacket msg, FriendlyByteBuf buf) {
        msg.journal.write(buf);
    }

    public static SyncJournalPacket decode(FriendlyByteBuf buf) {
        return new SyncJournalPacket(PlayerJournal.read(buf));
    }

    public static void handle(SyncJournalPacket msg, Supplier<NetworkEvent.Context> ctx) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> ClientAccess.receiveJournal(msg.journal));
        ctx.get().setPacketHandled(true);
    }
}

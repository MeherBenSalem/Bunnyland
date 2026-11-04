package com.sugarplumstudios.bunnyland.network;

import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

public final class ModNetwork {
    private static final String PROTOCOL = "1";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            Bunnyland.id("main"), () -> PROTOCOL, PROTOCOL::equals, PROTOCOL::equals);

    private ModNetwork() {
    }

    public static void register() {
        int id = 0;
        CHANNEL.messageBuilder(SyncJournalPacket.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(SyncJournalPacket::encode)
                .decoder(SyncJournalPacket::decode)
                .consumerMainThread(SyncJournalPacket::handle)
                .add();
        CHANNEL.messageBuilder(JournalToastPacket.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(JournalToastPacket::encode)
                .decoder(JournalToastPacket::decode)
                .consumerMainThread(JournalToastPacket::handle)
                .add();
    }

    public static void sendTo(ServerPlayer player, Object message) {
        // Fake players (automation mods, GameTest mocks) have no network channel to send to.
        if (player.connection == null || player.connection.connection.channel() == null) return;
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), message);
    }
}

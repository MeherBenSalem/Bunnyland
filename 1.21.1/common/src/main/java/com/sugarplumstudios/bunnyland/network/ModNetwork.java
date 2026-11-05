package com.sugarplumstudios.bunnyland.network;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.platform.Services;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;

import java.util.List;
import java.util.function.Function;

/** Bunnyland's messages. Each loader registers {@link #MESSAGES} with its own networking API. */
public final class ModNetwork {
    public static final String PROTOCOL = "1";

    public record Type<M extends ClientboundMessage>(ResourceLocation id, Class<M> type, Function<FriendlyByteBuf, M> decoder) {
    }

    public static final List<Type<?>> MESSAGES = List.of(
            new Type<>(Bunnyland.id("sync_journal"), SyncJournalPacket.class, SyncJournalPacket::decode),
            new Type<>(Bunnyland.id("journal_toast"), JournalToastPacket.class, JournalToastPacket::decode));

    private ModNetwork() {
    }

    public static Type<?> typeOf(ClientboundMessage message) {
        for (Type<?> type : MESSAGES) {
            if (type.type() == message.getClass()) return type;
        }
        throw new IllegalArgumentException("Unregistered message " + message.getClass());
    }

    public static void sendTo(ServerPlayer player, ClientboundMessage message) {
        // Fake players (automation mods, GameTest mocks) have no connection; the platforms check the rest.
        if (player.connection == null) return;
        Services.PLATFORM.sendToPlayer(player, message);
    }
}

package com.sugarplumstudios.bunnyland.network;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** A Bunnyland message as a vanilla custom payload (one payload type per message), so every loader can send it. */
public record MessagePayload(CustomPacketPayload.Type<MessagePayload> type, ClientboundMessage message) implements CustomPacketPayload {
    private static final Map<Identifier, CustomPacketPayload.Type<MessagePayload>> TYPES = new ConcurrentHashMap<>();

    public static CustomPacketPayload.Type<MessagePayload> typeFor(ModNetwork.Type<?> message) {
        return TYPES.computeIfAbsent(message.id(), CustomPacketPayload.Type::new);
    }

    public static MessagePayload of(ClientboundMessage message) {
        return new MessagePayload(typeFor(ModNetwork.typeOf(message)), message);
    }

    public static StreamCodec<RegistryFriendlyByteBuf, MessagePayload> codec(ModNetwork.Type<?> message) {
        CustomPacketPayload.Type<MessagePayload> type = typeFor(message);
        return StreamCodec.of((buf, payload) -> payload.message().write(buf), buf -> new MessagePayload(type, message.decoder().apply(buf)));
    }
}

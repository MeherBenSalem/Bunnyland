package com.sugarplumstudios.bunnyland.neoforge;

import com.sugarplumstudios.bunnyland.network.ClientboundMessage;
import com.sugarplumstudios.bunnyland.network.MessagePayload;
import com.sugarplumstudios.bunnyland.network.ModNetwork;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

final class NeoForgeNetwork {
    private NeoForgeNetwork() {
    }

    static MessagePayload payload(ClientboundMessage message) {
        return MessagePayload.of(message);
    }

    static void register(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar(ModNetwork.PROTOCOL);
        for (ModNetwork.Type<?> type : ModNetwork.MESSAGES) {
            // Handlers run on the client's main thread.
            registrar.playToClient(MessagePayload.typeFor(type), MessagePayload.codec(type),
                    (payload, context) -> payload.message().handleOnClient());
        }
    }
}

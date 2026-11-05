package com.sugarplumstudios.bunnyland.forge;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.network.ClientboundMessage;
import com.sugarplumstudios.bunnyland.network.ModNetwork;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

public final class ForgeNetwork {
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            Bunnyland.id("main"), () -> ModNetwork.PROTOCOL, ModNetwork.PROTOCOL::equals, ModNetwork.PROTOCOL::equals);

    private ForgeNetwork() {
    }

    public static void register() {
        int id = 0;
        for (ModNetwork.Type<?> type : ModNetwork.MESSAGES) register(type, id++);
    }

    private static <M extends ClientboundMessage> void register(ModNetwork.Type<M> type, int id) {
        CHANNEL.messageBuilder(type.type(), id, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(ClientboundMessage::write)
                .decoder(type.decoder())
                .consumerMainThread((message, context) -> {
                    message.handleOnClient();
                    context.get().setPacketHandled(true);
                })
                .add();
    }
}

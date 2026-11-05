package com.sugarplumstudios.bunnyland.network;

import net.minecraft.network.FriendlyByteBuf;

/** A server -> client message. Handled on the client's main thread. */
public interface ClientboundMessage {
    void write(FriendlyByteBuf buf);

    /** Runs on the client only, so it may use client classes. */
    void handleOnClient();
}

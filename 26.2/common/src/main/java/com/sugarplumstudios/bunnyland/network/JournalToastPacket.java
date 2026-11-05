package com.sugarplumstudios.bunnyland.network;

import com.sugarplumstudios.bunnyland.client.ClientAccess;
import net.minecraft.network.FriendlyByteBuf;

/** Server -> client: show a "discovered / befriended / rare variant" toast. */
public record JournalToastPacket(int kind, int species, int variant) implements ClientboundMessage {
    public static final int DISCOVERED = 0;
    public static final int TAMED = 1;
    public static final int RARE = 2;

    @Override
    public void write(FriendlyByteBuf buf) {
        buf.writeByte(kind);
        buf.writeByte(species);
        buf.writeByte(variant);
    }

    public static JournalToastPacket decode(FriendlyByteBuf buf) {
        return new JournalToastPacket(buf.readByte(), buf.readByte(), buf.readByte());
    }

    @Override
    public void handleOnClient() {
        ClientAccess.showToast(kind, species, variant);
    }
}

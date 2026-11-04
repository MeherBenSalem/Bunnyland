package com.sugarplumstudios.bunnyland.network;

import com.sugarplumstudios.bunnyland.client.ClientAccess;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Server -> client: show a "discovered / befriended / rare variant" toast. */
public record JournalToastPacket(int kind, int species, int variant) {
    public static final int DISCOVERED = 0;
    public static final int TAMED = 1;
    public static final int RARE = 2;

    public static void encode(JournalToastPacket msg, FriendlyByteBuf buf) {
        buf.writeByte(msg.kind);
        buf.writeByte(msg.species);
        buf.writeByte(msg.variant);
    }

    public static JournalToastPacket decode(FriendlyByteBuf buf) {
        return new JournalToastPacket(buf.readByte(), buf.readByte(), buf.readByte());
    }

    public static void handle(JournalToastPacket msg, Supplier<NetworkEvent.Context> ctx) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> ClientAccess.showToast(msg.kind, msg.species, msg.variant));
        ctx.get().setPacketHandled(true);
    }
}

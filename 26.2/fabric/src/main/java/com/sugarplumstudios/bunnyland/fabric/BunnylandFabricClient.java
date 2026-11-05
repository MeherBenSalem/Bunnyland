package com.sugarplumstudios.bunnyland.fabric;

import com.sugarplumstudios.bunnyland.client.BunnylandClient;
import com.sugarplumstudios.bunnyland.network.MessagePayload;
import com.sugarplumstudios.bunnyland.network.ModNetwork;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.particle.v1.ParticleProviderRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

public final class BunnylandFabricClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BunnylandClient.init();
        BunnylandClient.registerRenderers(EntityRendererRegistry::register);
        BunnylandClient.registerParticles((type, factory) ->
                ParticleProviderRegistry.getInstance().register(type, factory::create));
        for (ModNetwork.Type<?> type : ModNetwork.MESSAGES) receive(type);
    }

    private static void receive(ModNetwork.Type<?> type) {
        ClientPlayNetworking.registerGlobalReceiver(MessagePayload.typeFor(type),
                (payload, context) -> context.client().execute(payload.message()::handleOnClient));
    }
}

package com.sugarplumstudios.bunnyland.neoforge;

import com.sugarplumstudios.bunnyland.client.BunnylandClient;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterParticleProvidersEvent;

final class NeoForgeClient {
    private NeoForgeClient() {
    }

    static void init(IEventBus modBus) {
        BunnylandClient.init();
        modBus.addListener((EntityRenderersEvent.RegisterRenderers event) ->
                BunnylandClient.registerRenderers(event::registerEntityRenderer));
        modBus.addListener((RegisterParticleProvidersEvent event) ->
                BunnylandClient.registerParticles((type, factory) -> event.registerSpriteSet(type, factory::create)));
    }
}

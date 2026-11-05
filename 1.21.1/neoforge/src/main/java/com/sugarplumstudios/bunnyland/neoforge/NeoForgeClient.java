package com.sugarplumstudios.bunnyland.neoforge;

import com.sugarplumstudios.bunnyland.client.BunnylandClient;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterClientReloadListenersEvent;
import net.neoforged.neoforge.client.event.RegisterColorHandlersEvent;
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
        modBus.addListener((RegisterColorHandlersEvent.Item event) ->
                event.register(BunnylandClient.DYED_ITEM_COLOR, BunnylandClient.dyedItems()));
        modBus.addListener((RegisterClientReloadListenersEvent event) ->
                event.registerReloadListener((ResourceManagerReloadListener) manager -> BunnylandClient.onResourcesReloaded()));
        modBus.addListener((FMLClientSetupEvent event) ->
                event.enqueueWork(() -> BunnylandClient.registerItemProperties(ItemProperties::register)));
    }
}

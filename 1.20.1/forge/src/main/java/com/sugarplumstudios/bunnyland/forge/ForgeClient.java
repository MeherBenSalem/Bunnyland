package com.sugarplumstudios.bunnyland.forge;

import com.sugarplumstudios.bunnyland.client.BunnylandClient;
import com.sugarplumstudios.bunnyland.client.dev.DevSnapshots;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterClientReloadListenersEvent;
import net.minecraftforge.client.event.RegisterColorHandlersEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

final class ForgeClient {
    private ForgeClient() {
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
        modBus.addListener((FMLClientSetupEvent event) -> {
            event.enqueueWork(() -> BunnylandClient.registerItemProperties(ItemProperties::register));
            if (DevSnapshots.enabled()) MinecraftForge.EVENT_BUS.register(DevSnapshots.class);
        });
    }
}

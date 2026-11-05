package com.sugarplumstudios.bunnyland.fabric;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.client.BunnylandClient;
import com.sugarplumstudios.bunnyland.network.ClientboundMessage;
import com.sugarplumstudios.bunnyland.network.ModNetwork;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.particle.v1.ParticleFactoryRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.ColorProviderRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.object.builder.v1.client.model.FabricModelPredicateProviderRegistry;
import net.fabricmc.fabric.api.resource.ResourceManagerHelper;
import net.fabricmc.fabric.api.resource.SimpleSynchronousResourceReloadListener;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.resources.ResourceManager;

public final class BunnylandFabricClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BunnylandClient.init();
        BunnylandClient.registerRenderers(EntityRendererRegistry::register);
        BunnylandClient.registerParticles((type, factory) ->
                ParticleFactoryRegistry.getInstance().register(type, factory::create));
        ColorProviderRegistry.ITEM.register(BunnylandClient.DYED_ITEM_COLOR, BunnylandClient.dyedItems());
        BunnylandClient.registerItemProperties(FabricModelPredicateProviderRegistry::register);
        ResourceManagerHelper.get(PackType.CLIENT_RESOURCES).registerReloadListener(new SimpleSynchronousResourceReloadListener() {
            @Override
            public ResourceLocation getFabricId() {
                return Bunnyland.id("glow_cache");
            }

            @Override
            public void onResourceManagerReload(ResourceManager manager) {
                BunnylandClient.onResourcesReloaded();
            }
        });
        for (ModNetwork.Type<?> type : ModNetwork.MESSAGES) receive(type);
    }

    private static <M extends ClientboundMessage> void receive(ModNetwork.Type<M> type) {
        ClientPlayNetworking.registerGlobalReceiver(type.id(), (client, handler, buf, responseSender) -> {
            M message = type.decoder().apply(buf);
            client.execute(message::handleOnClient);
        });
    }
}

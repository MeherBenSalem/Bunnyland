package com.sugarplumstudios.bunnyland.client;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.client.dev.DevSnapshots;
import com.sugarplumstudios.bunnyland.client.particle.BunnylandParticle;
import com.sugarplumstudios.bunnyland.client.render.CreatureGlowLayer;
import com.sugarplumstudios.bunnyland.client.render.CreatureRenderer;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.item.PetCarrierItem;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.DyeableLeatherItem;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterClientReloadListenersEvent;
import net.minecraftforge.client.event.RegisterColorHandlersEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;

@Mod.EventBusSubscriber(modid = Bunnyland.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientModEvents {
    private ClientModEvents() {
    }

    @SubscribeEvent
    @SuppressWarnings("unchecked")
    public static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        for (Species species : Species.values()) {
            EntityType<BunnylandAnimal> type = (EntityType<BunnylandAnimal>) ModEntities.get(species);
            event.registerEntityRenderer(type, ctx -> new CreatureRenderer<>(ctx, species));
        }
    }

    @SubscribeEvent
    public static void onRegisterParticles(RegisterParticleProvidersEvent event) {
        event.registerSpriteSet(ModParticles.SPARKLE.get(), sprites -> new BunnylandParticle.Provider(sprites, BunnylandParticle.Kind.SPARKLE));
        event.registerSpriteSet(ModParticles.ZZZ.get(), sprites -> new BunnylandParticle.Provider(sprites, BunnylandParticle.Kind.ZZZ));
    }

    @SubscribeEvent
    public static void onItemColors(RegisterColorHandlersEvent.Item event) {
        event.register((stack, tint) -> tint == 0 ? ((DyeableLeatherItem) stack.getItem()).getColor(stack) | 0xFF000000 : -1,
                ModItems.PET_COLLAR.get(), ModItems.PET_BOW.get());
    }

    @SubscribeEvent
    public static void onReloadListeners(RegisterClientReloadListenersEvent event) {
        event.registerReloadListener((ResourceManagerReloadListener) manager -> CreatureGlowLayer.clearCache());
    }

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> ItemProperties.register(ModItems.PET_CARRIER.get(), Bunnyland.id("occupied"),
                (stack, level, entity, seed) -> PetCarrierItem.hasPet(stack) ? 1.0F : 0.0F));
        if (DevSnapshots.enabled()) MinecraftForge.EVENT_BUS.register(DevSnapshots.class);
    }
}

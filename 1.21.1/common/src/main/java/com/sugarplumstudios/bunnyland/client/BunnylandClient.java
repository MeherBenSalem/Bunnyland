package com.sugarplumstudios.bunnyland.client;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.client.particle.BunnylandParticle;
import com.sugarplumstudios.bunnyland.client.render.CreatureGlowLayer;
import com.sugarplumstudios.bunnyland.client.render.CreatureRenderer;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.item.PetCarrierItem;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import net.minecraft.client.color.item.ItemColor;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.item.ClampedItemPropertyFunction;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import com.sugarplumstudios.bunnyland.item.DyeableCosmeticItem;
import net.minecraft.world.item.Item;

/** Client start-up shared by every loader. Each loader calls these from its own registration events. */
public final class BunnylandClient {
    private BunnylandClient() {
    }

    public static void init() {
        BunnylandConfig.loadClient();
    }

    public interface RendererSink {
        void register(EntityType<BunnylandAnimal> type, EntityRendererProvider<BunnylandAnimal> provider);
    }

    @SuppressWarnings("unchecked")
    public static void registerRenderers(RendererSink sink) {
        for (Species species : Species.values()) {
            sink.register((EntityType<BunnylandAnimal>) ModEntities.get(species), ctx -> new CreatureRenderer<>(ctx, species));
        }
    }

    public interface ParticleSink {
        void register(SimpleParticleType type, ParticleProviderFactory factory);
    }

    public interface ParticleProviderFactory {
        ParticleProvider<SimpleParticleType> create(SpriteSet sprites);
    }

    public static void registerParticles(ParticleSink sink) {
        sink.register(ModParticles.SPARKLE.get(), sprites -> new BunnylandParticle.Provider(sprites, BunnylandParticle.Kind.SPARKLE));
        sink.register(ModParticles.ZZZ.get(), sprites -> new BunnylandParticle.Provider(sprites, BunnylandParticle.Kind.ZZZ));
    }

    /** Tints the dyeable collar and bow (layer 0) with their colour. */
    public static final ItemColor DYED_ITEM_COLOR = (stack, tint) ->
            tint == 0 ? ((DyeableCosmeticItem) stack.getItem()).getColor(stack) | 0xFF000000 : -1;

    public static Item[] dyedItems() {
        return new Item[]{ModItems.PET_COLLAR.get(), ModItems.PET_BOW.get()};
    }

    public interface ItemPropertySink {
        void register(Item item, ResourceLocation id, ClampedItemPropertyFunction function);
    }

    public static void registerItemProperties(ItemPropertySink sink) {
        sink.register(ModItems.PET_CARRIER.get(), Bunnyland.id("occupied"),
                (stack, level, entity, seed) -> PetCarrierItem.hasPet(stack) ? 1.0F : 0.0F);
    }

    /** Called whenever client resources reload. */
    public static void onResourcesReloaded() {
        CreatureGlowLayer.clearCache();
    }
}

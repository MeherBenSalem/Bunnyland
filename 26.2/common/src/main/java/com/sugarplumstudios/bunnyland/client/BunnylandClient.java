package com.sugarplumstudios.bunnyland.client;

import com.sugarplumstudios.bunnyland.client.particle.BunnylandParticle;
import com.sugarplumstudios.bunnyland.client.render.CreatureGlowLayer;
import com.sugarplumstudios.bunnyland.client.render.CreatureRenderer;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.world.entity.EntityType;

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

    // Since 1.21.4 the collar and bow tints and the carrier's "occupied" look come from their item model
    // definitions (assets/bunnyland/items/*.json), so there is nothing to register here.

    /** Called whenever client resources reload. */
    public static void onResourcesReloaded() {
        CreatureGlowLayer.clearCache();
    }
}

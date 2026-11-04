package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, Bunnyland.MOD_ID);

    /** Pastel twinkles around rare variants and overjoyed pets. */
    public static final RegistryObject<SimpleParticleType> SPARKLE = PARTICLES.register("sparkle", () -> new SimpleParticleType(false));
    /** Sleepy Zzz's above napping creatures. */
    public static final RegistryObject<SimpleParticleType> ZZZ = PARTICLES.register("zzz", () -> new SimpleParticleType(false));

    private ModParticles() {
    }
}

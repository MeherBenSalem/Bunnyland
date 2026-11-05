package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.platform.Services;
import net.minecraft.core.registries.Registries;
import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import com.sugarplumstudios.bunnyland.platform.RegistryEntry;

public final class ModParticles {

    /** Pastel twinkles around rare variants and overjoyed pets. */
    public static final RegistryEntry<SimpleParticleType> SPARKLE = Services.PLATFORM.register(Registries.PARTICLE_TYPE, "sparkle", () -> new SimpleParticleType(false) { });
    /** Sleepy Zzz's above napping creatures. */
    public static final RegistryEntry<SimpleParticleType> ZZZ = Services.PLATFORM.register(Registries.PARTICLE_TYPE, "zzz", () -> new SimpleParticleType(false) { });

    private ModParticles() {
    }
}

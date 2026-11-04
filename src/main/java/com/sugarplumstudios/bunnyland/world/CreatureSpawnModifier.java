package com.sugarplumstudios.bunnyland.world;

import com.mojang.serialization.Codec;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModBiomeModifiers;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import net.minecraft.core.Holder;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraftforge.common.world.BiomeModifier;
import net.minecraftforge.common.world.ModifiableBiomeInfo;

/**
 * Adds every creature to the biomes in its {@code bunnyland:spawns/<id>} biome tag, using the spawn
 * weights and group sizes from the common config (read when a world loads).
 */
public class CreatureSpawnModifier implements BiomeModifier {
    @Override
    public void modify(Holder<Biome> biome, Phase phase, ModifiableBiomeInfo.BiomeInfo.Builder builder) {
        if (phase != Phase.ADD) return;
        double multiplier = BunnylandConfig.COMMON.spawnWeightMultiplier.get();
        for (Species species : Species.values()) {
            BunnylandConfig.SpawnSettings settings = BunnylandConfig.COMMON.spawns.get(species);
            if (!settings.enabled.get() || !biome.is(species.spawnBiomes)) continue;
            int weight = (int) Math.round(settings.weight.get() * multiplier);
            if (weight <= 0) continue;
            int min = settings.minGroup.get();
            int max = Math.max(min, settings.maxGroup.get());
            builder.getMobSpawnSettings().addSpawn(species.category(),
                    new MobSpawnSettings.SpawnerData(ModEntities.get(species), weight, min, max));
        }
    }

    @Override
    public Codec<? extends BiomeModifier> codec() {
        return ModBiomeModifiers.CREATURE_SPAWNS.get();
    }
}

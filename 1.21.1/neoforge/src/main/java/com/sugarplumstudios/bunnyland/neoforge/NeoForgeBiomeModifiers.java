package com.sugarplumstudios.bunnyland.neoforge;

import com.mojang.serialization.MapCodec;
import com.sugarplumstudios.bunnyland.Bunnyland;
import net.neoforged.neoforge.common.world.BiomeModifier;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

public final class NeoForgeBiomeModifiers {
    public static final DeferredRegister<MapCodec<? extends BiomeModifier>> SERIALIZERS =
            DeferredRegister.create(NeoForgeRegistries.Keys.BIOME_MODIFIER_SERIALIZERS, Bunnyland.MOD_ID);

    /** Referenced by data/bunnyland/neoforge/biome_modifier/creature_spawns.json. */
    public static final DeferredHolder<MapCodec<? extends BiomeModifier>, MapCodec<CreatureSpawnModifier>> CREATURE_SPAWNS =
            SERIALIZERS.register("creature_spawns", () -> MapCodec.unit(CreatureSpawnModifier::new));

    private NeoForgeBiomeModifiers() {
    }
}

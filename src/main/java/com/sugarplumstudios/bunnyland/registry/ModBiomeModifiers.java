package com.sugarplumstudios.bunnyland.registry;

import com.mojang.serialization.Codec;
import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.world.CreatureSpawnModifier;
import net.minecraftforge.common.world.BiomeModifier;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModBiomeModifiers {
    public static final DeferredRegister<Codec<? extends BiomeModifier>> SERIALIZERS =
            DeferredRegister.create(ForgeRegistries.Keys.BIOME_MODIFIER_SERIALIZERS, Bunnyland.MOD_ID);

    /** Referenced by data/bunnyland/forge/biome_modifier/creature_spawns.json. */
    public static final RegistryObject<Codec<CreatureSpawnModifier>> CREATURE_SPAWNS =
            SERIALIZERS.register("creature_spawns", () -> Codec.unit(CreatureSpawnModifier::new));

    private ModBiomeModifiers() {
    }
}

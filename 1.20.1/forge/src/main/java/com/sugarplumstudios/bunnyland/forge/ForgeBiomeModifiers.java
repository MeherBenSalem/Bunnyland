package com.sugarplumstudios.bunnyland.forge;

import com.mojang.serialization.Codec;
import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraftforge.common.world.BiomeModifier;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ForgeBiomeModifiers {
    public static final DeferredRegister<Codec<? extends BiomeModifier>> SERIALIZERS =
            DeferredRegister.create(ForgeRegistries.Keys.BIOME_MODIFIER_SERIALIZERS, Bunnyland.MOD_ID);

    /** Referenced by data/bunnyland/forge/biome_modifier/creature_spawns.json. */
    public static final RegistryObject<Codec<CreatureSpawnModifier>> CREATURE_SPAWNS =
            SERIALIZERS.register("creature_spawns", () -> Codec.unit(CreatureSpawnModifier::new));

    private ForgeBiomeModifiers() {
    }
}

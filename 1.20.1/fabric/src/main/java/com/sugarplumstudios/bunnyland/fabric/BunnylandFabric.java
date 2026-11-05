package com.sugarplumstudios.bunnyland.fabric;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.journal.JournalEvents;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.world.CreatureSpawning;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.biome.v1.ModificationPhase;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.biome.MobSpawnSettings;

public final class BunnylandFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        Bunnyland.init();

        for (Species species : Species.values()) {
            FabricDefaultAttributeRegistry.register(ModEntities.get(species), ModEntities.attributes(species));
        }
        CreatureSpawning.register(SpawnPlacements::register);
        addSpawns();

        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> JournalEvents.onLogin(handler.player));
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            for (ServerPlayer player : server.getPlayerList().getPlayers()) JournalEvents.onPlayerTick(player);
        });
    }

    /** Adds every creature to the biomes in its bunnyland:spawns/<id> biome tag, as the Forge biome modifier does. */
    private static void addSpawns() {
        for (Species species : Species.values()) {
            BiomeModifications.create(Bunnyland.id("spawns/" + species.id)).add(ModificationPhase.ADDITIONS,
                    BiomeSelectors.tag(species.spawnBiomes), (selection, context) -> {
                        BunnylandConfig.SpawnSettings settings = BunnylandConfig.COMMON.spawns.get(species);
                        if (!settings.enabled.get()) return;
                        int weight = (int) Math.round(settings.weight.get() * BunnylandConfig.COMMON.spawnWeightMultiplier.get());
                        if (weight <= 0) return;
                        int min = settings.minGroup.get();
                        int max = Math.max(min, settings.maxGroup.get());
                        context.getSpawnSettings().addSpawn(species.category(),
                                new MobSpawnSettings.SpawnerData(ModEntities.get(species), weight, min, max));
                    });
        }
    }
}

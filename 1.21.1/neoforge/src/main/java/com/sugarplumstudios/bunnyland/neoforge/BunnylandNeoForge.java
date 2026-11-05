package com.sugarplumstudios.bunnyland.neoforge;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.journal.JournalEvents;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.world.CreatureSpawning;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

@Mod(Bunnyland.MOD_ID)
public final class BunnylandNeoForge {
    public BunnylandNeoForge(IEventBus modBus) {
        Bunnyland.init();
        NeoForgeBiomeModifiers.SERIALIZERS.register(modBus);
        NeoForgePlatform.registerAll(modBus);

        modBus.addListener(NeoForgeNetwork::register);
        modBus.addListener(BunnylandNeoForge::onAttributes);
        modBus.addListener(BunnylandNeoForge::onSpawnPlacements);
        NeoForge.EVENT_BUS.addListener(BunnylandNeoForge::onLogin);
        NeoForge.EVENT_BUS.addListener(BunnylandNeoForge::onPlayerTick);

        if (FMLEnvironment.dist == Dist.CLIENT) NeoForgeClient.init(modBus);
    }

    private static void onAttributes(EntityAttributeCreationEvent event) {
        for (Species species : Species.values()) event.put(ModEntities.get(species), ModEntities.attributes(species));
    }

    private static void onSpawnPlacements(RegisterSpawnPlacementsEvent event) {
        CreatureSpawning.register((type, placement, heightmap, predicate) ->
                event.register(type, placement, heightmap, predicate, RegisterSpawnPlacementsEvent.Operation.REPLACE));
    }

    private static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) JournalEvents.onLogin(player);
    }

    private static void onPlayerTick(PlayerTickEvent.Post event) {
        if (event.getEntity() instanceof ServerPlayer player) JournalEvents.onPlayerTick(player);
    }
}

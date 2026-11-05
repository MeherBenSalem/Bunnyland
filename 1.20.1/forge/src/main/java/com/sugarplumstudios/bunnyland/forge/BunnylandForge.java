package com.sugarplumstudios.bunnyland.forge;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.journal.JournalEvents;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.world.CreatureSpawning;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;

@Mod(Bunnyland.MOD_ID)
public final class BunnylandForge {
    public BunnylandForge() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        Bunnyland.init();
        ForgeBiomeModifiers.SERIALIZERS.register(modBus);
        ForgePlatform.registerAll(modBus);
        ForgeNetwork.register();

        modBus.addListener(BunnylandForge::onAttributes);
        modBus.addListener(BunnylandForge::onSpawnPlacements);
        MinecraftForge.EVENT_BUS.addListener(BunnylandForge::onLogin);
        MinecraftForge.EVENT_BUS.addListener(BunnylandForge::onPlayerTick);

        if (FMLEnvironment.dist == Dist.CLIENT) ForgeClient.init(modBus);
    }

    private static void onAttributes(EntityAttributeCreationEvent event) {
        for (Species species : Species.values()) event.put(ModEntities.get(species), ModEntities.attributes(species));
    }

    private static void onSpawnPlacements(SpawnPlacementRegisterEvent event) {
        CreatureSpawning.register((type, placement, heightmap, predicate) ->
                event.register(type, placement, heightmap, predicate, SpawnPlacementRegisterEvent.Operation.REPLACE));
    }

    private static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) JournalEvents.onLogin(player);
    }

    private static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase == TickEvent.Phase.END && event.player instanceof ServerPlayer player) JournalEvents.onPlayerTick(player);
    }
}

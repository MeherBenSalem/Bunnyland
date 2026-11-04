package com.sugarplumstudios.bunnyland.event;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.world.CreatureSpawning;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = Bunnyland.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ModEvents {
    private ModEvents() {
    }

    @SubscribeEvent
    public static void onAttributes(EntityAttributeCreationEvent event) {
        for (Species species : Species.values()) {
            event.put(ModEntities.get(species), ModEntities.attributes(species));
        }
    }

    @SubscribeEvent
    public static void onSpawnPlacements(SpawnPlacementRegisterEvent event) {
        CreatureSpawning.register(event);
    }
}

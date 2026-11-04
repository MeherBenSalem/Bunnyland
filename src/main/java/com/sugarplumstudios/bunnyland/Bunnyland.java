package com.sugarplumstudios.bunnyland;

import com.mojang.logging.LogUtils;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.network.ModNetwork;
import com.sugarplumstudios.bunnyland.registry.ModBiomeModifiers;
import com.sugarplumstudios.bunnyland.registry.ModBlocks;
import com.sugarplumstudios.bunnyland.registry.ModCreativeTabs;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

@Mod(Bunnyland.MOD_ID)
public class Bunnyland {
    public static final String MOD_ID = "bunnyland";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Bunnyland() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();

        ModEntities.ENTITIES.register(modBus);
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModSounds.SOUNDS.register(modBus);
        ModParticles.PARTICLES.register(modBus);
        ModCreativeTabs.TABS.register(modBus);
        ModBiomeModifiers.SERIALIZERS.register(modBus);

        ModNetwork.register();

        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, BunnylandConfig.COMMON_SPEC);
        ModLoadingContext.get().registerConfig(ModConfig.Type.CLIENT, BunnylandConfig.CLIENT_SPEC);
    }

    public static ResourceLocation id(String path) {
        return new ResourceLocation(MOD_ID, path);
    }
}

package com.sugarplumstudios.bunnyland;

import com.mojang.logging.LogUtils;
import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.registry.ModBlocks;
import com.sugarplumstudios.bunnyland.registry.ModCreativeTabs;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;

/** Shared start-up, called by each loader's entry point. */
public final class Bunnyland {
    public static final String MOD_ID = "bunnyland";
    public static final Logger LOGGER = LogUtils.getLogger();

    private Bunnyland() {
    }

    /** Loads the config and registers everything. Entity types come first: Fabric spawn eggs need them. */
    public static void init() {
        BunnylandConfig.loadCommon();
        touch(ModSounds.class, ModEntities.class, ModBlocks.class, ModItems.class, ModParticles.class, ModCreativeTabs.class);
    }

    private static void touch(Class<?>... classes) {
        for (Class<?> c : classes) {
            try {
                Class.forName(c.getName(), true, c.getClassLoader());
            } catch (ClassNotFoundException e) {
                throw new IllegalStateException(e);
            }
        }
    }

    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MOD_ID, path);
    }
}

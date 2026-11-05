package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.platform.Services;
import net.minecraft.core.registries.Registries;
import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import com.sugarplumstudios.bunnyland.platform.RegistryEntry;

public final class ModCreativeTabs {

    public static final RegistryEntry<CreativeModeTab> BUNNYLAND = Services.PLATFORM.register(Registries.CREATIVE_MODE_TAB, "bunnyland", () -> Services.PLATFORM.creativeTab()
            .title(Component.translatable("itemGroup.bunnyland"))
            .icon(() -> new ItemStack(ModItems.BUNNY_BISCUIT.get()))
            .displayItems((params, output) -> ModItems.TAB_ORDER.forEach(item -> output.accept(item.get())))
            .build());

    private ModCreativeTabs() {
    }
}

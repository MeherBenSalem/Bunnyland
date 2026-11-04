package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Bunnyland.MOD_ID);

    public static final RegistryObject<CreativeModeTab> BUNNYLAND = TABS.register("bunnyland", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.bunnyland"))
            .icon(() -> new ItemStack(ModItems.BUNNY_BISCUIT.get()))
            .displayItems((params, output) -> ModItems.TAB_ORDER.forEach(item -> output.accept(item.get())))
            .build());

    private ModCreativeTabs() {
    }
}

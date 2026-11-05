package com.sugarplumstudios.bunnyland.item;

import java.util.function.Consumer;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** An item with a one-line hint underneath its name ({@code tooltip.bunnyland.<item id>}). */
public class TooltipItem extends Item {
    public TooltipItem(Properties properties) {
        super(properties);
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, TooltipDisplay display, Consumer<Component> tooltip, TooltipFlag flag) {
        tooltip.accept(Component.translatable(getDescriptionId().replace("item.", "tooltip.")).withStyle(ChatFormatting.GRAY));
    }
}

package com.sugarplumstudios.bunnyland.client.toast;

import net.minecraft.resources.ResourceLocation;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.network.JournalToastPacket;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.toasts.Toast;
import net.minecraft.client.gui.components.toasts.ToastComponent;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** "New creature discovered!" style toast with the creature's spawn egg as its icon. */
public class JournalToast implements Toast {
    private static final long DURATION = 5000L;
    private final Component title;
    private final Component subtitle;
    private final ItemStack icon;
    private final int titleColor;

    public JournalToast(int kind, Species species, int variant) {
        String key = switch (kind) {
            case JournalToastPacket.TAMED -> "toast.bunnyland.tamed";
            case JournalToastPacket.RARE -> "toast.bunnyland.rare";
            default -> "toast.bunnyland.discovered";
        };
        this.title = Component.translatable(key);
        this.subtitle = kind == JournalToastPacket.RARE
                ? Component.empty().append(species.variantDisplayName(variant)).append(" ").append(species.displayName())
                : species.displayName();
        this.icon = new ItemStack(ModItems.SPAWN_EGGS.get(species).get());
        this.titleColor = kind == JournalToastPacket.RARE ? 0xFFD86B : kind == JournalToastPacket.TAMED ? 0xFF9EC4 : 0xC9B6F0;
    }

    @Override
    public Visibility render(GuiGraphics graphics, ToastComponent toasts, long timeSinceLastVisible) {
        graphics.blitSprite(ResourceLocation.withDefaultNamespace("toast/advancement"), 0, 0, width(), height());
        graphics.drawString(toasts.getMinecraft().font, title, 30, 7, titleColor, false);
        graphics.drawString(toasts.getMinecraft().font, subtitle, 30, 18, 0xFFFFFF, false);
        graphics.renderFakeItem(icon, 8, 8);
        return timeSinceLastVisible >= DURATION ? Visibility.HIDE : Visibility.SHOW;
    }
}

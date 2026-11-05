package com.sugarplumstudios.bunnyland.client.toast;

import net.minecraft.resources.Identifier;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.network.JournalToastPacket;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.gui.components.toasts.Toast;
import net.minecraft.client.gui.components.toasts.ToastManager;
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

    private Visibility visibility = Visibility.SHOW;

    @Override
    public Visibility getWantedVisibility() {
        return visibility;
    }

    @Override
    public void update(ToastManager manager, long fullyVisibleForMs) {
        visibility = fullyVisibleForMs >= DURATION ? Visibility.HIDE : Visibility.SHOW;
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor graphics, Font font, long fullyVisibleForMs) {
        graphics.blitSprite(RenderPipelines.GUI_TEXTURED, Identifier.withDefaultNamespace("toast/advancement"), 0, 0, width(), height());
        graphics.text(font, title, 30, 7, 0xFF000000 | titleColor, false);
        graphics.text(font, subtitle, 30, 18, 0xFFFFFFFF, false);
        graphics.fakeItem(icon, 8, 8);
    }
}

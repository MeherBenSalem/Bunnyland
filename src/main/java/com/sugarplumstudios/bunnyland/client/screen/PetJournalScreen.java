package com.sugarplumstudios.bunnyland.client.screen;

import com.mojang.blaze3d.systems.RenderSystem;
import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.client.ClientAccess;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.journal.PlayerJournal;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.joml.Quaternionf;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** The Pet Journal: an index of every creature plus one page each with a live, animated preview. */
public class PetJournalScreen extends Screen {
    private static final ResourceLocation TEXTURE = Bunnyland.id("textures/gui/pet_journal.png");
    private static final int W = 292;
    private static final int H = 184;
    private static final int TITLE = 0x7A3E6A;
    private static final int HEADER = 0xB0558A;
    private static final int BODY = 0x5E4B5E;
    private static final int MUTED = 0xA08CA0;

    private final Map<Species, BunnylandAnimal> previews = new EnumMap<>(Species.class);
    private final Map<Species, Integer> previewVariant = new EnumMap<>(Species.class);
    /** -1 = index, otherwise the species ordinal. */
    private int page = -1;
    private int left;
    private int top;
    private int ticks;
    private float dragYaw;

    public PetJournalScreen() {
        super(Component.translatable("gui.bunnyland.journal.title"));
    }

    public PetJournalScreen atPage(int page) {
        this.page = page;
        return this;
    }

    @Override
    protected void init() {
        left = (width - W) / 2;
        top = (height - H) / 2;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void tick() {
        ticks++;
        for (BunnylandAnimal e : previews.values()) e.tickCount++;
    }

    private static PlayerJournal journal() {
        return ClientAccess.journal();
    }

    private BunnylandAnimal preview(Species species) {
        BunnylandAnimal e = previews.get(species);
        if (e == null && Minecraft.getInstance().level != null) {
            Entity created = ModEntities.get(species).create(Minecraft.getInstance().level);
            if (created instanceof BunnylandAnimal animal) {
                e = animal;
                previews.put(species, e);
            }
        }
        if (e != null) e.setVariant(previewVariant.getOrDefault(species, firstSeenVariant(species)));
        return e;
    }

    private static int firstSeenVariant(Species species) {
        for (int v = 0; v < species.variantCount(); v++) {
            if (journal().hasSeenVariant(species, v)) return v;
        }
        return 0;
    }

    // ------------------------------------------------------------------ rendering

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        renderBackground(g);
        g.blit(TEXTURE, left, top, 0, 0, W, H, 512, 256);
        if (page < 0) renderIndex(g, mouseX, mouseY);
        else renderSpecies(g, Species.values()[page], mouseX, mouseY);
        renderArrows(g, mouseX, mouseY);
        super.render(g, mouseX, mouseY, partialTick);
    }

    private void renderArrows(GuiGraphics g, int mouseX, int mouseY) {
        int y = top + H - 22;
        if (page >= 0) {
            boolean hover = inside(mouseX, mouseY, left + 14, y, 18, 10);
            g.blit(TEXTURE, left + 14, y, hover ? 60 : 40, 192, 18, 10, 512, 256);
        }
        if (page < Species.values().length - 1) {
            boolean hover = inside(mouseX, mouseY, left + W - 32, y, 18, 10);
            g.blit(TEXTURE, left + W - 32, y, hover ? 20 : 0, 192, 18, 10, 512, 256);
        }
        if (page >= 0) {
            Component pageText = Component.literal((page + 1) + " / " + Species.values().length);
            g.drawString(font, pageText, left + W - 40 - font.width(pageText), y + 1, MUTED, false);
        }
    }

    private void renderIndex(GuiGraphics g, int mouseX, int mouseY) {
        PlayerJournal j = journal();
        int cx = left + 76;
        centered(g, title, cx, top + 16, TITLE);
        centered(g, Component.translatable("gui.bunnyland.journal.index"), cx, top + 28, HEADER);
        int n = Species.values().length;
        int y = top + 46;
        iconLine(g, 114, Component.translatable("gui.bunnyland.journal.discovered_count", j.discoveredCount(), n), left + 22, y);
        iconLine(g, 124, Component.translatable("gui.bunnyland.journal.tamed_count", j.tamedCount(), n), left + 22, y + 13);
        iconLine(g, 102, Component.translatable("gui.bunnyland.journal.rare_count", j.rareSeenCount(), PlayerJournal.rareTotal()),
                left + 22, y + 26);

        // A friend you've met, slowly turning at the bottom of the page.
        List<Species> met = new ArrayList<>();
        for (Species s : Species.values()) if (j.isDiscovered(s)) met.add(s);
        Species featured = met.isEmpty() ? Species.COTTON_BUNNY : met.get((ticks / 100) % met.size());
        BunnylandAnimal e = preview(featured);
        if (e != null) renderCreature(g, e, cx, top + 158, displayScale(featured) * 0.8F, ticks * 1.5F + 200, met.isEmpty());

        for (int i = 0; i < n; i++) {
            Species s = Species.values()[i];
            int ex = left + 154;
            int ey = top + 13 + i * 10;
            boolean hover = inside(mouseX, mouseY, ex - 2, ey - 1, 128, 10);
            if (hover) g.fill(ex - 2, ey - 1, ex + 126, ey + 9, 0x30F28AB0);
            int icon = j.isTamed(s) ? 124 : j.isDiscovered(s) ? 114 : 92;
            g.blit(TEXTURE, ex, ey, icon, 192, 7, 7, 512, 256);
            Component name = j.isDiscovered(s) ? s.displayName() : Component.translatable("gui.bunnyland.journal.unknown");
            g.drawString(font, name, ex + 11, ey, j.isDiscovered(s) ? BODY : MUTED, false);
        }
    }

    private void renderSpecies(GuiGraphics g, Species s, int mouseX, int mouseY) {
        PlayerJournal j = journal();
        boolean known = j.isDiscovered(s);
        int cx = left + 76;
        centered(g, known ? s.displayName() : Component.translatable("gui.bunnyland.journal.unknown"), cx, top + 14, TITLE);
        Component status = j.isTamed(s) ? Component.translatable("gui.bunnyland.journal.tamed")
                : known ? Component.translatable("gui.bunnyland.journal.not_tamed") : Component.translatable("gui.bunnyland.journal.unknown");
        int statusIcon = j.isTamed(s) ? 124 : known ? 114 : 92;
        int sw = font.width(status) + 10;
        g.blit(TEXTURE, cx - sw / 2, top + 26, statusIcon, 192, 7, 7, 512, 256);
        g.drawString(font, status, cx - sw / 2 + 10, top + 26, j.isTamed(s) ? HEADER : MUTED, false);

        BunnylandAnimal e = preview(s);
        if (e != null) renderCreature(g, e, cx, top + 112, displayScale(s), 200 + ticks * 1.2F + dragYaw, !known);

        // Variants: seen ones can be clicked to preview them.
        if (known) {
            small(g, Component.translatable("gui.bunnyland.journal.variants"), left + 16, top + 120, HEADER, 1.0F);
            for (int v = 0; v < s.variantCount(); v++) {
                int vx = left + 16 + (v % 2) * 62;
                int vy = top + 131 + (v / 2) * 9;
                boolean seen = j.hasSeenVariant(s, v);
                boolean selected = previewVariant.getOrDefault(s, firstSeenVariant(s)) == v;
                if (s.isRare(v)) g.blit(TEXTURE, vx, vy, 102, 192, 9, 7, 512, 256);
                Component vn = seen ? s.variantDisplayName(v) : Component.literal("???");
                small(g, vn, vx + (s.isRare(v) ? 10 : 2), vy + 1, selected ? TITLE : seen ? BODY : MUTED, 0.75F);
            }
        }

        // Right page
        int rx = left + 154;
        int rw = 124;
        int y = top + 12;
        if (!known) {
            y += wrap(g, Component.translatable("gui.bunnyland.journal.unknown_hint"), rx, y, rw, BODY, 0.85F) + 8;
            small(g, Component.translatable("gui.bunnyland.journal.habitat"), rx, y, HEADER, 1.0F);
            wrap(g, s.journalText("habitat"), rx, y + 11, rw, BODY, 0.75F);
            return;
        }
        y += wrap(g, s.journalText("description"), rx, y, rw, BODY, 0.75F) + 5;
        small(g, Component.translatable("gui.bunnyland.journal.habitat"), rx, y, HEADER, 1.0F);
        y += 10;
        y += wrap(g, s.journalText("habitat"), rx, y, rw, BODY, 0.75F) + 5;
        small(g, Component.translatable("gui.bunnyland.journal.taming"), rx, y, HEADER, 1.0F);
        y += 10;
        y = itemRow(g, s.tamingTreats, rx, y, mouseX, mouseY) + 2;
        small(g, Component.translatable("gui.bunnyland.journal.food"), rx, y, HEADER, 1.0F);
        y += 10;
        y = itemRow(g, s.breedingFood, rx, y, mouseX, mouseY) + 3;
        wrap(g, s.journalText("tip").copy().withStyle(st -> st.withItalic(true)), rx, y, rw, MUTED, 0.7F);
    }

    private int itemRow(GuiGraphics g, TagKey<Item> tag, int x, int y, int mouseX, int mouseY) {
        List<Item> items = new ArrayList<>();
        BuiltInRegistries.ITEM.getTag(tag).ifPresent(set -> set.forEach(h -> items.add(h.value())));
        int shown = Math.min(items.size(), 7);
        ItemStack hovered = ItemStack.EMPTY;
        for (int i = 0; i < shown; i++) {
            ItemStack stack = new ItemStack(items.get(i));
            g.renderItem(stack, x + i * 17, y);
            if (inside(mouseX, mouseY, x + i * 17, y, 16, 16)) hovered = stack;
        }
        if (!hovered.isEmpty()) g.renderTooltip(font, hovered, mouseX, mouseY);
        return y + (shown > 0 ? 17 : 0);
    }

    private void renderCreature(GuiGraphics g, BunnylandAnimal e, int x, int y, float scale, float yaw, boolean silhouette) {
        Quaternionf pose = new Quaternionf().rotateZ((float) Math.PI);
        Quaternionf tilt = new Quaternionf().rotateX(-10.0F * Mth.DEG_TO_RAD);
        pose.mul(tilt);
        float body = e.yBodyRot, bodyO = e.yBodyRotO, yRot = e.getYRot(), xRot = e.getXRot(), head = e.yHeadRot, headO = e.yHeadRotO;
        e.yBodyRot = yaw;
        e.yBodyRotO = yaw;
        e.setYRot(yaw);
        e.setXRot(0);
        e.yHeadRot = yaw;
        e.yHeadRotO = yaw;
        if (silhouette) RenderSystem.setShaderColor(0.32F, 0.25F, 0.38F, 1.0F);
        InventoryScreen.renderEntityInInventory(g, x, y, Math.round(scale), pose, tilt, e);
        RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
        e.yBodyRot = body;
        e.yBodyRotO = bodyO;
        e.setYRot(yRot);
        e.setXRot(xRot);
        e.yHeadRot = head;
        e.yHeadRotO = headO;
    }

    private static float displayScale(Species s) {
        return switch (s) {
            case STRAWBERRY_MOUSE -> 72;
            case DREAMY_HAMSTER -> 60;
            case HONEY_BEAR -> 38;
            case MOON_DEER -> 26;
            case RAINBOW_BUTTERFLY -> 62;
            case CHERRY_BLOSSOM_BIRD -> 70;
            case PASTEL_AXOLOTL -> 52;
            case TINY_SWAN -> 42;
            case BLOSSOM_FOX, CLOUD_KITTY -> 44;
            default -> 50;
        };
    }

    // ------------------------------------------------------------------ text helpers

    private void centered(GuiGraphics g, Component text, int cx, int y, int color) {
        g.drawString(font, text, cx - font.width(text) / 2, y, color, false);
    }

    private void iconLine(GuiGraphics g, int iconU, Component text, int x, int y) {
        g.blit(TEXTURE, x, y, iconU, 192, iconU == 102 ? 9 : 7, 7, 512, 256);
        g.drawString(font, text, x + 12, y, BODY, false);
    }

    private void small(GuiGraphics g, Component text, int x, int y, int color, float scale) {
        g.pose().pushPose();
        g.pose().translate(x, y, 0);
        g.pose().scale(scale, scale, 1.0F);
        g.drawString(font, text, 0, 0, color, false);
        g.pose().popPose();
    }

    /** Draws wrapped text at a scale and returns the height it used. */
    private int wrap(GuiGraphics g, Component text, int x, int y, int width, int color, float scale) {
        List<FormattedCharSequence> lines = font.split(text, (int) (width / scale));
        g.pose().pushPose();
        g.pose().translate(x, y, 0);
        g.pose().scale(scale, scale, 1.0F);
        for (int i = 0; i < lines.size(); i++) g.drawString(font, lines.get(i), 0, i * 9, color, false);
        g.pose().popPose();
        return Math.round(lines.size() * 9 * scale);
    }

    private static boolean inside(double mx, double my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }

    // ------------------------------------------------------------------ input

    private void turn(int delta) {
        int next = Mth.clamp(page + delta, -1, Species.values().length - 1);
        if (next != page) {
            page = next;
            dragYaw = 0;
            Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0F));
        }
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        int ay = top + H - 22;
        if (page >= 0 && inside(mx, my, left + 14, ay, 18, 10)) {
            turn(-1);
            return true;
        }
        if (page < Species.values().length - 1 && inside(mx, my, left + W - 32, ay, 18, 10)) {
            turn(1);
            return true;
        }
        if (page < 0) {
            for (int i = 0; i < Species.values().length; i++) {
                if (inside(mx, my, left + 152, top + 12 + i * 10, 128, 10)) {
                    turn(i + 1);
                    return true;
                }
            }
        } else {
            Species s = Species.values()[page];
            if (inside(mx, my, left + 8, top + 10, 136, 12)) {
                page = 0;
                turn(-1);
                return true;
            }
            if (journal().isDiscovered(s)) {
                for (int v = 0; v < s.variantCount(); v++) {
                    int vx = left + 16 + (v % 2) * 62;
                    int vy = top + 131 + (v / 2) * 9;
                    if (journal().hasSeenVariant(s, v) && inside(mx, my, vx, vy, 60, 9)) {
                        previewVariant.put(s, v);
                        Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1.4F));
                        return true;
                    }
                }
            }
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean mouseDragged(double mx, double my, int button, double dx, double dy) {
        if (page >= 0 && inside(mx, my, left + 8, top + 36, 136, 84)) {
            dragYaw -= (float) dx * 2.0F;
            return true;
        }
        return super.mouseDragged(mx, my, button, dx, dy);
    }

    @Override
    public boolean keyPressed(int key, int scan, int modifiers) {
        if (key == GLFW.GLFW_KEY_LEFT || key == GLFW.GLFW_KEY_PAGE_UP) {
            turn(-1);
            return true;
        }
        if (key == GLFW.GLFW_KEY_RIGHT || key == GLFW.GLFW_KEY_PAGE_DOWN) {
            turn(1);
            return true;
        }
        return super.keyPressed(key, scan, modifiers);
    }
}

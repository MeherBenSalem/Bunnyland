package com.sugarplumstudios.bunnyland.client.screen;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.client.ClientAccess;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.journal.PlayerJournal;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import com.mojang.blaze3d.platform.InputConstants;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** The Pet Journal: an index of every creature plus one page each with a live, animated preview. */
public class PetJournalScreen extends Screen {
    private static final Identifier TEXTURE = Bunnyland.id("textures/gui/pet_journal.png");
    private static final int W = 292;
    private static final int H = 184;
    private static final int TITLE = 0xFF7A3E6A;
    private static final int HEADER = 0xFFB0558A;
    private static final int BODY = 0xFF5E4B5E;
    private static final int MUTED = 0xFFA08CA0;

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
            Entity created = ModEntities.get(species).create(Minecraft.getInstance().level, EntitySpawnReason.LOAD);
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
    public void extractRenderState(GuiGraphicsExtractor g, int mouseX, int mouseY, float partialTick) {
        g.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, left, top, 0, 0, W, H, 512, 256);
        if (page < 0) renderIndex(g, mouseX, mouseY);
        else renderSpecies(g, Species.values()[page], mouseX, mouseY);
        renderArrows(g, mouseX, mouseY);
        super.extractRenderState(g, mouseX, mouseY, partialTick);
    }

    private void renderArrows(GuiGraphicsExtractor g, int mouseX, int mouseY) {
        int y = top + H - 22;
        if (page >= 0) {
            boolean hover = inside(mouseX, mouseY, left + 14, y, 18, 10);
            g.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, left + 14, y, hover ? 60 : 40, 192, 18, 10, 512, 256);
        }
        if (page < Species.values().length - 1) {
            boolean hover = inside(mouseX, mouseY, left + W - 32, y, 18, 10);
            g.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, left + W - 32, y, hover ? 20 : 0, 192, 18, 10, 512, 256);
        }
        if (page >= 0) {
            Component pageText = Component.literal((page + 1) + " / " + Species.values().length);
            g.text(font, pageText, left + W - 40 - font.width(pageText), y + 1, MUTED, false);
        }
    }

    private void renderIndex(GuiGraphicsExtractor g, int mouseX, int mouseY) {
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
            g.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, ex, ey, icon, 192, 7, 7, 512, 256);
            Component name = j.isDiscovered(s) ? s.displayName() : Component.translatable("gui.bunnyland.journal.unknown");
            g.text(font, name, ex + 11, ey, j.isDiscovered(s) ? BODY : MUTED, false);
        }
    }

    private void renderSpecies(GuiGraphicsExtractor g, Species s, int mouseX, int mouseY) {
        PlayerJournal j = journal();
        boolean known = j.isDiscovered(s);
        int cx = left + 76;
        centered(g, known ? s.displayName() : Component.translatable("gui.bunnyland.journal.unknown"), cx, top + 14, TITLE);
        Component status = j.isTamed(s) ? Component.translatable("gui.bunnyland.journal.tamed")
                : known ? Component.translatable("gui.bunnyland.journal.not_tamed") : Component.translatable("gui.bunnyland.journal.unknown");
        int statusIcon = j.isTamed(s) ? 124 : known ? 114 : 92;
        int sw = font.width(status) + 10;
        g.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, cx - sw / 2, top + 26, statusIcon, 192, 7, 7, 512, 256);
        g.text(font, status, cx - sw / 2 + 10, top + 26, j.isTamed(s) ? HEADER : MUTED, false);

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
                if (s.isRare(v)) g.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, vx, vy, 102, 192, 9, 7, 512, 256);
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

    private int itemRow(GuiGraphicsExtractor g, TagKey<Item> tag, int x, int y, int mouseX, int mouseY) {
        List<Item> items = new ArrayList<>();
        for (Holder<Item> h : BuiltInRegistries.ITEM.getTagOrEmpty(tag)) items.add(h.value());
        int shown = Math.min(items.size(), 7);
        ItemStack hovered = ItemStack.EMPTY;
        for (int i = 0; i < shown; i++) {
            ItemStack stack = new ItemStack(items.get(i));
            g.item(stack, x + i * 17, y);
            if (inside(mouseX, mouseY, x + i * 17, y, 16, 16)) hovered = stack;
        }
        if (!hovered.isEmpty()) g.setTooltipForNextFrame(font, hovered, mouseX, mouseY);
        return y + (shown > 0 ? 17 : 0);
    }

    private void renderCreature(GuiGraphicsExtractor g, BunnylandAnimal e, int x, int y, float scale, float yaw, boolean silhouette) {
        Quaternionf pose = new Quaternionf().rotateZ((float) Math.PI);
        Quaternionf tilt = new Quaternionf().rotateX(-10.0F * Mth.DEG_TO_RAD);
        pose.mul(tilt);
        e.journalSilhouette = silhouette;
        EntityRenderState state = Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(e).createRenderState(e, 1.0F);
        e.journalSilhouette = false;
        state.shadowPieces.clear();
        state.outlineColor = 0;
        if (state instanceof LivingEntityRenderState living) {
            living.bodyRot = yaw;
            living.yRot = 0;
            living.xRot = 0;
            living.boundingBoxWidth /= living.scale;
            living.boundingBoxHeight /= living.scale;
            living.scale = 1.0F;
        }
        // The creature stands on (x, y): centre a box on its middle.
        int cy = Math.round(y - state.boundingBoxHeight * scale / 2.0F);
        g.entity(state, scale, new Vector3f(0.0F, state.boundingBoxHeight / 2.0F, 0.0F), pose, tilt, x - 70, cy - 70, x + 70, cy + 70);
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

    private void centered(GuiGraphicsExtractor g, Component text, int cx, int y, int color) {
        g.text(font, text, cx - font.width(text) / 2, y, color, false);
    }

    private void iconLine(GuiGraphicsExtractor g, int iconU, Component text, int x, int y) {
        g.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, x, y, iconU, 192, iconU == 102 ? 9 : 7, 7, 512, 256);
        g.text(font, text, x + 12, y, BODY, false);
    }

    private void small(GuiGraphicsExtractor g, Component text, int x, int y, int color, float scale) {
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(scale, scale);
        g.text(font, text, 0, 0, color, false);
        g.pose().popMatrix();
    }

    /** Draws wrapped text at a scale and returns the height it used. */
    private int wrap(GuiGraphicsExtractor g, Component text, int x, int y, int width, int color, float scale) {
        List<FormattedCharSequence> lines = font.split(text, (int) (width / scale));
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(scale, scale);
        for (int i = 0; i < lines.size(); i++) g.text(font, lines.get(i), 0, i * 9, color, false);
        g.pose().popMatrix();
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
    public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
        double mx = event.x();
        double my = event.y();
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
        return super.mouseClicked(event, doubleClick);
    }

    @Override
    public boolean mouseDragged(MouseButtonEvent event, double dx, double dy) {
        if (page >= 0 && inside(event.x(), event.y(), left + 8, top + 36, 136, 84)) {
            dragYaw -= (float) dx * 2.0F;
            return true;
        }
        return super.mouseDragged(event, dx, dy);
    }

    @Override
    public boolean keyPressed(KeyEvent event) {
        int key = event.key();
        if (key == InputConstants.KEY_LEFT || key == InputConstants.KEY_PAGEUP) {
            turn(-1);
            return true;
        }
        if (key == InputConstants.KEY_RIGHT || key == InputConstants.KEY_PAGEDOWN) {
            turn(1);
            return true;
        }
        return super.keyPressed(event);
    }
}

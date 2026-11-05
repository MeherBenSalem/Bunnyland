package com.sugarplumstudios.bunnyland.client.dev;

import com.mojang.logging.LogUtils;
import com.sugarplumstudios.bunnyland.client.screen.PetJournalScreen;
import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.tutorial.TutorialSteps;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import org.slf4j.Logger;

import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;

/**
 * Developer tool for visual checks. Only active when the game is started with
 * {@code -Dbunnyland.devshots=true} (the {@code snapshots} run in build.gradle): it builds a superflat showcase
 * world with every creature, variant highlights, accessories, sleeping poses, beds and bowls, saves
 * screenshots to {@code run/screenshots/bunnyland_*.png} and quits. It does nothing in normal play.
 */
public final class DevSnapshots {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final int Y = -60;

    private record Step(int delay, BooleanSupplier ready, Runnable action) {
    }

    private static final List<Step> steps = new ArrayList<>();
    private static int index;
    private static int wait;

    private DevSnapshots() {
    }

    public static boolean enabled() {
        return Boolean.getBoolean("bunnyland.devshots");
    }

    private static Minecraft mc() {
        return Minecraft.getInstance();
    }

    private static void step(int delay, Runnable action) {
        steps.add(new Step(delay, () -> true, action));
    }

    private static void waitFor(BooleanSupplier ready, Runnable action) {
        steps.add(new Step(20, ready, action));
    }

    private static void command(String cmd) {
        if (mc().player != null) mc().player.connection.sendCommand(cmd);
    }

    private static void quiet() {
        // Losing window focus opens the pause menu (and pauses the world); never photograph that.
        if (mc().screen instanceof PauseScreen) mc().setScreen(null);
        mc().gui.getChat().clearMessages(false);
        mc().getTutorial().setStep(TutorialSteps.NONE);
        mc().getToasts().clear();
    }

    private static void shot(String name) {
        step(25, DevSnapshots::quiet);
        step(15, () -> Screenshot.grab(mc().gameDirectory, "bunnyland_" + name + ".png", mc().getMainRenderTarget(),
                msg -> LOGGER.info("[devshots] {}", msg.getString())));
    }

    /** Points the camera from (x, y, z) with the given yaw/pitch. */
    private static void camera(double x, double y, double z, float yaw, float pitch) {
        step(2, () -> command(String.format(java.util.Locale.ROOT, "tp @s %.2f %.2f %.2f %.1f %.1f", x, y, z, yaw, pitch)));
    }

    private static String id(Species s) {
        return "bunnyland:" + s.id;
    }

    private static void summon(Species s, double x, double z, String extraNbt) {
        String nbt = "{NoAI:1b,PersistenceRequired:1b,Rotation:[0f,0f]" + (extraNbt.isEmpty() ? "" : "," + extraNbt) + "}";
        command(String.format(java.util.Locale.ROOT, "summon %s %.2f %d %.2f %s", id(s), x, Y, z, nbt));
    }

    private static double viewDistance(Species s) {
        return switch (s) {
            case MOON_DEER -> 3.6;
            case HONEY_BEAR -> 2.8;
            case RAINBOW_BUTTERFLY -> 2.1;
            case STRAWBERRY_MOUSE, CHERRY_BLOSSOM_BIRD -> 1.5;
            case DREAMY_HAMSTER, PASTEL_AXOLOTL -> 1.8;
            default -> 2.2;
        };
    }

    private static double viewHeight(Species s) {
        return switch (s) {
            case MOON_DEER -> 1.5;
            case HONEY_BEAR, TINY_SWAN -> 0.9;
            case STRAWBERRY_MOUSE, RAINBOW_BUTTERFLY, CHERRY_BLOSSOM_BIRD, DREAMY_HAMSTER, PASTEL_AXOLOTL -> 0.45;
            default -> 0.7;
        };
    }

    private static float viewPitch(Species s) {
        return switch (s) {
            case STRAWBERRY_MOUSE, DREAMY_HAMSTER, CHERRY_BLOSSOM_BIRD, RAINBOW_BUTTERFLY, PASTEL_AXOLOTL -> 24;
            default -> 12;
        };
    }

    static {
        Species[] all = Species.values();
        waitFor(() -> mc().getOverlay() == null && mc().screen instanceof TitleScreen && mc().level == null, () -> {
            mc().options.onboardAccessibility = false;
            mc().options.pauseOnLostFocus = false;
            mc().getWindow().setWindowed(1280, 720);
        });
        step(20, () -> {
            LevelSettings settings = new LevelSettings("Bunnyland Snapshots", GameType.CREATIVE, false, Difficulty.PEACEFUL, true,
                    new GameRules(), WorldDataConfiguration.DEFAULT);
            mc().createWorldOpenFlows().createFreshLevel("bunnyland_snapshots_" + System.currentTimeMillis(), settings,
                    new WorldOptions(20261103L, false, false),
                    ra -> ra.registryOrThrow(Registries.WORLD_PRESET).getHolderOrThrow(WorldPresets.FLAT).value().createWorldDimensions());
        });
        waitFor(() -> mc().level != null && mc().player != null && mc().screen == null, () -> {
            command("gamerule doMobSpawning false");
            command("gamerule doDaylightCycle false");
            command("gamerule doWeatherCycle false");
            command("gamerule sendCommandFeedback false");
            command("time set 6000");
            command("weather clear");
            mc().player.getAbilities().flying = true;
            mc().player.onUpdateAbilities();
            mc().options.fov().set(60);
        });

        // Row 1: bunnies (z=0); row 2: mammals (z=-14); row 3: the rest (z=-28)
        step(40, () -> {
            for (int i = 0; i < all.length; i++) {
                double x = -6 + (i % 5) * 3;
                double z = -(i / 5) * 14;
                summon(all[i], x + 0.5, z + 0.5, "");
            }
        });
        step(5, () -> mc().options.hideGui = true);
        String[] rows = {"bunnies", "mammals", "others"};
        for (int r = 0; r < 3; r++) {
            camera(0.5, Y + 2.2, -r * 14 + 7.5, 180, 14);
            shot("row_" + rows[r]);
        }
        // Close-ups of every creature, front and three-quarter views
        for (int i = 0; i < all.length; i++) {
            Species s = all[i];
            double x = -6 + (i % 5) * 3 + 0.5;
            double z = -(i / 5) * 14 + 0.5;
            double d = viewDistance(s);
            camera(x, Y + viewHeight(s), z + d, 180, viewPitch(s));
            shot("closeup_" + s.id);
            camera(x + d * 0.75, Y + viewHeight(s) + 0.3, z + d * 0.75, 135, viewPitch(s) + 6);
            shot("angle_" + s.id);
        }
        // Side views (to check silhouettes and tails)
        for (int i = 0; i < all.length; i += 1) {
            Species s = all[i];
            double x = -6 + (i % 5) * 3 + 0.5;
            double z = -(i / 5) * 14 + 0.5;
            camera(x + viewDistance(s) * 1.3, Y + viewHeight(s), z, 90, viewPitch(s));
            shot("side_" + s.id);
        }

        // Variant line-ups, one row per species (z = -50 - 4*i)
        step(10, () -> {
            for (int i = 0; i < all.length; i++) {
                Species s = all[i];
                for (int v = 0; v < s.variantCount(); v++) {
                    summon(s, -6 + v * 2 + 0.5, -50 - i * 5 + 0.5, "Variant:" + v);
                }
            }
        });
        for (int i = 0; i < all.length; i++) {
            Species s = all[i];
            double far = s == Species.MOON_DEER ? 6.5 : s == Species.HONEY_BEAR ? 5.5 : 4.6;
            camera(-6 + (s.variantCount() - 1) + 0.5, Y + 1.6, -50 - i * 5 + 0.5 + far, 180, 16);
            shot("variants_" + s.id);
        }

        // Dress-up: one cotton bunny per accessory plus collar/bow, then other species in outfits
        step(10, () -> {
            String[] outfits = {"CollarColor:5614010,BowColor:16766566", "Accessory:\"flower_crown\"", "Accessory:\"tiny_top_hat\"",
                    "Accessory:\"party_hat\"", "Accessory:\"star_clip\",BowColor:12100095", "Accessory:\"heart_glasses\"",
                    "Accessory:\"cozy_scarf\",CollarColor:16743342"};
            for (int k = 0; k < outfits.length; k++) summon(Species.COTTON_BUNNY, -6 + k * 2 + 0.5, -130.5, outfits[k]);
            Species[] models = {Species.BLOSSOM_FOX, Species.CLOUD_KITTY, Species.HONEY_BEAR, Species.MOON_DEER, Species.TINY_SWAN,
                    Species.DREAMY_HAMSTER, Species.RAINBOW_BUTTERFLY, Species.CHERRY_BLOSSOM_BIRD, Species.STRAWBERRY_MOUSE,
                    Species.PASTEL_AXOLOTL};
            String[] looks = {"Accessory:\"flower_crown\",CollarColor:16748491", "Accessory:\"tiny_top_hat\",BowColor:16766566",
                    "Accessory:\"party_hat\",CollarColor:6737151", "Accessory:\"cozy_scarf\"", "Accessory:\"heart_glasses\",BowColor:16743342",
                    "Accessory:\"party_hat\",CollarColor:12100095", "Accessory:\"flower_crown\"", "Accessory:\"tiny_top_hat\"",
                    "Accessory:\"star_clip\",CollarColor:16748491", "Accessory:\"flower_crown\",BowColor:12100095"};
            for (int k = 0; k < models.length; k++) summon(models[k], -9 + k * 2 + 0.5, -140.5, looks[k]);
        });
        camera(0.5, Y + 1.5, -126.0, 180, 14);
        shot("outfits_bunnies");
        camera(-0.5, Y + 2.0, -134.8, 180, 14);
        shot("outfits_mixed");
        camera(-6.5 + 0.0, Y + 0.75, -128.6, 180, 14);
        shot("outfit_closeup_collar_bow");
        camera(-2.5, Y + 0.75, -128.6, 180, 14);
        shot("outfit_closeup_tophat");

        // Sleeping and sitting poses
        step(10, () -> {
            Species[] sleepers = {Species.COTTON_BUNNY, Species.LAVENDER_BUNNY, Species.BLOSSOM_FOX, Species.CLOUD_KITTY,
                    Species.HONEY_BEAR, Species.MOON_DEER, Species.TINY_SWAN, Species.DREAMY_HAMSTER, Species.CHERRY_BLOSSOM_BIRD,
                    Species.RAINBOW_BUTTERFLY};
            for (int k = 0; k < sleepers.length; k++) summon(sleepers[k], -9 + k * 2 + 0.5, -150.5, "Napping:1b");
            for (int k = 0; k < sleepers.length; k++) summon(sleepers[k], -9 + k * 2 + 0.5, -158.5, "Sitting:1b,InSittingPose:1b");
        });
        camera(-0.5, Y + 2.0, -145.0, 180, 16);
        shot("sleeping");
        camera(-0.5, Y + 2.0, -153.0, 180, 16);
        shot("sitting");

        // Care blocks: beds with napping pets and bowls at each fill level
        step(10, () -> {
            String[] beds = {"pink", "lavender", "mint", "sky"};
            for (int k = 0; k < beds.length; k++) {
                command("setblock " + (-4 + k * 2) + " " + Y + " -168 bunnyland:" + beds[k] + "_pet_bed");
            }
            summon(Species.COTTON_BUNNY, -3.5, -167.5, "Napping:1b");
            summon(Species.CLOUD_KITTY, 0.5, -167.5, "Napping:1b");
            int[] food = {0, 2, 5, 8};
            for (int k = 0; k < food.length; k++) {
                command("setblock " + (-4 + k * 2) + " " + Y + " -171 bunnyland:feeding_bowl[food=" + food[k] + "]");
            }
        });
        camera(-1.0, Y + 2.2, -162.5, 180, 30);
        shot("beds_and_bowls");

        // A flying butterfly and bird (no gravity) and a swimming axolotl
        step(10, () -> {
            command("fill -4 " + (Y - 1) + " -183 4 " + (Y - 1) + " -179 minecraft:water");
            summon(Species.PASTEL_AXOLOTL, -2.5, -180.5, "Variant:1");
            summon(Species.TINY_SWAN, 1.5, -180.5, "");
            command(String.format(java.util.Locale.ROOT, "summon bunnyland:rainbow_butterfly -1.5 %d -176.5 {NoAI:1b,NoGravity:1b,Rotation:[0f,0f]}", Y + 1));
            command(String.format(java.util.Locale.ROOT, "summon bunnyland:cherry_blossom_bird 1.5 %d -176.5 {NoAI:1b,NoGravity:1b,Rotation:[0f,0f]}", Y + 1));
        });
        camera(0.0, Y + 1.8, -172.0, 180, 12);
        shot("flying_and_swimming");

        // Night: glowing moon creatures and rare variants
        step(10, () -> {
            command("time set 18000");
            summon(Species.MOON_BUNNY, -3.5, -190.5, "Variant:4");
            summon(Species.MOON_DEER, -0.5, -190.5, "");
            summon(Species.MOON_BUNNY, 2.5, -190.5, "");
            summon(Species.PASTEL_AXOLOTL, -5.5, -190.5, "Variant:5");
            summon(Species.RAINBOW_BUTTERFLY, 4.5, -190.5, "Variant:5");
        });
        camera(-0.5, Y + 1.8, -185.0, 180, 10);
        shot("night_glow");
        step(5, () -> command("time set 6000"));

        // The Pet Journal (creatures nearby get discovered while we fly past them)
        step(5, () -> {
            mc().options.hideGui = false;
            command("tp @s 0.5 " + (Y + 2) + " 4.5");
        });
        step(60, () -> command("tp @s 0.5 " + (Y + 2) + " -9.5"));
        step(60, () -> command("tp @s 0.5 " + (Y + 2) + " -23.5"));
        step(60, () -> command("tp @s 0.5 " + (Y + 2) + " -60"));
        step(60, () -> mc().setScreen(new PetJournalScreen()));
        shot("journal_index");
        step(5, () -> mc().setScreen(new PetJournalScreen().atPage(0)));
        shot("journal_cotton_bunny");
        step(5, () -> mc().setScreen(new PetJournalScreen().atPage(Species.MOON_DEER.ordinal())));
        shot("journal_moon_deer");
        step(5, () -> mc().setScreen(new PetJournalScreen().atPage(Species.RAINBOW_BUTTERFLY.ordinal())));
        shot("journal_butterfly");
        step(5, () -> {
            mc().setScreen(null);
            LOGGER.info("[devshots] finished, quitting");
            mc().stop();
        });
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END || index >= steps.size()) return;
        Step s = steps.get(index);
        if (!s.ready().getAsBoolean()) return;
        if (wait++ < s.delay()) return;
        wait = 0;
        index++;
        try {
            s.action().run();
        } catch (RuntimeException e) {
            LOGGER.error("[devshots] step {} failed", index - 1, e);
        }
    }
}

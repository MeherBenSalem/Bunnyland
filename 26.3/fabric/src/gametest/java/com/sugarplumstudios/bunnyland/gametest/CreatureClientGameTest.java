package com.sugarplumstudios.bunnyland.gametest;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;

/**
 * Spawns the Rainbow Butterfly in front of the player on a flower patch, lets it fly, rest and visit flowers, then
 * does the same with every other creature. The test fails if the game crashes or a creature can't be rendered.
 */
public class CreatureClientGameTest implements FabricClientGameTest {
    private static final String[] CREATURES = {
            "cotton_bunny", "strawberry_bunny", "moon_bunny", "lavender_bunny", "snowball_bunny", "blossom_fox",
            "cloud_kitty", "strawberry_mouse", "honey_bear", "moon_deer", "pastel_axolotl", "tiny_swan",
            "cherry_blossom_bird", "dreamy_hamster"
    };

    @Override
    public void runTest(ClientGameTestContext context) {
        try (var world = context.worldBuilder().create()) {
            var server = world.getServer();
            context.waitTicks(40);
            step("world ready");
            server.runCommand("time set noon");
            server.runCommand("execute as @a at @s run fill ~-6 ~-1 ~-6 ~6 ~-1 ~6 minecraft:grass_block");
            server.runCommand("execute as @a at @s run fill ~-6 ~ ~-6 ~6 ~3 ~6 minecraft:air");
            server.runCommand("execute as @a at @s run fill ~-6 ~ ~2 ~6 ~ ~6 minecraft:poppy");
            server.runCommand("execute as @a at @s run tp @s ~ ~ ~ 0 20");
            context.waitTicks(20);

            step("summon rainbow_butterfly");
            for (int i = 0; i < 6; i++) {
                server.runCommand("execute as @a at @s run summon bunnyland:rainbow_butterfly ~" + (i - 3) + " ~1 ~4");
            }
            server.runCommand("execute as @a at @s run summon bunnyland:rainbow_butterfly ~ ~1 ~3 {Age:-24000}");
            context.waitTicks(100);
            context.takeScreenshot("rainbow_butterfly");
            step("rainbow_butterfly rendered");
            context.waitTicks(500);
            context.takeScreenshot("rainbow_butterfly_later");
            step("rainbow_butterfly survived 30 s");

            for (String creature : CREATURES) {
                server.runCommand("execute as @a at @s run summon bunnyland:" + creature + " ~ ~ ~4");
                context.waitTicks(20);
                step(creature + " rendered");
            }
            context.waitTicks(200);
            context.takeScreenshot("all_creatures");
            step("all creatures survived");
        }
    }

    private static void step(String what) {
        System.out.println("[bunnyland-gametest] " + what);
    }
}

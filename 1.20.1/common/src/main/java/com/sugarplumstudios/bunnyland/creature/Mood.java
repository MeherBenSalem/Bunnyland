package com.sugarplumstudios.bunnyland.creature;

import net.minecraft.network.chat.Component;

/** How a pet feels, derived from its happiness (0-100). */
public enum Mood {
    SAD("sad", 0),
    CONTENT("content", 25),
    HAPPY("happy", 60),
    OVERJOYED("overjoyed", 85);

    public final String id;
    public final int threshold;

    Mood(String id, int threshold) {
        this.id = id;
        this.threshold = threshold;
    }

    public Component displayName() {
        return Component.translatable("mood.bunnyland." + id);
    }

    public static Mood of(int happiness) {
        Mood result = SAD;
        for (Mood m : values()) {
            if (happiness >= m.threshold) result = m;
        }
        return result;
    }
}

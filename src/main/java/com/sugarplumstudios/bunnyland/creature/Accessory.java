package com.sugarplumstudios.bunnyland.creature;

import com.sugarplumstudios.bunnyland.registry.ModItems;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Supplier;

/** Cosmetic accessories a pet can wear (one at a time, besides its collar and bow). */
public enum Accessory {
    NONE("none", null, false),
    FLOWER_CROWN("flower_crown", () -> ModItems.FLOWER_CROWN, true),
    TINY_TOP_HAT("tiny_top_hat", () -> ModItems.TINY_TOP_HAT, true),
    PARTY_HAT("party_hat", () -> ModItems.PARTY_HAT, true),
    STAR_CLIP("star_clip", () -> ModItems.STAR_CLIP, false),
    HEART_GLASSES("heart_glasses", () -> ModItems.HEART_GLASSES, false),
    COZY_SCARF("cozy_scarf", () -> ModItems.COZY_SCARF, false);

    public final String id;
    /** The model bone that shows this accessory. */
    public final String bone;
    /** Hats replace a creature's own headwear (the Dreamy Hamster's nightcap). */
    public final boolean isHat;
    private final Supplier<RegistryObject<Item>> item;

    Accessory(String id, Supplier<RegistryObject<Item>> item, boolean isHat) {
        this.id = id;
        this.bone = "acc_" + (id.equals("tiny_top_hat") ? "top_hat" : id);
        this.item = item;
        this.isHat = isHat;
    }

    public Item item() {
        return item == null ? null : item.get().get();
    }

    public Component displayName() {
        return Component.translatable("accessory.bunnyland." + id);
    }

    public static Accessory byId(String id) {
        for (Accessory a : values()) {
            if (a.id.equals(id)) return a;
        }
        return NONE;
    }

    public static Accessory byOrdinal(int ordinal) {
        Accessory[] all = values();
        return ordinal >= 0 && ordinal < all.length ? all[ordinal] : NONE;
    }
}

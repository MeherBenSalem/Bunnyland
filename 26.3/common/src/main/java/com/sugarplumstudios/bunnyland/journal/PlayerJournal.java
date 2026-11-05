package com.sugarplumstudios.bunnyland.journal;

import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;

/** One player's Pet Journal: which creatures they discovered and befriended, and which variants they've seen. */
public class PlayerJournal {
    public static final int NEW_SPECIES = 1;
    public static final int NEW_VARIANT = 2;
    public static final int NEW_RARE = 4;
    public static final int NEW_TAMED = 8;

    private int discovered;
    private int tamed;
    private final int[] variants = new int[Species.values().length];
    private boolean starterGiven;

    public boolean isDiscovered(Species species) {
        return (discovered & (1 << species.ordinal())) != 0;
    }

    public boolean isTamed(Species species) {
        return (tamed & (1 << species.ordinal())) != 0;
    }

    public boolean hasSeenVariant(Species species, int variant) {
        return (variants[species.ordinal()] & (1 << variant)) != 0;
    }

    /** Records a sighting. Returns a mask of NEW_* flags describing what was new. */
    public int see(Species species, int variant) {
        int changes = 0;
        int bit = 1 << species.ordinal();
        if ((discovered & bit) == 0) {
            discovered |= bit;
            changes |= NEW_SPECIES;
        }
        variant = species.clampVariant(variant);
        if (!hasSeenVariant(species, variant)) {
            variants[species.ordinal()] |= 1 << variant;
            changes |= NEW_VARIANT;
            if (species.isRare(variant)) changes |= NEW_RARE;
        }
        return changes;
    }

    public int tame(Species species, int variant) {
        int changes = see(species, variant);
        int bit = 1 << species.ordinal();
        if ((tamed & bit) == 0) {
            tamed |= bit;
            changes |= NEW_TAMED;
        }
        return changes;
    }

    public boolean starterGiven() {
        return starterGiven;
    }

    public void setStarterGiven() {
        starterGiven = true;
    }

    public int discoveredCount() {
        return Integer.bitCount(discovered);
    }

    public int tamedCount() {
        return Integer.bitCount(tamed);
    }

    public int rareSeenCount() {
        int n = 0;
        for (Species s : Species.values()) {
            for (int v = s.common.size(); v < s.variantCount(); v++) {
                if (hasSeenVariant(s, v)) n++;
            }
        }
        return n;
    }

    public static int rareTotal() {
        int n = 0;
        for (Species s : Species.values()) n += s.rare.size();
        return n;
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putInt("Discovered", discovered);
        tag.putInt("Tamed", tamed);
        tag.putIntArray("Variants", variants);
        tag.putBoolean("StarterGiven", starterGiven);
        return tag;
    }

    public static PlayerJournal load(CompoundTag tag) {
        PlayerJournal j = new PlayerJournal();
        j.discovered = tag.getIntOr("Discovered", 0);
        j.tamed = tag.getIntOr("Tamed", 0);
        int[] v = tag.getIntArray("Variants").orElse(new int[0]);
        System.arraycopy(v, 0, j.variants, 0, Math.min(v.length, j.variants.length));
        j.starterGiven = tag.getBooleanOr("StarterGiven", false);
        return j;
    }

    public void write(FriendlyByteBuf buf) {
        buf.writeVarInt(discovered);
        buf.writeVarInt(tamed);
        buf.writeVarIntArray(variants);
    }

    public static PlayerJournal read(FriendlyByteBuf buf) {
        PlayerJournal j = new PlayerJournal();
        j.discovered = buf.readVarInt();
        j.tamed = buf.readVarInt();
        int[] v = buf.readVarIntArray(64);
        System.arraycopy(v, 0, j.variants, 0, Math.min(v.length, j.variants.length));
        return j;
    }
}

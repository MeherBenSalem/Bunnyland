package com.sugarplumstudios.bunnyland.journal;

import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Every player's Pet Journal, saved with the world (so it survives deaths and dimension changes). */
public class JournalData extends SavedData {
    private static final String NAME = "bunnyland_journal";
    private final Map<UUID, PlayerJournal> journals = new HashMap<>();

    public static JournalData get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(JournalData::new, JournalData::load, null), NAME);
    }

    public PlayerJournal of(UUID player) {
        return journals.computeIfAbsent(player, id -> new PlayerJournal());
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {
        ListTag list = new ListTag();
        journals.forEach((id, journal) -> {
            CompoundTag entry = journal.save();
            entry.putUUID("Player", id);
            list.add(entry);
        });
        tag.put("Journals", list);
        return tag;
    }

    public static JournalData load(CompoundTag tag, HolderLookup.Provider registries) {
        JournalData data = new JournalData();
        ListTag list = tag.getList("Journals", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag entry = list.getCompound(i);
            if (entry.hasUUID("Player")) data.journals.put(entry.getUUID("Player"), PlayerJournal.load(entry));
        }
        return data;
    }
}

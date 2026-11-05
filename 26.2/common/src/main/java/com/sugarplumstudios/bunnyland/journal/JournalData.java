package com.sugarplumstudios.bunnyland.journal;

import com.sugarplumstudios.bunnyland.Bunnyland;
import net.minecraft.core.UUIDUtil;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.world.level.saveddata.SavedDataType;
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
    private static final SavedDataType<JournalData> TYPE = new SavedDataType<>(Bunnyland.id("journal"), JournalData::new,
            CompoundTag.CODEC.xmap(JournalData::load, data -> data.save(new CompoundTag())), DataFixTypes.SAVED_DATA_COMMAND_STORAGE);
    private final Map<UUID, PlayerJournal> journals = new HashMap<>();

    public static JournalData get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(TYPE);
    }

    public PlayerJournal of(UUID player) {
        return journals.computeIfAbsent(player, id -> new PlayerJournal());
    }

    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        journals.forEach((id, journal) -> {
            CompoundTag entry = journal.save();
            entry.store("Player", UUIDUtil.CODEC, id);
            list.add(entry);
        });
        tag.put("Journals", list);
        return tag;
    }

    public static JournalData load(CompoundTag tag) {
        JournalData data = new JournalData();
        ListTag list = tag.getListOrEmpty("Journals");
        for (int i = 0; i < list.size(); i++) {
            CompoundTag entry = list.getCompoundOrEmpty(i);
            entry.read("Player", UUIDUtil.CODEC).ifPresent(id -> data.journals.put(id, PlayerJournal.load(entry)));
        }
        return data;
    }
}

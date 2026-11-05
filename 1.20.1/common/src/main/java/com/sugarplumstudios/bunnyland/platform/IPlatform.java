package com.sugarplumstudios.bunnyland.platform;

import com.sugarplumstudios.bunnyland.network.ClientboundMessage;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;

import java.nio.file.Path;
import java.util.function.Supplier;

/** What Bunnyland needs from the mod loader. One implementation per loader. */
public interface IPlatform {
    String name();

    boolean isModLoaded(String modId);

    Path configDir();

    /** Registers an object under bunnyland:name in the given registry. */
    <R, T extends R> RegistryEntry<T> register(ResourceKey<? extends Registry<R>> registry, String name, Supplier<T> factory);

    /** A spawn egg for an entity type that may not be registered yet. */
    Item spawnEgg(Supplier<? extends EntityType<? extends Mob>> type, int background, int highlight, Item.Properties properties);

    CreativeModeTab.Builder creativeTab();

    /** Sends a message to one player's client. */
    void sendToPlayer(ServerPlayer player, ClientboundMessage message);

    /** Whether this entity may change blocks (the mobGriefing game rule, or the loader's event for it). */
    boolean mobGriefing(Level level, Entity entity);

    /** Whether another mod cancelled this player taming the animal. */
    boolean tamingCancelled(Animal animal, Player player);
}

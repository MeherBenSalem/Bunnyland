package com.sugarplumstudios.bunnyland.fabric;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.gamerules.GameRules;
import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.network.ClientboundMessage;
import com.sugarplumstudios.bunnyland.network.MessagePayload;
import com.sugarplumstudios.bunnyland.platform.IPlatform;
import com.sugarplumstudios.bunnyland.platform.RegistryEntry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.level.Level;

import java.nio.file.Path;
import java.util.function.Supplier;

public final class FabricPlatform implements IPlatform {
    @Override
    public String name() {
        return "Fabric";
    }

    @Override
    public boolean isModLoaded(String modId) {
        return FabricLoader.getInstance().isModLoaded(modId);
    }

    @Override
    public Path configDir() {
        return FabricLoader.getInstance().getConfigDir();
    }

    @Override
    @SuppressWarnings("unchecked")
    public <R, T extends R> RegistryEntry<T> register(ResourceKey<? extends Registry<R>> registry, String name, Supplier<T> factory) {
        Registry<R> target = (Registry<R>) BuiltInRegistries.REGISTRY.getValue(registry.identifier());
        if (target == null) throw new IllegalArgumentException("Unknown registry " + registry);
        T value = Registry.register(target, Bunnyland.id(name), factory.get());
        return new RegistryEntry<>(Bunnyland.id(name), () -> value);
    }

    @Override
    @SuppressWarnings("unchecked")
    public Item spawnEgg(Supplier<? extends EntityType<? extends Mob>> type, Item.Properties properties) {
        return new SpawnEggItem(properties.spawnEgg(type.get()));
    }

    @Override
    public CreativeModeTab.Builder creativeTab() {
        return CreativeModeTab.builder(CreativeModeTab.Row.TOP, 0);
    }

    @Override
    public void sendToPlayer(ServerPlayer player, ClientboundMessage message) {
        MessagePayload payload = MessagePayload.of(message);
        if (ServerPlayNetworking.canSend(player, payload.type())) ServerPlayNetworking.send(player, payload);
    }

    @Override
    public boolean mobGriefing(Level level, Entity entity) {
        return level instanceof ServerLevel server && server.getGameRules().get(GameRules.MOB_GRIEFING);
    }

    @Override
    public boolean tamingCancelled(Animal animal, Player player) {
        return false;
    }
}

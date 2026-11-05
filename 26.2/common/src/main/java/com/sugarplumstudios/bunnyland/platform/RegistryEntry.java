package com.sugarplumstudios.bunnyland.platform;

import net.minecraft.resources.Identifier;

import java.util.Objects;
import java.util.function.Supplier;

/**
 * A registered object, filled in by the loader's registry (immediately on Fabric, during registry events on
 * Forge and NeoForge). Read it with {@link #get()} once registries are populated.
 */
public final class RegistryEntry<T> implements Supplier<T> {
    private final Identifier id;
    private Supplier<? extends T> source;

    public RegistryEntry(Identifier id, Supplier<? extends T> source) {
        this.id = id;
        this.source = source;
    }

    public Identifier id() {
        return id;
    }

    @Override
    public T get() {
        return Objects.requireNonNull(source.get(), () -> "Registry entry not yet available: " + id);
    }
}

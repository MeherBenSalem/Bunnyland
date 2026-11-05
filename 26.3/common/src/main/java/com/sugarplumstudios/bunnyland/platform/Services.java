package com.sugarplumstudios.bunnyland.platform;

import java.util.ServiceLoader;

/** Loader-specific implementations, found through META-INF/services in each loader's jar. */
public final class Services {
    public static final IPlatform PLATFORM = load(IPlatform.class);

    private Services() {
    }

    public static <T> T load(Class<T> type) {
        return ServiceLoader.load(type, Services.class.getClassLoader()).findFirst()
                .orElseThrow(() -> new IllegalStateException("No implementation of " + type.getName()));
    }
}

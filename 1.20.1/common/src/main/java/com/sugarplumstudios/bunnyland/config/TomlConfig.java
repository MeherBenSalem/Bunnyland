package com.sugarplumstudios.bunnyland.config;

import com.sugarplumstudios.bunnyland.Bunnyland;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * A small commented TOML config file, written in the same layout as Forge's config files so a
 * {@code bunnyland-common.toml} from earlier versions keeps working. Missing or invalid values fall back to their
 * defaults (and are written back), out-of-range numbers are clamped, and unknown keys are dropped.
 */
public final class TomlConfig {
    private final String fileName;
    private final List<Node> nodes;

    private TomlConfig(String fileName, List<Node> nodes) {
        this.fileName = fileName;
        this.nodes = nodes;
    }

    // ------------------------------------------------------------------ values

    public abstract static sealed class Value<T> permits BooleanValue, IntValue, DoubleValue {
        final String path;
        final T defaultValue;
        T value;

        Value(String path, T defaultValue) {
            this.path = path;
            this.defaultValue = defaultValue;
            this.value = defaultValue;
        }

        public T get() {
            return value;
        }

        abstract T parse(String raw);

        abstract String range();

        String format() {
            return String.valueOf(value);
        }
    }

    public static final class BooleanValue extends Value<Boolean> {
        BooleanValue(String path, boolean defaultValue) {
            super(path, defaultValue);
        }

        @Override
        Boolean parse(String raw) {
            if (raw.equals("true")) return true;
            if (raw.equals("false")) return false;
            return null;
        }

        @Override
        String range() {
            return null;
        }
    }

    public static final class IntValue extends Value<Integer> {
        private final int min;
        private final int max;

        IntValue(String path, int defaultValue, int min, int max) {
            super(path, defaultValue);
            this.min = min;
            this.max = max;
        }

        @Override
        Integer parse(String raw) {
            try {
                return Math.max(min, Math.min(max, Integer.parseInt(raw)));
            } catch (NumberFormatException e) {
                return null;
            }
        }

        @Override
        String range() {
            return min + " ~ " + max;
        }
    }

    public static final class DoubleValue extends Value<Double> {
        private final double min;
        private final double max;

        DoubleValue(String path, double defaultValue, double min, double max) {
            super(path, defaultValue);
            this.min = min;
            this.max = max;
        }

        @Override
        Double parse(String raw) {
            try {
                return Math.max(min, Math.min(max, Double.parseDouble(raw)));
            } catch (NumberFormatException e) {
                return null;
            }
        }

        @Override
        String range() {
            return min + " ~ " + max;
        }
    }

    // ------------------------------------------------------------------ building

    private sealed interface Node permits Section, Entry {
    }

    private record Section(String path, List<String> comments, int depth) implements Node {
    }

    private record Entry(Value<?> value, String key, List<String> comments, int depth) implements Node {
    }

    /** Mirrors the subset of ForgeConfigSpec.Builder that Bunnyland uses. */
    public static final class Builder {
        private final List<Node> nodes = new ArrayList<>();
        private final Deque<String> sections = new ArrayDeque<>();
        private List<String> pendingComments = new ArrayList<>();

        public Builder comment(String... lines) {
            pendingComments.addAll(List.of(lines));
            return this;
        }

        public Builder push(String name) {
            sections.addLast(name);
            nodes.add(new Section(String.join(".", sections), takeComments(), sections.size() - 1));
            return this;
        }

        public Builder pop() {
            sections.removeLast();
            return this;
        }

        public BooleanValue define(String key, boolean defaultValue) {
            return add(new BooleanValue(path(key), defaultValue), key);
        }

        public IntValue defineInRange(String key, int defaultValue, int min, int max) {
            return add(new IntValue(path(key), defaultValue, min, max), key);
        }

        public DoubleValue defineInRange(String key, double defaultValue, double min, double max) {
            return add(new DoubleValue(path(key), defaultValue, min, max), key);
        }

        public TomlConfig build(String fileName) {
            return new TomlConfig(fileName, List.copyOf(nodes));
        }

        private <V extends Value<?>> V add(V value, String key) {
            nodes.add(new Entry(value, key, takeComments(), sections.size()));
            return value;
        }

        private String path(String key) {
            return sections.isEmpty() ? key : String.join(".", sections) + "." + key;
        }

        private List<String> takeComments() {
            List<String> out = pendingComments;
            pendingComments = new ArrayList<>();
            return out;
        }
    }

    // ------------------------------------------------------------------ file io

    /** Reads the file from the config folder (creating or completing it), then writes it back in full. */
    public void load(Path configDir) {
        Path file = configDir.resolve(fileName);
        Map<String, String> raw = new HashMap<>();
        if (Files.exists(file)) {
            try {
                String section = "";
                for (String line : Files.readAllLines(file, StandardCharsets.UTF_8)) {
                    String l = line.strip();
                    if (l.isEmpty() || l.startsWith("#")) continue;
                    if (l.startsWith("[") && l.endsWith("]")) {
                        section = l.substring(1, l.length() - 1).strip().replace("\"", "");
                        continue;
                    }
                    int eq = l.indexOf('=');
                    if (eq < 0) continue;
                    String key = l.substring(0, eq).strip().replace("\"", "");
                    String val = l.substring(eq + 1).strip();
                    int hash = val.indexOf(" #");
                    if (hash >= 0) val = val.substring(0, hash).strip();
                    raw.put(section.isEmpty() ? key : section + "." + key, val.toLowerCase(Locale.ROOT));
                }
            } catch (IOException e) {
                Bunnyland.LOGGER.warn("Could not read {}, using defaults", file, e);
            }
        }
        for (Node node : nodes) {
            if (node instanceof Entry entry) set(entry.value(), raw.get(entry.value().path));
        }
        try {
            Files.createDirectories(configDir);
            Files.writeString(file, render(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            Bunnyland.LOGGER.warn("Could not write {}", file, e);
        }
    }

    private static <T> void set(Value<T> value, String raw) {
        T parsed = raw == null ? null : value.parse(raw);
        if (raw != null && parsed == null) {
            Bunnyland.LOGGER.warn("Invalid value {} for {}, using the default {}", raw, value.path, value.defaultValue);
        }
        value.value = parsed == null ? value.defaultValue : parsed;
    }

    private String render() {
        StringBuilder out = new StringBuilder();
        for (Node node : nodes) {
            if (node instanceof Section section) {
                String indent = "\t".repeat(section.depth());
                out.append('\n');
                for (String c : section.comments()) out.append(indent).append('#').append(c).append('\n');
                out.append(indent).append('[').append(section.path()).append("]\n");
            } else if (node instanceof Entry entry) {
                String indent = "\t".repeat(entry.depth());
                for (String c : entry.comments()) out.append(indent).append('#').append(c).append('\n');
                String range = entry.value().range();
                if (range != null) out.append(indent).append("#Range: ").append(range).append('\n');
                out.append(indent).append(entry.key()).append(" = ").append(entry.value().format()).append('\n');
            }
        }
        return out.toString().stripLeading();
    }
}

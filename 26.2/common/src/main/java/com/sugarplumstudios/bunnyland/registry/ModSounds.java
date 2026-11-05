package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.platform.Services;
import net.minecraft.core.registries.Registries;
import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.creature.Species;
import net.minecraft.sounds.SoundEvent;
import com.sugarplumstudios.bunnyland.platform.RegistryEntry;

/** Mirrors tools/assetgen/sound_events.py, which also generates sounds.json and the .ogg files. */
public final class ModSounds {

    public static final RegistryEntry<SoundEvent> BUNNY_AMBIENT = register("entity.bunny.ambient");
    public static final RegistryEntry<SoundEvent> BUNNY_HURT = register("entity.bunny.hurt");
    public static final RegistryEntry<SoundEvent> BUNNY_DEATH = register("entity.bunny.death");
    public static final RegistryEntry<SoundEvent> BUNNY_HAPPY = register("entity.bunny.happy");
    public static final RegistryEntry<SoundEvent> FOX_AMBIENT = register("entity.blossom_fox.ambient");
    public static final RegistryEntry<SoundEvent> FOX_HURT = register("entity.blossom_fox.hurt");
    public static final RegistryEntry<SoundEvent> FOX_DEATH = register("entity.blossom_fox.death");
    public static final RegistryEntry<SoundEvent> FOX_HAPPY = register("entity.blossom_fox.happy");
    public static final RegistryEntry<SoundEvent> KITTY_AMBIENT = register("entity.cloud_kitty.ambient");
    public static final RegistryEntry<SoundEvent> KITTY_HURT = register("entity.cloud_kitty.hurt");
    public static final RegistryEntry<SoundEvent> KITTY_DEATH = register("entity.cloud_kitty.death");
    public static final RegistryEntry<SoundEvent> KITTY_PURR = register("entity.cloud_kitty.purr");
    public static final RegistryEntry<SoundEvent> MOUSE_AMBIENT = register("entity.strawberry_mouse.ambient");
    public static final RegistryEntry<SoundEvent> MOUSE_HURT = register("entity.strawberry_mouse.hurt");
    public static final RegistryEntry<SoundEvent> MOUSE_DEATH = register("entity.strawberry_mouse.death");
    public static final RegistryEntry<SoundEvent> BEAR_AMBIENT = register("entity.honey_bear.ambient");
    public static final RegistryEntry<SoundEvent> BEAR_HURT = register("entity.honey_bear.hurt");
    public static final RegistryEntry<SoundEvent> BEAR_DEATH = register("entity.honey_bear.death");
    public static final RegistryEntry<SoundEvent> BEAR_HAPPY = register("entity.honey_bear.happy");
    public static final RegistryEntry<SoundEvent> DEER_AMBIENT = register("entity.moon_deer.ambient");
    public static final RegistryEntry<SoundEvent> DEER_HURT = register("entity.moon_deer.hurt");
    public static final RegistryEntry<SoundEvent> DEER_DEATH = register("entity.moon_deer.death");
    public static final RegistryEntry<SoundEvent> AXOLOTL_AMBIENT = register("entity.pastel_axolotl.ambient");
    public static final RegistryEntry<SoundEvent> AXOLOTL_HURT = register("entity.pastel_axolotl.hurt");
    public static final RegistryEntry<SoundEvent> AXOLOTL_DEATH = register("entity.pastel_axolotl.death");
    public static final RegistryEntry<SoundEvent> SWAN_AMBIENT = register("entity.tiny_swan.ambient");
    public static final RegistryEntry<SoundEvent> SWAN_HURT = register("entity.tiny_swan.hurt");
    public static final RegistryEntry<SoundEvent> SWAN_DEATH = register("entity.tiny_swan.death");
    public static final RegistryEntry<SoundEvent> BUTTERFLY_AMBIENT = register("entity.rainbow_butterfly.ambient");
    public static final RegistryEntry<SoundEvent> BUTTERFLY_HURT = register("entity.rainbow_butterfly.hurt");
    public static final RegistryEntry<SoundEvent> BUTTERFLY_DEATH = register("entity.rainbow_butterfly.death");
    public static final RegistryEntry<SoundEvent> BIRD_AMBIENT = register("entity.cherry_blossom_bird.ambient");
    public static final RegistryEntry<SoundEvent> BIRD_HURT = register("entity.cherry_blossom_bird.hurt");
    public static final RegistryEntry<SoundEvent> BIRD_DEATH = register("entity.cherry_blossom_bird.death");
    public static final RegistryEntry<SoundEvent> BIRD_SING = register("entity.cherry_blossom_bird.sing");
    public static final RegistryEntry<SoundEvent> HAMSTER_AMBIENT = register("entity.dreamy_hamster.ambient");
    public static final RegistryEntry<SoundEvent> HAMSTER_HURT = register("entity.dreamy_hamster.hurt");
    public static final RegistryEntry<SoundEvent> HAMSTER_DEATH = register("entity.dreamy_hamster.death");
    public static final RegistryEntry<SoundEvent> PET_HAPPY = register("entity.pet.happy");
    public static final RegistryEntry<SoundEvent> PET_EAT = register("entity.pet.eat");
    public static final RegistryEntry<SoundEvent> PET_SNORE = register("entity.pet.snore");
    public static final RegistryEntry<SoundEvent> SQUEAKY_CARROT = register("item.squeaky_carrot.squeak");
    public static final RegistryEntry<SoundEvent> COLLAR_JINGLE = register("item.pet_collar.jingle");
    public static final RegistryEntry<SoundEvent> CARRIER_CAPTURE = register("item.pet_carrier.capture");
    public static final RegistryEntry<SoundEvent> CARRIER_RELEASE = register("item.pet_carrier.release");
    public static final RegistryEntry<SoundEvent> BOWL_FILL = register("block.feeding_bowl.fill");

    /** A creature's voice: ambient, hurt, death and the sound it makes when petted. */
    public record Voice(RegistryEntry<SoundEvent> ambient, RegistryEntry<SoundEvent> hurt,
                        RegistryEntry<SoundEvent> death, RegistryEntry<SoundEvent> happy) {
    }

    private ModSounds() {
    }

    private static RegistryEntry<SoundEvent> register(String name) {
        return Services.PLATFORM.register(Registries.SOUND_EVENT, name, () -> SoundEvent.createVariableRangeEvent(Bunnyland.id(name)));
    }

    public static Voice voice(Species species) {
        return switch (species) {
            case COTTON_BUNNY, STRAWBERRY_BUNNY, MOON_BUNNY, LAVENDER_BUNNY, SNOWBALL_BUNNY ->
                    new Voice(BUNNY_AMBIENT, BUNNY_HURT, BUNNY_DEATH, BUNNY_HAPPY);
            case BLOSSOM_FOX -> new Voice(FOX_AMBIENT, FOX_HURT, FOX_DEATH, FOX_HAPPY);
            case CLOUD_KITTY -> new Voice(KITTY_AMBIENT, KITTY_HURT, KITTY_DEATH, KITTY_PURR);
            case STRAWBERRY_MOUSE -> new Voice(MOUSE_AMBIENT, MOUSE_HURT, MOUSE_DEATH, PET_HAPPY);
            case HONEY_BEAR -> new Voice(BEAR_AMBIENT, BEAR_HURT, BEAR_DEATH, BEAR_HAPPY);
            case MOON_DEER -> new Voice(DEER_AMBIENT, DEER_HURT, DEER_DEATH, PET_HAPPY);
            case PASTEL_AXOLOTL -> new Voice(AXOLOTL_AMBIENT, AXOLOTL_HURT, AXOLOTL_DEATH, PET_HAPPY);
            case TINY_SWAN -> new Voice(SWAN_AMBIENT, SWAN_HURT, SWAN_DEATH, PET_HAPPY);
            case RAINBOW_BUTTERFLY -> new Voice(BUTTERFLY_AMBIENT, BUTTERFLY_HURT, BUTTERFLY_DEATH, PET_HAPPY);
            case CHERRY_BLOSSOM_BIRD -> new Voice(BIRD_AMBIENT, BIRD_HURT, BIRD_DEATH, BIRD_SING);
            case DREAMY_HAMSTER -> new Voice(HAMSTER_AMBIENT, HAMSTER_HURT, HAMSTER_DEATH, PET_HAPPY);
        };
    }
}

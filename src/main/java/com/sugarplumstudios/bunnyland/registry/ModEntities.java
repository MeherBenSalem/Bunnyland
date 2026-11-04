package com.sugarplumstudios.bunnyland.registry;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BlossomFox;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.entity.CherryBlossomBird;
import com.sugarplumstudios.bunnyland.entity.CloudKitty;
import com.sugarplumstudios.bunnyland.entity.CottonBunny;
import com.sugarplumstudios.bunnyland.entity.DreamyHamster;
import com.sugarplumstudios.bunnyland.entity.HoneyBear;
import com.sugarplumstudios.bunnyland.entity.LavenderBunny;
import com.sugarplumstudios.bunnyland.entity.MoonBunny;
import com.sugarplumstudios.bunnyland.entity.MoonDeer;
import com.sugarplumstudios.bunnyland.entity.PastelAxolotl;
import com.sugarplumstudios.bunnyland.entity.RainbowButterfly;
import com.sugarplumstudios.bunnyland.entity.SnowballBunny;
import com.sugarplumstudios.bunnyland.entity.StrawberryBunny;
import com.sugarplumstudios.bunnyland.entity.StrawberryMouse;
import com.sugarplumstudios.bunnyland.entity.TinySwan;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.EnumMap;
import java.util.Map;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Bunnyland.MOD_ID);

    private static final Map<Species, RegistryObject<? extends EntityType<? extends BunnylandAnimal>>> BY_SPECIES = new EnumMap<>(Species.class);

    public static final RegistryObject<EntityType<CottonBunny>> COTTON_BUNNY = register(Species.COTTON_BUNNY, CottonBunny::new, 0.5F, 0.6F);
    public static final RegistryObject<EntityType<StrawberryBunny>> STRAWBERRY_BUNNY = register(Species.STRAWBERRY_BUNNY, StrawberryBunny::new, 0.5F, 0.6F);
    public static final RegistryObject<EntityType<MoonBunny>> MOON_BUNNY = register(Species.MOON_BUNNY, MoonBunny::new, 0.5F, 0.6F);
    public static final RegistryObject<EntityType<LavenderBunny>> LAVENDER_BUNNY = register(Species.LAVENDER_BUNNY, LavenderBunny::new, 0.5F, 0.6F);
    public static final RegistryObject<EntityType<SnowballBunny>> SNOWBALL_BUNNY = register(Species.SNOWBALL_BUNNY, SnowballBunny::new, 0.55F, 0.6F);
    public static final RegistryObject<EntityType<BlossomFox>> BLOSSOM_FOX = register(Species.BLOSSOM_FOX, BlossomFox::new, 0.55F, 0.75F);
    public static final RegistryObject<EntityType<CloudKitty>> CLOUD_KITTY = register(Species.CLOUD_KITTY, CloudKitty::new, 0.5F, 0.8F);
    public static final RegistryObject<EntityType<StrawberryMouse>> STRAWBERRY_MOUSE = register(Species.STRAWBERRY_MOUSE, StrawberryMouse::new, 0.35F, 0.35F);
    public static final RegistryObject<EntityType<HoneyBear>> HONEY_BEAR = register(Species.HONEY_BEAR, HoneyBear::new, 0.75F, 0.95F);
    public static final RegistryObject<EntityType<MoonDeer>> MOON_DEER = register(Species.MOON_DEER, MoonDeer::new, 0.75F, 1.5F);
    public static final RegistryObject<EntityType<PastelAxolotl>> PASTEL_AXOLOTL = register(Species.PASTEL_AXOLOTL, PastelAxolotl::new, 0.6F, 0.35F);
    public static final RegistryObject<EntityType<TinySwan>> TINY_SWAN = register(Species.TINY_SWAN, TinySwan::new, 0.45F, 0.9F);
    public static final RegistryObject<EntityType<RainbowButterfly>> RAINBOW_BUTTERFLY = register(Species.RAINBOW_BUTTERFLY, RainbowButterfly::new, 0.4F, 0.35F);
    public static final RegistryObject<EntityType<CherryBlossomBird>> CHERRY_BLOSSOM_BIRD = register(Species.CHERRY_BLOSSOM_BIRD, CherryBlossomBird::new, 0.35F, 0.5F);
    public static final RegistryObject<EntityType<DreamyHamster>> DREAMY_HAMSTER = register(Species.DREAMY_HAMSTER, DreamyHamster::new, 0.45F, 0.45F);

    private ModEntities() {
    }

    private static <T extends BunnylandAnimal> RegistryObject<EntityType<T>> register(Species species, EntityType.EntityFactory<T> factory,
                                                                                     float width, float height) {
        RegistryObject<EntityType<T>> ro = ENTITIES.register(species.id, () -> EntityType.Builder.of(factory, species.category())
                .sized(width, height)
                .clientTrackingRange(10)
                .build(Bunnyland.id(species.id).toString()));
        BY_SPECIES.put(species, ro);
        return ro;
    }

    @SuppressWarnings("unchecked")
    public static EntityType<? extends BunnylandAnimal> get(Species species) {
        return BY_SPECIES.get(species).get();
    }

    public static AttributeSupplier attributes(Species species) {
        double health;
        double speed;
        double flying = 0;
        switch (species) {
            case BLOSSOM_FOX -> { health = 10; speed = 0.3; }
            case CLOUD_KITTY -> { health = 8; speed = 0.3; }
            case STRAWBERRY_MOUSE -> { health = 4; speed = 0.32; }
            case HONEY_BEAR -> { health = 20; speed = 0.22; }
            case MOON_DEER -> { health = 14; speed = 0.3; }
            case PASTEL_AXOLOTL -> { health = 10; speed = 1.0; }
            case TINY_SWAN -> { health = 8; speed = 0.25; }
            case RAINBOW_BUTTERFLY -> { health = 4; speed = 0.25; flying = 0.45; }
            case CHERRY_BLOSSOM_BIRD -> { health = 6; speed = 0.25; flying = 0.6; }
            case DREAMY_HAMSTER -> { health = 6; speed = 0.28; }
            default -> { health = 6; speed = 0.3; }
        }
        AttributeSupplier.Builder b = Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, health)
                .add(Attributes.MOVEMENT_SPEED, speed)
                .add(Attributes.FOLLOW_RANGE, 16.0D);
        if (flying > 0) b.add(Attributes.FLYING_SPEED, flying);
        return b.build();
    }
}

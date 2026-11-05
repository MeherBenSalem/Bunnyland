package com.sugarplumstudios.bunnyland.gametest;

import com.sugarplumstudios.bunnyland.Bunnyland;
import com.sugarplumstudios.bunnyland.block.FeedingBowlBlock;
import com.sugarplumstudios.bunnyland.creature.Accessory;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.item.DyeableCosmeticItem;
import com.sugarplumstudios.bunnyland.item.PetCarrierItem;
import com.sugarplumstudios.bunnyland.journal.JournalEvents;
import com.sugarplumstudios.bunnyland.registry.ModBlocks;
import com.sugarplumstudios.bunnyland.registry.ModEntities;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import com.mojang.authlib.GameProfile;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.List;
import java.util.UUID;

/** Server-side behaviour checks. Run with {@code ./gradlew runGameTestServer}. */
@GameTestHolder(Bunnyland.MOD_ID)
@PrefixGameTestTemplate(false)
public final class BunnylandGameTests {
    private static final String ARENA = "arena";

    private BunnylandGameTests() {
    }

    private static BunnylandAnimal spawn(GameTestHelper helper, Species species, double x, double z) {
        Entity e = helper.spawn(ModEntities.get(species), new Vec3(x, 1, z));
        if (!(e instanceof BunnylandAnimal animal)) throw new IllegalStateException("not a Bunnyland creature: " + e);
        return animal;
    }

    /** A Forge fake player standing in the arena, added to the level so pets can see their owner. */
    private static ServerPlayer player(GameTestHelper helper) {
        ServerPlayer p = FakePlayerFactory.get(helper.getLevel(), new GameProfile(UUID.randomUUID(), "bunnyland_tester"));
        Vec3 pos = helper.absoluteVec(new Vec3(4.5D, 1.0D, 4.5D));
        p.moveTo(pos.x, pos.y, pos.z);
        helper.getLevel().addNewPlayer(p);
        return p;
    }

    private static void release(GameTestHelper helper, ServerPlayer player) {
        helper.getLevel().removePlayerImmediately(player, Entity.RemovalReason.DISCARDED);
    }

    /** A pet owned by nobody online, so it never wanders off to follow anyone. */
    private static void tameToStranger(BunnylandAnimal pet) {
        pet.setTame(true, false);
        pet.setOwnerUUID(UUID.randomUUID());
    }

    private static void hold(ServerPlayer player, ItemStack stack) {
        player.setItemInHand(InteractionHand.MAIN_HAND, stack);
    }

    @GameTest(template = ARENA)
    public static void everyCreatureSpawns(GameTestHelper helper) {
        Species[] all = Species.values();
        for (int i = 0; i < all.length; i++) {
            BunnylandAnimal a = spawn(helper, all[i], 1.5 + (i % 5) * 1.5, 1.5 + (i / 5) * 2.5);
            helper.assertTrue(a.species() == all[i], "species mismatch for " + all[i]);
            helper.assertTrue(a.getVariant() >= 0 && a.getVariant() < all[i].variantCount(), "bad variant for " + all[i]);
            helper.assertTrue(a.getAnimatableInstanceCache() != null, "no GeckoLib cache for " + all[i]);
            helper.assertTrue(a.getHealth() > 0, "dead on arrival: " + all[i]);
            helper.assertTrue(a.getType().getCategory() == all[i].category(), "wrong category for " + all[i]);
        }
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void treatsTameCreatures(GameTestHelper helper) {
        ServerPlayer player = player(helper);
        Species[] tested = {Species.COTTON_BUNNY, Species.HONEY_BEAR, Species.RAINBOW_BUTTERFLY, Species.PASTEL_AXOLOTL, Species.MOON_DEER};
        ItemStack[] treats = {new ItemStack(ModItems.BUNNY_BISCUIT.get(), 64), new ItemStack(ModItems.HONEY_CAKE.get(), 64),
                new ItemStack(ModItems.FLOWER_NECTAR.get(), 16), new ItemStack(ModItems.FISH_CRACKER.get(), 64),
                new ItemStack(ModItems.MOON_COOKIE.get(), 64)};
        for (int i = 0; i < tested.length; i++) {
            BunnylandAnimal a = spawn(helper, tested[i], 1.5 + i * 1.5, 2.5);
            for (int tries = 0; tries < 100 && !a.isTame(); tries++) {
                hold(player, treats[i].copy());
                a.mobInteract(player, InteractionHand.MAIN_HAND);
            }
            helper.assertTrue(a.isTame() && a.isOwnedBy(player), tested[i] + " was not tamed by its treat");
            helper.assertTrue(JournalEvents.journal(player).isTamed(tested[i]), tested[i] + " missing from the journal");
        }
        // The wrong treat never tames.
        BunnylandAnimal bear = spawn(helper, Species.HONEY_BEAR, 6.5, 6.5);
        for (int tries = 0; tries < 40; tries++) {
            hold(player, new ItemStack(ModItems.BUNNY_BISCUIT.get()));
            bear.mobInteract(player, InteractionHand.MAIN_HAND);
        }
        helper.assertTrue(!bear.isTame(), "a Honey Bear was tamed with a Bunny Biscuit");
        release(helper, player);
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void sitFollowAndPetting(GameTestHelper helper) {
        ServerPlayer player = player(helper);
        BunnylandAnimal kitty = spawn(helper, Species.CLOUD_KITTY, 3.5, 3.5);
        kitty.tame(player);
        kitty.setHappiness(50);
        hold(player, ItemStack.EMPTY);
        kitty.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(kitty.isOrderedToSit(), "empty-hand use should make the pet sit");
        kitty.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(!kitty.isOrderedToSit(), "second use should make the pet follow again");
        player.setShiftKeyDown(true);
        kitty.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(kitty.getHappiness() == 58, "petting should add 8 happiness, got " + kitty.getHappiness());
        helper.assertTrue(!kitty.isOrderedToSit(), "petting must not toggle sitting");
        kitty.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(kitty.getHappiness() == 58, "petting has a cooldown");
        player.setShiftKeyDown(false);
        release(helper, player);
        helper.succeed();
    }

    @GameTest(template = ARENA, timeoutTicks = 400)
    public static void breedingMakesTamedBaby(GameTestHelper helper) {
        // Pets of an offline owner sit and wait (vanilla behaviour), so the owner has to be here.
        ServerPlayer player = player(helper);
        UUID owner = player.getUUID();
        BunnylandAnimal a = spawn(helper, Species.COTTON_BUNNY, 3.5, 4.5);
        BunnylandAnimal b = spawn(helper, Species.COTTON_BUNNY, 5.5, 4.5);
        for (BunnylandAnimal p : List.of(a, b)) {
            p.tame(player);
            p.setHappiness(80);
            p.setInLove(null);
        }
        helper.assertTrue(a.canMate(b), "parents should be able to mate at the start");
        helper.succeedWhen(() -> {
            List<? extends BunnylandAnimal> babies = helper.getLevel().getEntitiesOfClass(BunnylandAnimal.class,
                    new AABB(helper.absolutePos(BlockPos.ZERO)).inflate(10), BunnylandAnimal::isBaby);
            helper.assertTrue(!babies.isEmpty(), "no baby yet");
            BunnylandAnimal baby = babies.get(0);
            helper.assertTrue(baby.isTame() && owner.equals(baby.getOwnerUUID()), "the baby should belong to the parents' owner");
        });
    }

    @GameTest(template = ARENA)
    public static void lonelyPetsWontBreed(GameTestHelper helper) {
        BunnylandAnimal a = spawn(helper, Species.TINY_SWAN, 3.5, 4.5);
        BunnylandAnimal b = spawn(helper, Species.TINY_SWAN, 4.5, 4.5);
        for (BunnylandAnimal p : List.of(a, b)) {
            tameToStranger(p);
            p.setInLove(null);
        }
        a.setHappiness(15);
        b.setHappiness(90);
        helper.assertTrue(!a.canMate(b), "a lonely pet should refuse to mate");
        a.setHappiness(60);
        helper.assertTrue(a.canMate(b), "happy pets in love should be able to mate");
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void rareOffspringVariants(GameTestHelper helper) {
        RandomSource random = RandomSource.create(42L);
        for (Species s : Species.values()) {
            helper.assertTrue(!s.rare.isEmpty(), s + " has no rare variants");
            for (int i = 0; i < 20; i++) {
                helper.assertTrue(s.isRare(s.rollOffspringVariant(random, 0, 1, 1.0D)), "chance 1.0 must give a rare variant");
                int v = s.rollOffspringVariant(random, 0, 1, 0.0D);
                helper.assertTrue(v == 0 || v == 1, "chance 0 must copy a parent");
            }
        }
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void cosmeticsAndShears(GameTestHelper helper) {
        ServerPlayer player = player(helper);
        BunnylandAnimal fox = spawn(helper, Species.BLOSSOM_FOX, 4.5, 4.5);
        fox.tame(player);
        ItemStack collar = ((DyeableCosmeticItem) ModItems.PET_COLLAR.get()).withColor(0x55CCAA);
        hold(player, collar);
        fox.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(fox.getCollarColor() == 0x55CCAA, "collar colour should be applied, got " + Integer.toHexString(fox.getCollarColor()));
        hold(player, new ItemStack(ModItems.PET_BOW.get()));
        fox.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(fox.hasBow(), "bow should be equipped");
        hold(player, new ItemStack(ModItems.FLOWER_CROWN.get()));
        fox.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(fox.getAccessory() == Accessory.FLOWER_CROWN, "flower crown should be worn");
        hold(player, new ItemStack(ModItems.PARTY_HAT.get()));
        fox.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(fox.getAccessory() == Accessory.PARTY_HAT, "party hat should replace the crown");
        hold(player, new ItemStack(Items.SHEARS));
        for (int i = 0; i < 3; i++) fox.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(!fox.hasCollar() && !fox.hasBow() && fox.getAccessory() == Accessory.NONE, "shears should remove everything");
        List<ItemEntity> drops = helper.getLevel().getEntitiesOfClass(ItemEntity.class, fox.getBoundingBox().inflate(3));
        helper.assertTrue(drops.size() >= 4, "removed cosmetics should drop as items, found " + drops.size());
        boolean dyedCollarBack = drops.stream().anyMatch(d -> d.getItem().is(ModItems.PET_COLLAR.get())
                && ((DyeableCosmeticItem) ModItems.PET_COLLAR.get()).getColor(d.getItem()) == 0x55CCAA);
        helper.assertTrue(dyedCollarBack, "the collar should come back with its colour");
        release(helper, player);
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void strangersCannotDressPets(GameTestHelper helper) {
        ServerPlayer stranger = player(helper);
        BunnylandAnimal bunny = spawn(helper, Species.LAVENDER_BUNNY, 4.5, 4.5);
        tameToStranger(bunny);
        hold(stranger, new ItemStack(ModItems.TINY_TOP_HAT.get()));
        bunny.mobInteract(stranger, InteractionHand.MAIN_HAND);
        helper.assertTrue(bunny.getAccessory() == Accessory.NONE, "someone else's pet must not be dressed");
        release(helper, stranger);
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void carrierRoundTrip(GameTestHelper helper) {
        ServerPlayer player = player(helper);
        BunnylandAnimal hamster = spawn(helper, Species.DREAMY_HAMSTER, 3.5, 3.5);
        hamster.tame(player);
        hamster.setVariant(3);
        hamster.setCustomName(Component.literal("Mochi"));
        hamster.setAccessory(Accessory.STAR_CLIP);
        ItemStack carrier = new ItemStack(ModItems.PET_CARRIER.get());
        hold(player, carrier);
        hamster.mobInteract(player, InteractionHand.MAIN_HAND);
        ItemStack held = player.getMainHandItem();
        helper.assertTrue(PetCarrierItem.hasPet(held), "carrier should hold the hamster");
        helper.assertTrue(hamster.isRemoved(), "the hamster should be inside the carrier");

        BlockPos floor = helper.absolutePos(new BlockPos(6, 0, 6));
        held.useOn(new UseOnContext(player, InteractionHand.MAIN_HAND,
                new BlockHitResult(Vec3.atCenterOf(floor), Direction.UP, floor, false)));
        helper.assertTrue(!PetCarrierItem.hasPet(player.getMainHandItem()), "carrier should be empty again");
        List<? extends BunnylandAnimal> out = helper.getLevel().getEntitiesOfClass(BunnylandAnimal.class,
                new AABB(floor.above()).inflate(1.5), a -> a.species() == Species.DREAMY_HAMSTER);
        helper.assertTrue(out.size() == 1, "exactly one hamster should come out, found " + out.size());
        BunnylandAnimal back = out.get(0);
        helper.assertTrue(back.isOwnedBy(player) && back.getVariant() == 3 && back.getAccessory() == Accessory.STAR_CLIP
                && "Mochi".equals(back.getCustomName().getString()), "the hamster should keep its owner, variant, clip and name");
        release(helper, player);
        helper.succeed();
    }

    @GameTest(template = ARENA, timeoutTicks = 800)
    public static void hungryPetEatsFromBowl(GameTestHelper helper) {
        BlockPos bowl = new BlockPos(6, 1, 6);
        helper.setBlock(bowl, ModBlocks.FEEDING_BOWL.get().defaultBlockState().setValue(FeedingBowlBlock.FOOD, 4));
        BunnylandAnimal bear = spawn(helper, Species.HONEY_BEAR, 2.5, 2.5);
        bear.tame(player(helper));
        bear.setHappiness(30);
        bear.setHealth(bear.getMaxHealth() - 6);
        helper.succeedWhen(() -> {
            helper.assertBlockProperty(bowl, FeedingBowlBlock.FOOD, f -> f < 4, "the bowl should have been eaten from");
            helper.assertTrue(bear.getHappiness() > 30, "eating should cheer the bear up");
        });
    }

    @GameTest(template = ARENA)
    public static void fillingTheBowl(GameTestHelper helper) {
        ServerPlayer player = player(helper);
        BlockPos bowl = new BlockPos(4, 1, 4);
        helper.setBlock(bowl, ModBlocks.FEEDING_BOWL.get());
        BlockPos abs = helper.absolutePos(bowl);
        for (int i = 0; i < 10; i++) {
            hold(player, new ItemStack(ModItems.PET_KIBBLE.get()));
            helper.getLevel().getBlockState(abs).useItemOn(player.getMainHandItem(), helper.getLevel(), player, InteractionHand.MAIN_HAND,
                    new BlockHitResult(Vec3.atCenterOf(abs), Direction.UP, abs, false));
        }
        helper.assertBlockProperty(bowl, FeedingBowlBlock.FOOD, FeedingBowlBlock.MAX_FOOD);
        release(helper, player);
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void toysCheerPetsUp(GameTestHelper helper) {
        ServerPlayer player = player(helper);
        BunnylandAnimal kitty = spawn(helper, Species.CLOUD_KITTY, 3.5, 3.5);
        kitty.tame(player);
        kitty.setHappiness(40);
        ItemStack yarn = new ItemStack(ModItems.YARN_BALL.get());
        hold(player, yarn);
        kitty.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(kitty.getHappiness() == 58, "a favourite toy should add 18 happiness, got " + kitty.getHappiness());
        helper.assertTrue(player.getMainHandItem().getDamageValue() == 1, "playing wears the toy a little");
        kitty.mobInteract(player, InteractionHand.MAIN_HAND);
        helper.assertTrue(kitty.getHappiness() == 58, "toys have a cooldown");
        release(helper, player);
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void napsEndWhenHurt(GameTestHelper helper) {
        BunnylandAnimal deer = spawn(helper, Species.MOON_DEER, 4.5, 4.5);
        deer.setNapping(true);
        helper.assertTrue(deer.isNapping(), "deer should nap");
        deer.hurt(helper.getLevel().damageSources().generic(), 1.0F);
        helper.assertTrue(!deer.isNapping(), "getting hurt should wake it");
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void journalDiscovery(GameTestHelper helper) {
        ServerPlayer player = player(helper);
        BunnylandAnimal swan = spawn(helper, Species.TINY_SWAN, 6.5, 4.5);
        swan.setVariant(4);
        JournalEvents.scan(player);
        helper.assertTrue(JournalEvents.journal(player).isDiscovered(Species.TINY_SWAN), "a nearby swan should be discovered");
        helper.assertTrue(JournalEvents.journal(player).hasSeenVariant(Species.TINY_SWAN, 4), "its rare variant should be recorded");
        release(helper, player);
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void movementTypes(GameTestHelper helper) {
        helper.assertTrue(spawn(helper, Species.RAINBOW_BUTTERFLY, 2.5, 2.5).getNavigation() instanceof FlyingPathNavigation,
                "butterflies should fly");
        helper.assertTrue(spawn(helper, Species.CHERRY_BLOSSOM_BIRD, 4.5, 2.5).getNavigation() instanceof FlyingPathNavigation,
                "birds should fly");
        helper.assertTrue(spawn(helper, Species.PASTEL_AXOLOTL, 6.5, 2.5).getNavigation() instanceof AmphibiousPathNavigation,
                "axolotls should swim and walk");
        helper.succeed();
    }

    @GameTest(template = ARENA)
    public static void spawnsAddedToBiomes(GameTestHelper helper) {
        var biomes = helper.getLevel().registryAccess().registryOrThrow(Registries.BIOME);
        check(helper, biomes.getHolderOrThrow(Biomes.MEADOW).value(), MobCategory.CREATURE, ModEntities.COTTON_BUNNY.get());
        check(helper, biomes.getHolderOrThrow(Biomes.MEADOW).value(), MobCategory.AMBIENT, ModEntities.RAINBOW_BUTTERFLY.get());
        check(helper, biomes.getHolderOrThrow(Biomes.CHERRY_GROVE).value(), MobCategory.CREATURE, ModEntities.CHERRY_BLOSSOM_BIRD.get());
        check(helper, biomes.getHolderOrThrow(Biomes.SNOWY_PLAINS).value(), MobCategory.CREATURE, ModEntities.SNOWBALL_BUNNY.get());
        check(helper, biomes.getHolderOrThrow(Biomes.RIVER).value(), MobCategory.CREATURE, ModEntities.PASTEL_AXOLOTL.get());
        check(helper, biomes.getHolderOrThrow(Biomes.RIVER).value(), MobCategory.CREATURE, ModEntities.TINY_SWAN.get());
        check(helper, biomes.getHolderOrThrow(Biomes.TAIGA).value(), MobCategory.CREATURE, ModEntities.MOON_DEER.get());
        check(helper, biomes.getHolderOrThrow(Biomes.FOREST).value(), MobCategory.CREATURE, ModEntities.HONEY_BEAR.get());
        helper.succeed();
    }

    private static void check(GameTestHelper helper, Biome biome, MobCategory category, EntityType<?> type) {
        boolean found = biome.getMobSettings().getMobs(category).unwrap().stream()
                .anyMatch(d -> d.type == type);
        helper.assertTrue(found, type.getDescriptionId() + " should spawn in " + biome);
    }

    @GameTest(template = ARENA)
    public static void recipesLoad(GameTestHelper helper) {
        var recipes = helper.getLevel().getRecipeManager();
        long ours = recipes.getRecipeIds().filter(id -> id.getNamespace().equals(Bunnyland.MOD_ID)).count();
        helper.assertTrue(ours == 29, "expected 29 Bunnyland recipes, found " + ours);
        for (String id : List.of("bunny_biscuit", "pet_collar", "pink_pet_bed", "pet_carrier", "pet_journal", "feeding_bowl")) {
            helper.assertTrue(recipes.byKey(Bunnyland.id(id)).isPresent(), "missing recipe " + id);
        }
        helper.succeed();
    }
}

package com.sugarplumstudios.bunnyland.entity;

import com.sugarplumstudios.bunnyland.config.BunnylandConfig;
import com.sugarplumstudios.bunnyland.creature.Accessory;
import com.sugarplumstudios.bunnyland.creature.Mood;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.ai.EatFromBowlGoal;
import com.sugarplumstudios.bunnyland.entity.ai.NapGoal;
import com.sugarplumstudios.bunnyland.entity.ai.PetFollowOwnerGoal;
import com.sugarplumstudios.bunnyland.entity.ai.SeekPetBedGoal;
import com.sugarplumstudios.bunnyland.entity.ai.ZoomiesGoal;
import com.sugarplumstudios.bunnyland.item.DyeableCosmeticItem;
import com.sugarplumstudios.bunnyland.item.PetInteractable;
import com.sugarplumstudios.bunnyland.journal.JournalEvents;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import com.sugarplumstudios.bunnyland.registry.ModParticles;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.gameevent.GameEvent;
import com.sugarplumstudios.bunnyland.platform.Services;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.UUID;

/**
 * Shared behaviour of every Bunnyland creature: variants, cosmetics, happiness, napping, taming,
 * petting, playing, feeding, breeding (with rare offspring) and the GeckoLib animation controllers.
 */
public abstract class BunnylandAnimal extends TamableAnimal implements GeoEntity {
    public static final RawAnimation IDLE = RawAnimation.begin().thenLoop("idle");
    public static final RawAnimation WALK = RawAnimation.begin().thenLoop("walk");
    public static final RawAnimation RUN = RawAnimation.begin().thenLoop("run");
    public static final RawAnimation SIT = RawAnimation.begin().thenLoop("sit");
    public static final RawAnimation SLEEP = RawAnimation.begin().thenLoop("sleep");
    public static final RawAnimation FLY = RawAnimation.begin().thenLoop("fly");
    public static final RawAnimation SWIM = RawAnimation.begin().thenLoop("swim");
    public static final RawAnimation DANCE = RawAnimation.begin().thenLoop("dance");
    public static final RawAnimation EAT = RawAnimation.begin().thenPlay("eat");
    public static final RawAnimation HAPPY = RawAnimation.begin().thenPlay("happy");
    public static final RawAnimation PLAY = RawAnimation.begin().thenPlay("play");
    public static final RawAnimation SPECIAL = RawAnimation.begin().thenPlay("special");
    public static final String ACTION_CONTROLLER = "action";

    public static final int MAX_HAPPINESS = 100;
    public static final int NO_COLOR = -1;

    private static final EntityDataAccessor<Integer> DATA_VARIANT = SynchedEntityData.defineId(BunnylandAnimal.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_HAPPINESS = SynchedEntityData.defineId(BunnylandAnimal.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_COLLAR = SynchedEntityData.defineId(BunnylandAnimal.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_BOW = SynchedEntityData.defineId(BunnylandAnimal.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Byte> DATA_ACCESSORY = SynchedEntityData.defineId(BunnylandAnimal.class, EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Byte> DATA_STATE = SynchedEntityData.defineId(BunnylandAnimal.class, EntityDataSerializers.BYTE);
    private static final int STATE_NAPPING = 1;
    private static final int STATE_RUNNING = 2;

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private int petCooldown;
    private int playCooldown;
    private int eatCooldown;
    private int napCooldown;
    private int decayTimer = 1200;
    @Nullable
    private BlockPos bedPos;

    protected BunnylandAnimal(EntityType<? extends BunnylandAnimal> type, Level level) {
        super(type, level);
    }

    /** Which creature this is. A method (not a field) so it is usable while the entity is still being constructed. */
    public abstract Species species();

    // ------------------------------------------------------------------ synced state

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(DATA_VARIANT, 0);
        entityData.define(DATA_HAPPINESS, 50);
        entityData.define(DATA_COLLAR, NO_COLOR);
        entityData.define(DATA_BOW, NO_COLOR);
        entityData.define(DATA_ACCESSORY, (byte) 0);
        entityData.define(DATA_STATE, (byte) 0);
    }

    public int getVariant() {
        return species().clampVariant(entityData.get(DATA_VARIANT));
    }

    public void setVariant(int variant) {
        entityData.set(DATA_VARIANT, species().clampVariant(variant));
    }

    public boolean isRareVariant() {
        return species().isRare(getVariant());
    }

    public int getHappiness() {
        return entityData.get(DATA_HAPPINESS);
    }

    public void setHappiness(int happiness) {
        entityData.set(DATA_HAPPINESS, Mth.clamp(happiness, 0, MAX_HAPPINESS));
    }

    public void addHappiness(int amount) {
        setHappiness(getHappiness() + amount);
    }

    public Mood getMood() {
        return Mood.of(getHappiness());
    }

    public int getCollarColor() {
        return entityData.get(DATA_COLLAR);
    }

    public void setCollarColor(int color) {
        entityData.set(DATA_COLLAR, color);
    }

    public boolean hasCollar() {
        return getCollarColor() != NO_COLOR;
    }

    public int getBowColor() {
        return entityData.get(DATA_BOW);
    }

    public void setBowColor(int color) {
        entityData.set(DATA_BOW, color);
    }

    public boolean hasBow() {
        return getBowColor() != NO_COLOR;
    }

    public Accessory getAccessory() {
        return Accessory.byOrdinal(entityData.get(DATA_ACCESSORY));
    }

    public void setAccessory(Accessory accessory) {
        entityData.set(DATA_ACCESSORY, (byte) accessory.ordinal());
    }

    private boolean getState(int bit) {
        return (entityData.get(DATA_STATE) & bit) != 0;
    }

    private void setState(int bit, boolean on) {
        byte b = entityData.get(DATA_STATE);
        byte n = (byte) (on ? b | bit : b & ~bit);
        if (n != b) entityData.set(DATA_STATE, n);
    }

    public boolean isNapping() {
        return getState(STATE_NAPPING);
    }

    public void setNapping(boolean napping) {
        if (!napping && isNapping()) napCooldown = 300;
        if (!napping) bedPos = null;
        setState(STATE_NAPPING, napping);
    }

    public boolean isRunning() {
        return getState(STATE_RUNNING);
    }

    @Nullable
    public BlockPos getBedPos() {
        return bedPos;
    }

    public void setBedPos(@Nullable BlockPos pos) {
        bedPos = pos;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Variant", getVariant());
        tag.putBoolean("Rare", isRareVariant());
        tag.putInt("Happiness", getHappiness());
        if (hasCollar()) tag.putInt("CollarColor", getCollarColor());
        if (hasBow()) tag.putInt("BowColor", getBowColor());
        if (getAccessory() != Accessory.NONE) tag.putString("Accessory", getAccessory().id);
        tag.putBoolean("Napping", isNapping());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("VariantName")) {
            int v = species().variantByName(tag.getString("VariantName"));
            setVariant(Math.max(0, v));
        } else {
            setVariant(tag.getInt("Variant"));
        }
        if (tag.contains("Happiness")) setHappiness(tag.getInt("Happiness"));
        setCollarColor(tag.contains("CollarColor") ? tag.getInt("CollarColor") : NO_COLOR);
        setBowColor(tag.contains("BowColor") ? tag.getInt("BowColor") : NO_COLOR);
        setAccessory(Accessory.byId(tag.getString("Accessory")));
        setState(STATE_NAPPING, tag.getBoolean("Napping"));
    }

    // ------------------------------------------------------------------ goals

    @Override
    protected void registerGoals() {
        if (floatsInWater()) goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new PanicGoal(this, 1.6D));
        goalSelector.addGoal(2, new NapGoal(this));
        goalSelector.addGoal(3, new SitWhenOrderedToGoal(this));
        goalSelector.addGoal(4, new BreedGoal(this, 1.0D));
        goalSelector.addGoal(5, new TemptGoal(this, 1.1D, Ingredient.of(species().tempting), false));
        if (isShy()) {
            goalSelector.addGoal(6, new AvoidEntityGoal<>(this, Player.class, 8.0F, 1.1D, 1.5D,
                    e -> !isTame() && !e.isDiscrete() && BunnylandConfig.COMMON.wildCreaturesAreShy.get()
                            && !(e instanceof Player p && (p.isCreative() || p.isSpectator()))));
        }
        goalSelector.addGoal(7, new PetFollowOwnerGoal(this, followSpeed(), 7.0F, 2.5F, isFlyer()));
        goalSelector.addGoal(8, new EatFromBowlGoal(this));
        goalSelector.addGoal(8, new SeekPetBedGoal(this));
        addSpeciesGoals();
        goalSelector.addGoal(10, new FollowParentGoal(this, 1.1D));
        goalSelector.addGoal(11, new ZoomiesGoal(this));
        addWanderGoals();
        goalSelector.addGoal(13, new LookAtPlayerGoal(this, Player.class, 6.0F));
        goalSelector.addGoal(14, new RandomLookAroundGoal(this));
    }

    /** Species-specific goals, added at priority 9. */
    protected void addSpeciesGoals() {
    }

    /** Idle wandering, added at priority 12. */
    protected void addWanderGoals() {
        goalSelector.addGoal(12, new WaterAvoidingRandomStrollGoal(this, 0.8D));
    }

    protected boolean floatsInWater() {
        return true;
    }

    /** Wild shy creatures run from players who aren't sneaking. */
    protected boolean isShy() {
        return false;
    }

    public boolean isFlyer() {
        return false;
    }

    /** Swimmers are happy to be teleported into water by their owner. */
    public boolean likesWater() {
        return false;
    }

    protected double followSpeed() {
        return 1.15D;
    }

    // ------------------------------------------------------------------ sleeping

    /** Whether it is this species' bedtime (night for day creatures, day for night creatures). */
    public boolean isSleepTime() {
        Level level = level();
        if (level.dimensionType().hasFixedTime()) return false;
        boolean day = level.isDay();
        return species().schedule == Species.Schedule.DAY ? !day : day;
    }

    /** Decides whether this creature should be napping right now. */
    public boolean wantsToNap() {
        if (napCooldown > 0 || isInWaterOrBubble() || isPassenger() || getTarget() != null || isInLove() || isLeashed()) return false;
        if (!onGround()) return false;
        if (getLastHurtByMobTimestamp() > 0 && tickCount - getLastHurtByMobTimestamp() < 400) return false;
        if (!isTame()) return isSleepTime();
        LivingEntity owner = getOwner();
        if (owner instanceof Player p && p.isSleeping() && distanceToSqr(owner) < 256.0D) return true;
        if (isOrderedToSit()) return isSleepTime();
        if (bedPos != null && isSleepTime() && blockPosition().equals(bedPos)) {
            return owner == null || distanceToSqr(owner) < 24.0D * 24.0D;
        }
        return false;
    }

    // ------------------------------------------------------------------ ticking

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        setState(STATE_RUNNING, !isNapping() && getMoveControl().hasWanted() && getMoveControl().getSpeedModifier() >= 1.3D);
        if (petCooldown > 0) petCooldown--;
        if (playCooldown > 0) playCooldown--;
        if (eatCooldown > 0) eatCooldown--;
        if (napCooldown > 0) napCooldown--;
        if (isTame()) {
            if (BunnylandConfig.COMMON.happinessDecay.get() && --decayTimer <= 0) {
                decayTimer = BunnylandConfig.COMMON.happinessDecayMinutes.get() * 1200;
                if (getHappiness() > 10) addHappiness(-1);
            }
            Mood mood = getMood();
            int regen = mood == Mood.OVERJOYED ? 100 : mood == Mood.HAPPY ? 200 : 0;
            if (regen > 0 && getHealth() < getMaxHealth() && tickCount % regen == 0) heal(1.0F);
        }
        if (isNapping() && random.nextInt(400) == 0) {
            playSound(ModSounds.PET_SNORE.get(), 0.4F, getVoicePitch());
        }
        if (!isNapping() && !isInSittingPose() && getNavigation().isDone() && random.nextInt(1500) == 0) onIdleSpecial();
    }

    /** Every now and then an idle creature does its signature move (sniffing, grooming, preening, singing...). */
    protected void onIdleSpecial() {
        playAction("special");
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide && BunnylandConfig.CLIENT.ambientParticles.get()) clientParticles();
    }

    protected void clientParticles() {
        if (isNapping() && random.nextInt(45) == 0) {
            particle(ModParticles.ZZZ.get(), 0.25D, getBbHeight() + 0.2D);
        }
        if (isRareVariant() && random.nextInt(30) == 0) {
            particle(ModParticles.SPARKLE.get(), getBbWidth(), getBbHeight() * random.nextDouble());
        }
        if (isTame() && !isNapping()) {
            Mood mood = getMood();
            if (mood == Mood.OVERJOYED && random.nextInt(220) == 0) particle(ParticleTypes.HEART, 0.3D, getBbHeight() + 0.3D);
            if (mood == Mood.SAD && random.nextInt(160) == 0) particle(ParticleTypes.FALLING_WATER, 0.2D, getBbHeight() + 0.3D);
        }
    }

    protected void particle(ParticleOptions type, double spread, double height) {
        level().addParticle(type, getX() + (random.nextDouble() - 0.5D) * spread, getY() + height,
                getZ() + (random.nextDouble() - 0.5D) * spread, 0.0D, 0.0D, 0.0D);
    }

    protected void serverParticles(ParticleOptions type, int count, double spread) {
        if (level() instanceof ServerLevel server) {
            server.sendParticles(type, getX(), getY() + getBbHeight() * 0.8D, getZ(), count, spread, spread * 0.6D, spread, 0.02D);
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !level().isClientSide) {
            setNapping(false);
            if (isTame()) addHappiness(-3);
        }
        return hurt;
    }

    // ------------------------------------------------------------------ interaction

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        Level level = level();
        if (stack.getItem() instanceof PetInteractable interactable) {
            InteractionResult result = interactable.interactWithPet(this, player, hand, stack);
            if (result != InteractionResult.PASS) return result;
        }
        if (!isTame()) {
            if (stack.is(species().tamingTreats)) {
                if (!level.isClientSide) tryTame(player, hand, stack);
                return InteractionResult.sidedSuccess(level.isClientSide);
            }
            return super.mobInteract(player, hand);
        }
        if (!isOwnedBy(player)) return InteractionResult.PASS;

        if (stack.is(Items.SHEARS) && (hasCollar() || hasBow() || getAccessory() != Accessory.NONE)) {
            if (!level.isClientSide) {
                removeOneCosmetic(player);
                stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        boolean kibble = stack.is(ModItems.PET_KIBBLE.get());
        boolean food = isFood(stack);
        if (kibble || food) {
            boolean hurt = getHealth() < getMaxHealth();
            boolean lonely = getHappiness() < BunnylandConfig.COMMON.breedingHappiness.get();
            if (food && !isBaby() && !hurt && !lonely && getAge() == 0 && canFallInLove()) {
                return super.mobInteract(player, hand);
            }
            if (hurt || getHappiness() < MAX_HAPPINESS || isBaby()) {
                if (!level.isClientSide) {
                    feed(player, hand, stack, kibble ? FoodKind.KIBBLE : stack.is(species().tamingTreats) ? FoodKind.TREAT : FoodKind.FOOD);
                    if (food && lonely && !hurt && !isBaby() && getHappiness() < BunnylandConfig.COMMON.breedingHappiness.get()) {
                        player.displayClientMessage(Component.translatable("message.bunnyland.too_sad", getName()), true);
                    }
                }
                return InteractionResult.sidedSuccess(level.isClientSide);
            }
        }

        if (stack.isEmpty()) {
            if (!level.isClientSide) {
                if (player.isSecondaryUseActive()) pet(player);
                else toggleSit(player);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        return super.mobInteract(player, hand);
    }

    public enum FoodKind {
        FOOD(2.0F, 6), KIBBLE(3.0F, 8), TREAT(4.0F, 15);

        final float heal;
        final int happiness;

        FoodKind(float heal, int happiness) {
            this.heal = heal;
            this.happiness = happiness;
        }
    }

    private void tryTame(Player player, InteractionHand hand, ItemStack stack) {
        usePlayerItem(player, hand, stack);
        playAction("eat");
        playSound(ModSounds.PET_EAT.get(), 0.8F, getVoicePitch());
        setNapping(false);
        if (random.nextInt(species().tameOdds) == 0 && !Services.PLATFORM.tamingCancelled(this, player)) {
            tame(player);
            navigation.stop();
            setTarget(null);
            setOrderedToSit(false);
            setHappiness(65);
            level().broadcastEntityEvent(this, (byte) 7);
            playSound(ModSounds.PET_HAPPY.get(), 1.0F, 1.0F);
            if (player instanceof ServerPlayer sp) {
                JournalEvents.tamed(sp, this);
                sp.displayClientMessage(Component.translatable("message.bunnyland.tamed", getName()), true);
            }
        } else {
            level().broadcastEntityEvent(this, (byte) 6);
        }
    }

    public void feed(Player player, InteractionHand hand, ItemStack stack, FoodKind kind) {
        heal(kind.heal);
        addHappiness(kind.happiness);
        if (isBaby()) ageUp(AgeableMob.getSpeedUpSecondsWhenFeeding(-getAge()), true);
        usePlayerItem(player, hand, stack);
        setNapping(false);
        playAction("eat");
        playSound(ModSounds.PET_EAT.get(), 0.8F, getVoicePitch());
        gameEvent(GameEvent.EAT, this);
    }

    /** Eating a portion from a Feeding Bowl. */
    public void eatFromBowl() {
        heal(3.0F);
        addHappiness(8);
        eatCooldown = 1200;
        playAction("eat");
        playSound(ModSounds.PET_EAT.get(), 0.8F, getVoicePitch());
        gameEvent(GameEvent.EAT, this);
    }

    public boolean isReadyToEat() {
        return eatCooldown <= 0 && (getHealth() < getMaxHealth() || getHappiness() < 80);
    }

    public void pet(Player player) {
        setNapping(false);
        playAction("happy");
        playSound(voiceHappy(), 1.0F, getVoicePitch());
        if (petCooldown <= 0) {
            addHappiness(8);
            petCooldown = 600;
            onPetted(player);
        }
        serverParticles(ParticleTypes.HEART, 3, 0.3D);
        player.displayClientMessage(Component.translatable("message.bunnyland.mood", getName(), getMood().displayName(),
                getHappiness()), true);
    }

    /** Called when petting actually cheered the pet up (not on cooldown). */
    protected void onPetted(Player player) {
    }

    private void toggleSit(Player player) {
        boolean sit = !isOrderedToSit();
        setOrderedToSit(sit);
        setNapping(false);
        jumping = false;
        navigation.stop();
        setTarget(null);
        player.displayClientMessage(Component.translatable(sit ? "message.bunnyland.sitting" : "message.bunnyland.following", getName()), true);
    }

    /** Playtime with a toy. Returns false if the pet is still tired from the last game. */
    public boolean tryPlay(Player player, boolean favourite, boolean direct) {
        if (playCooldown > 0) {
            if (direct) player.displayClientMessage(Component.translatable("message.bunnyland.toy_tired", getName()), true);
            return false;
        }
        playCooldown = 200;
        setNapping(false);
        addHappiness(favourite ? 18 : 10);
        playAction(favourite && random.nextBoolean() ? "happy" : "play");
        serverParticles(favourite ? ParticleTypes.HEART : ModParticles.SPARKLE.get(), favourite ? 4 : 6, 0.35D);
        return true;
    }

    public void onDressedUp(Player player) {
        addHappiness(3);
        playAction("happy");
        serverParticles(ModParticles.SPARKLE.get(), 8, 0.4D);
        player.displayClientMessage(Component.translatable("message.bunnyland.dressed", getName()), true);
    }

    private void removeOneCosmetic(Player player) {
        Component what;
        if (getAccessory() != Accessory.NONE) {
            what = getAccessory().displayName();
            if (getAccessory().item() != null) spawnAtLocation(getAccessory().item());
            setAccessory(Accessory.NONE);
        } else if (hasBow()) {
            what = Component.translatable("accessory.bunnyland.bow");
            spawnAtLocation(((DyeableCosmeticItem) ModItems.PET_BOW.get()).withColor(getBowColor()));
            setBowColor(NO_COLOR);
        } else {
            what = Component.translatable("accessory.bunnyland.collar");
            spawnAtLocation(((DyeableCosmeticItem) ModItems.PET_COLLAR.get()).withColor(getCollarColor()));
            setCollarColor(NO_COLOR);
        }
        level().playSound(null, this, SoundEvents.SHEEP_SHEAR, SoundSource.PLAYERS, 0.6F, 1.4F);
        player.displayClientMessage(Component.translatable("message.bunnyland.undressed", getName(), what), true);
    }

    public void showStatus(ServerPlayer player) {
        Component species = species().displayName();
        Component variant = species().variantDisplayName(getVariant());
        if (isTame()) {
            player.displayClientMessage(Component.translatable("message.bunnyland.status", getName(), species, variant,
                    getHappiness()), true);
        } else {
            player.displayClientMessage(Component.translatable("message.bunnyland.status_wild", species, variant), true);
        }
    }

    /** Plays one of the one-shot animations (eat, happy, play, special) for everyone watching. */
    public void playAction(String animation) {
        if (!level().isClientSide) triggerAnim(ACTION_CONTROLLER, animation);
    }

    // ------------------------------------------------------------------ breeding

    @Override
    public boolean isFood(ItemStack stack) {
        return stack.is(species().breedingFood);
    }

    @Override
    public boolean canMate(Animal other) {
        if (!super.canMate(other) || !(other instanceof BunnylandAnimal mate)) return false;
        if (isOrderedToSit() || mate.isOrderedToSit()) return false;
        int needed = BunnylandConfig.COMMON.breedingHappiness.get();
        return (!isTame() || getHappiness() >= needed) && (!mate.isTame() || mate.getHappiness() >= needed);
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob mate) {
        Entity created = getType().create(level);
        if (!(created instanceof BunnylandAnimal baby)) return null;
        BunnylandAnimal other = mate instanceof BunnylandAnimal m ? m : this;
        double chance = BunnylandConfig.COMMON.rareOffspringChance.get();
        if (getMood() == Mood.OVERJOYED && other.getMood() == Mood.OVERJOYED) chance *= 2.0D;
        baby.setVariant(species().rollOffspringVariant(random, getVariant(), other.getVariant(), Math.min(1.0D, chance)));
        UUID owner = getOwnerUUID() != null ? getOwnerUUID() : other.getOwnerUUID();
        if (owner != null) {
            baby.setOwnerUUID(owner);
            baby.setTame(true);
            baby.setHappiness(75);
        }
        if (baby.isRareVariant()) {
            ServerPlayer cause = getLoveCause() != null ? getLoveCause() : other.getLoveCause();
            if (cause != null) JournalEvents.seeVariant(cause, species(), baby.getVariant());
            if (owner != null && level.getPlayerByUUID(owner) instanceof ServerPlayer sp && sp != cause) {
                JournalEvents.seeVariant(sp, species(), baby.getVariant());
            }
            level.sendParticles(ModParticles.SPARKLE.get(), getX(), getY() + 0.5D, getZ(), 20, 0.5D, 0.4D, 0.5D, 0.05D);
        }
        return baby;
    }

    // ------------------------------------------------------------------ spawning

    private static class VariantGroup extends AgeableMob.AgeableMobGroupData {
        final int variant;

        VariantGroup(int variant) {
            super(0.15F);
            this.variant = variant;
        }
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        @Nullable SpawnGroupData data, @Nullable CompoundTag tag) {
        int variant;
        if (data instanceof VariantGroup group && random.nextFloat() < 0.75F) {
            variant = group.variant;
        } else {
            variant = species().randomCommonVariant(random);
            if (random.nextDouble() < BunnylandConfig.COMMON.naturalRareChance.get()) variant = species().randomRareVariant(random);
        }
        if (data == null) data = new VariantGroup(variant);
        setVariant(variant);
        setHappiness(50);
        return super.finalizeSpawn(level, difficulty, reason, data, tag);
    }

    @Override
    public boolean canBeLeashed(Player player) {
        return !isLeashed();
    }

    // ------------------------------------------------------------------ sounds

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return isNapping() ? null : ModSounds.voice(species()).ambient().get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.voice(species()).hurt().get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.voice(species()).death().get();
    }

    protected SoundEvent voiceHappy() {
        return ModSounds.voice(species()).happy().get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 220;
    }

    @Override
    public float getVoicePitch() {
        return species().voicePitch * (isBaby() ? 1.3F : 1.0F) + (random.nextFloat() - random.nextFloat()) * 0.12F;
    }

    @Override
    protected float getSoundVolume() {
        return switch (species()) {
            case RAINBOW_BUTTERFLY -> 0.4F;
            case STRAWBERRY_MOUSE, DREAMY_HAMSTER -> 0.6F;
            default -> 0.8F;
        };
    }

    // ------------------------------------------------------------------ animation

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "base", 4, this::baseState));
        controllers.add(new AnimationController<>(this, ACTION_CONTROLLER, 3, state -> PlayState.STOP)
                .triggerableAnim("eat", EAT)
                .triggerableAnim("happy", HAPPY)
                .triggerableAnim("play", PLAY)
                .triggerableAnim("special", SPECIAL));
    }

    private PlayState baseState(AnimationState<BunnylandAnimal> state) {
        return state.setAndContinue(baseAnimation(state.isMoving()));
    }

    /** Chooses the looping animation for the current pose. */
    protected RawAnimation baseAnimation(boolean moving) {
        if (isNapping()) return SLEEP;
        if (isInSittingPose()) return SIT;
        if (moving) return isRunning() ? RUN : WALK;
        return IDLE;
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}

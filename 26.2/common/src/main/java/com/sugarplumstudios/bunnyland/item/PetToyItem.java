package com.sugarplumstudios.bunnyland.item;

import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

import java.util.Set;

/**
 * Toys for playtime. Use one on a pet, or use it in the air to play with every pet of yours nearby.
 * Each species has favourite toys that make it extra happy.
 */
public class PetToyItem extends TooltipItem implements PetInteractable {
    public enum Kind {
        YARN_BALL(Set.of(Species.CLOUD_KITTY, Species.BLOSSOM_FOX, Species.HONEY_BEAR)),
        SQUEAKY_CARROT(Set.of(Species.COTTON_BUNNY, Species.STRAWBERRY_BUNNY, Species.MOON_BUNNY, Species.LAVENDER_BUNNY,
                Species.SNOWBALL_BUNNY, Species.DREAMY_HAMSTER, Species.STRAWBERRY_MOUSE)),
        FEATHER_WAND(Set.of(Species.CLOUD_KITTY, Species.CHERRY_BLOSSOM_BIRD, Species.RAINBOW_BUTTERFLY, Species.TINY_SWAN,
                Species.MOON_DEER, Species.PASTEL_AXOLOTL));

        public final Set<Species> favourites;

        Kind(Set<Species> favourites) {
            this.favourites = favourites;
        }
    }

    private final Kind kind;

    public PetToyItem(Kind kind, Properties properties) {
        super(properties);
        this.kind = kind;
    }

    public Kind kind() {
        return kind;
    }

    private SoundEvent sound() {
        return switch (kind) {
            case YARN_BALL -> SoundEvents.WOOL_HIT;
            case SQUEAKY_CARROT -> ModSounds.SQUEAKY_CARROT.get();
            case FEATHER_WAND -> SoundEvents.PARROT_FLY;
        };
    }

    @Override
    public InteractionResult interactWithPet(BunnylandAnimal pet, Player player, InteractionHand hand, ItemStack stack) {
        if (!pet.isTame() || !pet.isOwnedBy(player)) return InteractionResult.PASS;
        if (!player.level().isClientSide()) {
            player.level().playSound(null, pet, sound(), SoundSource.PLAYERS, 0.8F, 1.0F + pet.getRandom().nextFloat() * 0.2F);
            if (pet.tryPlay(player, kind.favourites.contains(pet.species()), true)) {
                stack.hurtAndBreak(1, player, hand.asEquipmentSlot());
            }
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide()) {
            level.playSound(null, player, sound(), SoundSource.PLAYERS, 0.8F, 1.0F + level.getRandom().nextFloat() * 0.2F);
            int played = 0;
            for (BunnylandAnimal pet : level.getEntitiesOfClass(BunnylandAnimal.class, player.getBoundingBox().inflate(8.0D),
                    p -> p.isOwnedBy(player) && !p.isOrderedToSit())) {
                if (pet.tryPlay(player, kind.favourites.contains(pet.species()), false)) played++;
            }
            if (played > 0) stack.hurtAndBreak(1, player, hand.asEquipmentSlot());
        }
        player.getCooldowns().addCooldown(stack, 20);
        return InteractionResult.SUCCESS;
    }
}

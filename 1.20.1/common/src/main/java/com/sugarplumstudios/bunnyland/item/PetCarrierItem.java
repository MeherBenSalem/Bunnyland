package com.sugarplumstudios.bunnyland.item;

import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.gameevent.GameEvent;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Carries one of your pets around safely. Use it on a pet to pick it up (everything about it is kept:
 * name, variant, happiness, cosmetics), then use it on a block to let it out again.
 */
public class PetCarrierItem extends Item implements PetInteractable {
    private static final String TAG_PET = "Pet";
    private static final String TAG_NAME = "PetName";
    private static final String TAG_SPECIES = "PetSpecies";
    private static final String TAG_VARIANT = "PetVariant";

    public PetCarrierItem(Properties properties) {
        super(properties);
    }

    public static boolean hasPet(ItemStack stack) {
        CompoundTag tag = stack.getTag();
        return tag != null && tag.contains(TAG_PET, 10);
    }

    @Override
    public InteractionResult interactWithPet(BunnylandAnimal pet, Player player, InteractionHand hand, ItemStack stack) {
        if (hasPet(stack)) return InteractionResult.PASS;
        Level level = player.level();
        if (!pet.isTame() || !pet.isOwnedBy(player)) {
            if (!level.isClientSide) player.displayClientMessage(Component.translatable("message.bunnyland.carrier_wrong_pet"), true);
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        if (pet.isPassenger() || pet.isVehicle()) {
            if (!level.isClientSide) player.displayClientMessage(Component.translatable("message.bunnyland.carrier_busy"), true);
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        if (!level.isClientSide) {
            if (pet.isLeashed()) pet.dropLeash(true, !player.getAbilities().instabuild);
            pet.setNapping(false);
            CompoundTag data = new CompoundTag();
            if (!pet.save(data)) return InteractionResult.PASS;
            CompoundTag tag = stack.getOrCreateTag();
            tag.put(TAG_PET, data);
            tag.putString(TAG_NAME, Component.Serializer.toJson(pet.getName()));
            tag.putString(TAG_SPECIES, pet.species().id);
            tag.putInt(TAG_VARIANT, pet.getVariant());
            level.playSound(null, pet, ModSounds.CARRIER_CAPTURE.get(), SoundSource.NEUTRAL, 1.0F, 1.0F);
            level.gameEvent(player, GameEvent.ENTITY_INTERACT, pet.position());
            pet.discard();
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        ItemStack stack = context.getItemInHand();
        if (!hasPet(stack)) return InteractionResult.PASS;
        Level level = context.getLevel();
        if (level instanceof ServerLevel server) {
            BlockPos clicked = context.getClickedPos();
            BlockPos pos = level.getBlockState(clicked).getCollisionShape(level, clicked).isEmpty()
                    ? clicked : clicked.relative(context.getClickedFace());
            if (context.getClickedFace() == Direction.DOWN) pos = pos.below();
            Optional<Entity> created = EntityType.create(stack.getTag().getCompound(TAG_PET), server);
            if (created.isEmpty()) return InteractionResult.FAIL;
            Entity pet = created.get();
            pet.setUUID(UUID.randomUUID());
            Player player = context.getPlayer();
            float yaw = player != null ? player.getYRot() + 180.0F : 0.0F;
            pet.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, yaw, 0.0F);
            pet.setYHeadRot(yaw);
            pet.setYBodyRot(yaw);
            pet.setDeltaMovement(0, 0, 0);
            pet.fallDistance = 0;
            server.addFreshEntity(pet);
            server.playSound(null, pos, ModSounds.CARRIER_RELEASE.get(), SoundSource.NEUTRAL, 1.0F, 1.0F);
            server.gameEvent(player, GameEvent.ENTITY_PLACE, pos);
            CompoundTag tag = stack.getTag();
            tag.remove(TAG_PET);
            tag.remove(TAG_NAME);
            tag.remove(TAG_SPECIES);
            tag.remove(TAG_VARIANT);
            if (tag.isEmpty()) stack.setTag(null);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        if (!hasPet(stack)) {
            tooltip.add(Component.translatable("tooltip.bunnyland.carrier.empty").withStyle(ChatFormatting.GRAY));
            return;
        }
        CompoundTag tag = stack.getTag();
        Component name = Component.Serializer.fromJson(tag.getString(TAG_NAME));
        tooltip.add(Component.translatable("tooltip.bunnyland.carrier.holding", name == null ? Component.literal("?") : name)
                .withStyle(ChatFormatting.LIGHT_PURPLE));
        Species species = Species.byId(tag.getString(TAG_SPECIES));
        if (species != null) {
            tooltip.add(Component.translatable("tooltip.bunnyland.carrier.details", species.displayName(),
                    species.variantDisplayName(tag.getInt(TAG_VARIANT))).withStyle(ChatFormatting.GRAY));
        }
        tooltip.add(Component.translatable("tooltip.bunnyland.carrier.release").withStyle(ChatFormatting.DARK_GRAY));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return false;
    }
}

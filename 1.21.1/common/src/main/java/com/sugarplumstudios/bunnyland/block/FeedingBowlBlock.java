package com.sugarplumstudios.bunnyland.block;

import net.minecraft.world.ItemInteractionResult;
import com.sugarplumstudios.bunnyland.registry.ModItems;
import com.sugarplumstudios.bunnyland.registry.ModSounds;
import com.sugarplumstudios.bunnyland.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Holds up to {@link #MAX_FOOD} portions of pet food. Tamed pets that are hungry or a little sad walk over
 * and eat a portion by themselves. Comparators read how full it is.
 */
public class FeedingBowlBlock extends Block {
    public static final int MAX_FOOD = 8;
    public static final IntegerProperty FOOD = IntegerProperty.create("food", 0, MAX_FOOD);
    private static final VoxelShape SHAPE = Block.box(3, 0, 3, 13, 4, 13);

    public FeedingBowlBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FOOD, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FOOD);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    protected boolean isPathfindable(BlockState state, PathComputationType type) {
        return false;
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        int food = state.getValue(FOOD);
        if (stack.is(ModTags.BOWL_FOOD)) {
            if (food >= MAX_FOOD) {
                if (!level.isClientSide) player.displayClientMessage(Component.translatable("message.bunnyland.bowl_full"), true);
                return ItemInteractionResult.sidedSuccess(level.isClientSide);
            }
            if (!level.isClientSide) {
                level.setBlock(pos, state.setValue(FOOD, food + 1), Block.UPDATE_ALL);
                level.playSound(null, pos, ModSounds.BOWL_FILL.get(), SoundSource.BLOCKS, 0.8F, 0.9F + level.random.nextFloat() * 0.2F);
                level.gameEvent(player, GameEvent.BLOCK_CHANGE, pos);
                if (!player.getAbilities().instabuild) stack.shrink(1);
                player.displayClientMessage(Component.translatable("message.bunnyland.bowl_level", food + 1, MAX_FOOD), true);
            }
            return ItemInteractionResult.sidedSuccess(level.isClientSide);
        }
        return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        int food = state.getValue(FOOD);
        if (!level.isClientSide) player.displayClientMessage(Component.translatable("message.bunnyland.bowl_level", food, MAX_FOOD), true);
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    /** Removes one portion. Returns false if the bowl was empty. */
    public static boolean eatPortion(Level level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (!(state.getBlock() instanceof FeedingBowlBlock) || state.getValue(FOOD) <= 0) return false;
        level.setBlock(pos, state.setValue(FOOD, state.getValue(FOOD) - 1), Block.UPDATE_ALL);
        if (level instanceof ServerLevel server) {
            server.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, new ItemStack(ModItems.PET_KIBBLE.get())),
                    pos.getX() + 0.5, pos.getY() + 0.3, pos.getZ() + 0.5, 6, 0.15, 0.05, 0.15, 0.05);
        }
        return true;
    }

    public static boolean hasFood(BlockState state) {
        return state.getBlock() instanceof FeedingBowlBlock && state.getValue(FOOD) > 0;
    }

    @Override
    @SuppressWarnings("deprecation")
    public boolean hasAnalogOutputSignal(BlockState state) {
        return true;
    }

    @Override
    @SuppressWarnings("deprecation")
    public int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        return Math.round(state.getValue(FOOD) * 15.0F / MAX_FOOD);
    }
}

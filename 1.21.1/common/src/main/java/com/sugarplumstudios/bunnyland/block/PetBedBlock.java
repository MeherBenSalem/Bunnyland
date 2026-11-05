package com.sugarplumstudios.bunnyland.block;

import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A cosy cushion. Tamed pets curl up on it to sleep, which makes them happier. */
public class PetBedBlock extends Block {
    /** Pets stand on the cushion; the rim is only decoration. */
    public static final double CUSHION_HEIGHT = 4.0 / 16.0;
    private static final VoxelShape OUTLINE = Block.box(1, 0, 1, 15, 6, 15);
    private static final VoxelShape COLLISION = Block.box(1, 0, 1, 15, 4, 15);

    public PetBedBlock(Properties properties) {
        super(properties);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return OUTLINE;
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return COLLISION;
    }

    @Override
    protected boolean isPathfindable(BlockState state, PathComputationType type) {
        return type == PathComputationType.LAND;
    }

    /** Whether another creature is already napping in this bed. */
    public static boolean isOccupied(Level level, BlockPos pos, BunnylandAnimal except) {
        return !level.getEntitiesOfClass(BunnylandAnimal.class, new AABB(pos).inflate(0.1D),
                a -> a != except && a.isNapping()).isEmpty();
    }
}

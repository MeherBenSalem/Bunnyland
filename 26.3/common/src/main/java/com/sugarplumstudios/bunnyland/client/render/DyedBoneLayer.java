package com.sugarplumstudios.bunnyland.client.render;

import com.geckolib.cache.model.GeoBone;
import com.geckolib.cache.model.cuboid.CuboidGeoBone;
import com.geckolib.cache.model.cuboid.GeoCube;
import com.geckolib.constant.dataticket.DataTicket;
import com.geckolib.renderer.GeoEntityRenderer;
import com.geckolib.renderer.base.RenderPassInfo;
import com.geckolib.renderer.layer.builtin.CustomBoneTextureGeoLayer;
import com.geckolib.util.RenderUtil;
import com.mojang.blaze3d.vertex.PoseStack;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import it.unimi.dsi.fastutil.ints.IntIntPair;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;

/** Draws one bone (the collar or the bow) in the dye colour stored in the render state. */
public class DyedBoneLayer<T extends BunnylandAnimal> extends CustomBoneTextureGeoLayer<T, Void, LivingEntityRenderState> {
    private final DataTicket<Integer> colour;

    public DyedBoneLayer(GeoEntityRenderer<T, LivingEntityRenderState> renderer, String bone, DataTicket<Integer> colour) {
        super(renderer, bone, Identifier.withDefaultNamespace("missingno"));
        this.colour = colour;
    }

    @Override
    public boolean shouldRenderBone(LivingEntityRenderState state) {
        return state.getOrDefaultGeckolibData(colour, -1) >= 0;
    }

    @Override
    protected Identifier getTextureResource(LivingEntityRenderState state) {
        return getRenderer().getTextureLocation(state);
    }

    @Override
    protected void renderBone(RenderPassInfo<LivingEntityRenderState> info, GeoBone bone, SubmitNodeCollector collector) {
        if (!(bone instanceof CuboidGeoBone cuboid)) return;
        LivingEntityRenderState state = info.renderState();
        Identifier texture = getTextureResource(state);
        IntIntPair size = RenderUtil.getTextureDimensions(texture);
        float width = size.firstInt();
        float height = size.secondInt();
        int light = info.packedLight();
        int overlay = info.packedOverlay();
        int tint = ARGB.multiply(info.renderColor(), 0xFF000000 | state.getOrDefaultGeckolibData(colour, 0xFFFFFF));
        collector.submitCustomGeometry(info.poseStack(), getRenderType(state, texture), (pose, buffer) -> {
            PoseStack stack = new PoseStack();
            stack.last().set(pose);
            bone.translateAwayFromPivotPoint(stack);
            for (GeoCube cube : cuboid.cubes) {
                stack.pushPose();
                renderCube(cube, stack, buffer, light, overlay, tint, width, height);
                stack.popPose();
            }
        });
    }
}

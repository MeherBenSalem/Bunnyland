package com.sugarplumstudios.bunnyland.client.render;

import net.minecraft.util.FastColor;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/** Renders every Bunnyland creature: baby proportions, dyed collars and bows, and the glow layer. */
public class CreatureRenderer<T extends BunnylandAnimal> extends GeoEntityRenderer<T> {
    public CreatureRenderer(EntityRendererProvider.Context context, Species species) {
        super(context, new CreatureModel<>(species));
        this.shadowRadius = species.shadowRadius;
        addRenderLayer(new CreatureGlowLayer<>(this));
    }

    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, T animatable, BakedGeoModel model,
                                    boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float baby = animatable.isBaby() ? 0.62F : 1.0F;
        super.scaleModelForRender(widthScale * baby, heightScale * baby, poseStack, animatable, model, isReRender, partialTick,
                packedLight, packedOverlay);
    }

    @Override
    public void renderRecursively(PoseStack poseStack, T animatable, GeoBone bone, RenderType renderType, MultiBufferSource bufferSource,
                                  VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay,
                                  int colour) {
        if (!isReRender) {
            String name = bone.getName();
            int dye = name.equals("collar") ? animatable.getCollarColor() : name.equals("bow") ? animatable.getBowColor() : -1;
            if (dye >= 0) colour = FastColor.ARGB32.multiply(colour, 0xFF000000 | dye);
        }
        super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender, partialTick, packedLight,
                packedOverlay, colour);
    }
}

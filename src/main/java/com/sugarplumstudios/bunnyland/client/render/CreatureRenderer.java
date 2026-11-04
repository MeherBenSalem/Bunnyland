package com.sugarplumstudios.bunnyland.client.render;

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
                                  float red, float green, float blue, float alpha) {
        if (!isReRender) {
            String name = bone.getName();
            int color = name.equals("collar") ? animatable.getCollarColor() : name.equals("bow") ? animatable.getBowColor() : -1;
            if (color >= 0) {
                red *= ((color >> 16) & 0xFF) / 255.0F;
                green *= ((color >> 8) & 0xFF) / 255.0F;
                blue *= (color & 0xFF) / 255.0F;
            }
        }
        super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender, partialTick, packedLight,
                packedOverlay, red, green, blue, alpha);
    }
}

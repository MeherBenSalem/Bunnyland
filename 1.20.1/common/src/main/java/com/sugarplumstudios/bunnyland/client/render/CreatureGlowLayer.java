package com.sugarplumstudios.bunnyland.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Full-bright markings (moon crescents, antlers, rare-variant sparkles). Only variants that ship a
 * {@code <variant>_glow.png} pay for the extra pass.
 */
public class CreatureGlowLayer<T extends BunnylandAnimal> extends GeoRenderLayer<T> {
    private static final Map<ResourceLocation, Boolean> HAS_GLOW = new ConcurrentHashMap<>();

    public CreatureGlowLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    public static void clearCache() {
        HAS_GLOW.clear();
    }

    @Override
    public void render(PoseStack poseStack, T animatable, BakedGeoModel bakedModel, RenderType renderType, MultiBufferSource bufferSource,
                       VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        if (animatable.isInvisible()) return;
        ResourceLocation texture = animatable.species().glowTexture(animatable.getVariant());
        boolean exists = HAS_GLOW.computeIfAbsent(texture, t -> Minecraft.getInstance().getResourceManager().getResource(t).isPresent());
        if (!exists) return;
        RenderType glow = RenderType.eyes(texture);
        getRenderer().reRender(bakedModel, poseStack, bufferSource, animatable, glow, bufferSource.getBuffer(glow), partialTick,
                0xF000F0, OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F);
    }
}

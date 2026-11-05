package com.sugarplumstudios.bunnyland.client.render;

import com.geckolib.renderer.GeoEntityRenderer;
import com.geckolib.renderer.base.RenderPassInfo;
import com.geckolib.renderer.layer.builtin.AutoGlowingGeoLayer;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.resources.Identifier;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Full-bright markings (moon crescents, antlers, rare-variant sparkles). Only variants that ship a
 * {@code <variant>_glow.png} pay for the extra pass.
 */
public class CreatureGlowLayer<T extends BunnylandAnimal> extends AutoGlowingGeoLayer<T, Void, LivingEntityRenderState> {
    private static final Map<Identifier, Boolean> HAS_GLOW = new ConcurrentHashMap<>();

    public CreatureGlowLayer(GeoEntityRenderer<T, LivingEntityRenderState> renderer) {
        super(renderer);
    }

    public static void clearCache() {
        HAS_GLOW.clear();
    }

    @Override
    protected Identifier getTextureResource(LivingEntityRenderState state) {
        Identifier base = getRenderer().getTextureLocation(state);
        String path = base.getPath();
        return base.withPath(path.substring(0, path.length() - ".png".length()) + "_glow.png");
    }

    @Override
    public void submitRenderTask(RenderPassInfo<LivingEntityRenderState> info, SubmitNodeCollector collector) {
        if (info.renderState().isInvisible) return;
        Identifier texture = getTextureResource(info.renderState());
        if (!HAS_GLOW.computeIfAbsent(texture, t -> Minecraft.getInstance().getResourceManager().getResource(t).isPresent())) return;
        super.submitRenderTask(info, collector);
    }
}

package com.sugarplumstudios.bunnyland.client.render;

import com.geckolib.renderer.GeoEntityRenderer;
import com.geckolib.renderer.base.BoneSnapshots;
import com.geckolib.renderer.base.RenderPassInfo;
import com.sugarplumstudios.bunnyland.creature.Accessory;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.util.Mth;

/** Renders every Bunnyland creature: baby proportions, cosmetics, blinks, head turns, dyed collars and bows, and the glow layer. */
public class CreatureRenderer<T extends BunnylandAnimal> extends GeoEntityRenderer<T, LivingEntityRenderState> {
    public CreatureRenderer(EntityRendererProvider.Context context, Species species) {
        super(context, new CreatureModel<>(species));
        this.shadowRadius = species.shadowRadius;
        withRenderLayer(new CreatureGlowLayer<>(this));
        withRenderLayer(new DyedBoneLayer<>(this, "collar", CreatureModel.COLLAR));
        withRenderLayer(new DyedBoneLayer<>(this, "bow", CreatureModel.BOW));
    }

    @Override
    public int getRenderColor(T animal, Void relatedObject, float partialTick) {
        return animal.journalSilhouette ? 0xFF524061 : super.getRenderColor(animal, relatedObject, partialTick);
    }

    @Override
    public void scaleModelForRender(RenderPassInfo<LivingEntityRenderState> info, float widthScale, float heightScale) {
        float baby = info.renderState().isBaby ? 0.62F : 1.0F;
        super.scaleModelForRender(info, widthScale * baby, heightScale * baby);
    }

    @Override
    public void adjustModelBonesForRender(RenderPassInfo<LivingEntityRenderState> info, BoneSnapshots bones) {
        LivingEntityRenderState state = info.renderState();
        show(bones, "collar", state.getOrDefaultGeckolibData(CreatureModel.COLLAR, -1) >= 0);
        show(bones, "collar_bell", state.getOrDefaultGeckolibData(CreatureModel.COLLAR, -1) >= 0);
        show(bones, "bow", state.getOrDefaultGeckolibData(CreatureModel.BOW, -1) >= 0);
        Accessory worn = Accessory.byOrdinal(state.getOrDefaultGeckolibData(CreatureModel.ACCESSORY, 0));
        for (Accessory a : Accessory.values()) {
            if (a != Accessory.NONE) show(bones, a.bone, worn == a);
        }
        show(bones, "headwear", !worn.isHat);
        show(bones, "eyelids", state.getOrDefaultGeckolibData(CreatureModel.EYES_CLOSED, false));

        boolean napping = state.getOrDefaultGeckolibData(CreatureModel.NAPPING, false);
        bones.ifPresent("look", look -> {
            if (napping) return;
            look.setRotX(-Mth.clamp(state.xRot, -40.0F, 40.0F) * Mth.DEG_TO_RAD);
            look.setRotY(-Mth.clamp(state.yRot, -60.0F, 60.0F) * Mth.DEG_TO_RAD);
        });
    }

    private static void show(BoneSnapshots bones, String bone, boolean visible) {
        bones.ifPresent(bone, b -> b.skipRender(!visible));
    }
}

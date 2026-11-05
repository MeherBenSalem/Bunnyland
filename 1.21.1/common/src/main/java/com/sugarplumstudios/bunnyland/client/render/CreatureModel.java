package com.sugarplumstudios.bunnyland.client.render;

import com.sugarplumstudios.bunnyland.creature.Accessory;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.model.data.EntityModelData;

/**
 * One model per species. Picks the variant texture, shows only the cosmetics the pet is wearing, closes
 * the eyes for blinks and naps, and turns the {@code look} bone towards what the creature is looking at.
 */
public class CreatureModel<T extends BunnylandAnimal> extends GeoModel<T> {
    private final Species species;

    public CreatureModel(Species species) {
        this.species = species;
    }

    @Override
    public ResourceLocation getModelResource(T animal) {
        return species.model();
    }

    @Override
    public ResourceLocation getTextureResource(T animal) {
        return species.texture(animal.getVariant());
    }

    @Override
    public ResourceLocation getAnimationResource(T animal) {
        return species.animation();
    }

    @Override
    public void setCustomAnimations(T animal, long instanceId, AnimationState<T> state) {
        super.setCustomAnimations(animal, instanceId, state);
        show("collar", animal.hasCollar());
        show("collar_bell", animal.hasCollar());
        show("bow", animal.hasBow());
        Accessory worn = animal.getAccessory();
        for (Accessory a : Accessory.values()) {
            if (a != Accessory.NONE) show(a.bone, worn == a);
        }
        show("headwear", !worn.isHat);

        boolean napping = animal.isNapping();
        long t = animal.tickCount + animal.getId() * 37L;
        show("eyelids", napping || t % 97 < 3 || t % 331 < 3);

        getBone("look").ifPresent(look -> {
            EntityModelData data = state.getData(DataTickets.ENTITY_MODEL_DATA);
            if (data == null || napping) {
                look.setRotX(0);
                look.setRotY(0);
                return;
            }
            look.setRotX(Mth.clamp(data.headPitch(), -40.0F, 40.0F) * Mth.DEG_TO_RAD);
            look.setRotY(Mth.clamp(data.netHeadYaw(), -60.0F, 60.0F) * Mth.DEG_TO_RAD);
        });
    }

    private void show(String bone, boolean visible) {
        getBone(bone).ifPresent(b -> b.setHidden(!visible));
    }
}

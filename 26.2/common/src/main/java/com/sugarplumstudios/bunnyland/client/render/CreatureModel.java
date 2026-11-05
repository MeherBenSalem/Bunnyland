package com.sugarplumstudios.bunnyland.client.render;

import com.geckolib.constant.dataticket.DataTicket;
import com.geckolib.model.GeoModel;
import com.geckolib.renderer.base.GeoRenderState;
import com.sugarplumstudios.bunnyland.creature.Species;
import com.sugarplumstudios.bunnyland.entity.BunnylandAnimal;
import net.minecraft.resources.Identifier;
import org.jspecify.annotations.Nullable;

/**
 * One model per species. GeckoLib 5 draws from a render state, so everything the renderer needs from the creature
 * (variant, cosmetics, naps and blinks) is copied into it here; {@link CreatureRenderer} then shows the right bones.
 */
public class CreatureModel<T extends BunnylandAnimal> extends GeoModel<T> {
    static final DataTicket<Integer> VARIANT = DataTicket.create("bunnyland_variant", Integer.class);
    static final DataTicket<Integer> COLLAR = DataTicket.create("bunnyland_collar", Integer.class);
    static final DataTicket<Integer> BOW = DataTicket.create("bunnyland_bow", Integer.class);
    static final DataTicket<Integer> ACCESSORY = DataTicket.create("bunnyland_accessory", Integer.class);
    static final DataTicket<Boolean> NAPPING = DataTicket.create("bunnyland_napping", Boolean.class);
    static final DataTicket<Boolean> EYES_CLOSED = DataTicket.create("bunnyland_eyes_closed", Boolean.class);
    static final DataTicket<Boolean> SILHOUETTE = DataTicket.create("bunnyland_silhouette", Boolean.class);

    private final Species species;

    public CreatureModel(Species species) {
        this.species = species;
    }

    @Override
    public void addAdditionalStateData(T animal, @Nullable Object relatedObject, GeoRenderState state) {
        state.addGeckolibData(VARIANT, animal.getVariant());
        state.addGeckolibData(COLLAR, animal.getCollarColor());
        state.addGeckolibData(BOW, animal.getBowColor());
        state.addGeckolibData(ACCESSORY, animal.getAccessory().ordinal());
        boolean napping = animal.isNapping();
        long t = animal.tickCount + animal.getId() * 37L;
        state.addGeckolibData(NAPPING, napping);
        state.addGeckolibData(EYES_CLOSED, napping || t % 97 < 3 || t % 331 < 3);
        state.addGeckolibData(SILHOUETTE, animal.journalSilhouette);
    }

    @Override
    public Identifier getModelResource(GeoRenderState state) {
        return species.model();
    }

    @Override
    public Identifier getTextureResource(GeoRenderState state) {
        return species.texture(state.getOrDefaultGeckolibData(VARIANT, 0));
    }

    @Override
    public Identifier getAnimationResource(T animal) {
        return species.animation();
    }

    Species species() {
        return species;
    }
}

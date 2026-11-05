package com.sugarplumstudios.bunnyland.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.util.RandomSource;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;

/** Twinkling sparkles and sleepy drifting Zzz's. */
public class BunnylandParticle extends SingleQuadParticle {
    public enum Kind {
        SPARKLE, ZZZ
    }

    private final SpriteSet sprites;
    private final Kind kind;
    private final float baseSize;
    private final float swayPhase;

    protected BunnylandParticle(ClientLevel level, double x, double y, double z, double xd, double yd, double zd,
                                SpriteSet sprites, Kind kind) {
        super(level, x, y, z, sprites.first());
        this.sprites = sprites;
        this.kind = kind;
        this.hasPhysics = false;
        this.swayPhase = random.nextFloat() * Mth.TWO_PI;
        if (kind == Kind.SPARKLE) {
            this.xd = xd + (random.nextDouble() - 0.5D) * 0.01D;
            this.yd = yd + 0.005D + random.nextDouble() * 0.008D;
            this.zd = zd + (random.nextDouble() - 0.5D) * 0.01D;
            this.lifetime = 16 + random.nextInt(14);
            this.baseSize = 0.08F + random.nextFloat() * 0.06F;
            this.friction = 0.9F;
        } else {
            this.xd = 0.004D;
            this.yd = 0.016D + random.nextDouble() * 0.008D;
            this.zd = 0.0D;
            this.lifetime = 40 + random.nextInt(20);
            this.baseSize = 0.1F + random.nextFloat() * 0.04F;
            this.friction = 0.98F;
        }
        this.quadSize = baseSize;
        setSpriteFromAge(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        if (removed) return;
        setSpriteFromAge(sprites);
        if (kind == Kind.ZZZ) xd += Mth.sin(age * 0.25F + swayPhase) * 0.0015D;
        float life = (float) age / lifetime;
        setAlpha(life > 0.7F ? 1.0F - (life - 0.7F) / 0.3F : 1.0F);
    }

    @Override
    public float getQuadSize(float partialTick) {
        float life = Mth.clamp((age + partialTick) / lifetime, 0.0F, 1.0F);
        return kind == Kind.SPARKLE ? baseSize * Mth.sin(life * Mth.PI) : baseSize * (0.6F + 0.6F * life);
    }

    @Override
    protected int getLightCoords(float partialTick) {
        return kind == Kind.SPARKLE ? 0xF000F0 : super.getLightCoords(partialTick);
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    public record Provider(SpriteSet sprites, Kind kind) implements ParticleProvider<SimpleParticleType> {
        @Override
        public Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                       double xd, double yd, double zd, RandomSource random) {
            return new BunnylandParticle(level, x, y, z, xd, yd, zd, sprites, kind);
        }
    }
}

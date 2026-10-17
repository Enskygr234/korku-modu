package com.korkumodu.client;

import com.korkumodu.KorkuModu;
import com.korkumodu.entity.Albasti;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.resources.ResourceLocation;

/** Uzun boylu, solgun, yüzü saçla örtülü; karanlıkta parlayan kırmızı gözler. */
public class AlbastiRenderer extends HumanoidMobRenderer<Albasti, HumanoidModel<Albasti>> {
	private static final ResourceLocation TEXTURE = KorkuModu.id("textures/entity/albasti.png");
	private static final RenderType EYES = RenderType.eyes(KorkuModu.id("textures/entity/albasti_eyes.png"));

	public AlbastiRenderer(EntityRendererProvider.Context ctx) {
		super(ctx, new HumanoidModel<>(ctx.bakeLayer(ModelLayers.ZOMBIE)), 0.4F);
		this.addLayer(new Eyes(this));
	}

	@Override
	public ResourceLocation getTextureLocation(Albasti entity) {
		return TEXTURE;
	}

	@Override
	protected void scale(Albasti entity, PoseStack pose, float partialTick) {
		pose.scale(1.12F, 1.12F, 1.12F);
	}

	static class Eyes extends EyesLayer<Albasti, HumanoidModel<Albasti>> {
		Eyes(RenderLayerParent<Albasti, HumanoidModel<Albasti>> parent) {
			super(parent);
		}

		@Override
		public RenderType renderType() {
			return EYES;
		}
	}
}

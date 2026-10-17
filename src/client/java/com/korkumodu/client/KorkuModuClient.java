package com.korkumodu.client;

import com.korkumodu.KorkuModu;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

public class KorkuModuClient implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		EntityRendererRegistry.register(KorkuModu.ALBASTI, AlbastiRenderer::new);
	}
}

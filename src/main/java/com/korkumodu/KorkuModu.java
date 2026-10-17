package com.korkumodu;

import com.korkumodu.entity.Albasti;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SpawnEggItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KorkuModu implements ModInitializer {
	public static final String MOD_ID = "korkumodu";
	public static final Logger LOG = LoggerFactory.getLogger(MOD_ID);

	public static ResourceLocation id(String path) {
		return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
	}

	// ---- Yaratıklar ----
	public static final EntityType<Albasti> ALBASTI = Registry.register(
			BuiltInRegistries.ENTITY_TYPE,
			id("albasti"),
			EntityType.Builder.of(Albasti::new, MobCategory.MONSTER)
					.sized(0.6F, 2.2F)
					.eyeHeight(2.0F)
					.clientTrackingRange(10)
					.build("albasti"));

	// ---- Eşyalar ----
	public static final Item NAZAR_BONCUGU = Registry.register(
			BuiltInRegistries.ITEM, id("nazar_boncugu"), new Item(new Item.Properties().stacksTo(1)));

	public static final Item ALBASTI_SPAWN_EGG = Registry.register(
			BuiltInRegistries.ITEM, id("albasti_spawn_egg"),
			new SpawnEggItem(ALBASTI, 0xE6E1D6, 0x7A0A0A, new Item.Properties()));

	public static final CreativeModeTab TAB = Registry.register(
			BuiltInRegistries.CREATIVE_MODE_TAB, id("korku"),
			FabricItemGroup.builder()
					.icon(() -> new ItemStack(NAZAR_BONCUGU))
					.title(Component.translatable("itemGroup.korkumodu"))
					.displayItems((params, output) -> {
						output.accept(NAZAR_BONCUGU);
						output.accept(ALBASTI_SPAWN_EGG);
					})
					.build());

	@Override
	public void onInitialize() {
		ModSounds.init();
		FabricDefaultAttributeRegistry.register(ALBASTI, Albasti.createAttributes());

		// Üst dünyada, karanlıkta, nadiren (zombi ağırlığı 100, bizimki 6)
		BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ALBASTI, 6, 1, 1);

		ServerTickEvents.END_WORLD_TICK.register(Atmosfer::tick);
		LOG.info("Korku Modu yüklendi. Arkana bakma.");
	}
}

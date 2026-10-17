package com.korkumodu;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.sounds.SoundEvent;

public final class ModSounds {
	public static final SoundEvent ALBASTI_AMBIENT = register("albasti.ambient");
	public static final SoundEvent ALBASTI_SCREAM = register("albasti.scream");
	public static final SoundEvent ALBASTI_HURT = register("albasti.hurt");
	public static final SoundEvent ALBASTI_DEATH = register("albasti.death");
	public static final SoundEvent FISILTI = register("fisilti");

	private static SoundEvent register(String name) {
		var id = KorkuModu.id(name);
		return Registry.register(BuiltInRegistries.SOUND_EVENT, id, SoundEvent.createVariableRangeEvent(id));
	}

	/** Sınıfın yüklenmesini (ve kayıtların yapılmasını) garanti eder. */
	public static void init() {}

	private ModSounds() {}
}

package com.korkumodu;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Gece ve mağaralarda, sadece o oyuncunun duyacağı ürkütücü olaylar:
 * arkadan ayak sesleri, uzaktan kapı vurma, kulağa fısıltı, tuhaf mesajlar.
 */
public final class Atmosfer {
	/** Saniyede bir kontrol; ortalama ~2 dakikada bir olay. */
	private static final int CHANCE_PER_SECOND = 120;

	private static final String[] MESAJLAR = {
			"arkana bakma",
			"seni görüyorum",
			"neden yalnızsın?",
			"o ses benim değildi",
			"burada değilsin. ama ben buradayım.",
			"ışığın sönmek üzere",
			"...",
			"Albastı uyandı",
	};

	/** Sıradaki ayak seslerinin zamanlaması (oyuncu başına). */
	private static final Map<UUID, int[]> adimlar = new HashMap<>();

	public static void tick(ServerLevel level) {
		if (level.dimension() != Level.OVERWORLD) return;
		long t = level.getGameTime();

		for (ServerPlayer p : level.players()) {
			if (p.isSpectator() || p.isCreative()) continue;

			// Sıradaki ayak sesi varsa çal (3 adım, giderek yaklaşan)
			int[] a = adimlar.get(p.getUUID());
			if (a != null && t % 8 == 0) {
				ayakSesi(p, a[0]);
				if (--a[0] <= 0) adimlar.remove(p.getUUID());
			}

			if (t % 20 != 0) continue;
			if (!korkuluAn(level, p)) continue;
			RandomSource r = p.getRandom();
			if (r.nextInt(CHANCE_PER_SECOND) != 0) continue;

			int olay = r.nextInt(10);
			if (olay < 4) {
				adimlar.put(p.getUUID(), new int[]{3});
			} else if (olay < 6) {
				calUzakta(p, SoundEvents.ZOMBIE_ATTACK_WOODEN_DOOR, 12, 0.5F, 0.8F);
			} else if (olay < 8) {
				calKulakta(p, ModSounds.FISILTI);
			} else if (olay < 9) {
				calHolder(p, SoundEvents.AMBIENT_CAVE, arkasi(p, 6), 0.9F, 1.0F);
			} else {
				String m = MESAJLAR[r.nextInt(MESAJLAR.length)];
				p.displayClientMessage(Component.literal(m).withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC), false);
			}
		}
	}

	/** Gece yüzeyde ya da gökyüzü görünmeyen derin yerlerde. */
	private static boolean korkuluAn(ServerLevel level, ServerPlayer p) {
		BlockPos pos = p.blockPosition();
		boolean yeraltı = pos.getY() < 50 && !level.canSeeSky(pos);
		return level.isNight() || yeraltı;
	}

	private static Vec3 arkasi(ServerPlayer p, double mesafe) {
		Vec3 bakis = p.getViewVector(1.0F);
		Vec3 geri = new Vec3(-bakis.x, 0, -bakis.z).normalize().scale(mesafe);
		return p.position().add(geri);
	}

	private static void ayakSesi(ServerPlayer p, int kalan) {
		// Her adımda biraz daha yakın: 6, 4.5, 3 blok arkada
		Vec3 pos = arkasi(p, 3 + kalan * 1.5);
		SoundEvent ses = p.getRandom().nextBoolean() ? SoundEvents.GRAVEL_STEP : SoundEvents.STONE_STEP;
		cal(p, ses, pos, 0.6F, 0.9F);
	}

	private static void calUzakta(ServerPlayer p, SoundEvent ses, double mesafe, float vol, float pitch) {
		double aci = p.getRandom().nextDouble() * Math.PI * 2;
		Vec3 pos = p.position().add(Math.cos(aci) * mesafe, 0, Math.sin(aci) * mesafe);
		cal(p, ses, pos, vol, pitch);
	}

	private static void calKulakta(ServerPlayer p, SoundEvent ses) {
		cal(p, ses, arkasi(p, 1.2).add(0, p.getEyeHeight(), 0), 0.7F, 1.0F);
	}

	private static void cal(ServerPlayer p, SoundEvent ses, Vec3 pos, float vol, float pitch) {
		calHolder(p, BuiltInRegistries.SOUND_EVENT.wrapAsHolder(ses), pos, vol, pitch);
	}

	private static void calHolder(ServerPlayer p, Holder<SoundEvent> ses, Vec3 pos, float vol, float pitch) {
		p.connection.send(new ClientboundSoundPacket(ses, SoundSource.AMBIENT, pos.x, pos.y, pos.z, vol, pitch, p.getRandom().nextLong()));
	}

	private Atmosfer() {}
}

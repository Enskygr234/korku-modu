package com.korkumodu.entity;

import com.korkumodu.KorkuModu;
import com.korkumodu.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Albastı: sadece ona bakmadığında hareket eder.
 * Bakınca donar. Yaklaştıkça etrafı kararır. Nazar boncuğu taşıyana dokunamaz.
 */
public class Albasti extends Monster {
	private static final EntityDataAccessor<Boolean> FROZEN =
			SynchedEntityData.defineId(Albasti.class, EntityDataSerializers.BOOLEAN);

	/** Bakış konisi: 1.0 tam merkez, 0.55 ≈ ekranın büyük kısmı. */
	private static final double LOOK_DOT = 0.55;
	private static final double WATCH_RANGE = 64.0;

	/** Bu oyuncular onu zaten "görmüş" sayılır; ilk bakışta çığlık atar. */
	private final Set<UUID> seenBy = new HashSet<>();

	public Albasti(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.xpReward = 15;
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 40.0)
				.add(Attributes.MOVEMENT_SPEED, 0.36)
				.add(Attributes.ATTACK_DAMAGE, 7.0)
				.add(Attributes.FOLLOW_RANGE, 48.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(FROZEN, false);
	}

	public boolean isFrozen() {
		return this.entityData.get(FROZEN);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, true) {
			@Override
			public boolean canUse() {
				return !isFrozen() && super.canUse();
			}

			@Override
			public boolean canContinueToUse() {
				return !isFrozen() && super.canContinueToUse();
			}
		});
		this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.6) {
			@Override
			public boolean canUse() {
				return !isFrozen() && super.canUse();
			}
		});
		this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(
				this, Player.class, 10, false, false, p -> !hasNazar(p)));
	}

	public static boolean hasNazar(LivingEntity entity) {
		return entity instanceof Player p && p.getInventory().contains(new ItemStack(KorkuModu.NAZAR_BONCUGU));
	}

	/** Herhangi bir oyuncu şu an ona bakıyor mu? */
	private Player findWatcher() {
		Player closest = null;
		double best = Double.MAX_VALUE;
		for (Player p : this.level().players()) {
			if (p.isSpectator() || !p.isAlive()) continue;
			double d2 = this.distanceToSqr(p);
			if (d2 > WATCH_RANGE * WATCH_RANGE) continue;
			Vec3 look = p.getViewVector(1.0F).normalize();
			Vec3 to = new Vec3(this.getX() - p.getX(), this.getEyeY() - p.getEyeY(), this.getZ() - p.getZ()).normalize();
			if (look.dot(to) > LOOK_DOT && p.hasLineOfSight(this) && d2 < best) {
				best = d2;
				closest = p;
			}
		}
		return closest;
	}

	@Override
	public void aiStep() {
		if (!this.level().isClientSide) {
			Player watcher = findWatcher();
			boolean frozen = watcher != null;
			this.entityData.set(FROZEN, frozen);

			if (frozen) {
				this.getNavigation().stop();
				Vec3 v = this.getDeltaMovement();
				this.setDeltaMovement(0, Math.min(v.y, 0), 0);

				// İlk kez yakından görülünce çığlık
				if (watcher instanceof ServerPlayer sp && !seenBy.contains(sp.getUUID()) && this.distanceToSqr(sp) < 8 * 8) {
					seenBy.add(sp.getUUID());
					playTo(sp, ModSounds.ALBASTI_SCREAM, 1.0F);
					sp.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0, false, false));
				}

				// Nazar boncuğu taşıyan bakarsa yakındaysa dağılıp kaybolur
				if (hasNazar(watcher) && this.distanceToSqr(watcher) < 6 * 6) {
					vanish();
					return;
				}
			}

			// Karanlık aurası: her 2 saniyede bir yakındaki oyuncuların ekranı kararır
			if (this.tickCount % 40 == 0) {
				for (Player p : this.level().players()) {
					if (!p.isSpectator() && !hasNazar(p) && this.distanceToSqr(p) < 20 * 20) {
						p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 80, 0, false, false));
					}
				}
			}
		}

		if (isFrozen()) {
			// Donukken yürüme animasyonu da dursun, kafası da dönmesin
			this.yHeadRot = this.yHeadRotO;
			this.setYRot(this.yRotO);
			this.yBodyRot = this.yBodyRotO;
		}
		super.aiStep();
	}

	@Override
	public void travel(Vec3 input) {
		if (isFrozen()) {
			super.travel(Vec3.ZERO);
		} else {
			super.travel(input);
		}
	}

	@Override
	public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
		if (isFrozen()) return false;
		return super.doHurtTarget(target);
	}

	private void vanish() {
		if (this.level() instanceof ServerLevel sl) {
			sl.sendParticles(ParticleTypes.LARGE_SMOKE, getX(), getY() + 1.1, getZ(), 40, 0.3, 0.6, 0.3, 0.02);
			sl.playSound(null, blockPosition(), ModSounds.ALBASTI_DEATH, SoundSource.HOSTILE, 1.0F, 1.3F);
		}
		this.discard();
	}

	private void playTo(ServerPlayer player, SoundEvent sound, float volume) {
		player.connection.send(new ClientboundSoundPacket(
				BuiltInRegistries.SOUND_EVENT.wrapAsHolder(sound), SoundSource.HOSTILE,
				getX(), getY(), getZ(), volume, 0.9F + random.nextFloat() * 0.2F, random.nextLong()));
	}

	// ---- Doğma: sadece karanlıkta, sağlam zemin üstünde ----
	@Override
	public boolean checkSpawnRules(LevelAccessor level, MobSpawnType reason) {
		if (reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) {
			BlockPos below = this.blockPosition().below();
			if (!level.getBlockState(below).isValidSpawn(level, below, this.getType())) return false;
			if (!(level instanceof ServerLevelAccessor sla) || !Monster.isDarkEnoughToSpawn(sla, this.blockPosition(), this.random)) {
				return false;
			}
		}
		return super.checkSpawnRules(level, reason);
	}

	// ---- Sesler ----
	@Override
	protected SoundEvent getAmbientSound() {
		return isFrozen() ? null : ModSounds.ALBASTI_AMBIENT;
	}

	@Override
	public int getAmbientSoundInterval() {
		return 200;
	}

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return ModSounds.ALBASTI_HURT;
	}

	@Override
	protected SoundEvent getDeathSound() {
		return ModSounds.ALBASTI_DEATH;
	}

	@Override
	protected float getSoundVolume() {
		return 0.8F;
	}
}

#!/usr/bin/env python3
"""Modun seslerini sıfırdan sentezler (numpy) ve .ogg'a çevirir (ffmpeg).
Çalıştır: python3 tools/sounds.py"""
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources", "assets", "korkumodu", "sounds")
rng = np.random.default_rng(13)


def t(sec):
    return np.arange(int(SR * sec)) / SR


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def bandpass(x, lo, hi):
    return lowpass(x, hi) - lowpass(x, lo)


def env(n, attack=0.05, release=0.3):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] = np.linspace(1, 0, r)
    return e


def norm(x, peak=0.85):
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def save(name, x):
    x = np.clip(norm(x), -1, 1)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:a", "libvorbis", "-q:a", "4",
                    os.path.join(OUT, name + ".ogg")], check=True)
    os.remove(path)


def whisper(sec, seed):
    """Anlaşılmaz fısıltı: hece hece açılıp kapanan, ünsüz sesli gürültü."""
    r = np.random.default_rng(seed)
    n = int(SR * sec)
    noise = r.standard_normal(n)
    hiss = bandpass(noise, 1800, 7000)          # 's' 'ş' sesleri
    breath = bandpass(noise, 300, 1400) * 0.5   # nefes
    # hece zarfı: düzensiz aralıklarla açılıp kapanır
    syl = np.zeros(n)
    pos = 0
    while pos < n:
        length = int(SR * r.uniform(0.08, 0.22))
        gap = int(SR * r.uniform(0.03, 0.15))
        end = min(n, pos + length)
        syl[pos:end] = np.hanning(end - pos) * r.uniform(0.4, 1.0)
        pos = end + gap
    x = (hiss + breath) * syl
    # hafif yankı
    d = int(SR * 0.09)
    x[d:] += 0.35 * x[:-d]
    return x * env(n, 0.1, 0.4)


save("fisilti1", whisper(2.2, 1))
save("fisilti2", whisper(1.7, 2))

# Çığlık: kayan perdeli, bozuk testere dalgası + tiz gürültü
tt = t(1.4)
f = 1150 * np.exp(-tt * 0.9) + 420
phase = 2 * np.pi * np.cumsum(f) / SR
vib = 1 + 0.03 * np.sin(2 * np.pi * 7 * tt)
saw = 2 * ((phase * vib / (2 * np.pi)) % 1) - 1
scream = np.tanh(3 * (saw + 0.6 * np.sin(phase * 2.01))) + 0.4 * bandpass(rng.standard_normal(len(tt)), 2500, 9000)
scream *= env(len(tt), 0.01, 0.6)
save("ciglik", scream)

# İnilti (canı yanınca): kısa, alçak, titreyen
tt = t(0.6)
f = 230 - 80 * tt
phase = 2 * np.pi * np.cumsum(f) / SR
moan = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3.02 * phase)
moan *= (1 + 0.4 * np.sin(2 * np.pi * 11 * tt)) * env(len(tt), 0.02, 0.3)
moan += 0.15 * bandpass(rng.standard_normal(len(tt)), 400, 3000) * env(len(tt), 0.01, 0.3)
save("inilti", moan)

# Dağılma (ölüm / nazarla kaybolma): yükselen tıslama + derinleşen uğultu
tt = t(2.0)
noise = rng.standard_normal(len(tt))
sweep = bandpass(noise, 800, 8000) * np.linspace(1, 0, len(tt)) ** 2
rumble = np.sin(2 * np.pi * np.cumsum(90 - 40 * tt) / SR) * np.linspace(1, 0, len(tt))
save("dagilma", (sweep + 0.8 * rumble) * env(len(tt), 0.005, 0.5))
print("sesler hazır")

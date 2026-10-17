#!/usr/bin/env python3
"""Korku Modu tanıtım fragmanı (1920x1080, 30 fps).
Kullanım: python3 tools/video_fragman.py CIKTI.mp4 OYUN_KAYDI.mp4 T0
  OYUN_KAYDI: GitHub'daki "Oyun içi çekim" iş akışının sahne.mp4 dosyası
  T0: kayıtta sahnenin başladığı saniye (Albastı'nın ilk göründüğü an)
Yazı kartları Pillow ile çizilir; oyun görüntüleri kayıttan kesilir; ses numpy ile kurulur."""
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SR = 1920, 1080, 30, 44100
OUT, GAME, T0 = sys.argv[1], sys.argv[2], float(sys.argv[3])
HERE = os.path.dirname(os.path.abspath(__file__))
SOUNDS = os.path.join(HERE, "..", "src", "main", "resources", "assets", "korkumodu", "sounds")
NAZAR_PNG = os.path.join(HERE, "..", "src", "main", "resources", "assets", "korkumodu", "textures", "item", "nazar_boncugu.png")

BONE = (233, 228, 216)
MUTED = (140, 134, 128)
BLOOD = (200, 24, 30)
FD = "/usr/share/fonts/opentype/inter/"
F_BIG = ImageFont.truetype(FD + "InterDisplay-Black.otf", 190)
F_H = ImageFont.truetype(FD + "InterDisplay-SemiBold.otf", 72)
F_S = ImageFont.truetype(FD + "Inter-Medium.otf", 40)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def col(c, k):
    return tuple(int(v * k) for v in c)


def eyes(img, cx, cy, size, k):
    if k <= 0:
        return
    glow = Image.new("RGB", (size * 8, size * 4))
    g = ImageDraw.Draw(glow)
    for ox in (size * 2, size * 5):
        g.rectangle([ox, size * 1.5, ox + size, size * 2.1], fill=col((255, 40, 30), k))
    comp = Image.blend(glow.filter(ImageFilter.GaussianBlur(size * 0.7)), glow, 0.5)
    img.paste(comp, (int(cx - size * 4), int(cy - size * 2)), Image.eval(comp.convert("L"), lambda v: min(255, v * 3)))


# ---------------------------------------------------------------- kartlar
# Her kart: (süre, çizim fonksiyonu(img, d, t, dur))

def card_text(lines, size_font=F_H, color=BONE, typewriter=False):
    def draw(img, d, t, dur):
        fade = min(ease(t / 0.8), ease((dur - t) / 0.6))
        y = H / 2 - (len(lines) - 1) * 50
        for i, line in enumerate(lines):
            s = line
            if typewriter:
                n = int(len(line) * max(0, min(1, (t - i * 1.4) / 1.2)))
                s = line[:n]
            d.text((W / 2, y + i * 100), s, font=size_font, fill=col(color, fade), anchor="mm")
    return draw


def card_title(img, d, t, dur):
    k = ease((t - 0.3) / 1.2)
    eyes(img, W / 2, 330, 44, k * (0.8 + 0.2 * math.sin(t * 9)))
    fade = ease((t - 0.9) / 0.5) * ease((dur - t) / 0.5)
    d.text((W / 2, 600), "Albastı", font=F_BIG, fill=col(BONE, fade), anchor="mm")


def card_nazar(img, d, t, dur):
    fade = min(ease(t / 0.6), ease((dur - t) / 0.5))
    size = int(260 + 60 * ease(t / dur))
    nz = Image.open(NAZAR_PNG).convert("RGBA").resize((size, size), Image.NEAREST)
    bg = Image.new("RGBA", nz.size, (0, 0, 0, 255))
    bg.alpha_composite(nz)
    bg = Image.eval(bg.convert("RGB"), lambda v: int(v * fade))
    img.paste(bg, (int(W / 2 - size / 2), int(H / 2 - size / 2 - 80)))
    d.text((W / 2, H / 2 + size / 2), "Seni sadece nazar korur.", font=F_H, fill=col(BONE, fade), anchor="mm")


def card_end(img, d, t, dur):
    eyes(img, W / 2, 300, 30, ease(t / 1.0) * (0.75 + 0.25 * math.sin(t * 6)))
    k1 = ease((t - 0.6) / 0.8)
    d.text((W / 2, 520), "Korku Modu", font=F_BIG, fill=col(BONE, k1), anchor="mm")
    k2 = ease((t - 1.6) / 0.8)
    d.text((W / 2, 660), "Minecraft 1.21.1, Fabric", font=F_S, fill=col(BLOOD, k2), anchor="mm")
    k3 = ease((t - 2.6) / 0.8)
    d.text((W / 2, 880), "github.com/Enskygr234/korku-modu", font=F_S, fill=col(MUTED, k3), anchor="mm")


# ---------------------------------------------------------------- kurgu
# ("kart", süre, fonksiyon) ya da ("oyun", başlangıç (T0'a göre), süre)
EDIT = [
    ("kart", 4.5, card_text(["Türk efsanelerinde,", "gece yalnız yürüyenleri bekleyen biri var."], typewriter=True)),
    ("kart", 3.5, card_title),
    ("oyun", 3.0, 2.0, 2.4),     # uzakta, fenerlerin arasında duruyor (yakınlaştırılmış)
    ("kart", 2.6, card_text(["Ona bakarsan donar."])),
    ("kart", 2.4, card_text(["Arkanı dönersen..."])),
    ("oyun", 5.2, 3.6, 1.0),     # arkanı döndün: fener, karanlık çöküyor
    ("oyun", 10.0, 3.0, 1.0),    # geri döndüğünde burnunun dibinde
    ("kart", 4.0, card_nazar),
    ("kart", 6.0, card_end),
]


def render_video(tmp):
    parts = []
    for i, item in enumerate(EDIT):
        out = os.path.join(tmp, f"p{i:02d}.mp4")
        if item[0] == "oyun":
            start, dur, z = T0 + item[1], item[2], item[3]
            crop = f"crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.62," if z > 1 else ""
            # kayıttan kes, 1080p'ye büyüt, hafif soğuk renk ve gren
            vf = (crop + "scale=1920:1080:flags=lanczos,eq=contrast=1.12:brightness=0.03:saturation=0.8,"
                  "colorbalance=bs=0.08:bm=0.04,noise=alls=7:allf=t,"
                  f"fade=t=in:st=0:d=0.15,fade=t=out:st={dur - 0.2}:d=0.2,fps={FPS}")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", GAME,
                            "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", out], check=True)
        else:
            dur = item[1]
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                   "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                   "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
            for f in range(int(dur * FPS)):
                img = Image.new("RGB", (W, H))
                if item[0] == "kart":
                    item[2](img, ImageDraw.Draw(img), f / FPS, dur)
                ff.stdin.write(img.tobytes())
            ff.stdin.close()
            ff.wait()
        parts.append(out)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in parts)
    video = os.path.join(tmp, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video], check=True)
    return video


# ---------------------------------------------------------------- ses

def load_ogg(name):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(SOUNDS, name + ".ogg"),
                          "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(clip))
    if i < len(buf):
        buf[i:j] += clip[: j - i] * gain


def heartbeat():
    t = np.arange(int(0.35 * SR)) / SR
    thump = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 18)
    out = np.zeros(int(0.9 * SR))
    place(out, thump, 0.0)
    place(out, thump * 0.7, 0.22)
    return out


def footstep(seed):
    r = np.random.default_rng(seed)
    n = int(0.12 * SR)
    x = r.standard_normal(n) * np.exp(-np.arange(n) / SR * 40)
    a = np.exp(-2 * np.pi * 900 / SR)
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y * 4


def boom():
    t = np.arange(int(2.5 * SR)) / SR
    return (np.sin(2 * np.pi * (45 - 10 * t) * t) * np.exp(-t * 1.6) + 0.3 * np.random.default_rng(9).standard_normal(len(t)) * np.exp(-t * 6)) * 0.9


def soundtrack(total):
    n = int(total * SR)
    t = np.arange(n) / SR
    mixb = (np.sin(2 * np.pi * 41 * t) * 0.5 + np.sin(2 * np.pi * 41.3 * t) * 0.4 + np.sin(2 * np.pi * 61.7 * t) * 0.15)
    mixb *= 0.25 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t))
    # kurgudaki kesim zamanları
    starts, acc = [], 0.0
    for item in EDIT:
        starts.append(acc)
        acc += item[2] if item[0] == "oyun" else item[1]
    whisper1, whisper2 = load_ogg("fisilti1"), load_ogg("fisilti2")
    scream, vanish = load_ogg("ciglik"), load_ogg("dagilma")
    place(mixb, whisper1, 0.4, 0.5)
    place(mixb, boom(), starts[1] + 0.3, 0.9)                   # başlık vuruşu
    for k in range(6):                                           # uzak çekimden itibaren kalp atışı
        place(mixb, heartbeat(), starts[2] + k * 0.85, 0.6)
    place(mixb, whisper2, starts[4] + 0.2, 0.45)
    for k in range(6):                                           # arkanı dönünce yaklaşan ayak sesleri
        place(mixb, footstep(k), starts[5] + 0.4 + k * 0.5, 0.35 + 0.15 * k)
    place(mixb, scream, starts[6] + 0.02, 1.0)                   # geri dönünce çığlık
    place(mixb, boom(), starts[6] + 0.02, 0.8)
    place(mixb, vanish, starts[7] + 2.2, 0.9)                  # nazar kartının sonunda dağılma sesi
    place(mixb, boom(), starts[8] + 0.5, 0.7)
    fade = int(1.0 * SR)
    mixb[-fade:] *= np.linspace(1, 0, fade)
    mixb /= np.max(np.abs(mixb)) + 1e-9
    return (mixb * 0.85 * 32767).astype(np.int16)


def main():
    total = sum(item[2] if item[0] == "oyun" else item[1] for item in EDIT)
    with tempfile.TemporaryDirectory() as tmp:
        video = render_video(tmp)
        wav = os.path.join(tmp, "a.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(soundtrack(total).tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", OUT], check=True)
    print("hazır:", OUT, f"{total:.1f} sn")


if __name__ == "__main__":
    main()

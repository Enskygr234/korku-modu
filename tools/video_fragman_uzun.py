#!/usr/bin/env python3
"""Korku Modu oynanış fragmanı (1920x1080, 30 fps, oyunun kendi sesiyle).
Kullanım: python3 tools/video_fragman_uzun.py CIKTI.mp4 OYNANIS.mp4
  OYNANIS: "Oyun içi çekim" iş akışının sahne.mp4 kaydı (görüntü + oyun sesi)."""
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SR = 1920, 1080, 30, 44100
OUT, GAME = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "src", "main", "resources", "assets", "korkumodu")
FD = "/usr/share/fonts/opentype/inter/"
BONE = (233, 228, 216)
MUTED = (140, 134, 128)
BLOOD = (200, 24, 30)
F_BIG = ImageFont.truetype(FD + "InterDisplay-Black.otf", 190)
F_H = ImageFont.truetype(FD + "InterDisplay-SemiBold.otf", 72)
F_S = ImageFont.truetype(FD + "Inter-Medium.otf", 40)
OVERLAY_FONT = FD + "InterDisplay-SemiBold.otf"


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


# ------------------------------------------------------------ kartlar

def card_lines(lines, typewriter=False, color=BONE):
    def draw(img, d, t, dur):
        fade = min(ease(t / 0.7), ease((dur - t) / 0.5))
        y0 = H / 2 - (len(lines) - 1) * 50
        for i, line in enumerate(lines):
            s = line
            if typewriter:
                s = line[: int(len(line) * max(0, min(1, (t - 0.3 - i * 1.1) / 0.9)))]
            d.text((W / 2, y0 + i * 100), s, font=F_H, fill=col(color, fade), anchor="mm")
    return draw


def card_title(img, d, t, dur):
    eyes(img, W / 2, 330, 44, ease((t - 0.2) / 1.0) * (0.8 + 0.2 * math.sin(t * 9)))
    fade = ease((t - 0.7) / 0.4) * ease((dur - t) / 0.4)
    d.text((W / 2, 600), "Albastı", font=F_BIG, fill=col(BONE, fade), anchor="mm")


def card_nazar(img, d, t, dur):
    fade = min(ease(t / 0.5), ease((dur - t) / 0.4))
    size = int(240 + 60 * ease(t / dur))
    nz = Image.open(os.path.join(RES, "textures", "item", "nazar_boncugu.png")).convert("RGBA").resize((size, size), Image.NEAREST)
    bg = Image.new("RGBA", nz.size, (0, 0, 0, 255))
    bg.alpha_composite(nz)
    img.paste(Image.eval(bg.convert("RGB"), lambda v: int(v * fade)), (int(W / 2 - size / 2), int(H / 2 - size / 2 - 80)))
    d.text((W / 2, H / 2 + size / 2 + 10), "Seni sadece nazar korur.", font=F_H, fill=col(BONE, fade), anchor="mm")


def card_features(img, d, t, dur):
    items = ["Albastı", "Nazar boncuğu", "Gecenin sesleri"]
    for i, s in enumerate(items):
        k = min(ease((t - 0.2 - i * 0.6) / 0.4), ease((dur - t) / 0.4))
        d.text((W / 2, H / 2 - 120 + i * 120), s, font=F_H, fill=col(BLOOD if i == 0 else BONE, k), anchor="mm")


def card_end(img, d, t, dur):
    eyes(img, W / 2, 300, 30, ease(t / 1.0) * (0.75 + 0.25 * math.sin(t * 6)))
    d.text((W / 2, 520), "Korku Modu", font=F_BIG, fill=col(BONE, ease((t - 0.6) / 0.8)), anchor="mm")
    d.text((W / 2, 660), "Minecraft 1.21.1, Fabric", font=F_S, fill=col(BLOOD, ease((t - 1.5) / 0.8)), anchor="mm")
    d.text((W / 2, 880), "github.com/Enskygr234/korku-modu", font=F_S, fill=col(MUTED, ease((t - 2.4) / 0.8)), anchor="mm")


# ------------------------------------------------------------ kurgu
# ("kart", süre, çizim, [efektler])  efekt: (ad, saniye, kazanç)
# ("oyun", başlangıç, süre, üst_yazı | None, oyun_sesi_kazancı)
EDIT = [
    ("kart", 4.2, card_lines(["Gece.", "Orman.", "Yalnızsın."], typewriter=True), [("fisilti1", 0.5, 0.6)]),
    ("oyun", 8.6, 2.6, None, 0.8),                        # yürüyüş, meşale elde
    ("oyun", 11.2, 3.4, "Ileride biri var.", 0.8),        # uzakta, ağaçların arasında
    ("kart", 3.0, card_title, [("boom", 0.25, 0.9)]),
    ("oyun", 12.6, 2.4, "Ona bakarsan donar.", 0.8),
    ("oyun", 15.0, 4.4, "Arkani donersen...", 0.9),       # arkanı dön, yürü, karanlık çöker
    ("oyun", 19.4, 3.6, None, 1.0),                        # geri dönüş: kırmızı gözler, çığlık
    ("oyun", 23.0, 5.6, None, 1.0),                        # kaç, karanlık, çığlık
    ("kart", 3.4, card_nazar, [("dagilma", 2.4, 0.8)]),
    ("oyun", 29.2, 6.0, None, 0.8),                        # nazar elde, sakinlik, "arkana bakma"
    ("kart", 3.2, card_features, [("boom", 0.2, 0.5)]),
    ("oyun", 40.0, 4.5, "Bu gece yalniz degilsin.", 0.7),
    ("kart", 6.0, card_end, [("boom", 0.5, 0.8)]),
]
# Türkçe karakterli üst yazılar (drawtext dosyadan okur, doğru yazımlar burada)
OVERLAY_TR = {
    "Ileride biri var.": "İleride biri var.",
    "Arkani donersen...": "Arkanı dönersen...",
    "Bu gece yalniz degilsin.": "Bu gece yalnız değilsin.",
}


def synth(name):
    t = np.arange(int(2.5 * SR)) / SR
    if name == "boom":
        return (np.sin(2 * np.pi * (45 - 10 * t) * t) * np.exp(-t * 1.6)
                + 0.3 * np.random.default_rng(9).standard_normal(len(t)) * np.exp(-t * 6)) * 0.9
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(RES, "sounds", name + ".ogg"),
                          "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def write_wav(path, mono):
    st = np.repeat(np.clip(mono, -1, 1)[:, None], 2, axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def card_segment(tmp, i, dur, draw, sfx):
    vid = os.path.join(tmp, f"c{i}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))):
        img = Image.new("RGB", (W, H))
        draw(img, ImageDraw.Draw(img), f / FPS, dur)
        ff.stdin.write(img.tobytes())
    ff.stdin.close()
    ff.wait()
    audio = np.zeros(int(dur * SR), np.float32)
    for name, at, gain in sfx:
        clip = synth(name) * gain
        a = int(at * SR)
        b = min(len(audio), a + len(clip))
        audio[a:b] += clip[: b - a]
    wav = os.path.join(tmp, f"c{i}.wav")
    write_wav(wav, audio)
    return vid, wav


def game_segment(tmp, i, start, dur, text, gain):
    out = os.path.join(tmp, f"g{i}.mp4")
    vf = "scale=1920:1080:flags=lanczos,eq=contrast=1.06:brightness=0.02,noise=alls=5:allf=t,"
    if text:
        tf = os.path.join(tmp, f"t{i}.txt")
        with open(tf, "w", encoding="utf-8") as fh:
            fh.write(OVERLAY_TR.get(text, text))
        a = f"if(lt(t,0.6),t/0.6,if(gt(t,{dur - 0.6}),({dur}-t)/0.6,1))"
        vf += (f"drawtext=fontfile={OVERLAY_FONT}:textfile={tf}:fontsize=66:fontcolor=0xE9E4D8:"
               f"shadowcolor=black@0.8:shadowx=0:shadowy=3:x=(w-text_w)/2:y=h*0.36:alpha='{a}',")
    vf += f"fade=t=in:st=0:d=0.12,fade=t=out:st={dur - 0.15}:d=0.15,fps={FPS}"
    af = f"volume={gain},afade=t=in:d=0.08,afade=t=out:st={dur - 0.12}:d=0.12,aresample={SR},aformat=channel_layouts=stereo"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", GAME,
                    "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "pcm_s16le", "-f", "matroska", out + ".mkv"], check=True)
    return out + ".mkv"


def music_bed(total):
    t = np.arange(int(total * SR)) / SR
    bed = np.sin(2 * np.pi * 41 * t) * 0.5 + np.sin(2 * np.pi * 41.3 * t) * 0.4 + np.sin(2 * np.pi * 61.7 * t) * 0.15
    bed *= 0.18 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * t))
    fade = int(1.5 * SR)
    bed[:fade] *= np.linspace(0, 1, fade)
    bed[-fade:] *= np.linspace(1, 0, fade)
    return bed


def main():
    with tempfile.TemporaryDirectory() as tmp:
        inputs = []
        total = 0.0
        for i, item in enumerate(EDIT):
            if item[0] == "kart":
                v, a = card_segment(tmp, i, item[1], item[2], item[3])
                seg = os.path.join(tmp, f"s{i}.mkv")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "pcm_s16le",
                                "-shortest", seg], check=True)
                total += item[1]
            else:
                seg = game_segment(tmp, i, item[1], item[2], item[3], item[4])
                total += item[2]
            inputs.append(seg)
        # birleştir (yeniden kodlayarak; zaman damgaları temiz olsun)
        args = ["ffmpeg", "-y", "-loglevel", "error"]
        for p in inputs:
            args += ["-i", p]
        n = len(inputs)
        fc = "".join(f"[{k}:v][{k}:a]" for k in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        joined = os.path.join(tmp, "joined.mkv")
        subprocess.run(args + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
                               "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", joined], check=True)
        bed = os.path.join(tmp, "bed.wav")
        write_wav(bed, music_bed(total + 1))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-i", bed, "-filter_complex",
                        "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                        OUT], check=True)
    print("hazır:", OUT, f"{total:.1f} sn")


if __name__ == "__main__":
    main()

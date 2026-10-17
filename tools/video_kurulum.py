#!/usr/bin/env python3
"""Korku Modu kurulum videosu (1920x1080, 30 fps, Türkçe).
Kullanım: python3 tools/video_kurulum.py CIKTI.mp4 [oyun_klibi.mp4]
Kareleri Pillow ile çizer, ffmpeg'e akıtır; sesi numpy ile sentezler."""
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "kurulum.mp4"
CLIP = sys.argv[2] if len(sys.argv) > 2 else None

# ---- palet ----
INK = (9, 8, 10)
PANEL = (24, 22, 26)
PANEL2 = (36, 33, 38)
LINE = (58, 54, 60)
BONE = (233, 228, 216)
MUTED = (150, 144, 138)
BLOOD = (196, 22, 28)
NAZAR = (70, 140, 230)
OK = (96, 190, 90)

FD = "/usr/share/fonts/opentype/inter/"
def font(name, size):
    return ImageFont.truetype(FD + name, size)

F_TITLE = font("InterDisplay-Black.otf", 150)
F_H1 = font("InterDisplay-Bold.otf", 84)
F_H2 = font("Inter-SemiBold.otf", 44)
F_BODY = font("Inter-Regular.otf", 38)
F_SMALL = font("Inter-Medium.otf", 30)
F_UI = font("Inter-Medium.otf", 30)
F_UIB = font("Inter-Bold.otf", 30)
F_MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 32)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


# ---- arka plan: hafif gren + köşe karartma (bir kere hesaplanır) ----
rng = np.random.default_rng(3)
grain = (rng.random((H, W)) * 10).astype(np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
vig = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
vig = np.clip(vig, 0.25, 1)
bg_arr = np.stack([(INK[i] + grain) * vig for i in range(3)], -1).astype(np.uint8)
BG = Image.fromarray(bg_arr, "RGB")


def text(d, xy, s, f, fill=BONE, anchor="la", alpha=1.0, base=INK):
    d.text(xy, s, font=f, fill=mix(base, fill, alpha), anchor=anchor)


def eyes(img, cx, cy, size, k):
    """Karanlıkta parlayan iki kırmızı göz (Albastı)."""
    if k <= 0:
        return
    glow = Image.new("RGB", (size * 8, size * 4), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    for ox in (size * 2, size * 5):
        g.rectangle([ox, size * 1.5, ox + size, size * 2.1], fill=mix((0, 0, 0), (255, 40, 30), k))
    blur = glow.filter(ImageFilter.GaussianBlur(size * 0.6))
    sharp = glow
    comp = Image.blend(blur, sharp, 0.5)
    img.paste(comp, (int(cx - size * 4), int(cy - size * 2)), Image.eval(comp.convert("L"), lambda v: min(255, v * 3)))


def step_header(d, n, total, title, t):
    k = ease(t / 0.6)
    text(d, (140, 120), f"Adım {n} / {total}", F_SMALL, BLOOD, alpha=k)
    text(d, (140 - 30 * (1 - k), 160), title, F_H1, BONE, alpha=k)


def panel(d, box, fill=PANEL, r=18):
    d.rounded_rectangle(box, r, fill=fill, outline=LINE, width=2)


def cursor(d, x, y, click=0.0):
    if click > 0:
        rr = 20 + 40 * click
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=mix(INK, BONE, 1 - click), width=3)
    pts = [(x, y), (x, y + 44), (x + 11, y + 33), (x + 20, y + 52), (x + 28, y + 48), (x + 19, y + 30), (x + 33, y + 30)]
    d.polygon(pts, fill=BONE, outline=INK)


def move(t, t0, t1, a, b):
    k = ease((t - t0) / max(0.001, t1 - t0))
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def click_k(t, tc):
    return max(0.0, 1 - (t - tc) / 0.5) if t >= tc else 0.0


def note(d, s, t, t0=1.2, y=930):
    k = ease((t - t0) / 0.5)
    if k > 0:
        text(d, (140, y), s, F_BODY, MUTED, alpha=k)


def browser(d, box, url, k=1.0):
    x0, y0, x1, y1 = box
    panel(d, box, PANEL)
    d.rounded_rectangle([x0, y0, x1, y0 + 70], 18, fill=PANEL2)
    d.rectangle([x0, y0 + 40, x1, y0 + 70], fill=PANEL2)
    for i, c in enumerate([(200, 70, 70), (210, 170, 60), (90, 170, 90)]):
        d.ellipse([x0 + 24 + i * 30, y0 + 26, x0 + 42 + i * 30, y0 + 44], fill=c)
    d.rounded_rectangle([x0 + 140, y0 + 16, x1 - 30, y0 + 54], 19, fill=INK)
    text(d, (x0 + 165, y0 + 35), url, F_UI, BONE, anchor="lm")


def button(d, box, label, fill, ink=INK, hot=0.0):
    x0, y0, x1, y1 = box
    if hot > 0:
        d.rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], 14, outline=mix(INK, BONE, hot), width=3)
    d.rounded_rectangle(box, 10, fill=fill)
    text(d, ((x0 + x1) / 2, (y0 + y1) / 2), label, F_UIB, ink, anchor="mm")


def jarfile(d, x, y, name, k=1.0):
    d.rounded_rectangle([x, y, x + 64, y + 80], 8, fill=mix(INK, (190, 120, 50), k))
    d.polygon([(x + 44, y), (x + 64, y + 20), (x + 44, y + 20)], fill=mix(INK, (230, 170, 90), k))
    text(d, (x + 84, y + 40), name, F_UI, BONE, anchor="lm", alpha=k)


# ================================================================ sahneler

def s_title(img, d, t, dur):
    eyes(img, W / 2, 330, 40, ease((t - 0.6) / 1.4) * (0.75 + 0.25 * math.sin(t * 5)))
    k = ease((t - 1.6) / 0.8)
    text(d, (W / 2, 560), "Korku Modu", F_TITLE, BONE, anchor="mm", alpha=k)
    k2 = ease((t - 2.4) / 0.8)
    text(d, (W / 2, 680), "Kurulum rehberi", F_H2, MUTED, anchor="mm", alpha=k2)
    text(d, (W / 2, 740), "Minecraft Java 1.21.1, Fabric", F_SMALL, BLOOD, anchor="mm", alpha=k2)


def s_needs(img, d, t, dur):
    k = ease(t / 0.6)
    text(d, (140, 140), "Neler lazım?", F_H1, BONE, alpha=k)
    rows = [
        ("Minecraft Java Sürümü", "Satın alınmış, resmi launcher ile"),
        ("Fabric Loader", "Modları çalıştıran yükleyici, ücretsiz"),
        ("Fabric API", "Çoğu Fabric modunun ihtiyaç duyduğu kütüphane"),
        ("Korku Modu", "korku-modu-1.21.1.jar"),
    ]
    for i, (a, b) in enumerate(rows):
        kk = ease((t - 0.8 - i * 0.45) / 0.5)
        y = 330 + i * 150
        if kk <= 0:
            continue
        d.rounded_rectangle([140, y, 1780, y + 120], 16, fill=mix(INK, PANEL, kk), outline=mix(INK, LINE, kk), width=2)
        d.ellipse([180, y + 40, 220, y + 80], fill=mix(INK, BLOOD if i == 3 else NAZAR, kk))
        text(d, (260, y + 18), a, F_H2, BONE, alpha=kk, base=PANEL)
        text(d, (260, y + 72), b, F_SMALL, MUTED, alpha=kk, base=PANEL)
        if i in (1, 2):
            text(d, (1740, y + 60), "1.21.1 sürümünü seç", F_SMALL, BLOOD, anchor="rm", alpha=kk, base=PANEL)


def s_installer_dl(img, d, t, dur):
    step_header(d, 1, 6, "Fabric Installer'ı indir", t)
    k = ease((t - 0.4) / 0.6)
    box = (140, 330, 1780, 860)
    if k > 0:
        browser(d, box, "fabricmc.net/use/installer")
        text(d, (220, 470), "Fabric Installer", F_H1, BONE, base=PANEL)
        text(d, (220, 560), "Modlu Minecraft için yükleyici", F_BODY, MUTED, base=PANEL)
        hot = click_k(t, 3.6)
        button(d, (220, 650, 760, 740), "Download for Windows", NAZAR, BONE, hot)
        button(d, (800, 650, 1180, 740), "Download for macOS", PANEL2, BONE)
        cx, cy = move(t, 1.5, 3.4, (1500, 800), (480, 700))
        cursor(d, cx, cy, hot)
        if t > 4.0:
            kk = ease((t - 4.0) / 0.4)
            d.rounded_rectangle([1260, 760, 1740, 840], 12, fill=mix(PANEL, PANEL2, kk))
            text(d, (1290, 800), "fabric-installer.exe", F_UI, BONE, anchor="lm", alpha=kk, base=PANEL2)
    note(d, "Mac kullanıyorsan macOS sürümünü indir. Diğer adımlar aynı.", t, 4.6)


def s_installer_run(img, d, t, dur):
    step_header(d, 2, 6, "Installer'ı aç, 1.21.1 seç, kur", t)
    k = ease((t - 0.4) / 0.6)
    if k <= 0:
        return
    box = (360, 300, 1560, 900)
    panel(d, box, PANEL)
    text(d, (400, 345), "Fabric Installer", F_UIB, BONE, anchor="lm", base=PANEL)
    # sekmeler
    d.rounded_rectangle([400, 390, 560, 440], 8, fill=PANEL2)
    text(d, (480, 415), "Client", F_UIB, BONE, anchor="mm", base=PANEL2)
    text(d, (620, 415), "Server", F_UI, MUTED, anchor="mm", base=PANEL)
    rows = [("Minecraft Version", "1.21.1"), ("Loader Version", "en yenisi (varsayılan)"), ("Launcher Location", "C:\\Users\\Sen\\AppData\\Roaming\\.minecraft")]
    for i, (a, b) in enumerate(rows):
        y = 490 + i * 90
        text(d, (400, y + 25), a, F_UI, MUTED, anchor="lm", base=PANEL)
        hot = 0.0
        if i == 0:
            hot = 0.6 + 0.4 * math.sin(t * 6) if 2.4 < t < 5.0 else 0.0
        d.rounded_rectangle([760, y, 1510, y + 50], 8, fill=INK, outline=mix(LINE, BLOOD, hot), width=3 if hot else 2)
        val = b if (i != 0 or t > 2.6) else "26.3"
        text(d, (780, y + 25), val, F_UI if i else F_UIB, BONE if i == 0 else MUTED, anchor="lm")
    # profil kutusu
    d.rounded_rectangle([400, 760, 432, 792], 6, fill=OK)
    d.line([(408, 776), (415, 784), (426, 768)], fill=INK, width=4)
    text(d, (450, 776), "Create profile", F_UI, BONE, anchor="lm", base=PANEL)
    hot = click_k(t, 6.4)
    button(d, (1300, 790, 1510, 860), "Install", NAZAR, BONE, hot)
    if t < 2.6:
        cx, cy = move(t, 1.0, 2.2, (1700, 950), (1200, 515))
    else:
        cx, cy = move(t, 4.8, 6.2, (1200, 515), (1400, 820))
    cursor(d, cx, cy, click_k(t, 2.3) or hot)
    if t > 7.0:
        kk = ease((t - 7.0) / 0.4)
        d.rounded_rectangle([660, 520, 1260, 680], 16, fill=mix(PANEL, PANEL2, kk), outline=mix(PANEL, OK, kk), width=3)
        text(d, (960, 575), "Successfully installed", F_H2, OK, anchor="mm", alpha=kk, base=PANEL2)
        text(d, (960, 635), "Fabric Loader kuruldu", F_SMALL, MUTED, anchor="mm", alpha=kk, base=PANEL2)
    note(d, "Minecraft Version kutusundan mutlaka 1.21.1 seç.", t, 2.8, 960)


def s_fabric_api(img, d, t, dur):
    step_header(d, 3, 6, "Fabric API'yi indir", t)
    if t < 0.4:
        return
    browser(d, (140, 330, 1780, 880), "modrinth.com/mod/fabric-api/versions")
    text(d, (220, 470), "Fabric API", F_H1, BONE, base=PANEL)
    # filtre
    d.rounded_rectangle([220, 560, 520, 616], 10, fill=INK, outline=BLOOD if t > 1.8 else LINE, width=3)
    text(d, (245, 588), "Sürüm: 1.21.1", F_UI, BONE, anchor="lm")
    for i in range(3):
        y = 650 + i * 70
        name = ["fabric-api-0.116.x+1.21.1.jar", "fabric-api-0.115.x+1.21.1.jar", "fabric-api-0.114.x+1.21.1.jar"][i]
        d.rounded_rectangle([220, y, 1700, y + 56], 8, fill=PANEL2 if i == 0 else PANEL)
        text(d, (250, y + 28), name, F_MONO, BONE if i == 0 else MUTED, anchor="lm", base=PANEL2 if i == 0 else PANEL)
        if i == 0:
            button(d, (1490, y + 6, 1690, y + 50), "İndir", OK, INK, click_k(t, 4.0))
    cx, cy = move(t, 2.2, 3.8, (1000, 950), (1590, 678))
    cursor(d, cx, cy, click_k(t, 4.0))
    note(d, "Listenin en üstündeki 1.21.1 sürümü yeterli.", t, 4.4, 940)


def s_mod(img, d, t, dur):
    step_header(d, 4, 6, "Korku Modu'nu indir", t)
    if t < 0.4:
        return
    browser(d, (140, 330, 1780, 860), "github.com/Enskygr234/korku-modu/releases")
    text(d, (220, 460), "Korku Modu - son sürüm", F_H2, BONE, base=PANEL)
    text(d, (220, 520), "Minecraft 1.21.1, Fabric", F_SMALL, MUTED, base=PANEL)
    d.rounded_rectangle([220, 600, 1700, 670], 10, fill=PANEL2)
    jar_y = 603
    d.rounded_rectangle([240, jar_y + 12, 280, jar_y + 56], 6, fill=(190, 120, 50))
    text(d, (300, 635), "korku-modu-1.21.1.jar", F_MONO, BONE, anchor="lm", base=PANEL2)
    text(d, (1670, 635), "118 KB", F_SMALL, MUTED, anchor="rm", base=PANEL2)
    cx, cy = move(t, 1.2, 3.0, (1200, 950), (520, 640))
    cursor(d, cx, cy, click_k(t, 3.2))
    note(d, "İndirme linki modun GitHub sayfasında, \"Releases\" bölümünde.", t, 3.6, 940)


def s_mods_folder(img, d, t, dur):
    step_header(d, 5, 6, "İki .jar dosyasını mods klasörüne at", t)
    if t < 0.4:
        return
    # Win + R
    k = ease((t - 0.5) / 0.4)
    for i, key in enumerate(["Win", "R"]):
        x = 140 + i * 170
        d.rounded_rectangle([x, 320, x + 140, 400], 12, fill=mix(INK, PANEL2, k), outline=mix(INK, LINE, k), width=2)
        text(d, (x + 70, 360), key, F_H2, BONE, anchor="mm", alpha=k, base=PANEL2)
    text(d, (350 + 120, 360), "tuşlarına bas, şunu yaz:", F_BODY, MUTED, anchor="lm", alpha=k)
    typed = "%appdata%\\.minecraft"
    n = int(len(typed) * max(0, min(1, (t - 1.2) / 1.6)))
    d.rounded_rectangle([140, 430, 960, 500], 10, fill=INK, outline=LINE, width=2)
    text(d, (165, 465), typed[:n] + ("|" if int(t * 2) % 2 == 0 and t < 3.2 else ""), F_MONO, BONE, anchor="lm")
    if t > 3.4:
        kk = ease((t - 3.4) / 0.5)
        box = (140, 540, 1780, 900)
        d.rounded_rectangle(box, 18, fill=mix(INK, PANEL, kk), outline=mix(INK, LINE, kk), width=2)
        text(d, (180, 585), ".minecraft", F_UIB, BONE, anchor="lm", alpha=kk, base=PANEL)
        folders = ["mods", "saves", "versions", "resourcepacks"]
        for i, f in enumerate(folders):
            x = 200 + i * 260
            hot = f == "mods"
            col = (215, 170, 70) if hot else (140, 120, 80)
            d.rounded_rectangle([x, 640, x + 120, 730], 10, fill=mix(PANEL, col, kk))
            d.rounded_rectangle([x, 625, x + 50, 650], 6, fill=mix(PANEL, col, kk))
            text(d, (x + 60, 765), f, F_UIB if hot else F_UI, BONE if hot else MUTED, anchor="mm", alpha=kk, base=PANEL)
            if hot and t > 5.0:
                pulse = 0.5 + 0.5 * math.sin(t * 6)
                d.rounded_rectangle([x - 14, 612, x + 134, 790], 14, outline=mix(PANEL, BLOOD, pulse), width=3)
        # sürüklenen jar dosyaları
        if t > 5.4:
            for j, name in enumerate(["fabric-api-...jar", "korku-modu-1.21.1.jar"]):
                t0 = 5.6 + j * 1.2
                px, py = move(t, t0, t0 + 1.0, (1300, 620 + j * 110), (230, 660))
                if t < t0 + 1.0:
                    jarfile(d, px, py, name)
                    cursor(d, px + 40, py + 50)
            if t > 8.2:
                kk2 = ease((t - 8.2) / 0.4)
                text(d, (1260, 685), "2 dosya mods klasöründe", F_UIB, OK, anchor="lm", alpha=kk2, base=PANEL)
    note(d, "mods klasörü yoksa kendin oluştur: sağ tık, Yeni, Klasör, adı mods.", t, 5.0, 960)


def s_launcher(img, d, t, dur):
    step_header(d, 6, 6, "Launcher'da Fabric profiliyle oyna", t)
    if t < 0.4:
        return
    box = (140, 330, 1780, 880)
    panel(d, box, PANEL)
    # gece manzarası: tepeler, ağaçlar, ay
    d.rectangle([142, 332, 1778, 758], fill=(14, 16, 28))
    d.ellipse([1540, 380, 1610, 450], fill=(210, 210, 200))
    import random as _r
    rr = _r.Random(4)
    for x in range(142, 1778, 16):
        h = 120 + int(50 * math.sin(x / 140)) + rr.randint(0, 8)
        d.rectangle([x, 758 - h, x + 16, 758], fill=(22, 30, 24))
    for x in (300, 520, 980, 1300, 1650):
        d.rectangle([x, 560, x + 16, 640], fill=(40, 28, 20))
        d.polygon([(x - 40, 600), (x + 8, 470), (x + 56, 600)], fill=(16, 34, 22))
    text(d, (190, 380), "Minecraft: Java Edition", F_H2, BONE, base=(14, 16, 28))
    d.rectangle([142, 760, 1778, 878], fill=PANEL2)
    # profil seçici
    open_k = ease((t - 1.6) / 0.4) if t < 3.4 else 1 - ease((t - 3.4) / 0.3)
    d.rounded_rectangle([200, 785, 760, 855], 10, fill=INK, outline=LINE, width=2)
    sel = "fabric-loader-1.21.1" if t > 3.3 else "Son sürüm"
    text(d, (225, 820), sel, F_UIB if t > 3.3 else F_UI, BONE, anchor="lm")
    if open_k > 0.02:
        items = ["Son sürüm", "fabric-loader-1.21.1"]
        for i, it in enumerate(items):
            y = 785 - (i + 1) * 70 * open_k
            hot = i == 1
            d.rounded_rectangle([200, y, 760, y + 62], 8, fill=PANEL2 if hot else INK, outline=BLOOD if hot else LINE, width=2)
            text(d, (225, y + 31), it, F_UIB if hot else F_UI, BONE, anchor="lm")
    hot = click_k(t, 5.4)
    button(d, (820, 778, 1200, 862), "OYNA", OK, INK, hot)
    if t < 2.8:
        cx, cy = move(t, 0.8, 1.4, (1500, 500), (480, 820))
    elif t < 3.4:
        cx, cy = move(t, 2.8, 3.2, (480, 820), (480, 680))
    else:
        cx, cy = move(t, 4.2, 5.2, (480, 680), (1010, 820))
    cursor(d, cx, cy, click_k(t, 1.5) or click_k(t, 3.3) or hot)
    note(d, "Ana menünün sol altında \"Fabric (Modded)\" yazıyorsa kurulum tamam.", t, 6.0, 940)


def s_end(img, d, t, dur):
    eyes(img, W / 2, 380, 34, ease(t / 1.0) * (0.8 + 0.2 * math.sin(t * 7)))
    k = ease((t - 1.0) / 0.8)
    text(d, (W / 2, 600), "Kurulum tamam.", F_H1, BONE, anchor="mm", alpha=k)
    k2 = ease((t - 2.2) / 0.8)
    text(d, (W / 2, 700), "Geceyi bekle. Arkana bakma.", F_H2, BLOOD, anchor="mm", alpha=k2)
    k3 = ease((t - 3.4) / 0.8)
    text(d, (W / 2, 900), "github.com/Enskygr234/korku-modu", F_SMALL, MUTED, anchor="mm", alpha=k3)


SCENES = [(s_title, 5.0), (s_needs, 7.0), (s_installer_dl, 7.5), (s_installer_run, 9.5), (s_fabric_api, 7.0),
          (s_mod, 6.0), (s_mods_folder, 10.5), (s_launcher, 9.0), (s_end, 6.0)]


# ================================================================ ses

def soundtrack(total, clicks):
    sr = 44100
    n = int(total * sr)
    tt = np.arange(n) / sr
    drone = (np.sin(2 * np.pi * 55 * tt) * 0.35 + np.sin(2 * np.pi * 55.4 * tt) * 0.3 + np.sin(2 * np.pi * 82.5 * tt) * 0.12)
    drone *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * tt)
    noise = np.random.default_rng(1).standard_normal(n)
    a = np.exp(-2 * np.pi * 400 / sr)
    wind = np.zeros(n)
    acc = 0.0
    for i in range(0, n):
        acc = (1 - a) * noise[i] + a * acc
        wind[i] = acc
    wind *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tt + 1)) * 2.5
    mixd = drone * 0.5 + wind * 0.25
    for c in clicks:
        i0 = int(c * sr)
        m = int(0.03 * sr)
        if i0 + m < n:
            mixd[i0:i0 + m] += np.random.default_rng(int(c * 10)).standard_normal(m) * np.linspace(1, 0, m) * 0.6
    fade = int(1.5 * sr)
    mixd[:fade] *= np.linspace(0, 1, fade)
    mixd[-fade:] *= np.linspace(1, 0, fade)
    mixd /= np.max(np.abs(mixd)) + 1e-9
    return (mixd * 0.7 * 32767).astype(np.int16), sr


def main():
    total = sum(d for _, d in SCENES)
    with tempfile.TemporaryDirectory() as tmp:
        silent = os.path.join(tmp, "v.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                               "-crf", "20", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
        clicks = []
        start = 0.0
        for fn, dur in SCENES:
            frames = int(dur * FPS)
            for f in range(frames):
                t = f / FPS
                img = BG.copy()
                d = ImageDraw.Draw(img)
                fn(img, d, t, dur)
                # sahne geçişi: kısa karartma
                edge = min(t, dur - t)
                if edge < 0.35:
                    img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, edge / 0.35)
                ff.stdin.write(img.tobytes())
            start += dur
        ff.stdin.close()
        ff.wait()
        # tıklama sesleri (sahne başlangıçlarına göre yaklaşık)
        offs = {}
        acc = 0.0
        for fn, dur in SCENES:
            offs[fn.__name__] = acc
            acc += dur
        clicks = [offs["s_installer_dl"] + 3.6, offs["s_installer_run"] + 2.3, offs["s_installer_run"] + 6.4,
                  offs["s_fabric_api"] + 4.0, offs["s_mod"] + 3.2, offs["s_launcher"] + 1.5,
                  offs["s_launcher"] + 3.3, offs["s_launcher"] + 5.4]
        pcm, sr = soundtrack(total, clicks)
        wav = os.path.join(tmp, "a.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "160k", "-shortest", OUT], check=True)
    print("hazır:", OUT, f"{total:.1f} sn")


if __name__ == "__main__":
    main()

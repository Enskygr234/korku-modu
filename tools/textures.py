#!/usr/bin/env python3
"""Modun piksel dokularını üretir (Pillow). Çalıştır: python3 tools/textures.py"""
import os
import random
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources", "assets", "korkumodu")
random.seed(7)


def jitter(c, n=10):
    return tuple(max(0, min(255, v + random.randint(-n, n))) for v in c[:3]) + ((c[3],) if len(c) > 3 else (255,))


def fill(img, x0, y0, x1, y1, c, n=8):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), jitter(c, n))


# ------------------------------------------------------------- Albastı ----
SKIN = (214, 210, 200, 255)   # ölü, gri-beyaz ten
SKIN_D = (170, 166, 158, 255)
HAIR = (18, 16, 20, 255)
DRESS = (226, 222, 212, 255)  # eski beyaz elbise
DRESS_D = (150, 144, 132, 255)
EYE = (255, 30, 20, 255)

tex = Image.new("RGBA", (64, 64), (0, 0, 0, 0))

# Kafa (0,0): üst 8..16, alt 16..24 (y 0..8); yanlar y 8..16: sağ 0, ön 8, sol 16, arka 24
fill(tex, 8, 0, 16, 8, HAIR)          # üst
fill(tex, 16, 0, 24, 8, SKIN_D)       # alt (çene altı)
fill(tex, 0, 8, 8, 16, HAIR)          # sağ yan
fill(tex, 16, 8, 24, 16, HAIR)        # sol yan
fill(tex, 24, 8, 32, 16, HAIR)        # arka
fill(tex, 8, 8, 16, 16, SKIN)         # yüz
# yüz: göz çukurları ve ağız
for x, y in [(9, 11), (10, 11), (13, 11), (14, 11)]:
    tex.putpixel((x, y), (40, 10, 10, 255))
for x in range(10, 14):
    tex.putpixel((x, 14), (30, 8, 8, 255))
tex.putpixel((11, 15), (30, 8, 8, 255))
tex.putpixel((12, 15), (30, 8, 8, 255))
# saçın alnı örtmesi
fill(tex, 8, 8, 16, 10, HAIR)

# Şapka katmanı (32,0): saç tutamları yüzün önüne sarkıyor, arası boşluklu
fill(tex, 40, 0, 48, 8, HAIR)
for x0 in (32, 48, 56):
    fill(tex, x0, 8, x0 + 8, 16, HAIR)
front = [(40, 1), (41, 1), (42, 0), (45, 0), (46, 1), (47, 1)]  # (x, gap) -> ön perde
for x in range(40, 48):
    # gözlerin önü (x 41-42, 45-46) kısmen açık; yanlar tamamen saç
    open_rows = range(11, 13) if x in (41, 42, 45, 46) else range(0)
    for y in range(8, 16):
        if y in open_rows:
            continue
        if x in (43, 44) and y > 12:
            continue  # ağız aralığı
        tex.putpixel((x, y), jitter(HAIR, 6))

# Gövde (16,16): üst 20..28 (y16..20), alt 28..36; yanlar y20..32: sağ 16, ön 20, sol 28, arka 32
fill(tex, 20, 16, 28, 20, DRESS)
fill(tex, 28, 16, 36, 20, DRESS_D)
fill(tex, 16, 20, 20, 32, DRESS)
fill(tex, 20, 20, 28, 32, DRESS)
fill(tex, 28, 20, 32, 32, DRESS)
fill(tex, 32, 20, 40, 32, DRESS)
fill(tex, 32, 20, 40, 26, HAIR)  # sırtta uzun saç
# elbisede kir/yırtık izleri
for _ in range(14):
    tex.putpixel((random.randint(16, 39), random.randint(22, 31)), jitter(DRESS_D, 12))

# Kollar (40,16): üst 44..48, alt 48..52 (y16..20); yanlar y20..32: 40, ön 44, 48, arka 52
fill(tex, 44, 16, 48, 20, DRESS)
fill(tex, 48, 16, 52, 20, SKIN_D)
for x0 in (40, 44, 48, 52):
    fill(tex, x0, 20, x0 + 4, 26, DRESS)      # kol yeni
    fill(tex, x0, 26, x0 + 4, 32, SKIN)       # çıplak, solgun kol
fill(tex, 48, 16, 52, 20, (90, 40, 40, 255))  # uzun, kirli tırnaklar (el altı)

# Bacaklar (0,16): üst 4..8, alt 8..12; yanlar y20..32: 0, ön 4, 8, arka 12
fill(tex, 4, 16, 8, 20, DRESS)
fill(tex, 8, 16, 12, 20, SKIN_D)
for x0 in (0, 4, 8, 12):
    fill(tex, x0, 20, x0 + 4, 29, DRESS)      # etek
    fill(tex, x0, 29, x0 + 4, 32, SKIN_D)     # çıplak ayak

# Ters ayak (efsaneye göre Albastı'nın ayakları ters): ayağın arka yüzünde parmaklar
for x in (12, 14):
    tex.putpixel((x, 31), (120, 110, 100, 255))

tex.save(os.path.join(ROOT, "textures", "entity", "albasti.png"))

# Gözler katmanı: sadece göz pikselleri (karanlıkta parlar)
eyes = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
for x, y in [(9, 11), (10, 11), (13, 11), (14, 11)]:
    eyes.putpixel((x, y), EYE)
eyes.save(os.path.join(ROOT, "textures", "entity", "albasti_eyes.png"))

# --------------------------------------------------------- Nazar boncuğu --
nz = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
cx, cy = 7.5, 7.5
for y in range(16):
    for x in range(16):
        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if d <= 7.0:
            c = (20, 60, 170)        # koyu mavi dış halka
        else:
            continue
        if d <= 4.6:
            c = (245, 245, 250)      # beyaz
        if d <= 3.2:
            c = (90, 170, 235)       # açık mavi
        if d <= 1.6:
            c = (12, 12, 20)         # siyah göz bebeği
        if d > 6.3:
            c = (12, 40, 120)        # kenar gölgesi
        nz.putpixel((x, y), c + (255,))
# parlama
for p in [(5, 4), (4, 5), (5, 5)]:
    nz.putpixel(p, (200, 230, 255, 255))
# ip deliği
nz.putpixel((7, 0), (0, 0, 0, 0)); nz.putpixel((8, 0), (0, 0, 0, 0))
nz.save(os.path.join(ROOT, "textures", "item", "nazar_boncugu.png"))

# ------------------------------------------------------------- Mod ikonu --
icon = Image.new("RGBA", (16, 16), (6, 6, 10, 255))
for y in range(16):
    for x in range(16):
        if (x < 3 or x > 12) or y < 3:
            icon.putpixel((x, y), jitter(HAIR, 4))
# solgun yüz şeridi, saç arasından
for y in range(4, 16):
    for x in range(5, 11):
        if not (x in (7, 8) and y < 9):
            icon.putpixel((x, y), jitter((150, 146, 140, 255), 10))
for x, y in [(5, 7), (6, 7), (9, 7), (10, 7)]:
    icon.putpixel((x, y), EYE)
for x in range(6, 10):
    icon.putpixel((x, 11), (30, 8, 8, 255))
icon.resize((128, 128), Image.NEAREST).save(os.path.join(ROOT, "icon.png"))
print("dokular hazır")

# Korku Modu

Türk efsanelerinden korku modu. **Minecraft 1.21.1, Fabric.**

**İndir:** https://github.com/Enskygr234/korku-modu/releases/download/son-surum/korku-modu-1.21.1.jar

## İçindekiler

- **Albastı:** Gece ve karanlık mağaralarda nadiren ortaya çıkar. Sadece ona bakmadığında hareket eder; bakınca donar. Yakınındayken ekran kararır. İlk kez yakından gördüğünde çığlık atar.
- **Nazar Boncuğu:** Envanterinde taşırsan Albastı sana saldıramaz. Yakından bakarsan dağılıp kaybolur.
  Tarif: üstte mavi boya, ortada `mavi boya - cam - mavi boya`, altta ip.
- **Atmosfer:** Gece ya da derin mağaralarda arkandan yaklaşan ayak sesleri, uzaktan kapı vurma, kulağına fısıltı ve tuhaf mesajlar. Sadece sen duyarsın.

## Kurulum

1. [Fabric Loader](https://fabricmc.net/use/installer/) kur, sürüm olarak **1.21.1** seç.
2. [Fabric API](https://modrinth.com/mod/fabric-api) indir (1.21.1 sürümü).
3. Fabric API ve bu modun `.jar` dosyasını `.minecraft/mods` klasörüne at.
4. Launcher'da **fabric-loader-1.21.1** profilini seçip oyna.

## Geliştirme

- Dokular `tools/textures.py`, sesler `tools/sounds.py` ile üretilir.
- Kurulum videosu `tools/video_kurulum.py`, fragman `tools/video_fragman.py` ile üretilir. Fragmandaki oyun görüntüleri "Oyun içi çekim" iş akışının kaydından (`cekimler` dalı) gelir.
- `main` dalına her gönderimde GitHub Actions modu derleyip yukarıdaki linke koyar.

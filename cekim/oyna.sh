#!/usr/bin/env bash
# Oyunu gerçek klavye/fare girdisiyle oynatır. Zamanlar, veri paketindeki hazirla anına göre (saniye).
WIN="$1"
at() { local hedef=$1; local simdi; simdi=$(echo "$(date +%s.%N) - $T0" | bc); local kalan; kalan=$(echo "$hedef - $simdi" | bc); [ "$(echo "$kalan > 0" | bc)" = 1 ] && sleep "$kalan"; }
# Fareyi yumuşak çevir: toplam piksel, süre (sn). ~0.15 derece/piksel
bak() { local dx=$1 dy=${3:-0} sure=$2; local adim; adim=$(echo "$sure * 50 / 1" | bc); [ "$adim" -lt 1 ] && adim=1
  local px=$(( dx / adim )) py=$(( dy / adim ))
  for _ in $(seq 1 "$adim"); do xdotool mousemove_relative -- "$px" "$py"; sleep 0.02; done; }
bas() { xdotool keydown "$1"; }
birak() { xdotool keyup "$1"; }

xdotool windowfocus --sync "$WIN" 2>/dev/null || true
xdotool mousemove --window "$WIN" 640 360 click 3   # sağ tık: fareyi oyuna kilitle (meşale yere konmaz, havaya)
sleep 3                     # orman kurulsun, chunklar yüklensin
xdotool keydown space; sleep 0.25; xdotool keyup space   # zıpla: veri paketi sahneyi bu anda başlatır
T0=$(date +%s.%N)
echo "sahne basladi $T0"
at 0.8;  bak -180 1.0 40          # etrafa bakın
at 1.9;  bak 300 1.2 -40
at 3.0;  bak -120 0.6; bas w      # yürümeye başla
at 5.0;  bak 60 0.8
at 7.0;  birak w
at 7.6;  bak 140 1.2              # sağda bir şey... (ileride, sağda belirdi)
at 12.0; bak -1200 1.0            # arkanı dön
at 13.0; bas w
at 15.6; birak w
at 16.0; bak 1200 1.0             # geri dön: 7 blok arkanda
at 17.4; bas s
at 19.0; birak s
at 19.5; bak -1200 0.8; bas Control_L; bas w   # kaç
at 21.5; bak 80 0.4
at 22.6; bak -80 0.4
at 24.0; bak 1200 0.5             # dönüp bak: burnunun dibinde
at 25.4; xdotool keydown 3; sleep 0.15; xdotool keyup 3   # nazar boncuğu slotu
at 25.6; birak w; birak Control_L
at 27.5; bak -300 2.0 60          # sakinleş, etrafa bak
at 30.0; bak 500 2.5 -60
at 33.0; bas w
at 37.0; birak w

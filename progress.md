# Geliştirme Günlüğü — Bilgisayar Simülasyonu

> Sürüm: **SimOS 1.1** · Son güncelleme: **30.10.2026**
> Amaç: Windows 11 / macOS / GNOME görünümlü masaüstünü taklit eden,
> aralarında canlı geçiş yapılabilen bir Python masaüstü simülasyonu.

## Durum özeti

| Alan | Durum |
|---|---|
| Masaüstü, duvar kağıdı, simgeler | ✅ Tamam |
| 3 tema (win11 / macos / gnome) + canlı geçiş | ✅ Tamam |
| Panel / menü çubuğu / dock / başlat menüsü / sistem menüsü | ✅ Tamam |
| Pencereler (sürükle, odak, küçült, büyüt, kapat) | ✅ Tamam |
| Pencereleri kenardan/köşeden boyutlandırma | ✅ Tamam (1.1) |
| Panel ikonunda pencere önizlemesi | ✅ Tamam (1.1) |
| Tema tercihini hatırlama (`settings.json`) | ✅ Tamam (1.1) |
| 6 uygulama (Dosyalar, Notlar, Hesap, Terminal, Ayarlar, Hakkında) | ✅ Tamam |
| Açılış ekranı, canlı saat, tam ekran | ✅ Tamam |
| Otomatik testler | ✅ 9/9 geçiyor |
| Gerçek dosya kaydet/aç | ⬜ Yapılmadı (planlı) |
| Ekran görüntüsü ile görsel doğrulama | ⚠️ Ortam engeli (aşağıda) |

## Tamamlananlar

### Faz 1 — İskelet ve çizim katmanı
- `sim/draw.py`: yuvarlatılmış dikdörtgen (`rounded`, `rounded_top`), renk karıştırma
  (`mix`, `lighten`, `darken`, `hex_to_rgb`).
- `sim/themes.py`: `THEMES` sözlüğü; her tema için duvar kağıdı, pencere, panel ve dock
  tanımları; yazı tipi ailesi çözümleme (`_resolve_family`) ve `load_theme()`.
- `sim/wallpaper.py`: Pillow ile dikey gradyan + Gauss bulanık lekeler. Pillow yoksa
  canvas şeritleriyle aynı görünümün kaba hâli çizilir.
- `sim/icons.py`: 6 uygulama için canvas üzerine çizilen vektörel ikonlar (dosya
  kutusu, not, hesap tuş takımı, `>_`, dişli, bilgi).

### Faz 2 — Pencere sistemi
- `sim/window.py` — `SimWindow`:
  - Gövde, kenarlık, gölge, başlık çubuğu; tema başına 3 farklı kontrol düzeni
    (`win` / `mac` / `gnome`).
  - Başlıktan sürükleme, çift tıkla büyütme, küçültme, büyütme/geri alma, kapatma.
  - İçerik, `canvas.create_window` ile gömülü bir `tk.Frame`; chrome her zaman
    içeriğin **altında** (`tag_lower`).
- `sim/apps/base.py`: tema renkleriyle `label`, `button`, `entry`, `text`, `header`,
  `separator` üreten `App` tabanı + `get_state()` ile tema geçişinde durum taşıma.

### Faz 3 — Uygulamalar
- **Dosyalar**: sahte ana dizin, çift tıklayınca metin önizlemesi.
- **Notlar**: gerçek `tk.Text` editörü, "Kaydet" (simülasyon), içerik tema geçişinde korunur.
- **Hesap Makinesi**: dört işlem, yüzde, işaret değiştirme, hatalı ifade yakalama.
- **Terminal**: `help`, `ls`, `whoami`, `uname`, `date`, `echo`, `clear`, `themes`,
  `theme <id>`, `open <app>`, `neofetch`, `exit`.
- **Ayarlar**: 3 tema kartı (tıklayınca anında geçiş), sistem bilgisi, koyu mod/ses
  anahtarları (görsel).
- **Hakkında**.

### Faz 4 — Paneller ve menüler
- `sim/panel.py`:
  - **win11**: alt görev çubuğu; solda başlat, ortada uygulama ikonları + çalışma
    göstergesi, sağda saat/tarih.
  - **macOS**: üst menü çubuğu (elma, menü adları, saat) + alt dock.
  - **GNOME**: üst bar ("Etkinlikler", ortada saat) + yüzen dash + güç simgesi.
  - Başlat menüsü (uygulama ızgarası) ve sistem menüsü (tema seçimi, tam ekran, çıkış).
  - Saat saniyede bir `_tick()` ile güncellenir.

### Faz 5 — Masaüstü yönetimi
- `sim/desktop.py`:
  - Tam ekran `Tk` + tek `Canvas`; tüm çizim tek yüzeyde.
  - `open_app` / `focus_window` / `close_window` / `activate_app`; aynı uygulama iki kez
    açılmaz, panel ikonu aktifken pencereyi küçültür.
  - `set_theme`: pencereleri anlık görüntüleyip (uygulama durumu, geometri, küçültülmüş,
    büyütülmüş) yeniden kurar; büyütülmüş pencereler yeni temanın kullanılabilir alanına
    oturtulur.
  - Kısayollar: `Ctrl+1/2/3`, `F11`, `Esc`, `Ctrl+Q`.
  - Yeniden boyutlandırma 150 ms debounce, tam ekran geçişinde ek 400/500 ms güvenlik
    denemeleri (Wayland/KDE'de ilk ölçüm geç geliyor).
  - Açılış ekranı (900 ms) panellerin üstünde tutulur.

### Faz 6 — Sağlamlaştırma
Düzeltilen hatalar:

1. `tk.Text` / `tk.Label` fabrikalarında çift `wrap` / `justify` argümanı → `setdefault`.
2. Başlat düğmesinin arka planı `plaunch` etiketi taşımıyordu → tıklama menüyü kapatıyordu.
3. Popup dışına tıklama kontrolü panel etiketlerini tanımıyordu → `plaunch`, `papp-`,
   `psys` beyaz listeye eklendi.
4. Pencere chrome öğeleri `win{uid}` etiketi taşımıyordu → z-order ve sürükleme bozuluyordu.
5. Kapatma/max glyph'leri ayrı etiketli olduğu için tıklama hedefi kaçıyordu → glyph'e de
   kontrol etiketi verildi.
6. Küçültülmüş pencerede `redraw()` erken çıkış yapmıyordu → gizli pencere yeniden çiziliyordu.
7. macOS dock üstündeki tema etiketi kaldırıldı (istenmeyen görsel gürültü).
8. Büyütme glyph'inin hover sonrası dolgusu bozuluyordu → hover sadece kutuyu renklendiriyor.
9. Tema değişiminde büyütülmüş durum kayboluyordu → `maximized` + `_restore_geo` taşınıyor.
10. Açılış ekranı panel çiziminde altta kalıyordu → her panel çiziminden sonra `tag_raise`.

### Faz 7 — 1.1: boyutlandırma, önizleme, tercihler
- **Pencere boyutlandırma** (`sim/window.py`):
  - Sağ, alt ve sağ alt köşede görünmez tutamaç bölgeleri (`-rz-r`, `-rz-b`, `-rz-br`).
  - `MIN_WIDTH=340`, `MIN_HEIGHT=240`; ekran dışına taşma engellenir.
  - Sağ alt köşede iki ince grip çizgisi; kenara gelince imleç değişir.
  - Büyütülmüş pencerede tutamaçtan çekmek pencereyi önce geri küçültür.
- **Fare yakalaması** (`sim/desktop.py`):
  - Sürükleme/boyutlandırma `<B1-Motion>` ve `<ButtonRelease-1>` ile **canvas**
    seviyesinde izlenir (`begin_pointer_action`); imleç tutamacın dışına çıksa da işlem sürer.
- **Panel önizlemesi** (`sim/panel.py`):
  - İkon üzerinde 400 ms bekleyince üstte küçük pencere kartı; 220 ms gecikmeyle kapanır.
  - Kartta minyatür pencere + başlık + durum: `Etkin` / `Küçültüldü` / `Açık`.
  - Karta tıklayınca pencere odaklanır; kart ekran kenarlarına taşmaz.
- **Tercih kalıcılığı** (`sim/settings.py`):
  - `~/.config/simos/settings.json` (XDG uyumlu); `SIMOS_CONFIG_DIR` ile geçersiz kılınır.
  - Atomik yazma (`.tmp` + `replace`); bozuk/eksik dosyada sessizce varsayılana döner.
  - Tema her `set_theme()` sonunda kaydedilir, açılışta `_initial_theme()` yükler.
  - Ayarlar uygulamasında "Tercihler" satırı dosya yolunu gösterir.

## Testler

Geçici test betikleri `/tmp/opencode/` altında (depoya dahil değil, yeniden üretilebilir).
Betikler `SIMOS_CONFIG_DIR` ile ayrı bir ayar dizini kullanır; böylece gerçek
`~/.config/simos/settings.json` ve testler birbirini etkilemez.

| Betik | Kapsam | Sonuç |
|---|---|---|
| `sim_smoke.py` | 6 uygulamayı aç, hesap 7+8, terminal `theme`, tema turu, küçült/büyüt | ✅ |
| `sim_events.py` | Gerçek fare olayları: başlat menüsü, panel ikonu, masaüstü simgesi, sürükleme, kapatma, dock, sistem menüsü | ✅ |
| `sim_extra.py` | Ayarlar kartından geçiş, içerik geometrisi, büyütme korunumu, editör girişi, terminal komutları | ✅ |
| `sim_stress.py` | 6 tur × 3 tema, menü aç/kapa, tüm pencerelerde işlemler, frame sızıntısı | ✅ |
| `sim_polish.py` | Tam ekran gidiş-dönüş, hover renkleri, glyph dolgusu, saat | ✅ |
| `sim_resize.py` | Tam ekrandan çıkma, `1280x800` yeniden boyut, duvar kağıdı/panel tazeleme | ✅ |
| `sim_resize_win.py` | Köşe/kenar boyutlandırma, min boyut, ekran sınırı, büyütülmüşken küçülme, sürükleme | ✅ |
| `sim_settings.py` | Tema kaydet/yükle, bozuk JSON, geçersiz tema, XDG yolu, yazılamayan dizin | ✅ |
| `sim_preview.py` | Hover gecikmesi, konum, durum etiketi, karta tıklama, kapanma, 3 tema | ✅ |

Ek doğrulamalar: `python3 -m py_compile` temiz; uygulama 7 sn çalıştırıldığında
stdout/stderr boş ve `settings.json` içinde `theme: win11` yazılı.

## Bilinen sınırlar

- **Görsel doğrulama yapılamadı**: oturum KDE/Wayland; `grim` "compositor doesn't support
  the screen capture protocol" hatası veriyor, `scrot` boş dosya üretiyor. Yerleşim
  sayısal/strüktürel olarak (bbox, item sırası, koordinat) doğrulandı.
- Dosya işlemleri sahte: `Notlar` kaydetmiyor, `Dosyalar` gerçek diski okumuyor.
- Tema geçişi pencereyi baştan kurar; uygulama durumu yalnız `get_state()` ile taşınanla sınırlı.
- `gui/` klasörü ilk iskelet denemesidir, simülasyon tarafından kullanılmaz.
- Ekran görüntüsü/duvar kağıdı dışa aktarma yok; her şey çalışma anında çizilir.
- Önizleme yalnızca **açık** pencereler için çıkar; kapalı uygulama ikonunda kart yoktur.
- Testlerde imleç panelin üzerindeyken panel yeniden çizilirse sahte Enter/Leave
  olayları önizlemeyi bozabilir; betikler imleci önce ekranın ortasına taşır.

## Sıradaki işler

1. `Notlar` ve `Dosyalar` için gerçek dosya okuma/yazma (`pathlib`, güvenli dizin).
2. Yeni tema: Ubuntu (Yaru) veya KDE Plasma (Breeze) — `THEMES` + `THEME_ORDER`.
3. Yeni uygulamalar: Takvim, Müzik çalar, Metin editörü.
4. Pencere önizlemesine küçültme/kapatma düğmeleri ve canlı içerik görüntüsü.
5. Tercih dosyasına duvar kağıdı/panel yoğunluğu gibi ek ayarlar.
6. Görsel regresyon için Xvfb + `import` (ImageMagick) tabanlı ekran görüntüsü testi.

## Sürüm geçmişi

| Sürüm | Tarih | Not |
|---|---|---|
| 1.0 | 30.10.2026 | 3 tema, 6 uygulama, panel/menü sistemi, 6 test betiği |
| 1.1 | 30.10.2026 | Pencere boyutlandırma, panel önizlemesi, tema tercihi kalıcılığı; 9 test betiği |

# Bilgisayar Simülasyonu (Python + tkinter)

Windows 11 / macOS / GNOME görünümlü, tamamen kodla çizilmiş bir masaüstü
simülasyonu. Duvar kağıdı, panel/dock, açılıp kapanan pencereler, sürükleme,
köşeden boyutlandırma, küçültme/büyütme ve 6 çalışan uygulama içerir.

## Çalıştırma

```bash
pip install -r requirements.txt   # sadece Pillow (opsiyonel, duvar kağıdı için)
python3 main.py
```

Tam ekran açılır. `Esc` tam ekrandan çıkarır, `F11` geri alır.

## Temalar

| Tema | Panel düzeni | Pencere kontrolleri |
|---|---|---|
| **Windows 11** | Alt görev çubuğu, sağda saat/tarih | Sağ üstte `− □ ×` |
| **macOS** | Üst menü çubuğu + alt dock | Solda kırmızı/sarı/yeşil trafik ışıkları |
| **GNOME** | Üst bar + yüzen dash | Sağ üstte yuvarlak kapatma |

Tema değiştirmenin 4 yolu:

1. **Ayarlar** uygulamasındaki tema kartları
2. Paneldeki tema adı / saat üzerine tıkla → **sistem menüsü**
3. **Terminal**: `theme macos`
4. `Ctrl+1` (Windows), `Ctrl+2` (macOS), `Ctrl+3` (GNOME)

Geçiş sırasında açık pencereler, konumları ve içerikleri korunur
(not metni, hesap sonucu, terminal geçmişi, büyütülmüş pencereler dahil).

## Uygulamalar

- **Dosyalar** — sahte ana dizin, metin dosyası önizlemesi
- **Notlar** — tema uyumlu editör, kaydetme durumu
- **Hesap Makinesi** — çalışan dört işlem (`7 + 8 =`)
- **Terminal** — `help`, `ls`, `neofetch`, `theme`, `open`, `clear`, `exit`
- **Ayarlar** — canlı tema seçici, sistem bilgisi
- **Hakkında**

Panelden, masaüstü simgelerinden veya başlat menüsünden açılır. Aynı uygulama
tekrar açılmaz; ikonuna tıklamak pencereyi öne getirir, aktifken küçültür.

## Kısayollar

| Kısayol | İşlev |
|---|---|
| `Ctrl+1/2/3` | Tema değiştir |
| `F11` | Tam ekran |
| `Esc` | Menüyü kapat / tam ekrandan çık |
| `Ctrl+Q` | Çıkış |

Fare: başlık çubuğundan sürükle, çift tıkla büyüt, sağ/alt kenardan veya sağ alt
köşeden boyutlandır, köşedeki düğmelerle kapat/küçült. Panel ikonunda ~0,4 sn
beklersen açık pencerenin küçük önizlemesi çıkar; karta tıklayınca pencere öne gelir.

Tema tercihi `~/.config/simos/settings.json` içinde saklanır; uygulama bir sonraki
açılışta son temayla başlar. `SIMOS_CONFIG_DIR` ile başka bir dizin kullanılabilir.

## Yapı

```
main.py               giriş noktası
sim/
  desktop.py          masaüstü: duvar kağıdı, simgeler, pencere yönetimi, kısayollar
  themes.py           Windows / macOS / GNOME renkleri, yazı tipleri, panel tanımları
  wallpaper.py        Pillow ile gradyan + bulanık leke duvar kağıdı (fallback: canvas)
  icons.py            canvas üzerine çizilen vektörel uygulama ikonları
  draw.py             yuvarlatılmış dikdörtgen ve renk karıştırma yardımcıları
  window.py           SimWindow: sürükleme, boyutlandırma, odak, z-order, küçültme/büyütme/kapatma
  panel.py            görev çubuğu / menü çubuğu / dock / başlat menüsü / sistem menüsü / önizleme
  settings.py         tema tercihi: ~/.config/simos/settings.json (XDG uyumlu)
  apps/
    base.py           App tabanı + tema renkleriyle widget üreticileri
    files.py  notes.py  calc.py  terminal.py  settings.py  about.py
```

Yeni uygulama eklemek: `sim/apps/` altında `App`'den türeyen bir sınıf yaz
(`id`, `title`, `width`, `height`, `build()`), sonra `sim/apps/__init__.py`
içindeki `APP_CLASSES` / `APP_ORDER` listelerine ekle.

Yeni tema eklemek: `sim/themes.py` içindeki `THEMES` sözlüğüne aynı anahtarlarla
bir girdi ekle ve `THEME_ORDER` listesine yaz.

## Dokümanlar

| Dosya | İçerik |
|---|---|
| `install.md` | kurulum, çalıştırma, sorun giderme |
| `progress.md` | durum, tamamlananlar, testler, yol haritası |
| `CLAUDE.md` | yapay zekâ ajanları için mimari ve kod kuralları |

## Notlar

- Pillow yoksa duvar kağıdı canvas şeritleriyle çizilir, uygulama yine çalışır.
- Dosya kaydetme/açma bilinçli olarak simülasyon seviyesinde bırakıldı.
- `gui/` klasörü önceki "boş GUI iskeleti" çalışmasıdır; simülasyon onu kullanmaz.
# karma

# Kurulum

Windows 11 / macOS / GNOME görünümlü masaüstü simülasyonunu çalıştırma adımları.
Tamamı Python + tkinter; ağır bir bağımlılık yok.

## Gereksinimler

| Gereksinim | Sürüm | Not |
|---|---|---|
| Python | 3.10+ (3.14 ile test edildi) | `tkinter` standart kütüphanede |
| tkinter | — | Ayrı kurulum gerekmez (aşağıdaki nota bak) |
| Pillow | 10+ | **Opsiyonel**; duvar kağıdı için. Yoksa canvas ile çizilir |
| İşletim sistemi | Linux / Windows / macOS | 1920×1200 tam ekranda test edildi |

`tkinter` eksikse (bazı minimal Linux dağıtımlarında olur):

```bash
# Debian / Ubuntu
sudo apt install python3-tk
# Fedora
sudo dnf install python3-tkinter
# Arch
sudo pacman -S tk
```

Kontrol:

```bash
python3 -c "import tkinter; print('tkinter OK')"
```

## Hızlı kurulum

```bash
cd /home/can/Masaüstü/proje/open_code/masaüstü

python3 -m venv .venv          # proje içinde .venv zaten var, atlanabilir
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python3 main.py
```

Pillow kurmak istemiyorsan `requirements.txt` adımını atla; uygulama yine açılır,
duvar kağıdı canvas şeritleriyle çizilir (biraz daha düz görünür).

### Sistem Python'u ile (venv'siz)

```bash
pip install --user Pillow
python3 main.py
```

## Çalıştırma

```bash
python3 main.py
```

- Tam ekran açılır, yaklaşık 1 saniyelik açılış ekranı gösterir.
- `Esc` → tam ekrandan çıkar (pencere moduna geçer), tekrar `Esc`/`F11` → tam ekran.
- `Ctrl+Q` → çıkış.
- Son kullanılan tema `~/.config/simos/settings.json` içinden okunur; ilk açılış
  Windows 11'dir. Tercih dosyası yoksa/bozuksa varsayılana döner, hata vermez.

## İlk 30 saniye

1. `Ctrl+1` / `Ctrl+2` / `Ctrl+3` ile Windows 11 → macOS → GNOME geçişini dene.
2. Alttaki/üstteki panelde ortadaki ikonlardan birine tıkla (ör. Terminal).
3. Pencereyi başlık çubuğundan sürükle, çift tıkla büyüt, sağ üstteki düğmelerle kapat.
4. Pencereyi sağ kenarından, alt kenarından veya sağ alt köşesinden tutup boyutlandır.
5. Panelde açık bir uygulamanın ikonunda ~0,4 sn bekle → pencere önizleme kartı çıkar;
   karta tıkla → pencere öne gelir.
6. Terminale `theme macos` yaz → tema anında değişir, açık pencereler korunur.
7. Panelde saate tıkla → sistem menüsü (tema seçimi, tam ekran, çıkış).

## Kısayollar

| Kısayol | İşlev |
|---|---|
| `Ctrl+1` | Windows 11 teması |
| `Ctrl+2` | macOS teması |
| `Ctrl+3` | GNOME teması |
| `F11` | Tam ekran aç/kapa |
| `Esc` | Menüyü kapat / tam ekrandan çık |
| `Ctrl+Q` | Çıkış |

## Doğrulama

Kurulumun sağlam olduğunu görmek için:

```bash
python3 -m py_compile main.py sim/*.py sim/apps/*.py && echo "derleme OK"
SIMOS_CONFIG_DIR=/tmp/simos-test python3 -c "from sim.desktop import Desktop; d=Desktop(); d.root.update(); d._apply_resize(); print('tema:', d.theme_id, d.width, 'x', d.height); d.root.destroy()"
```

İkinci komut `tema: win11 1920 x 1200` benzeri bir satır yazıp kapanmalı. (Ekran
çözünürlüğüne göre değişir; `_apply_resize()` tam ekran ölçümünün oturmasını bekler.)
`SIMOS_CONFIG_DIR` gerçek tercih dosyanı değiştirmeden geçici bir dizin kullanır.

## Tercih dosyası

| Yol | İçerik |
|---|---|
| `~/.config/simos/settings.json` | `{"theme": "win11"}` — son kullanılan tema |
| `$XDG_CONFIG_HOME/simos/settings.json` | `XDG_CONFIG_HOME` ayarlıysa bu yol kullanılır |
| `$SIMOS_CONFIG_DIR/settings.json` | Test/deneme için dizini tamamen değiştirir |

- Dosya atomik yazılır (önce `settings.json.tmp`, sonra yerine taşınır).
- Bozuk JSON, eksik dosya veya yazılamayan dizin: uygulama sessizce varsayılan
  temayla devam eder; hiçbir hata penceresi çıkmaz.
- Ayarlar uygulamasındaki **Tercihler** satırı etkin dosya yolunu gösterir.
- Tercihi sıfırlamak için dosyayı sil: `rm ~/.config/simos/settings.json`.

## Sorun giderme

**`ModuleNotFoundError: No module named 'tkinter'`**
→ Yukarıdaki `python3-tk` paketini kur.

**Pencere açılıyor ama boş/siyah görünüyor**
→ Wayland oturumunda tam ekran ilk ölçümü gecikebilir. Uygulama 150/400/500 ms'de
yeniden ölçer; birkaç saniye bekle. Sürerse `QT_QPA_PLATFORM=xcb` gibi bir X11
oturumunda dene veya `python3 main.py` yerine terminalden hata çıktısını izle.

**Duvar kağıdı düz renk**
→ Pillow kurulu değil. `pip install Pillow` (bu normal bir durum, hata değil).

**Yazı tipleri farklı görünüyor**
→ Tema tanımları sırayla Inter → Segoe UI → Liberation Sans → DejaVu Sans dener.
Linux'ta genelde Liberation/DejaVu kullanılır. Daha yakın görünüm için:
`sudo apt install fonts-liberation fonts-cantarell`.

**`ImportError: cannot import name 'Desktop' from 'sim'`**
→ Komutu proje kökünden çalıştır. `main.py` ile aynı dizinde olmalısın.

**Ekran görüntüsü alamıyorum**
→ KDE/Wayland'de `grim` desteklenmeyebilir, `scrot` boş görüntü verebilir. Bu bir
uygulama hatası değil. X11 oturumunda `import -window root ekran.png` deneyebilirsin.

**Uygulama her açılışta farklı temayla başlıyor**
→ Bu bir hata değil: son tema hatırlanıyor. Sabit başlangıç için
`rm ~/.config/simos/settings.json` veya `SIMOS_CONFIG_DIR=/tmp/simos-temiz python3 main.py`.

**Tercih dosyası oluşmuyor**
→ Dizin yazılamıyor olabilir (`~/.config` izinleri). Uygulama çalışmaya devam eder,
yalnız tema hatırlanmaz. `SIMOS_CONFIG_DIR` ile yazılabilir bir dizin göster.

**Çıkışta `TclError: can't invoke "..." command: application has been destroyed`**
→ Bilinmiyor; normalde `Ctrl+Q` veya `Esc` ile temiz kapanır. Böyle bir iz görürsen
hangi işlemden sonra olduğunu not et.

## Kaldırma

Proje yalnızca kendi `.venv` klasörüne ve tema tercihi için
`~/.config/simos/settings.json` dosyasına yazar (kayıt defteri/servis yok).
Silmek için:

```bash
rm -rf .venv __pycache__ sim/__pycache__ sim/apps/__pycache__
rm -f ~/.config/simos/settings.json   # tercihi de sil
```

## Dosya düzeni

```
main.py             giriş noktası (python3 main.py)
requirements.txt    Pillow (opsiyonel)
README.md           kısa tanıtım ve mimari
install.md          bu dosya
progress.md         geliştirme günlüğü ve yol haritası
CLAUDE.md           yapay zekâ ajanları için proje rehberi
sim/                simülasyonun tamamı
sim/settings.py     tema tercihi (XDG uyumlu JSON)
```

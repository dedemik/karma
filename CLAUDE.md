# CLAUDE.md

Bu dosya, bu depoda çalışan yapay zekâ ajanları (Claude Code vb.) içindir.
Projeyi hızlı anlamak, mevcut mimariyi bozmadan değişiklik yapmak için gerekli
bilgiler burada. Kullanıcıya Türkçe yanıt ver.

## Proje nedir

Tek bir `tkinter.Canvas` üzerine çizilmiş, Windows 11 / macOS / GNOME görünümlü
bir masaüstü simülasyonu. Gerçek pencere yöneticisi kullanılmaz: pencere süslemeleri
canvas öğesi, içerikleri canvas'a gömülü `tk.Frame`. Amaç görsel taklit + canlı tema
geçişi, üretim aracı değil.

## Komutlar

```bash
python3 main.py                                  # çalıştır (tam ekran)
python3 -m py_compile main.py sim/*.py sim/apps/*.py   # hızlı sözdizimi kontrolü
pip install -r requirements.txt                  # Pillow (opsiyonel)
```

Otomatik test dosyası depoda yok. Davranışı doğrularken `/tmp/opencode/` altında
geçici betik yaz (depoyu kirletme). Testler için minimum iskelet:

```python
import os, sys
sys.path.insert(0, "/home/can/Masaüstü/proje/open_code/masaüstü")
os.environ["SIMOS_CONFIG_DIR"] = "/tmp/opencode/simos-test-config"   # gerçek tercihi kirletme
from sim.desktop import Desktop

d = Desktop()
d.root.update(); d._apply_resize()      # boyutların oturması için şart
d.canvas.delete("boot")
d.root.update()
```

Gerçek fare olayı simüle ederken **önce `<Motion>`, sonra `<ButtonPress-1>`** üret ve
her adımda `d.root.update()` çağır; aksi hâlde `current` etiketi güncellenmez ve
`tag_bind` tetiklenmez. Test başında imleci panelin dışına taşı
(`event_generate("<Motion>", x=..., y=..., warp=True)`); panel yeniden çizilirken
gerçek imleç bir ikonun üzerindeyse sahte Enter/Leave olayları önizleme işlerini bozar.

## Mimari

```
main.py → sim.desktop.Desktop
             ├── sim.themes       THEMES, THEME_ORDER, load_theme()
             ├── sim.settings     load_settings() / save_settings(), settings_path()
             ├── sim.wallpaper    Pillow gradyan (fallback: canvas şeritleri)
             ├── sim.icons        draw_app_icon() — vektörel uygulama ikonları
             ├── sim.panel        paneller, başlat menüsü, sistem menüsü, önizleme
             ├── sim.window       SimWindow — süsleme, sürükleme, boyutlandırma, kontroller
             └── sim.apps         App tabanı + 6 uygulama + kayıt defteri
```

Veri akışı:

- `Desktop.set_theme(id)` → pencereleri **yok eder**, `win.app.get_state()` ile durum
  alır, yeni temayı yükler, duvar kağıdı + simgeler + panelleri çizer, pencereleri
  aynı geometri/durumla yeniden açar. Sonunda `settings["theme"]` yazılır.
- `Desktop._initial_theme()` → kayıtlı tema `THEMES` içinde varsa onu, yoksa `win11`.
- `Desktop.open_app(id)` → `APP_CLASSES[id]` → `App.build(frame)` → `SimWindow`.
  Aynı `id` için ikinci pencere açılmaz.
- `Desktop.focus_window(win)` → diğerlerini pasifleştirir, `tag_raise`, panelleri
  yeniden çizer (aktiflik noktaları için), `app.on_focus()`.
- `Desktop.activate_app(id)` → panel/dock ikon davranışı: yoksa aç, küçültülmüşse geri
  getir, aktifse küçült, değilse öne al.
- `Desktop.begin_pointer_action(win, mode, data)` → başlık sürükleme (`move`) veya
  kenar boyutlandırma (`resize`) başlatır; hareket/bırakma canvas `<B1-Motion>` /
  `<ButtonRelease-1>` üzerinden `win._drag_move` / `win._resize_move` çağırır.
- `sim.panel.schedule_preview(...)` → 400 ms sonra `show_preview()`; kartın hedefi
  `Desktop._preview_target` ile izlenir, `schedule_preview_hide()` 220 ms sonra siler.

## Değişmezler (bunları bozma)

1. **Etiket ikiliği**: Bir pencerenin her canvas öğesi hem `chrome{uid}` hem `win{uid}`
   etiketini taşımalı. `canvas.move(win.tag, ...)` ve z-order buna bağlı.
   `redraw()` sonunda `canvas.tag_lower(self.chrome, self.content)` çağrılır.
2. **Panel en üstte**: `draw_panels()` sonunda `canvas.tag_raise("panel")`; açık popup
   varsa `tag_raise("popup")`; açılış ekranı varsa `tag_raise("boot")`.
3. **Popup kapanma kuralı**: `Desktop._on_canvas_click` içindeki beyaz liste
   (`popup`, `ltile-`, `sysrow-`, `plaunch`, `papp-`, `psys`). Yeni bir panel/menü
   etiketi eklersen buraya da ekle, yoksa menü kendi tıklamasıyla kapanır.
4. **Widget fabrikaları**: `App.label`, `App.text`, `App.button` gibi yardımcılar
   `**kwargs` alır; varsayılanları `kwargs.setdefault(...)` ile ver, doğrudan
   `tk.X(..., wrap=..., **kwargs)` yazma — çift argüman `TypeError` üretir.
5. **Uygulama durumu**: Tema geçişinde korunacak her şey `App.get_state()` içinde
   dönmeli ve `App.__init__` içinde `self.state`'ten okunmalı. Aksi hâlde tema
   değişince kaybolur.
6. **Küçültülmüş pencere**: `SimWindow.redraw()` başında `if self.minimized: return`.
   Bu koruma kaldırılırsa gizli pencere görünür hâle gelir.
7. **Yeniden boyutlandırma**: `<Configure>` → 150 ms debounce → `_apply_resize()`.
   Tam ekran geçişinde ayrıca 150/400/500 ms gecikmeli çağrılar var; kaldırma,
   Wayland/KDE'de canvas boyutu geç güncelleniyor.
8. **Tek canvas**: Yeni görsel katman eklerken ayrı `Toplevel`/`Canvas` açma; mevcut
   canvas'a etiketli öğe olarak çiz. Sıralama: `wallpaper` → `deskicon` → pencere
   chrome → pencere içeriği → `panel` → `preview` → `popup` → `boot`.
9. **Fare yakalaması**: Sürükleme/boyutlandırma hareketini pencere etiketine değil
   canvas'a bağla (`_on_pointer_motion` / `_on_pointer_release`). Etikete bağlarsan
   imleç tutamaçtan çıkınca işlem kopar. `SimWindow.destroy()` `_pointer_action`
   kendine aitse temizlemeli.
10. **Boyutlandırma bölgeleri**: `-rz-r`, `-rz-b`, `-rz-br` etiketleri hem `chrome{uid}`
    hem `win{uid}` taşımalı; `MIN_WIDTH`/`MIN_HEIGHT` altına inilmez, pencere ekran
    dışına taşmaz. Büyütülmüşken tutamaçtan çekmek önce `toggle_maximize()` çağırır.
11. **Önizleme**: Kart öğeleri yalnız `preview` etiketini taşır (panel değil).
    `draw_panels()` ve menüler `cancel_preview()` çağırır. Hedef uygulama
    `Desktop._preview_target` alanında tutulur; gösterim anında hedef değişmişse kart
    açılmaz. `preview` beyaz listeye eklenmez (karta tıklama menü kapatmasın diye ayrı
    `tag_bind` var).
12. **Tercihler**: `sim/settings.py` dışında dosya yazma. `save_settings()` hata
    yutmalı; `load_settings()` her zaman sözlük döndürmeli. `set_theme()` sonunda
    tema kaydedilir; testlerde `SIMOS_CONFIG_DIR` ayarlanmadan çalıştırma, gerçek
    `~/.config/simos/settings.json` kirlenir.

## Kod kuralları

- Türkçe: docstring, yorum, kullanıcıya görünen tüm metinler Türkçe.
- `from __future__ import annotations` her modülde var; type hint kullan.
- 4 boşluk girinti, satırlar ~100 karakter, sınıflar arasında iki boş satır.
- Tema renklerini **asla** koda gömme; `self.theme["window"]["accent"]` gibi oku.
  İstisna: duvar kağıdı/ikon gradyanları ve macOS trafik ışığı renkleri tema
  tanımının parçası.
- Yeni renk gerekiyorsa `sim/themes.py` içindeki ilgili sözlüğe ekle ve üç temada da
  tanımla; eksik anahtar `KeyError` ile çalışma anında patlar.
- Widget'ları yalnızca `App.build(parent)` içinde, verilen `parent`'a `pack`/`grid` et.
  Pencere geometrisini uygulamalar değil `SimWindow` yönetir.
- Sihirli sayı yerine tema sözlüğündeki `radius`, `titlebar`, `pad`, `height` alanlarını kullan.

## Yeni uygulama ekleme

1. `sim/apps/yeni.py`: `App`'den türet, `id`, `title`, `width`, `height` ver,
   `build(self, parent)` yaz. Durum taşınacaksa `get_state()` + `self.state.get(...)`.
2. `sim/apps/__init__.py`: sınıfı import et, `APP_CLASSES`, `APP_ORDER` listelerine ekle.
   Masaüstünde simgesi görünsün istiyorsan `DESKTOP_APPS`'a da ekle.
3. `sim/icons.py`: `TILE_COLORS`'a renk, `draw_app_icon` içine `elif app_id == ...`
   dalı ekle. İkon çizilmezse panelde boş kutu görünür.
4. Ayarlar/Hakkında gibi metinlerde yeni uygulamadan söz ediliyorsa güncelle.

## Yeni tema ekleme

1. `sim/themes.py` → `THEMES` sözlüğüne `win11`/`macos`/`gnome` ile **aynı anahtarları**
   içeren bir girdi ekle (`label`, `families`, `accent`, `wallpaper`, `desktop`,
   `window`, `panel`, `dock`).
2. `THEME_ORDER` listesine ekle — kısayol numarası, sistem menüsü sırası ve testler
   bu listeyi kullanır.
3. `window["controls"]` yeni bir düzen gerektiriyorsa `SimWindow._draw_controls`
   içine dal ekle; mevcut `win` / `mac` / `gnome` davranışını değiştirme.
4. `panel["style"]` yeni bir panel tipiyse `sim/panel.py:draw_panels` ve `Desktop.useful_area`
   güncellenmeli (maksimize alanı panel/dock yüksekliğine bağlı).

## Bilinen tuzaklar

- **Testlerde boyut**: `Desktop()` sonrası `d.width/height` ilk anda `1920x1134`
  olabilir; `d.root.update(); d._apply_resize()` çağırmadan koordinat testi yapma.
- **bbox payı**: `canvas.bbox("panel")` kenarlarda ±2 px taşabilir; sınır testlerinde
  tolerans kullan.
- **`tk.Text` durumu**: Salt okunur metinlerde `state="disabled"`; yazmadan önce
  `state="normal"` yapıp sonra geri al.
- **`eval`**: Hesap makinesi `eval` kullanır ama `{"__builtins__": None}` ile
  kısıtlıdır. Bu davranışı genişletme.
- **`set_theme()` yan etkisi**: Her tema değişimi tercih dosyasına yazar. Beklenmedik
  disk yazımı istemiyorsan testte `SIMOS_CONFIG_DIR` kullan.
- **Önizleme zamanlaması**: Gösterim 400 ms, kapanma 220 ms gecikmeli. Testlerde
  `time.sleep(0.65)` + `d.root.update()`; tek `update()` bazı ortamlarda after işini
  işlemez. Gösterim sırasında `_preview_target` değişirse kart açılmaz.
- **Boyutlandırma testi**: Tutamacın merkezine `<Motion>` üretip `current` etiketini
  doğrula, sonra `<ButtonPress-1>` ve tek adımda büyük `<B1-Motion>` gönder; yakalama
  canvas seviyesinde olduğu için imleç bölge dışına çıksa da sürer.
- **Ekran görüntüsü**: Bu makinede KDE/Wayland `grim`'i desteklemiyor, `scrot` boş
  dosya üretiyor. Görsel doğrulama gerekiyorsa Xvfb + ImageMagick `import` gibi bir
  yol dene; başarısız olursa geometri/etiket testleriyle yetin ve bunu kullanıcıya söyle.
- **`gui/` klasörü**: Eski, kullanılmayan iskelet. Simülasyon `sim/` kullanır;
  `gui/` içindeki kodu düzeltmeye veya ona bağımlılık kurmaya gerek yok.
- **Türkçe karakterler**: Kaynak dosyaları UTF-8; `str.lower()` Türkçe `I/İ`
  davranışına dikkat et (terminal komutları ASCII tutuluyor).

## Değişiklik sonrası kontrol listesi

1. `python3 -m py_compile main.py sim/*.py sim/apps/*.py`
2. Üç temada da aç: `d.set_theme(t)` + `d.root.update()`.
3. En az bir uygulamayı aç, sürükle, küçült, büyüt, kapat.
4. Sağ/alt kenardan ve köşeden boyutlandır; min boyut ve ekran sınırını dene.
5. Panel ikonunda bekle → önizleme kartı çıkıyor, karta tıklayınca odaklanıyor mu?
6. Tema değiştir → uygulama sayısı, boyutu ve durumu korunuyor mu?
7. `d.canvas.winfo_children()` sayısı açık pencere sayısına eşit mi (frame sızıntısı)?
8. `settings.json` son temayı içeriyor mu; yeni `Desktop()` o temayla mı açılıyor?
9. `progress.md` içindeki ilgili bölümü güncelle.

## Dosyalar

| Yol | İçerik |
|---|---|
| `main.py` | giriş noktası |
| `sim/desktop.py` | tema geçişi, pencere yönetimi, kısayollar, resize, fare yakalama, önizleme iptali |
| `sim/window.py` | `SimWindow` süsleme/sürükleme/boyutlandırma/kontroller |
| `sim/panel.py` | panel, dock, başlat menüsü, sistem menüsü, saat, pencere önizlemesi |
| `sim/settings.py` | tercih dosyası okuma/yazma (XDG uyumlu, atomik, sessiz hata) |
| `sim/themes.py` | tema sözlükleri ve font çözümleme |
| `sim/icons.py` | vektörel uygulama ikonları |
| `sim/wallpaper.py` | Pillow gradyan + canvas fallback |
| `sim/draw.py` | yuvarlatılmış dikdörtgen, renk yardımcıları |
| `sim/apps/base.py` | `App` tabanı ve tema uyumlu widget fabrikaları |
| `README.md` | kullanıcıya dönük tanıtım |
| `install.md` | kurulum ve sorun giderme |
| `progress.md` | durum, testler, yol haritası |
| `.claudeignore` | ajan bağlamından çıkarılacak dosyalar |

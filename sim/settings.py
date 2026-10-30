"""Kullanıcı tercihleri: ~/.config/simos/settings.json.

Simülasyon ayarları küçük bir JSON dosyasında tutulur. Dosya okunamaz ya da
yazılamazsa uygulama sessizce varsayılanlarla devam eder; hiçbir hata kullanıcıya
yansıtılmaz.

Testler için `SIMOS_CONFIG_DIR` ortam değişkeniyle dizin değiştirilebilir.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

APP_DIR = "simos"
FILE_NAME = "settings.json"


def config_dir() -> Path:
    """Ayar dizinini döndürür (XDG uyumlu, ortam değişkeniyle geçersiz kılınabilir)."""
    override = os.environ.get("SIMOS_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".config"
    return root / APP_DIR


def settings_path() -> Path:
    return config_dir() / FILE_NAME


def load_settings() -> dict:
    """Ayarları okur; bozuk/eksik dosyada boş sözlük döndürür."""
    try:
        with settings_path().open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(values: dict) -> None:
    """Ayarları atomik olarak yazar (önce .tmp, sonra yerine taşı)."""
    try:
        path = settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(values, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
    except OSError:
        pass

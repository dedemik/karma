"""Uygulama kayıt defteri."""

from __future__ import annotations

from .about import AboutApp
from .calc import CalcApp
from .files import FilesApp
from .notes import NotesApp
from .settings import SettingsApp
from .terminal import TerminalApp

APP_CLASSES = {
    cls.id: cls
    for cls in (FilesApp, NotesApp, CalcApp, TerminalApp, SettingsApp, AboutApp)
}

APP_ORDER = ["files", "notes", "calc", "terminal", "settings", "about"]

DESKTOP_APPS = ["files", "notes", "terminal", "settings"]

__all__ = ["APP_CLASSES", "APP_ORDER", "DESKTOP_APPS"]

"""Тексты интерфейса и настройки дополнения."""

from __future__ import annotations

import anki.lang
from aqt import mw

# Имя папки дополнения — по нему Anki хранит настройки.
ADDON = __name__.split(".")[0]

DEFAULTS: dict[str, object] = {
    "header": "",  # пусто — «Размер» / «Size» по языку Anki
}

_TEXTS = {
    "ru": {
        "size": "Размер",
        "tooltip": "Текст: {text}\nМедиа: {media} ({files} файл.)\nЗаписей: {notes}",
        "dlg_title": "Размер колоды — настройки",
        "header": "Заголовок столбца",
        "hint": "Размер = текст записей + медиафайлы, с подколодами. "
        "Файл, нужный нескольким записям, считается один раз.",
        "defaults": "По умолчанию",
    },
    "en": {
        "size": "Size",
        "tooltip": "Text: {text}\nMedia: {media} ({files} files)\nNotes: {notes}",
        "dlg_title": "Deck Size Column — settings",
        "header": "Column header",
        "hint": "Size = note text + media files, including subdecks. "
        "A file used by several notes is counted once.",
        "defaults": "Defaults",
    },
}


def is_russian() -> bool:
    # Читаем при каждом вызове: язык задаётся уже после загрузки дополнения.
    return (anki.lang.current_lang or "").lower().startswith("ru")


def t(text_id: str, /, **kwargs: object) -> str:
    return _TEXTS["ru" if is_russian() else "en"][text_id].format(**kwargs)


def get_config() -> dict:
    stored = mw.addonManager.getConfig(ADDON) or {}
    return {key: stored.get(key, default) for key, default in DEFAULTS.items()}


def save_config(cfg: dict) -> None:
    mw.addonManager.writeConfig(ADDON, cfg)

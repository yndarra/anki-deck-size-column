"""Тексты интерфейса и настройки дополнения."""

from __future__ import annotations

import anki.lang
from aqt import mw

# Имя папки дополнения — по нему Anki хранит настройки.
ADDON = __name__.split(".")[0]

# Пустая строка в заголовке = оставить текст самой Anki.
DEFAULTS: dict[str, object] = {
    "size_column": True,
    "size_header": "",
    "header_deck": "",
    "header_new": "",
    "header_learn": "",
    "header_due": "",
    "wrap_names": True,
    "name_width": "20em",
}

_TEXTS = {
    "ru": {
        "size": "Размер",
        "tooltip": "Текст: {text}\nМедиа: {media} ({files} файл.)\nЗаписей: {notes}",
        "settings_menu": "Настройки списка колод…",
        "dlg_title": "Список колод — настройки",
        "grp_size": "Столбец размера (текст + медиа, с подколодами)",
        "grp_headers": "Заголовки столбцов (пусто — как в Anki)",
        "grp_wrap": "Перенос длинных названий колод",
        "show_size": "Показывать столбец размера",
        "size_header": "Заголовок",
        "h_deck": "Колода",
        "h_new": "Новые",
        "h_learn": "Изучаемые",
        "h_due": "К повторению",
        "wrap": "Переносить название на следующие строки, а не растягивать таблицу",
        "width": "Ширина столбца названия",
        "width_hint": "например 20em, 300px",
        "defaults": "По умолчанию",
    },
    "en": {
        "size": "Size",
        "tooltip": "Text: {text}\nMedia: {media} ({files} files)\nNotes: {notes}",
        "settings_menu": "Deck list settings…",
        "dlg_title": "Deck list — settings",
        "grp_size": "Size column (text + media, including subdecks)",
        "grp_headers": "Column headers (empty — Anki's own)",
        "grp_wrap": "Wrapping long deck names",
        "show_size": "Show the size column",
        "size_header": "Header",
        "h_deck": "Deck",
        "h_new": "New",
        "h_learn": "Learn",
        "h_due": "Due",
        "wrap": "Wrap long names onto new lines instead of widening the table",
        "width": "Name column width",
        "width_hint": "e.g. 20em, 300px",
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

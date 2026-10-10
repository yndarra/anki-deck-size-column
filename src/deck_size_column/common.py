"""Тексты интерфейса и настройки дополнения."""

from __future__ import annotations

import json

import anki.lang
from aqt import mw

# Имя папки дополнения — по нему Anki хранит настройки.
ADDON = __name__.split(".")[0]

# Цветовые точки: «с какого размера» и цвет плашки для светлой и тёмной темы.
# В режиме градиента цвет между соседними точками меняется плавно (по
# логарифмической шкале — размеры колод отличаются в сотни раз), выше
# последней точки — её цвет. Без градиента — ступеньками, как в Note Size.
# Пороги крупнее, чем у Note Size (там 100 KB / 1 MB для одной записи),
# потому что колода — это сотни и тысячи записей.
# По умолчанию: серый (совсем маленькие колоды, до 100 KB) → зелёный к 10 MB →
# жёлтый к 30 MB → оранжевый к 100 MB → красный к 1 GB → чёрный к 2 GB и дальше.
DEFAULT_STOPS = [
    {"size": "0 B", "light_color": "#D4D4D4", "dark_color": "#4A4A4A"},
    {"size": "100 KB", "light_color": "#D4D4D4", "dark_color": "#4A4A4A"},
    {"size": "10 MB", "light_color": "#90EE90", "dark_color": "#15803D"},
    {"size": "30 MB", "light_color": "#FFE45C", "dark_color": "#A18800"},
    {"size": "100 MB", "light_color": "#FFA500", "dark_color": "#C2410C"},
    {"size": "1 GB", "light_color": "#F44336", "dark_color": "#B91C1C"},
    {"size": "2 GB", "light_color": "#000000", "dark_color": "#000000"},
]

DEFAULTS: dict[str, object] = {
    "header": "",  # пусто — «Размер» / «Size» по языку Anki
    "colors_enabled": True,
    "gradient": True,
    "stops": DEFAULT_STOPS,
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
        "colors": "Цвет плашки по размеру (как в Note Size)",
        "gradient": "Плавный переход цвета между точками (градиент)",
        "col_max": "С размера",
        "col_light": "Светлая тема",
        "col_dark": "Тёмная тема",
        "add": "Добавить точку",
        "remove": "Удалить точку",
        "levels_hint": "Щёлкни по цвету, чтобы выбрать другой. Размер: 0 B, 500 KB, 10 MB, 1 GB. "
        "С градиентом цвет плавно перетекает от точки к точке, без — меняется ступенькой.",
    },
    "en": {
        "size": "Size",
        "tooltip": "Text: {text}\nMedia: {media} ({files} files)\nNotes: {notes}",
        "dlg_title": "Deck Size Column — settings",
        "header": "Column header",
        "hint": "Size = note text + media files, including subdecks. "
        "A file used by several notes is counted once.",
        "defaults": "Defaults",
        "colors": "Badge color by size (like Note Size)",
        "gradient": "Smooth color transition between points (gradient)",
        "col_max": "From size",
        "col_light": "Light theme",
        "col_dark": "Dark theme",
        "add": "Add point",
        "remove": "Remove point",
        "levels_hint": "Click a color to change it. Sizes: 0 B, 500 KB, 10 MB, 1 GB. "
        "With the gradient the color blends smoothly between points, without it — in steps.",
    },
}


def is_russian() -> bool:
    # Читаем при каждом вызове: язык задаётся уже после загрузки дополнения.
    return (anki.lang.current_lang or "").lower().startswith("ru")


def t(text_id: str, /, **kwargs: object) -> str:
    return _TEXTS["ru" if is_russian() else "en"][text_id].format(**kwargs)


def get_config() -> dict:
    stored = mw.addonManager.getConfig(ADDON) or {}
    # json-копия — чтобы правки в окне настроек не меняли DEFAULTS.
    return json.loads(json.dumps({key: stored.get(key, default) for key, default in DEFAULTS.items()}))


def save_config(cfg: dict) -> None:
    mw.addonManager.writeConfig(ADDON, cfg)

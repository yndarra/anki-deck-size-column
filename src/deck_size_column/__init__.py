"""Deck Size Column — столбец «Размер» в списке колод на главном экране Anki.

Размер колоды = текст записей + медиафайлы, на которые они ссылаются, вместе
с подколодами (как числа Новые / Изучаемые / Повтор). Подсказка при наведении
показывает текст, медиа, число файлов и записей отдельно.

Как устроено:
  • Перед отрисовкой списка (хук deck_browser_will_render_content) в блок под
    таблицей добавляются стиль и deck_size.js — он вставляет свои ячейки в уже
    готовую таблицу. HTML самой Anki не пересобираем, поэтому дополнение
    уживается с другими правками списка колод (Deck List Column Headers,
    Wrap Long Deck Names и т.п.).
  • Размеры считаются в фоне (sizes.py, ~0,5 с на 50 тыс. записей) и
    кешируются. Пока считается — прошлые значения или «…»; как только готово,
    ячейки обновляются без перерисовки страницы.
  • Пересчёт — только если изменились записи, карточки, колоды или папка медиа.
"""

from __future__ import annotations

import json
import os
from typing import Any

from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from aqt.operations import QueryOp

from . import sizes
from .common import ADDON, get_config, is_russian, t
from .settings import SettingsDialog

_JS_PATH = os.path.join(os.path.dirname(__file__), "deck_size.js")

# Кеш: «отпечаток» коллекции → {deck_id: [текст, подсказка, байты]}
_cache: dict[str, Any] = {"key": None, "cells": {}, "lang": None}
_computing = False

_CSS = (
    "<style>"
    "td.dsc-size { color: var(--fg-subtle); white-space: nowrap; }"
    # Бледнеет только текст: opacity задела бы и линию-разделитель под ячейкой.
    "td.dsc-size.dsc-empty { color: color-mix(in srgb, var(--fg-subtle) 45%, transparent); }"
    "</style>"
)


def _cache_key(col: Any) -> tuple:
    """Дешёвый отпечаток: меняется при любой правке записей/карточек/колод/медиа."""
    db = col.db
    try:
        media_mtime = os.stat(col.media.dir()).st_mtime_ns
    except OSError:
        media_mtime = 0
    return (
        col.mod,
        db.scalar("select max(mod) from notes"),
        db.scalar("select max(mod) from cards"),
        db.scalar("select count() from cards"),
        db.scalar("select max(mtime_secs) from decks"),
        media_mtime,
    )


def _cells(result: dict[int, sizes.DeckSize]) -> dict[str, list]:
    ru = is_russian()
    cells: dict[str, list] = {}
    for did, size in result.items():
        tip = t(
            "tooltip",
            text=sizes.format_size(size.text, ru),
            media=sizes.format_size(size.media, ru),
            files=size.media_files,
            notes=size.notes,
        )
        cells[str(did)] = [sizes.format_size(size.total, ru), tip, size.total]
    return cells


def _start_refresh() -> None:
    """Фоновый пересчёт, если коллекция изменилась с прошлого раза."""
    global _computing
    if _computing or mw.col is None:
        return
    _computing = True
    lang = "ru" if is_russian() else "en"

    def op(col: Any) -> dict | None:
        key = _cache_key(col)
        if key == _cache["key"] and lang == _cache["lang"]:
            return None  # ничего не поменялось
        return {"key": key, "cells": _cells(sizes.compute_deck_sizes(col)), "lang": lang}

    def done(data: dict | None) -> None:
        global _computing
        _computing = False
        if data is None:
            return
        _cache.update(data)
        # Если сейчас открыт список колод — обновляем ячейки на месте.
        if mw.state == "deckBrowser":
            mw.deckBrowser.web.eval(
                f"window.dscApplySizes && dscApplySizes({json.dumps(data['cells'])})"
            )

    def failed(err: Exception) -> None:
        global _computing
        _computing = False
        print("Deck Size Column: size calculation failed:", err)

    QueryOp(parent=mw, op=op, success=done).failure(failed).run_in_background()


def on_will_render(deck_browser: DeckBrowser, content: DeckBrowserContent) -> None:
    header = get_config()["header"] or t("size")
    with open(_JS_PATH, encoding="utf-8") as f:
        script = f.read()
    # Вставляем после таблицы (в блок статистики), а не внутрь <table>.
    content.stats += (
        _CSS
        + "<script>"
        + f"window.DSC_HEADER = {json.dumps(header)};"
        + f"window.DSC_SIZES = {json.dumps(_cache['cells'])};"
        + script
        + "</script>"
    )
    _start_refresh()


def open_settings() -> None:
    def saved(_cfg: dict) -> None:
        if mw.state == "deckBrowser":
            mw.deckBrowser.refresh()

    SettingsDialog(mw, saved).exec()


gui_hooks.deck_browser_will_render_content.append(on_will_render)
mw.addonManager.setConfigAction(ADDON, open_settings)

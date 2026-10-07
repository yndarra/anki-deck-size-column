"""Deck List Tweaks — правки списка колод на главном экране Anki.

  • столбец «Размер»: текст + медиа каждой колоды вместе с подколодами;
  • свои названия столбцов (например «Изуч.» вместо «Изучаемые»);
  • длинные названия колод переносятся на новые строки, а не растягивают таблицу.

Как устроено:
  • Перед отрисовкой списка (хук deck_browser_will_render_content) в страницу
    добавляются стили, настройки и deck_list.js — он правит уже готовую таблицу.
    HTML самой Anki не трогаем, поэтому дополнение уживается с другими.
  • Размеры считаются в фоне (sizes.py, ~0,5 с на 50 тыс. заметок) и
    кешируются. Пока считается — показываются прошлые значения или «…»;
    как только готово, ячейки обновляются без перерисовки страницы.
  • Пересчёт — только если что-то изменилось: коллекция, заметки, карточки
    или папка медиа (см. _cache_key).
"""

from __future__ import annotations

import json
import os
from typing import Any

from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from aqt.operations import QueryOp
from aqt.qt import QAction

from . import sizes
from .common import ADDON, get_config, is_russian, t
from .settings import SettingsDialog

_JS_PATH = os.path.join(os.path.dirname(__file__), "deck_list.js")

# Кеш: ключ состояния коллекции → {deck_id: [текст, подсказка, total]}
_cache: dict[str, Any] = {"key": None, "cells": {}, "lang": None}
_computing = False


def _cache_key(col: Any) -> tuple:
    """Дешёвый «отпечаток» коллекции: меняется при любой правке заметок/карточек/медиа."""
    db = col.db
    media_dir = col.media.dir()
    try:
        media_mtime = os.stat(media_dir).st_mtime_ns
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
    """Готовые строки для ячеек: размер, подсказка и число байт (для «пусто»)."""
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
            mw.deckBrowser.web.eval(f"window.dltApplySizes && dltApplySizes({json.dumps(data['cells'])})")

    def failed(err: Exception) -> None:
        global _computing
        _computing = False
        print("Deck List Tweaks: size calculation failed:", err)

    QueryOp(parent=mw, op=op, success=done).failure(failed).run_in_background()


def _css(cfg: dict) -> str:
    rules = [
        "td.dlt-size { color: var(--fg-subtle); white-space: nowrap; }",
        # Бледнеет только текст: opacity задела бы и линию-разделитель под ячейкой.
        "td.dlt-size.dlt-empty { color: color-mix(in srgb, var(--fg-subtle) 45%, transparent); }",
    ]
    if cfg["wrap_names"]:
        width = str(cfg["name_width"]).replace(";", "").replace("}", "")
        rules += [
            # Фиксированная ширина столбца названия: таблица больше не растягивается.
            f"td.decktd {{ white-space: normal; width: {width}; min-width: {width}; max-width: {width}; }}",
            ".dlt-name { display: flex; align-items: baseline; }",
            ".dlt-indent { white-space: pre; flex: none; }",
            ".dlt-name .collapse { flex: none; }",
            # Название занимает остаток строки и переносится внутри него —
            # продолжение встаёт под начало названия, а не под отступ.
            ".dlt-name a.deck { display: block; flex: 1 1 auto; min-width: 0;"
            " white-space: normal; overflow-wrap: break-word; }",
        ]
    return "<style>" + "\n".join(rules) + "</style>"


def on_will_render(deck_browser: DeckBrowser, content: DeckBrowserContent) -> None:
    cfg = get_config()
    js_cfg = dict(cfg)
    js_cfg["size_header"] = cfg["size_header"] or t("size")
    with open(_JS_PATH, encoding="utf-8") as f:
        script = f.read()
    # Вставляем после таблицы (в блок статистики), а не внутрь <table>.
    content.stats += (
        _css(cfg)
        + "<script>"
        + f"window.DLT_CONFIG = {json.dumps(js_cfg)};"
        + f"window.DLT_SIZES = {json.dumps(_cache['cells'])};"
        + script
        + "</script>"
    )
    if cfg["size_column"]:
        _start_refresh()


def open_settings() -> None:
    def saved(_cfg: dict) -> None:
        if mw.state == "deckBrowser":
            mw.deckBrowser.refresh()

    SettingsDialog(mw, saved).exec()


def _add_menu_item() -> None:
    action = QAction(t("settings_menu"), mw)
    action.triggered.connect(lambda _checked=False: open_settings())
    mw.form.menuTools.addAction(action)


gui_hooks.deck_browser_will_render_content.append(on_will_render)
gui_hooks.main_window_did_init.append(_add_menu_item)
mw.addonManager.setConfigAction(ADDON, open_settings)

"""Подсчёт размера колод: текст заметок + медиафайлы, на которые они ссылаются.

Модуль без GUI — его проверяют тесты на настоящей коллекции (tests/test_sizes.py).

Правила подсчёта:
  • Текст заметки — длина всех её полей в байтах UTF-8 (как в Note Size).
  • Медиа — файлы из collection.media, на которые ссылаются поля заметки
    (<img src>, <audio>/<video>/<source>/<object>, [sound:...]). Удалённые
    ссылки (http://...) и несуществующие файлы не считаются.
  • Колода включает свои подколоды — как числа Новые/Изучаемые/Повтор.
  • Заметка попадает в колоду, если в ней лежит хотя бы одна её карточка.
    Текст и каждый медиафайл внутри одной колоды считаются ОДИН раз, даже если
    на файл ссылаются несколько заметок.
"""

from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass, field

from anki.collection import Collection

# Те же теги, что распознаёт сама Anki (rslib/src/text.rs, HTML_MEDIA_TAGS).
_HTML_MEDIA = re.compile(
    r"""<\b(?:img|audio|video|object|source)\b[^>]*?\b(?:src|data)\s*=\s*
        (?:"([^"]+)"|'([^']+)'|([^\s>]+))""",
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)
_SOUND = re.compile(r"\[sound:(.+?)\]")
_REMOTE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def media_refs(text: str) -> set[str]:
    """Имена локальных медиафайлов, упомянутых в тексте поля(ей)."""
    names: set[str] = set()
    for match in _HTML_MEDIA.finditer(text):
        name = next(g for g in match.groups() if g)
        names.add(html.unescape(name))
    for match in _SOUND.finditer(text):
        names.add(html.unescape(match.group(1)))
    return {n for n in names if n and not _REMOTE.match(n)}


@dataclass
class DeckSize:
    text: int = 0  # байты текста полей
    media: int = 0  # байты медиафайлов (каждый файл один раз)
    media_files: int = 0  # сколько файлов
    notes: int = 0  # сколько заметок

    @property
    def total(self) -> int:
        return self.text + self.media


@dataclass
class _NoteInfo:
    text: int
    files: frozenset[str] = field(default_factory=frozenset)


def media_file_sizes(media_dir: str) -> dict[str, int]:
    """Размеры всех файлов папки медиа одним проходом (быстро даже для 60 тыс.)."""
    sizes: dict[str, int] = {}
    try:
        with os.scandir(media_dir) as it:
            for entry in it:
                if entry.is_file():
                    sizes[entry.name] = entry.stat().st_size
    except FileNotFoundError:
        pass
    return sizes


def compute_deck_sizes(col: Collection) -> dict[int, DeckSize]:
    """Размер каждой колоды (с подколодами): {deck_id: DeckSize}."""
    file_sizes = media_file_sizes(col.media.dir())

    # 1) Каждая заметка: размер текста и набор её медиафайлов (существующих).
    notes: dict[int, _NoteInfo] = {}
    for nid, flds in col.db.execute("select id, flds from notes"):
        files = frozenset(f for f in media_refs(flds) if f in file_sizes)
        # Разделитель полей \x1f — служебный, в размер текста не входит.
        notes[nid] = _NoteInfo(text=len(flds.replace("\x1f", "").encode("utf-8")), files=files)

    # 2) Какие заметки лежат в каждой колоде напрямую (без подколод).
    direct: dict[int, set[int]] = {}
    for did, nid in col.db.execute("select distinct did, nid from cards"):
        direct.setdefault(did, set()).add(nid)

    # 3) Подколоды: колода "A::B" входит в "A". Собираем по именам.
    names = {d.id: d.name for d in col.decks.all_names_and_ids()}
    children: dict[int, list[int]] = {did: [] for did in names}
    by_name = {name: did for did, name in names.items()}
    for did, name in names.items():
        if "::" in name:
            parent = by_name.get(name.rsplit("::", 1)[0])
            if parent is not None:
                children[parent].append(did)

    result: dict[int, DeckSize] = {}

    def subtree_notes(did: int) -> set[int]:
        acc = set(direct.get(did, ()))
        for child in children.get(did, ()):
            acc |= subtree_notes(child)
        return acc

    for did in names:
        nids = subtree_notes(did)
        files: set[str] = set()
        text = 0
        for nid in nids:
            info = notes.get(nid)
            if info is None:
                continue
            text += info.text
            files |= info.files
        result[did] = DeckSize(
            text=text,
            media=sum(file_sizes[f] for f in files),
            media_files=len(files),
            notes=len(nids),
        )
    return result


def size_parts(num: int, russian: bool) -> tuple[str, str]:
    """1536 → («1,5», «КБ»). Дробная часть только у чисел меньше 100."""
    units = ["Б", "КБ", "МБ", "ГБ"] if russian else ["B", "KB", "MB", "GB"]
    value = float(num)
    unit = 0
    while value >= 1024 and unit < len(units) - 1:
        value /= 1024
        unit += 1
    text = f"{value:.0f}" if unit == 0 or value >= 100 else f"{value:.1f}"
    if russian:
        text = text.replace(".", ",")
    return text, units[unit]


def format_size(num: int, russian: bool) -> str:
    """1536 → «1,5 КБ» / «1.5 KB»."""
    return " ".join(size_parts(num, russian))


_UNIT_BYTES = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_PARSE_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*([KMGT]?B)\s*$", re.IGNORECASE)


def parse_size(text: str) -> int | None:
    """«10 MB» / «1,5 gb» → байты; пустая строка или ошибка → None (без верхней границы)."""
    match = _PARSE_RE.match(text or "")
    if not match:
        return None
    number = float(match.group(1).replace(",", "."))
    return int(number * _UNIT_BYTES[match.group(2).upper()])

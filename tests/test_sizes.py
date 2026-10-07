"""Тесты подсчёта размеров на временной коллекции Anki. Запуск: run_tests.bat."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

from anki.collection import Collection

# sizes.py импортируем напрямую, минуя __init__.py (тот требует GUI Anki).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "deck_size_column"))
import sizes  # noqa: E402


class MediaRefsTest(unittest.TestCase):
    def test_tags_and_sound(self) -> None:
        text = (
            '<img src="a.png"> <img src=\'b c.jpg\'> <IMG SRC=d.gif>'
            '<video src="v.mp4"></video><audio src="x&amp;y.mp3"></audio>'
            "[sound:s.mp3] <img src=\"https://example.com/r.png\">"
        )
        self.assertEqual(
            sizes.media_refs(text),
            {"a.png", "b c.jpg", "d.gif", "v.mp4", "x&y.mp3", "s.mp3"},
        )

    def test_format(self) -> None:
        self.assertEqual(sizes.format_size(512, True), "512 Б")
        self.assertEqual(sizes.format_size(1536, True), "1,5 КБ")
        self.assertEqual(sizes.format_size(150 * 1024 * 1024, False), "150 MB")


class DeckSizesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.col = Collection(os.path.join(self.tmp.name, "collection.anki2"))
        self.basic = self.col.models.by_name("Basic")
        self.parent = self.col.decks.id("P")
        self.child = self.col.decks.id("P::C")
        self.other = self.col.decks.id("O")

    def tearDown(self) -> None:
        self.col.close()
        self.tmp.cleanup()

    def media(self, name: str, size: int) -> None:
        with open(os.path.join(self.col.media.dir(), name), "wb") as f:
            f.write(b"x" * size)

    def add(self, front: str, back: str, deck: int) -> None:
        note = self.col.new_note(self.basic)
        note["Front"], note["Back"] = front, back
        self.col.add_note(note, deck)

    def test_parent_includes_child_and_media_counted_once(self) -> None:
        self.media("big.png", 1000)
        self.media("s.mp3", 300)
        self.add("ab", '<img src="big.png">', self.parent)  # текст 2 + 18
        self.add("cd", '<img src="big.png">[sound:s.mp3]', self.child)
        self.add("ef", "gh", self.other)
        res = sizes.compute_deck_sizes(self.col)

        child = res[self.child]
        self.assertEqual(child.media, 1300)
        self.assertEqual(child.media_files, 2)
        self.assertEqual(child.notes, 1)

        parent = res[self.parent]
        # big.png на два раза не считается: 1000 + 300.
        self.assertEqual(parent.media, 1300)
        self.assertEqual(parent.notes, 2)
        self.assertEqual(parent.text, res[self.child].text + len('ab<img src="big.png">'))

        self.assertEqual(res[self.other].media, 0)
        self.assertEqual(res[self.other].text, 4)

    def test_missing_files_ignored(self) -> None:
        self.add("a", '<img src="nope.png">', self.other)
        self.assertEqual(sizes.compute_deck_sizes(self.col)[self.other].media, 0)

    def test_empty_deck(self) -> None:
        empty = self.col.decks.id("Empty")
        self.assertEqual(sizes.compute_deck_sizes(self.col)[empty].total, 0)


if __name__ == "__main__":
    unittest.main()

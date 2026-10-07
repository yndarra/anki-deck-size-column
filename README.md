# Deck List Tweaks: Size Column, Short Headers, Wrapped Names

An Anki add-on for the deck list on the main screen. It does three things, and each one can be turned off:

- **Size column.** Shows how much each deck takes: note text plus the media files its notes use. Subdecks are included, like the New / Learn / Due counts. Hover a cell to see text, media, number of files and notes separately. A media file is counted once per deck, even if several notes use it.
- **Custom column headers.** For example, short names like `Learn.` / `Due` (or `Изуч.` / `Повтор`) instead of the long default ones.
- **Wrapped deck names.** A long deck name wraps onto new lines inside a fixed-width column, like on AnkiMobile/AnkiDroid but without "…". It no longer stretches the whole table. Wrapped lines start under the name, not under the indent.

## Settings
**Tools → Deck list settings…** or Tools → Add-ons → *Deck List Tweaks* → **Config**. Changes apply immediately.

- size column on/off and its header;
- headers for Deck / New / Learn / Due (empty = Anki's own text);
- name wrapping on/off and the name column width (`20em`, `300px`, …).

## How it works
- The add-on does not replace Anki's deck list HTML. It adds a small script that edits the finished table, so it works alongside other add-ons.
- Sizes are calculated in the background (about 0.5 s for 50,000 notes / 1,000 decks) and cached. They are recalculated only when notes, cards, decks or the media folder change.

## Development
`run_tests.bat` runs tests against a real temporary collection (`pip install anki`). `build.bat` builds `dist/deck_list_tweaks.ankiaddon`. Requires Anki 23.10+. Tested with 26.09.

---

# Список колод: размер, короткие заголовки, перенос названий (RU)

- **Столбец «Размер»**: текст + медиа каждой колоды вместе с подколодами. Подсказка при наведении показывает текст, медиа, число файлов и записей. Файл, нужный нескольким записям, считается один раз.
- **Свои заголовки столбцов**, например «Изуч.» и «Повтор» вместо «Изучаемые» и «К повторению».
- **Перенос длинных названий**: название переносится на следующие строки внутри столбца фиксированной ширины, без троеточия, и больше не растягивает таблицу.

Настройки: **Инструменты → Настройки списка колод…** Изменения применяются сразу.

## License
MIT

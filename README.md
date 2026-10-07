# Deck Size Column

An Anki add-on that adds a **Size** column to the deck list on the main screen, after New / Learn / Due.

- Size = note text + media files used by those notes, **including subdecks** (like the New / Learn / Due counts).
- Hover a cell to see text, media, number of files and notes separately.
- A media file used by several notes is counted **once** per deck.
- Sizes are calculated in the background (about 0.5 s for 50,000 notes / 1,000 decks) and cached. They are recalculated only when notes, cards, decks or the media folder change.
- Styled like [Note Size](https://ankiweb.net/shared/info/1188705668): a colored badge with the number and unit in a monospace font. By default the color changes **smoothly** with size: green up to 10 MB, then orange by 100 MB, red by 1 GB, and it darkens to **black by 2 GB** (black above that). The gradient uses a log scale, so 100 MB and 900 MB look clearly different. Light and dark themes have separate colors, and the text color adapts to the badge.
- Settings (Tools → Add-ons → Config): the column header, color points (size + color for each theme; add/remove points, click a color cell to pick) and smooth gradient vs. steps.

It does not rebuild Anki's deck list. It only adds its own cells to the finished table, so it works with other deck-list add-ons, including [Deck List Column Headers](https://github.com/yndarra/anki-deck-list-headers) and [Wrap Long Deck Names](https://github.com/yndarra/anki-wrap-deck-names).

## Development
`run_tests.bat` runs tests against a real temporary collection (`pip install anki`). `build.bat` builds `dist/deck_size_column.ankiaddon`. Requires Anki 23.10+. Tested with 26.09.

---

# Размер колоды (RU)

Столбец **«Размер»** в списке колод: текст записей + медиафайлы, с подколодами. При наведении видно отдельно текст, медиа, число файлов и записей. Файл, нужный нескольким записям, считается один раз. Считается в фоне и пересчитывается только после изменений. Оформление как в Note Size: цветная плашка, цвет **плавно** меняется с размером: до 10 МБ зелёный, к 100 МБ оранжевый, к 1 ГБ красный, к 2 ГБ темнеет до **чёрного** (дальше чёрный). Шкала логарифмическая, поэтому 100 МБ и 900 МБ хорошо различаются. Отдельные цвета для светлой и тёмной темы, цвет текста подстраивается под плашку. В настройках (Инструменты → Дополнения → Config) задаются заголовок, цветовые точки (размер + цвета, точки можно добавлять и удалять) и режим: градиент или ступеньки.

## License
MIT

# Deck Size Column

An Anki add-on that adds a **Size** column to the deck list on the main screen, after New / Learn / Due.

- Size = note text + media files used by those notes, **including subdecks** (like the New / Learn / Due counts).
- Hover a cell to see text, media, number of files and notes separately.
- A media file used by several notes is counted **once** per deck.
- Sizes are calculated in the background (about 0.5 s for 50,000 notes / 1,000 decks) and cached. They are recalculated only when notes, cards, decks or the media folder change.
- Styled like [Note Size](https://ankiweb.net/shared/info/1188705668): a colored badge by size, with the number and unit in a monospace font. Default levels: green up to 10 MB, orange up to 100 MB, red above. There are separate colors for the light and dark theme.
- Settings (Tools → Add-ons → Config): the column header and color levels. You can add or remove levels, set the size limits and pick colors (click a color cell).

It does not rebuild Anki's deck list. It only adds its own cells to the finished table, so it works with other deck-list add-ons, including [Deck List Column Headers](https://github.com/yndarra/anki-deck-list-headers) and [Wrap Long Deck Names](https://github.com/yndarra/anki-wrap-deck-names).

## Development
`run_tests.bat` runs tests against a real temporary collection (`pip install anki`). `build.bat` builds `dist/deck_size_column.ankiaddon`. Requires Anki 23.10+. Tested with 26.09.

---

# Размер колоды (RU)

Столбец **«Размер»** в списке колод: текст записей + медиафайлы, с подколодами. При наведении видно отдельно текст, медиа, число файлов и записей. Файл, нужный нескольким записям, считается один раз. Считается в фоне и пересчитывается только после изменений. Оформление как в Note Size: цветная плашка по размеру (по умолчанию до 10 МБ зелёная, до 100 МБ оранжевая, больше — красная), отдельные цвета для светлой и тёмной темы. В настройках (Инструменты → Дополнения → Config) задаются заголовок и цветовые уровни: границы и цвета, уровни можно добавлять и удалять.

## License
MIT

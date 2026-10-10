<b>Adds a "Size" column to the deck list: note text + media of each deck, including subdecks.</b>

<ul>
<li>Size = note text + the media files those notes use, including subdecks (like the New / Learn / Due counts).</li>
<li>Hover a cell to see text, media, number of files and notes separately.</li>
<li>A media file used by several notes is counted once per deck.</li>
<li>Calculated in the background (≈0.5 s for 50k notes / 1,000 decks) and cached. It is recalculated only when notes, cards, decks or the media folder change.</li>
<li>Styled like Note Size: a colored badge whose color changes <b>smoothly</b> with size (log scale). Default: grey for tiny decks (≤100 KB) → green by 10 MB → yellow by 30 MB → orange by 100 MB → red by 1 GB → black by 2 GB. Light and dark themes have separate colors, and the text color adapts to the badge.</li>
<li>Settings window (Config button): the column header, color points (size + colors, add/remove, click to pick a color) and gradient vs. steps. Russian and English interface.</li>
</ul>

It does not rebuild Anki's deck list. It only adds its own cells, so it works with other deck-list add-ons. Companion add-ons: <a href="https://github.com/yndarra/anki-deck-list-headers">Deck List Column Headers</a> (short column names) and <a href="https://github.com/yndarra/anki-wrap-deck-names">Wrap Long Deck Names</a>.

Source code and tests: <a href="https://github.com/yndarra/anki-deck-size-column">github.com/yndarra/anki-deck-size-column</a>

<i>RU: столбец «Размер» в списке колод (текст + медиа, с подколодами).</i>

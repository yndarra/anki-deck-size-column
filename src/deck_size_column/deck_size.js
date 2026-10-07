// Deck Size Column — столбец «Размер» в списке колод на главном экране.
// Подставляется в страницу при каждой отрисовке списка; перед ним Python задаёт
//   window.DSC_HEADER — заголовок столбца;
//   window.DSC_STOPS — цветовые точки [{size: байты, light, dark}] по возрастанию или [];
//   window.DSC_GRADIENT — true: цвет плавно перетекает между точками, false: ступеньками;
//   window.DSC_SIZES  — {deck_id: [число, единица, подсказка, байты]}.
//
// Оформление как в Note Size: цветная плашка по размеру, число и единица
// моноширинным шрифтом. Цвет плашки берётся для текущей темы Anki
// (тёмную тему Anki помечает классами night-mode на <html> и nightMode на <body>).
//
// Совместимость с другими дополнениями списка колод: таблицу самой Anki не
// пересобираем, только добавляем свои ячейки с классом dsc-size — перед
// шестерёнкой (td.opts / th.optscol). Названия столбцов и ячейки названий
// колод не трогаем, поэтому порядок запуска с другими скриптами не важен.
(function () {
    "use strict";

    function addColumn() {
        const first = document.querySelector("table th");
        const row = first ? first.parentElement : null;
        if (!row || row.querySelector("th.dsc-size")) return; // уже добавлено
        const th = document.createElement("th");
        th.className = "count dsc-size";
        th.textContent = window.DSC_HEADER || "Size";
        row.insertBefore(th, row.querySelector("th.optscol"));

        document.querySelectorAll("tr.deck").forEach((tr) => {
            const td = document.createElement("td");
            td.className = "dsc-size";
            td.setAttribute("align", "end");
            tr.insertBefore(td, tr.querySelector("td.opts"));
        });
        // Строка для перетаскивания колод на верхний уровень — на столбец шире.
        document.querySelectorAll("tr.top-level-drag-row td").forEach((td) => {
            td.colSpan = (td.colSpan || 1) + 1;
        });
    }

    // Любой CSS-цвет (имя, #hex, rgb()) → [r, g, b] через вычисленный стиль.
    const rgbCache = {};
    function toRgb(color) {
        if (!(color in rgbCache)) {
            const probe = document.createElement("span");
            probe.style.color = color;
            document.body.appendChild(probe);
            const m = getComputedStyle(probe).color.match(/\d+(\.\d+)?/g) || [0, 0, 0];
            probe.remove();
            rgbCache[color] = m.slice(0, 3).map(Number);
        }
        return rgbCache[color];
    }

    function isDarkTheme() {
        // Anki помечает тёмную тему и на <html> (night-mode), и на <body> (nightMode).
        return (
            document.documentElement.classList.contains("night-mode") ||
            document.body.classList.contains("nightMode")
        );
    }

    // Цвет плашки для размера → [r, g, b] или null (цвета выключены).
    function colorFor(bytes) {
        const stops = window.DSC_STOPS || [];
        if (!stops.length) return null;
        const key = isDarkTheme() ? "dark" : "light";
        if (bytes <= stops[0].size) return toRgb(stops[0][key]);
        for (let i = 0; i < stops.length - 1; i++) {
            const a = stops[i], b = stops[i + 1];
            if (bytes >= b.size) continue;
            if (!window.DSC_GRADIENT) return toRgb(a[key]); // ступенька
            // Доля пути между точками — по логарифму размера: так 100 МБ и
            // 900 МБ различаются так же заметно, как 1 МБ и 9 МБ.
            const lo = Math.log(Math.max(a.size, 1)), hi = Math.log(b.size);
            const t = hi > lo ? (Math.log(Math.max(bytes, 1)) - lo) / (hi - lo) : 1;
            const ca = toRgb(a[key]), cb = toRgb(b[key]);
            return ca.map((v, j) => Math.round(v + (cb[j] - v) * Math.min(Math.max(t, 0), 1)));
        }
        return toRgb(stops[stops.length - 1][key]); // выше последней точки
    }

    // Яркость фона → тёмный или светлый текст, чтобы цифры читались на любой плашке.
    function isDark(rgb) {
        const [r, g, b] = rgb;
        return 0.299 * r + 0.587 * g + 0.114 * b < 140;
    }

    function span(cls, text) {
        const el = document.createElement("span");
        el.className = cls;
        el.textContent = text;
        return el;
    }

    // Заполняет ячейки. Python вызывает её ещё раз, когда фоновый подсчёт готов.
    window.dscApplySizes = function (sizes) {
        window.DSC_SIZES = sizes;
        document.querySelectorAll("tr.deck").forEach((tr) => {
            const td = tr.querySelector("td.dsc-size");
            if (!td) return;
            td.textContent = "";
            const item = sizes && sizes[tr.id];
            if (!item) {
                td.appendChild(span("dsc-wait", "…"));
                td.title = "";
                return;
            }
            const [number, unit, tip, bytes] = item;
            td.title = tip;
            const badge = span("dsc-badge", "");
            badge.appendChild(span("dsc-num", number));
            badge.appendChild(document.createTextNode(" "));
            badge.appendChild(span("dsc-unit", unit));
            const rgb = bytes > 0 ? colorFor(bytes) : null;
            if (rgb) {
                badge.style.backgroundColor = `rgb(${rgb.join(",")})`;
                const darkBg = isDark(rgb);
                badge.style.color = darkBg ? "#f2f2f2" : "#1a1a1a";
                badge.classList.toggle("dsc-dark-bg", darkBg);
            } else {
                badge.classList.add("dsc-plain");
            }
            if (bytes === 0) badge.classList.add("dsc-empty");
            td.appendChild(badge);
        });
    };

    addColumn();
    window.dscApplySizes(window.DSC_SIZES || {});
})();

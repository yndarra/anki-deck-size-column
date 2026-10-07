// Deck Size Column — столбец «Размер» в списке колод на главном экране.
// Подставляется в страницу при каждой отрисовке списка; перед ним Python задаёт
//   window.DSC_HEADER — заголовок столбца;
//   window.DSC_LEVELS — цветовые уровни [{max: байты|null, light, dark}] или [];
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

    // Цвет плашки для размера: первый уровень, чей max больше размера.
    function colorFor(bytes) {
        const levels = window.DSC_LEVELS || [];
        // Anki помечает тёмную тему и на <html> (night-mode), и на <body> (nightMode).
        const dark =
            document.documentElement.classList.contains("night-mode") ||
            document.body.classList.contains("nightMode");
        for (const level of levels) {
            if (level.max === null || bytes < level.max) {
                return dark ? level.dark : level.light;
            }
        }
        return "";
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
            const color = bytes > 0 ? colorFor(bytes) : "";
            if (color) badge.style.backgroundColor = color;
            else badge.classList.add("dsc-plain");
            if (bytes === 0) badge.classList.add("dsc-empty");
            td.appendChild(badge);
        });
    };

    addColumn();
    window.dscApplySizes(window.DSC_SIZES || {});
})();

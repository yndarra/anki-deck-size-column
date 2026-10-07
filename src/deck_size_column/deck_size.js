// Deck Size Column — столбец «Размер» в списке колод на главном экране.
// Подставляется в страницу при каждой отрисовке списка; перед ним Python задаёт
// window.DSC_HEADER (заголовок) и window.DSC_SIZES ({deck_id: [текст, подсказка, байты]}).
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

    // Заполняет ячейки. Python вызывает её ещё раз, когда фоновый подсчёт готов.
    window.dscApplySizes = function (sizes) {
        window.DSC_SIZES = sizes;
        document.querySelectorAll("tr.deck").forEach((tr) => {
            const td = tr.querySelector("td.dsc-size");
            if (!td) return;
            const item = sizes && sizes[tr.id];
            td.textContent = item ? item[0] : "…";
            td.title = item ? item[1] : "";
            td.classList.toggle("dsc-empty", !!item && item[2] === 0);
        });
    };

    addColumn();
    window.dscApplySizes(window.DSC_SIZES || {});
})();

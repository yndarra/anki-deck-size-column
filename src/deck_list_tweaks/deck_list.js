// Deck List Tweaks — правки списка колод на главном экране.
// Этот файл подставляется в страницу списка колод при каждой отрисовке;
// перед ним Python задаёт window.DLT_CONFIG и (если уже посчитано) window.DLT_SIZES.
//
// Что делает:
//  1) переименовывает заголовки столбцов (Колода / Новые / Изучаемые / К повторению);
//  2) добавляет столбец «Размер» перед шестерёнкой;
//  3) переносит длинные названия колод на новые строки вместо растягивания таблицы.
(function () {
    "use strict";
    const cfg = window.DLT_CONFIG || {};

    // Строка заголовков — первая строка таблицы, в ней <th>.
    function headerRow() {
        const th = document.querySelector("table th");
        return th ? th.parentElement : null;
    }

    // --- 1. Заголовки ----------------------------------------------------
    function renameHeaders() {
        const row = headerRow();
        if (!row) return;
        const cells = row.querySelectorAll("th");
        // Порядок у Anki: Колода, Новые, Изучаемые, К повторению, (шестерёнка).
        const texts = [cfg.header_deck, cfg.header_new, cfg.header_learn, cfg.header_due];
        texts.forEach((text, i) => {
            if (text && cells[i]) cells[i].textContent = text;
        });
    }

    // --- 2. Столбец размера ----------------------------------------------
    function addSizeColumn() {
        if (!cfg.size_column) return;
        const row = headerRow();
        if (!row || row.querySelector("th.dlt-size")) return;
        const th = document.createElement("th");
        th.className = "count dlt-size";
        th.textContent = cfg.size_header;
        row.insertBefore(th, row.querySelector("th.optscol"));

        document.querySelectorAll("tr.deck").forEach((tr) => {
            const td = document.createElement("td");
            td.className = "dlt-size";
            td.setAttribute("align", "end");
            tr.insertBefore(td, tr.querySelector("td.opts"));
        });
        // Строка-«ловушка» для перетаскивания колод на верхний уровень.
        document.querySelectorAll("tr.top-level-drag-row td").forEach((td) => {
            td.colSpan = (td.colSpan || 1) + 1;
        });
    }

    // Заполняет ячейки размера. Вызывается и при отрисовке, и позже из Python,
    // когда фоновый подсчёт закончится: window.dltApplySizes({id: [текст, подсказка]}).
    window.dltApplySizes = function (sizes) {
        window.DLT_SIZES = sizes;
        document.querySelectorAll("tr.deck").forEach((tr) => {
            const td = tr.querySelector("td.dlt-size");
            if (!td) return;
            const item = sizes && sizes[tr.id];
            td.textContent = item ? item[0] : "…";
            td.title = item ? item[1] : "";
            td.classList.toggle("dlt-empty", !!item && item[2] === 0);
        });
    };

    // --- 3. Перенос длинных названий -------------------------------------
    function wrapNames() {
        if (!cfg.wrap_names) return;
        document.querySelectorAll("td.decktd").forEach((td) => {
            if (td.querySelector(".dlt-name")) return;
            // Отступ (&nbsp;), значок свёртки и ссылку кладём в flex-строку:
            // так продолжение названия переносится под начало названия,
            // а не под отступ слева.
            const box = document.createElement("div");
            box.className = "dlt-name";
            const indent = document.createElement("span");
            indent.className = "dlt-indent";
            while (td.firstChild && td.firstChild.nodeType === Node.TEXT_NODE) {
                indent.appendChild(td.firstChild);
            }
            box.appendChild(indent);
            while (td.firstChild) box.appendChild(td.firstChild);
            td.appendChild(box);
        });
    }

    renameHeaders();
    addSizeColumn();
    wrapNames();
    window.dltApplySizes(window.DLT_SIZES || {});
})();

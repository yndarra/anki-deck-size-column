"""Окно настроек (кнопка Config в Инструменты → Дополнения).

Заголовок столбца и цветовые уровни, как в Note Size: таблица «до какого
размера → цвет для светлой темы → цвет для тёмной темы». Щелчок по ячейке
цвета открывает выбор цвета. У последнего уровня граница пустая — «и больше».
"""

from __future__ import annotations

from collections.abc import Callable

from aqt.qt import (
    QBrush,
    QCheckBox,
    QColor,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    Qt,
)

from . import sizes
from .common import DEFAULT_LEVELS, DEFAULTS, get_config, save_config, t

_COL_MAX, _COL_LIGHT, _COL_DARK = 0, 1, 2


def _color_item(name: str) -> QTableWidgetItem:
    """Ячейка-образец цвета: фон — сам цвет, текст — его имя."""
    item = QTableWidgetItem(name)
    color = QColor(name)
    if color.isValid():
        item.setBackground(QBrush(color))
        # Читаемый текст поверх и светлого, и тёмного фона.
        item.setForeground(QBrush(QColor("black" if color.lightness() > 128 else "white")))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None, on_saved: Callable[[dict], None]) -> None:
        super().__init__(parent)
        self.on_saved = on_saved
        self.setWindowTitle(t("dlg_title"))
        self.setMinimumWidth(520)
        form = QFormLayout(self)

        hint = QLabel(t("hint"))
        hint.setWordWrap(True)
        form.addRow(hint)

        cfg = get_config()
        self.header = QLineEdit(str(cfg["header"]))
        # Подсказка в пустом поле — текст по умолчанию.
        self.header.setPlaceholderText(t("size"))
        form.addRow(t("header"), self.header)

        self.colors = QCheckBox(t("colors"))
        self.colors.setChecked(bool(cfg["colors_enabled"]))
        self.colors.toggled.connect(self._update_enabled)
        form.addRow(self.colors)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([t("col_max"), t("col_light"), t("col_dark")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self._pick_color)
        form.addRow(self.table)

        row_buttons = QHBoxLayout()
        self.add_btn = QPushButton(t("add"))
        self.add_btn.clicked.connect(self._add_level)
        self.remove_btn = QPushButton(t("remove"))
        self.remove_btn.clicked.connect(self._remove_level)
        row_buttons.addWidget(self.add_btn)
        row_buttons.addWidget(self.remove_btn)
        row_buttons.addStretch()
        form.addRow(row_buttons)
        levels_hint = QLabel(t("levels_hint"))
        levels_hint.setWordWrap(True)
        form.addRow(levels_hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        reset = buttons.addButton(t("defaults"), QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(self._reset)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._fill(cfg["levels"])
        self._update_enabled()

    # --- таблица уровней --------------------------------------------------

    def _fill(self, levels: list[dict]) -> None:
        self.table.setRowCount(0)
        for level in levels:
            self._append(str(level.get("max_size") or ""), level.get("light_color") or "",
                         level.get("dark_color") or "")
        self._mark_last()

    def _append(self, max_size: str, light: str, dark: str) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, _COL_MAX, QTableWidgetItem(max_size))
        self.table.setItem(row, _COL_LIGHT, _color_item(light))
        self.table.setItem(row, _COL_DARK, _color_item(dark))

    def _mark_last(self) -> None:
        """У последнего уровня границы нет: показываем «и больше», правка запрещена."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, _COL_MAX)
            last = row == self.table.rowCount() - 1
            if last:
                item.setText(t("and_more"))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            else:
                if item.text() == t("and_more"):
                    item.setText("")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

    def _add_level(self) -> None:
        # Новый уровень вставляется перед последним, с границей вдвое больше предыдущей.
        rows = self.table.rowCount()
        prev = sizes.parse_size(self.table.item(rows - 2, _COL_MAX).text()) if rows >= 2 else None
        new_max = sizes.format_size((prev or 10 * 1024**2) * 2, False)
        self.table.insertRow(rows - 1)
        self.table.setItem(rows - 1, _COL_MAX, QTableWidgetItem(new_max))
        self.table.setItem(rows - 1, _COL_LIGHT, _color_item("LightYellow"))
        self.table.setItem(rows - 1, _COL_DARK, _color_item("Olive"))
        self._mark_last()
        self._update_enabled()

    def _remove_level(self) -> None:
        if self.table.rowCount() <= 1:
            return
        row = self.table.currentRow()
        self.table.removeRow(row if row >= 0 else self.table.rowCount() - 1)
        self._mark_last()
        self._update_enabled()

    def _pick_color(self, row: int, column: int) -> None:
        if column not in (_COL_LIGHT, _COL_DARK):
            return
        current = QColor(self.table.item(row, column).text())
        color = QColorDialog.getColor(current, self)
        if color.isValid():
            self.table.setItem(row, column, _color_item(color.name()))

    def _update_enabled(self) -> None:
        on = self.colors.isChecked()
        self.table.setEnabled(on)
        self.add_btn.setEnabled(on)
        self.remove_btn.setEnabled(on and self.table.rowCount() > 1)

    def _levels(self) -> list[dict]:
        levels = []
        last = self.table.rowCount() - 1
        for row in range(self.table.rowCount()):
            text = "" if row == last else self.table.item(row, _COL_MAX).text().strip()
            if row != last and sizes.parse_size(text) is None:
                continue  # непонятная граница — уровень пропускаем
            levels.append({
                "max_size": text,
                "light_color": self.table.item(row, _COL_LIGHT).text(),
                "dark_color": self.table.item(row, _COL_DARK).text(),
            })
        # Уровни по возрастанию границы; последний («и больше») — в конце.
        bounded = sorted(levels[:-1], key=lambda lv: sizes.parse_size(lv["max_size"]) or 0)
        return bounded + levels[-1:]

    # --- кнопки -----------------------------------------------------------

    def _reset(self) -> None:
        self.header.setText(str(DEFAULTS["header"]))
        self.colors.setChecked(True)
        self._fill(DEFAULT_LEVELS)
        self._update_enabled()

    def _save(self) -> None:
        cfg = get_config()
        cfg["header"] = self.header.text().strip()
        cfg["colors_enabled"] = self.colors.isChecked()
        cfg["levels"] = self._levels()
        save_config(cfg)
        self.on_saved(cfg)
        self.accept()

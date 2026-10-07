"""Окно настроек (кнопка Config в Инструменты → Дополнения).

Заголовок столбца и цветовые точки: таблица «с какого размера → цвет для
светлой темы → цвет для тёмной темы». Щелчок по ячейке цвета открывает выбор
цвета. Галка «градиент»: цвет плавно перетекает между точками; без неё —
меняется ступенькой, как в Note Size.
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
from .common import DEFAULT_STOPS, DEFAULTS, get_config, save_config, t

_COL_SIZE, _COL_LIGHT, _COL_DARK = 0, 1, 2


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
        self.setMinimumWidth(540)
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

        self.gradient = QCheckBox(t("gradient"))
        self.gradient.setChecked(bool(cfg["gradient"]))
        form.addRow(self.gradient)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([t("col_max"), t("col_light"), t("col_dark")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self._pick_color)
        form.addRow(self.table)

        row_buttons = QHBoxLayout()
        self.add_btn = QPushButton(t("add"))
        self.add_btn.clicked.connect(self._add_stop)
        self.remove_btn = QPushButton(t("remove"))
        self.remove_btn.clicked.connect(self._remove_stop)
        row_buttons.addWidget(self.add_btn)
        row_buttons.addWidget(self.remove_btn)
        row_buttons.addStretch()
        form.addRow(row_buttons)
        stops_hint = QLabel(t("levels_hint"))
        stops_hint.setWordWrap(True)
        form.addRow(stops_hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        reset = buttons.addButton(t("defaults"), QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(self._reset)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._fill(cfg["stops"])
        self._update_enabled()

    # --- таблица точек ----------------------------------------------------

    def _fill(self, stops: list[dict]) -> None:
        self.table.setRowCount(0)
        for stop in stops:
            self._append(str(stop.get("size") or ""), stop.get("light_color") or "",
                         stop.get("dark_color") or "")

    def _append(self, size: str, light: str, dark: str) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, _COL_SIZE, QTableWidgetItem(size))
        self.table.setItem(row, _COL_LIGHT, _color_item(light))
        self.table.setItem(row, _COL_DARK, _color_item(dark))

    def _add_stop(self) -> None:
        # Новая точка — в конец, с размером вдвое больше последнего; при сохранении
        # точки всё равно сортируются по размеру.
        last = 0
        for row in range(self.table.rowCount()):
            last = max(last, sizes.parse_size(self.table.item(row, _COL_SIZE).text()) or 0)
        self._append(sizes.format_size(max(last * 2, 1024**2), False), "Purple", "Indigo")
        self._update_enabled()

    def _remove_stop(self) -> None:
        if self.table.rowCount() <= 1:
            return
        row = self.table.currentRow()
        self.table.removeRow(row if row >= 0 else self.table.rowCount() - 1)
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
        for widget in (self.gradient, self.table, self.add_btn):
            widget.setEnabled(on)
        self.remove_btn.setEnabled(on and self.table.rowCount() > 1)

    def _stops(self) -> list[dict]:
        stops = []
        for row in range(self.table.rowCount()):
            text = self.table.item(row, _COL_SIZE).text().strip()
            if sizes.parse_size(text) is None:
                continue  # непонятный размер — точку пропускаем
            stops.append({
                "size": text,
                "light_color": self.table.item(row, _COL_LIGHT).text(),
                "dark_color": self.table.item(row, _COL_DARK).text(),
            })
        return sorted(stops, key=lambda s: sizes.parse_size(s["size"]) or 0)

    # --- кнопки -----------------------------------------------------------

    def _reset(self) -> None:
        self.header.setText(str(DEFAULTS["header"]))
        self.colors.setChecked(True)
        self.gradient.setChecked(True)
        self._fill(DEFAULT_STOPS)
        self._update_enabled()

    def _save(self) -> None:
        cfg = get_config()
        cfg["header"] = self.header.text().strip()
        cfg["colors_enabled"] = self.colors.isChecked()
        cfg["gradient"] = self.gradient.isChecked()
        cfg["stops"] = self._stops() or get_config()["stops"]
        cfg.pop("levels", None)  # старый формат (до градиента) больше не нужен
        save_config(cfg)
        self.on_saved(cfg)
        self.accept()

"""Окно настроек: столбец размера, заголовки, перенос названий.

После «Сохранить» список колод сразу перерисовывается — перезапуск не нужен.
"""

from __future__ import annotations

from collections.abc import Callable

from aqt.qt import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from .common import DEFAULTS, get_config, save_config, t


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None, on_saved: Callable[[dict], None]) -> None:
        super().__init__(parent)
        self.on_saved = on_saved
        self.setWindowTitle(t("dlg_title"))
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)

        # Размер
        size_box = QGroupBox(t("grp_size"))
        size_form = QFormLayout(size_box)
        self.size_column = QCheckBox(t("show_size"))
        self.size_header = QLineEdit()
        self.size_header.setPlaceholderText(t("size"))
        size_form.addRow(self.size_column)
        size_form.addRow(t("size_header"), self.size_header)
        layout.addWidget(size_box)

        # Заголовки: подсказка в поле — текст, который Anki покажет по умолчанию.
        head_box = QGroupBox(t("grp_headers"))
        head_form = QFormLayout(head_box)
        self.headers: dict[str, QLineEdit] = {}
        for key, label in (
            ("header_deck", "h_deck"),
            ("header_new", "h_new"),
            ("header_learn", "h_learn"),
            ("header_due", "h_due"),
        ):
            edit = QLineEdit()
            edit.setPlaceholderText(t(label))
            head_form.addRow(t(label), edit)
            self.headers[key] = edit
        layout.addWidget(head_box)

        # Перенос
        wrap_box = QGroupBox(t("grp_wrap"))
        wrap_form = QFormLayout(wrap_box)
        self.wrap = QCheckBox(t("wrap"))
        self.width = QLineEdit()
        self.width.setPlaceholderText(t("width_hint"))
        wrap_form.addRow(self.wrap)
        wrap_form.addRow(t("width"), self.width)
        layout.addWidget(wrap_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        reset = buttons.addButton(t("defaults"), QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(lambda: self._load(dict(DEFAULTS)))
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._load(get_config())

    def _load(self, cfg: dict) -> None:
        self.size_column.setChecked(bool(cfg["size_column"]))
        self.size_header.setText(str(cfg["size_header"]))
        for key, edit in self.headers.items():
            edit.setText(str(cfg[key]))
        self.wrap.setChecked(bool(cfg["wrap_names"]))
        self.width.setText(str(cfg["name_width"]))

    def _save(self) -> None:
        cfg = get_config()
        cfg["size_column"] = self.size_column.isChecked()
        cfg["size_header"] = self.size_header.text().strip()
        for key, edit in self.headers.items():
            cfg[key] = edit.text().strip()
        cfg["wrap_names"] = self.wrap.isChecked()
        cfg["name_width"] = self.width.text().strip() or str(DEFAULTS["name_width"])
        save_config(cfg)
        self.on_saved(cfg)
        self.accept()

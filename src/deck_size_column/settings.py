"""Окно настроек (кнопка Config в Инструменты → Дополнения)."""

from __future__ import annotations

from collections.abc import Callable

from aqt.qt import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QWidget

from .common import DEFAULTS, get_config, save_config, t


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None, on_saved: Callable[[dict], None]) -> None:
        super().__init__(parent)
        self.on_saved = on_saved
        self.setWindowTitle(t("dlg_title"))
        self.setMinimumWidth(420)
        form = QFormLayout(self)

        hint = QLabel(t("hint"))
        hint.setWordWrap(True)
        form.addRow(hint)

        self.header = QLineEdit(str(get_config()["header"]))
        # Подсказка в пустом поле — текст по умолчанию.
        self.header.setPlaceholderText(t("size"))
        form.addRow(t("header"), self.header)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        reset = buttons.addButton(t("defaults"), QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(lambda: self.header.setText(str(DEFAULTS["header"])))
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _save(self) -> None:
        cfg = get_config()
        cfg["header"] = self.header.text().strip()
        save_config(cfg)
        self.on_saved(cfg)
        self.accept()

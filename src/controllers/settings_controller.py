import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from src.utils.settings_utils import (
    load_arbitter_name,
    load_resave_rci,
    load_show_btn_resave,
    load_work_directory,
    save_arbitter_name,
    save_resave_rci,
    save_show_btn_resave,
    save_work_directory,
)


class SettingsController:
    def __init__(self, view):
        """
        :param view: экземпляр SettingsTab
        """
        self.view = view

        # Подписка на сигналы View
        self.view.browse_clicked.connect(self.handle_browse_work_dir_clicked)
        self.view.save_clicked.connect(self.handle_save_work_dir_clicked)
        self.view.arbitter_selector.currentTextChanged.connect(self.handle_arbitter_changed)
        self.view.checkbox_resave_rci.stateChanged.connect(self.handle_resave_rci_clicked)
        self.view.checkbox_show_btn_resave.stateChanged.connect(self.handle_show_btn_resave_clicked)
        self.view.aplly_settings_clicked.connect(self.handle_apply_settings_clicked)

        self._load_settings()  # Инициализация рабочего пути

    def handle_browse_work_dir_clicked(self):
        """Рабочая директория - Обзор"""
        folder_path = QFileDialog.getExistingDirectory(self.view, 'Выберите рабочую папку')
        if folder_path:
            self.view.set_work_dir(folder_path)
            save_work_directory(folder_path)  # Автосохранение после выбора

    def handle_save_work_dir_clicked(self):
        """Рабочая директория - Сохранить"""
        folder_path = self.view.get_work_dir()
        if folder_path:
            p = Path(folder_path)
            if not p.exists() or not p.is_dir():
                # Ошибка — папка не валидна
                QMessageBox.warning(self.view, 'Ошибка', 'Указанный путь не является папкой.')
                return

            save_work_directory(folder_path)

            QMessageBox.information(self.view, 'Настройки сохранены', 'Рабочая директория успешно обновлена.')
        else:
            QMessageBox.warning(self.view, 'Ошибка', 'Поле пути к рабочей директории пустое.')

    def handle_arbitter_changed(self, text: str):
        save_arbitter_name(text)
        QMessageBox.information(
            self.view, 'Настройки сохранены', 'Чтобы настройка применилась необходимо перезапустить программу'
        )

    def handle_resave_rci_clicked(self):
        """Пересохранять файлы РЦИ"""
        value = self.view.checkbox_resave_rci.isChecked()
        save_resave_rci(value)

    def handle_show_btn_resave_clicked(self):
        """Показать кнопку Пересохранять файлы"""
        value = self.view.checkbox_show_btn_resave.isChecked()
        save_show_btn_resave(value)
        QMessageBox.information(
            self.view, 'Настройки сохранены', 'Чтобы настройка применилась необходимо перезапустить программу'
        )

    def handle_apply_settings_clicked(self):
        """Применить настройки"""
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def _load_settings(self):
        """Подгрузка настроек при запуске программы"""
        self._load_work_directory()
        self._load_resave_rci()
        self._load_show_btn_resave()
        self._load_arbitter_name()

    def _load_work_directory(self) -> str | None:
        folder_path = load_work_directory()
        if folder_path:
            self.view.set_work_dir(folder_path)

    def _load_arbitter_name(self):
        value = load_arbitter_name()

        self.view.arbitter_selector.blockSignals(True)

        if value == 'А <ФИО>':
            self.view.arbitter_selector.setCurrentIndex(2)

        elif value == 'Арбитр <ФИО>':
            self.view.arbitter_selector.setCurrentIndex(1)

        elif value == '<Номер дела> <ФИО>':
            self.view.arbitter_selector.setCurrentIndex(0)

        self.view.arbitter_selector.blockSignals(False)


    def _load_resave_rci(self):
        value = load_resave_rci()
        if value:
            self.view.checkbox_resave_rci.blockSignals(True)
            self.view.checkbox_resave_rci.setChecked(value)
            self.view.checkbox_resave_rci.blockSignals(False)

    def _load_show_btn_resave(self):
        value = load_show_btn_resave()
        if value:
            self.view.checkbox_show_btn_resave.blockSignals(True)
            self.view.checkbox_show_btn_resave.setChecked(value)
            self.view.checkbox_show_btn_resave.blockSignals(False)

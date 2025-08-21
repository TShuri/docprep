import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from utils.settings_utils import (
    load_work_directory,
    save_work_directory,
)

from utils.templates_utils import save_bank_requisites_directory


class SettingsController:
    def __init__(self, view):
        """
        :param view: экземпляр SettingsTab
        """
        self.view = view
        
        # Подписка на сигналы View
        self.view.save_clicked.connect(self.handle_save_work_dir_clicked)
        self.view.browse_clicked.connect(self.handle_browse_work_dir_clicked)
        self.view.select_bank_clicked.connect(self.handle_browse_bank_requisites_clicked)
        self.view.aplly_settings_clicked.connect(self.handle_apply_settings_clicked)

        self.load_work_directory()  # Инициализация рабочего пути

    def handle_browse_work_dir_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self.view, 'Выберите рабочую папку')
        if folder_path:
            self.view.set_work_dir(folder_path)
            save_work_directory(folder_path)  # Автосохранение после выбора

    def handle_save_work_dir_clicked(self):
        folder_path = self.view.get_work_dir()
        if folder_path:
            p = Path(folder_path)
            if not p.exists() or not p.is_dir():
                self.view.append_log('Указанный путь не является папкой.')
                return
            save_work_directory(folder_path)
            
    def handle_browse_bank_requisites_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self.view, 'Выберите файл с реквизитами банков', '', 'Документы Word (*.docx)')
        if file_path:
            save_bank_requisites_directory(file_path)
            QMessageBox.information(
            self.view,
            "Для применения изменений",
            "Чтобы изменения вступили в силу, нажмите «Применить настройки»."
        )
            
    def handle_apply_settings_clicked(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def load_work_directory(self) -> str | None:
        folder_path = load_work_directory()
        if folder_path:
            self.view.set_work_dir(folder_path)

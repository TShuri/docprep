import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox

import src.core.calculator.utils as rci_utils
from src.core.calculator.logic import Logic
from src.utils.settings_utils import load_resave_rci


class CalculatorController:
    def __init__(self, view):
        self.view = view
        self.view.files_dropped.connect(self.handle_files_dropped)  # <-- drag&drop
        self.view.select_files_clicked.connect(self.handle_select_files)
        self.view.calculate_clicked.connect(self.handle_calculate)
        self.view.reset_clicked.connect(self.handle_reset)
        self.view.resave_clicked.connect(self.handle_resave)

        self.logic = Logic(output_func=self.view.append_text, ask_gp_callback=self.view.ask_gp_callback)
        self.files = []  # список для хранения выбранных файлов

    def handle_files_dropped(self, paths: list[str]):
        new_files = []
        for path in paths:
            if os.path.isdir(path):
                # рекурсивный поиск Excel
                for root, _, files in os.walk(path):
                    for f in files:
                        if f.lower().endswith('.xlsx') and f.startswith('Расчет цены иска'):
                            new_files.append(os.path.join(root, f))
            elif path.lower().endswith('.xlsx') and os.path.basename(path).startswith('Расчет цены иска'):
                new_files.append(path)

        # фильтруем уникальные
        existing_names = {os.path.basename(f) for f in self.files}
        unique_new_files = [f for f in new_files if os.path.basename(f) not in existing_names]

        if unique_new_files:
            self.files.extend(unique_new_files)
            self.view.print_select_files(self.files)

    def handle_select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self.view, 'Выберите файлы Excel', '', 'Excel Files (*.xlsx)')
        if files:
            unique_new_files = [f for f in files if f not in self.files]
            if unique_new_files:
                self.files.extend(unique_new_files)
                self.view.print_select_files(self.files)

    def handle_calculate(self):
        self.view.reset()
        self.view.print_select_files(self.files)

        if not self.files:
            QMessageBox.warning(self.view, 'Ошибка', 'Пожалуйста, выберите файлы для расчета.')
            return

        self.view.append_text('\nРасчет ...')
        result = self.logic.run(files=self.files)

        self.view.update_totals(result)  # <-- отдаём результат во view
        if load_resave_rci():
            logs = rci_utils.resave_files(self.files)
            self.view.append_text(logs)

    def handle_reset(self):
        self.files = []
        self.view.reset()

    def handle_resave(self):
        logs = rci_utils.resave_files(self.files)
        self.view.append_text(logs)

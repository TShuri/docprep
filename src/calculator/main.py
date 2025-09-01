import os
import sys
from pathlib import Path

from openpyxl import load_workbook
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.calculator.logic import Logic


class CalculatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('РЦИ калькулятор')
        self.resize(700, 500)
        self.setAcceptDrops(True)
        self.logic = Logic(output_func=self.append_text, ask_gp_callback=self.ask_gp_callback)
        self.files = []  # список для хранения выбранных файлов
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.btn_select_file = QPushButton('Выбрать файлы', self)
        self.btn_select_file.clicked.connect(self.on_select_file)
        layout.addWidget(self.btn_select_file)

        self.btn_run = QPushButton('Рассчитать', self)
        self.btn_run.clicked.connect(self.on_run)
        layout.addWidget(self.btn_run)

        self.btn_reset = QPushButton('Сброс', self)
        self.btn_reset.clicked.connect(self.on_reset)
        layout.addWidget(self.btn_reset)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText('Перетащите сюда файлы Excel или выберите их кнопкой Выбрать файлы')
        layout.addWidget(self.text_output)

        # === Группа для итогов ===
        self.group_totals = QGroupBox('Итоги (Разбивка)')
        self.totals_layout = QGridLayout()
        self.group_totals.setLayout(self.totals_layout)
        layout.addWidget(self.group_totals)

        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            new_files = []

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if os.path.isdir(path):
                        # Рекурсивно ищем только нужные .xlsx
                        new_files.extend(self.find_calc_xlsx_files(path))
                    elif path.lower().endswith('.xlsx') and os.path.basename(path).startswith('Расчет цены иска'):
                        new_files.append(path)

            # Проверка по имени файла
            existing_names = {os.path.basename(f) for f in self.files}
            unique_new_files = [f for f in new_files if os.path.basename(f) not in existing_names]

            self.print_select_files(unique_new_files)
            event.acceptProposedAction()
        else:
            event.ignore()

    def find_calc_xlsx_files(self, folder_path):
        """Возвращает список .xlsx файлов, начинающихся на 'Расчет цены иска' внутри папки рекурсивно."""
        matched_files = []
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith('.xlsx') and f.startswith('Расчет цены иска'):
                    matched_files.append(os.path.join(root, f))
        return matched_files

    def on_select_file(self):
        """Открывает диалог выбора файлов и добавляет выбранные файлы в список."""
        files, _ = QFileDialog.getOpenFileNames(self, 'Выберите файлы Excel', '', 'Excel Files (*.xlsx)')
        if files:
            unique_new_files = [f for f in files if f not in self.files]
            self.print_select_files(unique_new_files)

    def print_select_files(self, unique_new_files):
        """Выводит список файлов"""
        if unique_new_files:
            start_index = len(self.files) + 1  # начинаем нумерацию с текущего количества файлов + 1
            self.files.extend(unique_new_files)

            for i, f in enumerate(unique_new_files, start=start_index):
                self.append_text(f'[{i}] {os.path.basename(f)}')

    def on_reset(self):
        """Сбросить состояние калькулятора"""
        self.text_output.clear()
        self.files = []
        self.clear_totals()
        self.recreate_totals_group()

    def clear_totals(self):
        """Очищает виджеты из итоговой таблицы"""
        while self.totals_layout.count():
            item = self.totals_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def recreate_totals_group(self):
        """Очищаем и пересоздаём группу итогов"""
        self.layout().removeWidget(self.group_totals)
        self.group_totals.deleteLater()

        self.group_totals = QGroupBox('Итоги (Разбивка)')
        self.totals_layout = QGridLayout()
        self.group_totals.setLayout(self.totals_layout)
        self.layout().addWidget(self.group_totals)

    def append_text(self, msg):
        """Добавляет текст в окно вывода."""
        self.text_output.append(str(msg))

    def ask_gp_callback(self, msg):
        """Показать диалог для подтверждения госпошлины"""
        reply = QMessageBox.question(
            self, 'Госпошлина', msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def add_zalog(self, gosposhlina, row):
        self.btn_plus_zalog.hide()  # скрываем кнопку

        label_plus_zalog = QLabel('ГОСПОШЛИНА С ЗАЛОГОМ')
        value_field = QLineEdit(str(int(gosposhlina) + 25000))
        value_field.setReadOnly(True)

        # Горизонтальный layout для поля и кнопки
        h_layout = QHBoxLayout()
        btn_copy = QPushButton('Скопировать')
        btn_copy.setFixedWidth(100)
        btn_copy.clicked.connect(lambda _, field=value_field: QApplication.clipboard().setText(field.text()))

        h_layout.addWidget(value_field)
        h_layout.addWidget(btn_copy)

        # Добавляем label и горизонтальный layout в GridLayout
        self.totals_layout.addWidget(label_plus_zalog, row, 0)
        self.totals_layout.addLayout(h_layout, row, 1)

    def resave(self):
        """
        Пересохраняет файлы Excel (убирает вычисляемые формулы, пересобирает структуру).
        """
        for file in self.files:
            try:
                wb = load_workbook(file, data_only=True)
                wb.save(file)
            except Exception as e:
                self.append_text(f'<b>Ошибка при пересохранении файла {Path(file).name}: {e}</b>')
            finally:
                try:
                    wb.close()
                except Exception:
                    pass
        self.append_text('<b>Файлы пересохранены</b>')

    def on_run(self):
        """Запуск обработки"""
        if not self.files:
            QMessageBox.warning(self, '<b>Ошибка', 'Пожалуйста, выберите файлы для расчета.</b>')
            return
        self.append_text('\nРасчет ...')

        result = self.logic.run(files=self.files)

        self.clear_totals()
        gosposhlina = 0
        for row, (key, value) in enumerate(result.items()):
            label = QLabel(str(key))
            value_str = str(value).replace('.', ',')

            if key == 'ОПЛАТА ГОСПОШЛИНЫ':
                # Горизонтальный layout для этой строки
                h_layout = QHBoxLayout()
                value_field = QLineEdit(value_str)
                value_field.setReadOnly(True)
                btn_copy = QPushButton('Скопировать')
                btn_copy.setFixedWidth(100)  # можно задать фиксированную ширину кнопки
                btn_copy.clicked.connect(lambda _, field=value_field: QApplication.clipboard().setText(field.text()))

                # Добавляем виджеты в горизонтальный layout
                h_layout.addWidget(value_field)
                h_layout.addWidget(btn_copy)

                # Добавляем label и горизонтальный layout в Grid
                self.totals_layout.addWidget(label, row, 0)
                self.totals_layout.addLayout(h_layout, row, 1)

                gosposhlina = value
            else:
                value_field = QLineEdit(value_str)
                value_field.setReadOnly(True)
                self.totals_layout.addWidget(label, row, 0)
                self.totals_layout.addWidget(value_field, row, 1, 1, 2)  # растянуть на 2 колонки

        row += 1  # новая строка для кнопки
        self.btn_plus_zalog = QPushButton('Прибавить к Госпошлине залог 25 тыс.')
        self.totals_layout.addWidget(self.btn_plus_zalog, row, 0, 1, 2)
        self.btn_plus_zalog.clicked.connect(lambda: self.add_zalog(gosposhlina, row))

        self.resave()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec())

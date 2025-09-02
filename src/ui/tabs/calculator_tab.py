import os
import sys

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
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


class CalculatorTab(QWidget):
    select_files_clicked = pyqtSignal()
    calculate_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('РЦИ калькулятор')
        self.setAcceptDrops(True)
        self.initUI()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    paths.append(url.toLocalFile())
            if paths:
                self.files_dropped.emit(paths)  # отправляем в контроллер
            event.acceptProposedAction()
        else:
            event.ignore()

    def initUI(self):
        layout = QVBoxLayout()

        self.btn_select_file = QPushButton('Выбрать файлы', self)
        self.btn_select_file.clicked.connect(self.select_files_clicked.emit)
        layout.addWidget(self.btn_select_file)

        self.btn_run = QPushButton('Рассчитать', self)
        self.btn_run.clicked.connect(self.calculate_clicked.emit)
        layout.addWidget(self.btn_run)

        self.btn_reset = QPushButton('Сброс', self)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)
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

    # ==== Методы для контроллера =====
    def append_text(self, msg):
        """Добавляет текст в окно вывода."""
        self.text_output.append(str(msg))

    def reset(self):
        """Сбросить состояние калькулятора"""
        self.text_output.clear()
        self._clear_totals()
        self._recreate_totals_group()

    def print_select_files(self, unique_new_files, start_index):
        """Выводит список файлов"""
        for i, f in enumerate(unique_new_files, start=start_index):
            self.append_text(f'[{i}] {os.path.basename(f)}')

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

    def update_totals(self, result: dict):
        """Отрисовать таблицу итогов"""
        self._clear_totals()
        gosposhlina = 0

        for row, (key, value) in enumerate(result.items()):
            label = QLabel(str(key))
            value_str = str(value).replace('.', ',')

            if key == 'ОПЛАТА ГОСПОШЛИНЫ':
                h_layout = QHBoxLayout()
                value_field = QLineEdit(value_str)
                value_field.setReadOnly(True)
                btn_copy = QPushButton('Скопировать')
                btn_copy.setFixedWidth(100)
                btn_copy.clicked.connect(lambda _, field=value_field: QApplication.clipboard().setText(field.text()))
                h_layout.addWidget(value_field)
                h_layout.addWidget(btn_copy)

                self.totals_layout.addWidget(label, row, 0)
                self.totals_layout.addLayout(h_layout, row, 1)

                gosposhlina = float(value)
            else:
                value_field = QLineEdit(value_str)
                value_field.setReadOnly(True)
                self.totals_layout.addWidget(label, row, 0)
                self.totals_layout.addWidget(value_field, row, 1, 1, 2)

        # Кнопка "Прибавить к Госпошлине залог"
        row += 1
        self.btn_plus_zalog = QPushButton('Прибавить к Госпошлине залог 25 тыс.')
        self.totals_layout.addWidget(self.btn_plus_zalog, row, 0, 1, 2)
        self.btn_plus_zalog.clicked.connect(lambda: self.add_zalog(gosposhlina, row))

    # ==== Внутренние методы класса ====
    def _clear_totals(self):
        """Очищает виджеты из итоговой таблицы"""
        while self.totals_layout.count():
            item = self.totals_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _recreate_totals_group(self):
        """Очищаем и пересоздаём группу итогов"""
        self.layout().removeWidget(self.group_totals)
        self.group_totals.deleteLater()

        self.group_totals = QGroupBox('Итоги (Разбивка)')
        self.totals_layout = QGridLayout()
        self.group_totals.setLayout(self.totals_layout)
        self.layout().addWidget(self.group_totals)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorTab()
    window.show()
    sys.exit(app.exec())

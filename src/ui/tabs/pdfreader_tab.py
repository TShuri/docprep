import os
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget


class DragDropLabel(QLabel):
    file_dropped = pyqtSignal(str, str)  # file_key, path

    def __init__(self, text, file_key, allowed_exts, parent=None):
        super().__init__(text, parent)
        self.file_key = file_key
        self.allowed_exts = allowed_exts
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet('border: 1px solid gray; padding: 10px;')
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile().lower()
                if any(path.endswith(ext) for ext in self.allowed_exts):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            self.parent().reset_log(self.file_key)
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                fname = os.path.basename(path)
                if any(path.lower().endswith(ext) for ext in self.allowed_exts):
                    self.setText(fname)
                    self.file_dropped.emit(self.file_key, path)  # сигнал в контроллер
                    self.parent().log(f'Добавлен файл: {fname}', self.file_key)
                    event.acceptProposedAction()
                    return
            self.parent().log('Файл не распознан', self.file_key)
        else:
            event.ignore()


class PDFReaderTab(QWidget):
    process_clicked = pyqtSignal()  # Сигнал, для кнопки запуска формирования пакета
    reset_clicked = pyqtSignal()  # Сигнал, для кнопки сброса

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Верхнее поле: Заявление
        self.label_zayavlenie = DragDropLabel(
            'Перетащите Заявление (.docx)',
            'zayavlenie',
            allowed_exts=('.docx',),
            parent=self,
        )
        layout.addWidget(self.label_zayavlenie)

        # Нижний ряд: Публикация и Решение суда с логами
        grid = QGridLayout()

        # Слева: Публикация + лог
        left_layout = QVBoxLayout()
        self.label_publikaciya = DragDropLabel(
            'Перетащите публикацию (.pdf)',
            'publikaciya',
            allowed_exts=('.pdf',),
            parent=self,
        )
        self.text_log_publikaciya = QTextEdit()
        self.text_log_publikaciya.setReadOnly(True)
        self.text_log_publikaciya.setPlaceholderText('Логи Публикации')
        left_layout.addWidget(self.label_publikaciya)
        left_layout.addWidget(self.text_log_publikaciya)

        # Справа: Решение суда + лог
        right_layout = QVBoxLayout()
        self.label_reshenie = DragDropLabel(
            'Перетащите решение суда (.pdf)',
            'reshenie',
            allowed_exts=('.pdf',),
            parent=self,
        )
        self.text_log_reshenie = QTextEdit()
        self.text_log_reshenie.setReadOnly(True)
        self.text_log_reshenie.setPlaceholderText('Логи Решения суда')
        right_layout.addWidget(self.label_reshenie)
        right_layout.addWidget(self.text_log_reshenie)

        grid.addLayout(left_layout, 0, 0)
        grid.addLayout(right_layout, 0, 1)

        layout.addLayout(grid)

        # Кнопки обработки и сброса
        self.btn_process = QPushButton('Сверить файлы')
        self.btn_process.clicked.connect(lambda: self.process_clicked.emit())
        layout.addWidget(self.btn_process)

        self.btn_reset = QPushButton('Сбросить')
        self.btn_reset.clicked.connect(lambda: self.reset_clicked.emit())
        layout.addWidget(self.btn_reset)

        self.setLayout(layout)

    def log(self, msg, key=None):
        """Вывод логов в соответствующее окно"""
        if key == 'publikaciya':
            self.text_log_publikaciya.append(msg)
        elif key == 'reshenie':
            self.text_log_reshenie.append(msg)
        else:
            self.text_log_publikaciya.append(msg)
            self.text_log_reshenie.append(msg)

    def reset_log(self, key=None):
        """
        Сбрасывает логи.
        :param key: "publikaciya", "reshenie" или None для обоих
        """
        if key == 'publikaciya':
            self.text_log_publikaciya.clear()
        elif key == 'reshenie':
            self.text_log_reshenie.clear()
        else:  # Если key=None, очищаем оба лога
            self.text_log_publikaciya.clear()
            self.text_log_reshenie.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFReaderTab()
    window.show()
    sys.exit(app.exec())

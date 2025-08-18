from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PackageTab(QWidget):
    process_clicked = pyqtSignal()  # Сигнал, который контроллер слушает

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Кнопка запуска формирования пакета
        self.btn_process = QPushButton('Найти и сформировать пакет документов')
        self.btn_process.clicked.connect(lambda: self.process_clicked.emit())
        layout.addWidget(self.btn_process)
       
        # Блок "Текущее дело"
        case_layout = QHBoxLayout()

        self.label_case = QLabel('Текущее дело:')
        case_layout.addWidget(self.label_case)

        self.current_case = QLineEdit()
        self.current_case.setReadOnly(True)
        case_layout.addWidget(self.current_case)

        layout.addLayout(case_layout)


        # Поле для статуса
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        self.setLayout(layout)

        # # Рабочая папка (только для отображения, не редактируется)
        # self.input_path = QLineEdit()
        # self.input_path.setReadOnly(True)
        # layout.insertWidget(1, self.input_path)  # Вставляем под кнопкой case_layout

    # Методы для обновления интерфейса
    def set_current_case(self, text: str):
        self.current_case.setText(text)

    def append_log(self, text: str):
        self.logs.append(text)

    def reset(self):
        self.current_case.clear()
        self.logs.clear()

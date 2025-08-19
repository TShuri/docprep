from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PackageTab(QWidget):
    process_clicked = pyqtSignal()  # Сигнал, для кнопки запуска формирования пакета
    reset_clicked = pyqtSignal()  # Сигнал для кнопки сброса

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # == Выпадающий список банков ==
        bank_layout = QHBoxLayout()
        bank_layout.addWidget(QLabel('Выберите реквизиты банка:'))
        self.bank_selector = QComboBox()
        bank_layout.addWidget(self.bank_selector)
        layout.addLayout(bank_layout)

        # == Кнопка запуска формирования пакета ==
        self.btn_process = QPushButton('Найти и сформировать пакет документов')
        self.btn_process.clicked.connect(lambda: self.process_clicked.emit())
        layout.addWidget(self.btn_process)
        
        # == Кнопка сброса ==
        self.btn_reset = QPushButton('Сбросить')
        self.btn_reset.clicked.connect(lambda: self.reset_clicked.emit())
        layout.addWidget(self.btn_reset)
        
        # == Блок "Текущее дело" ==
        case_layout = QHBoxLayout()

        self.label_case = QLabel('Текущее дело:')
        case_layout.addWidget(self.label_case)

        self.current_case = QLineEdit()
        self.current_case.setReadOnly(True)
        case_layout.addWidget(self.current_case)

        layout.addLayout(case_layout)

        # == Поле для статуса ==
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        self.setLayout(layout)

    # Методы для обновления интерфейса
    def set_current_case(self, text: str):
        self.current_case.setText(text)
        
    def set_bank_list(self, banks: list[str]):
        self.bank_selector.clear()
        self.bank_selector.addItem("— выберите банк —")
        self.bank_selector.addItems(banks)
        self.bank_selector.setCurrentIndex(0)
        
    def reset_bank(self):
        self.bank_selector.setCurrentIndex(0)

    def append_log(self, text: str):
        self.logs.append(text)

    def reset(self):
        self.current_case.clear()
        self.logs.clear()

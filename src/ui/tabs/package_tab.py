from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
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

        # === Часть реквизиты ===
        group2 = QGroupBox('Часть Реквизиты')
        grid2 = QGridLayout()
        self.group2 = group2

        label2 = QLabel('Выберите реквизиты банка для вставки в заявление:')
        self.bank_selector = QComboBox()

        layout2 = QHBoxLayout()
        layout2.addWidget(label2)
        layout2.addWidget(self.bank_selector)

        grid2.addLayout(layout2, 0, 0)
        group2.setLayout(grid2)
        layout.addWidget(group2)

        # # === Группа "Вставка подписи" ===
        # group3 = QGroupBox('Часть Подпись')
        # grid3 = QGridLayout()
        # self.group3 = group3

        # label3 = QLabel('Вставить свою подпись')
        # self.radio_yes3 = QRadioButton('Да')
        # self.radio_no3 = QRadioButton('Нет')
        # self.radio_yes3.setChecked(True)

        # radio_layout3 = QHBoxLayout()
        # radio_layout3.addWidget(label3)
        # radio_layout3.addStretch()
        # radio_layout3.addWidget(self.radio_yes3)
        # radio_layout3.addWidget(self.radio_no3)

        # grid3.addLayout(radio_layout3, 0, 0)
        # group3.setLayout(grid3)
        # layout.addWidget(group3)
        # group3.setEnabled(False)

        # # == "Без заявления" ==
        # layout_checkbox = QHBoxLayout()
        # label_checkbox = QLabel('Распаковать архив без заявления')
        # self.checkbox_statement = QCheckBox()
        # layout_checkbox.addWidget(label_checkbox)
        # layout_checkbox.addStretch()
        # layout_checkbox.addWidget(self.checkbox_statement)
        # layout.addLayout(layout_checkbox)

        # == Кнопка запуска формирования пакета ==
        self.btn_process = QPushButton('Найти и сформировать пакет документов')
        self.btn_process.clicked.connect(lambda: self.process_clicked.emit())
        layout.addWidget(self.btn_process)

        # == Кнопка для вставки заявления в пакет документов ==
        # self.btn_insert_statement = QPushButton('Найти и добавить заявление в пакет документов')
        # self.btn_insert_statement.clicked.connect(lambda: self.insert_statement_clicked.emit())
        # self.btn_insert_statement.setVisible(False)  # Скрываем кнопку по умолчанию
        # self.btn_insert_statement.setEnabled(False)  # Делаем кнопку неактивной
        # layout.addWidget(self.btn_insert_statement)

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

        # == Поле для логов ==
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)
        self.setLayout(layout)

    # Методы для обновления интерфейса
    def set_current_case(self, text: str):
        self.current_case.setText(text)

    def set_bank_list(self, banks: list[str]):
        self.bank_selector.clear()
        self.bank_selector.addItem('— выберите банк —')
        self.bank_selector.addItems(banks)
        self.bank_selector.setCurrentIndex(0)

    def reset_bank(self):
        self.bank_selector.setCurrentIndex(0)

    def append_log(self, text: str):
        self.logs.append(text)

    def reset(self):
        self.current_case.clear()
        self.logs.clear()

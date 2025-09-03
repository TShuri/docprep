from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
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
    unpack_clicked = pyqtSignal()  # Сигнал, для кнопки распаковки архива документов
    insert_clicked = pyqtSignal()  # Сигнал, для кнопки вставки заявления
    reset_clicked = pyqtSignal()  # Сигнал для кнопки сброса

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # === Часть реквизиты ===
        group2 = QGroupBox('Часть Реквизиты')
        grid2 = QGridLayout()
        self.group2 = group2
        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel('Выберите реквизиты банка для вставки в заявление:'))
        self.bank_selector = QComboBox()
        layout2.addWidget(self.bank_selector)
        grid2.addLayout(layout2, 0, 0)
        group2.setLayout(grid2)
        main_layout.addWidget(group2)

        # === Часть Подпись ===
        group3 = QGroupBox('Часть Подпись')
        self.group3 = group3
        layout3 = QHBoxLayout()
        layout3.addWidget(QLabel('Вставить свою подпись в конце заявления'))
        layout3.addStretch()

        # Радиокнопки
        radio_yes = QRadioButton('Да')
        radio_no = QRadioButton('Нет')
        radio_yes.setChecked(True)  # по умолчанию "Да"
        # Объединяем в группу, чтобы выбор был взаимоисключающим
        radio_group = QButtonGroup()
        radio_group.addButton(radio_yes)
        radio_group.addButton(radio_no)
        layout3.addWidget(radio_yes)
        layout3.addWidget(radio_no)

        group3.setLayout(layout3)
        main_layout.addWidget(group3)

        self.radio_yes = radio_yes
        self.radio_no = radio_no
        self.radio_group = radio_group

        # == Распаковка ==
        group4 = QGroupBox('Распаковка')
        grid4 = QGridLayout()
        self.group4 = group4

        # Сохранение исходного заявления
        label_base = QLabel('Сохранить исходное заявление')
        self.checkbox_base_statement = QCheckBox()
        grid4.addWidget(label_base, 0, 0)
        grid4.addWidget(self.checkbox_base_statement, 0, 1)

        # Без заявления
        label_no = QLabel('Распаковать архив без заявления')
        self.checkbox_no_statement = QCheckBox()
        grid4.addWidget(label_no, 1, 0)
        grid4.addWidget(self.checkbox_no_statement, 1, 1)

        # Копирование папок обязательств
        label_copy = QLabel('Объединить содержимое папок всех обязательств в одну папку арбитра')
        self.checkbox_all_in_arbitter = QCheckBox()
        self.checkbox_all_in_arbitter.setChecked(True)
        grid4.addWidget(label_copy, 2, 0)
        grid4.addWidget(self.checkbox_all_in_arbitter, 2, 1)

        grid4.setColumnStretch(0, 1)
        grid4.setColumnStretch(1, 0)

        group4.setLayout(grid4)
        main_layout.addWidget(group4)

        # == Кнопка запуска формирования пакета ==
        self.btn_process = QPushButton('Найти и сформировать пакет документов')
        self.btn_process.clicked.connect(lambda: self.process_clicked.emit())
        main_layout.addWidget(self.btn_process)

        # == Кнопка распаковки архива документа (ПРИ ЧЕКБОКСЕ БЕЗ ЗАЯВЛЕНИЯ) ==
        self.btn_unpack = QPushButton('Найти и распаковать архив документов')
        self.btn_unpack.setVisible(False)
        self.btn_unpack.setEnabled(False)
        self.btn_unpack.clicked.connect(lambda: self.unpack_clicked.emit())
        main_layout.addWidget(self.btn_unpack)

        # == Кнопка для вставки заявления в пакет документов (ПРИ ЧЕКБОКСЕ БЕЗ ЗАЯВЛЕНИЯ) ==
        self.btn_insert = QPushButton('Найти и добавить заявление в распакованный архив документов')
        self.btn_insert.clicked.connect(lambda: self.insert_clicked.emit())
        self.btn_insert.setVisible(False)  # Скрываем кнопку по умолчанию
        self.btn_insert.setEnabled(False)  # Делаем кнопку неактивной
        main_layout.addWidget(self.btn_insert)

        # == Кнопка сброса ==
        self.btn_reset = QPushButton('Сбросить')
        self.btn_reset.clicked.connect(lambda: self.reset_clicked.emit())
        main_layout.addWidget(self.btn_reset)

        # == Блок "Текущее дело" ==
        case_layout = QHBoxLayout()
        case_layout.addWidget(QLabel('Текущее дело:'))
        self.current_case = QLineEdit()
        self.current_case.setReadOnly(True)
        case_layout.addWidget(self.current_case)
        main_layout.addLayout(case_layout)

        # == Поле для логов ==
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        main_layout.addWidget(self.logs)
        self.setLayout(main_layout)

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

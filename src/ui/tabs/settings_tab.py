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
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class SettingsTab(QWidget):
    save_clicked = pyqtSignal()
    browse_clicked = pyqtSignal()
    aplly_settings_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # === Группа "Рабочая директория" ===
        group1 = QGroupBox('Рабочая директория')
        grid1 = QGridLayout()

        # Метка и поле ввода
        grid1.addWidget(QLabel('Путь:'), 0, 0)
        self.work_dir_path = QLineEdit()
        self.work_dir_path.setPlaceholderText('Укажите путь к директории, куда будет скачиваться досье и заявление')
        grid1.addWidget(self.work_dir_path, 0, 1)

        # Кнопка "Обзор"
        self.btn_browse = QPushButton('Обзор')
        self.btn_browse.clicked.connect(lambda: self.browse_clicked.emit())
        grid1.addWidget(self.btn_browse, 0, 2)

        # Кнопка "Сохранить"
        self.btn_save = QPushButton('Сохранить')
        self.btn_save.clicked.connect(lambda: self.save_clicked.emit())
        grid1.addWidget(self.btn_save, 1, 1, 1, 2)  # растянется на 2 колонки справа

        group1.setLayout(grid1)
        main_layout.addWidget(group1)

        # === Группа "Пакет документов" ===
        group2 = QGroupBox('Пакет документов')
        grid2 = QGridLayout()
        self.group2 = group2

        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel('Выберите название папки арбитр'))

        self.arbitter_selector = QComboBox()
        banks = ['<Номер дела> <ФИО>', 'Арбитр <ФИО>', 'А <ФИО>']
        self.arbitter_selector.addItems(banks)
        self.arbitter_selector.setCurrentIndex(2)  # по умолчанию выбран первый
        layout2.addWidget(self.arbitter_selector)

        grid2.addLayout(layout2, 0, 0)
        group2.setLayout(grid2)
        main_layout.addWidget(group2)

        # === Группа "Заявление" ===
        group3 = QGroupBox('Заявление')
        grid3 = QGridLayout()

        self.checkbox_format_header = QCheckBox('Форматировать отступ шапки документа')
        grid3.addWidget(self.checkbox_format_header, 0, 0)

        group3.setLayout(grid3)
        main_layout.addWidget(group3)

        # === Группа "Калькулятор" ===
        group4 = QGroupBox('Калькулятор РЦИ')
        grid4 = QGridLayout()

        # Чекбокс "Автосохранение РЦИ"
        self.checkbox_resave_rci = QCheckBox('Пересохранять файлы РЦИ после расчета')
        grid4.addWidget(self.checkbox_resave_rci, 0, 0)

        self.checkbox_show_btn_resave = QCheckBox('Показать кнопку Пересохранять файлы')
        grid4.addWidget(self.checkbox_show_btn_resave, 1, 0)

        group4.setLayout(grid4)
        main_layout.addWidget(group4)

        # == Кнопка "Перезапустить программу" ==
        self.btn_apply = QPushButton('Перезапустить программу')

        self.btn_apply.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_apply.clicked.connect(lambda: self.aplly_settings_clicked.emit())
        main_layout.addWidget(self.btn_apply)

        # == Спейсер, чтобы прижать группу к верху ==
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

    # Методы для работы с GUI (контроллер вызывает их)
    def set_work_dir(self, path):
        self.work_dir_path.setText(str(path))

    def get_work_dir(self) -> str:
        return self.work_dir_path.text().strip()

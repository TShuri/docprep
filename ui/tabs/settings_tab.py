from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class SettingsTab(QWidget):
    # Сигналы, которые контроллер слушает
    save_clicked = pyqtSignal()
    browse_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # === Группа "Рабочая директория" ===
        group1 = QGroupBox("Рабочая директория")
        grid1 = QGridLayout()

        # Метка и поле ввода
        grid1.addWidget(QLabel("Путь:"), 0, 0)
        self.work_dir_path = QLineEdit()
        grid1.addWidget(self.work_dir_path, 0, 1)

        # Кнопка "Обзор"
        self.btn_browse = QPushButton("Обзор")
        self.btn_browse.clicked.connect(lambda: self.browse_clicked.emit())
        grid1.addWidget(self.btn_browse, 0, 2)

        # Кнопка "Сохранить"
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(lambda: self.save_clicked.emit())
        grid1.addWidget(self.btn_save, 1, 1, 1, 2)  # растянется на 2 колонки справа

        group1.setLayout(grid1)
        main_layout.addWidget(group1)

        # Спейсер, чтобы прижать группу к верху
        main_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        self.setLayout(main_layout)

    # Методы для работы с GUI (контроллер вызывает их)
    def set_work_dir(self, path: str):
        self.work_dir_path.setText(path)

    def get_work_dir(self) -> str:
        return self.work_dir_path.text().strip()

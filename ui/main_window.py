import sys

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from controllers.docprep_controller import DocPrepController


class DocPrepApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DocPrep')
        self.resize(500, 300)
        self.controller = DocPrepController()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        # Метка и поле ввода пути
        self.label_path = QLabel('Выберите рабочую папку:')
        layout.addWidget(self.label_path)

        self.input_path = QLineEdit()
        layout.addWidget(self.input_path)

        # Кнопка для выбора папки
        self.btn_browse = QPushButton('Обзор')
        self.btn_browse.clicked.connect(self.browse_folder)
        layout.addWidget(self.btn_browse)

        # Кнопка запуска формирования пакета
        self.btn_process = QPushButton('Найти и сформировать пакет документов')
        self.btn_process.clicked.connect(self.process_package)
        layout.addWidget(self.btn_process)

        # Поле для статуса
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        layout.addWidget(self.status)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Выберите рабочую папку')
        if folder:
            self.input_path.setText(folder)
            
    def reset_status(self):
        self.status.clear()
        
    def load_settings(self):
        folder_path = self.controller.load_work_directory()
        if folder_path:
            self.input_path.setText(folder_path)
        else:
            self.status.append('Рабочая папка не задана. Пожалуйста, выберите её вручную.')

    def process_package(self):
        self.reset_status()
        folder_path = self.input_path.text().strip()
        if not folder_path:
            self.status.append('Пожалуйста, укажите путь к рабочей папке.')
            return

        # Здесь будет логика подготовки пакета документов
        logs = self.controller.package_formation(folder_path)
        for log in logs:
            self.status.append(log)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = DocPrepApp()
#     window.show()
#     sys.exit(app.exec())

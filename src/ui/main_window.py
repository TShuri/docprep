from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from src.calculator.main import CalculatorWindow
from src.controllers.package_controller import PackageController
from src.controllers.pdfreader_controller import PDFReaderController
from src.controllers.settings_controller import SettingsController
from src.ui.tabs.package_tab import PackageTab
from src.ui.tabs.pdfreader_tab import PDFReaderTab
from src.ui.tabs.settings_tab import SettingsTab


class DocPrepApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DocPrep')
        self.resize(600, 600)
        self.setting_controller = None
        self.package_controller = None
        self.pdfreader_controller = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        # Вкладки
        package_tab = PackageTab()
        pdfreader_tab = PDFReaderTab()
        settings_tab = SettingsTab()
        calculator_tab = CalculatorWindow()

        # Контроллеры
        self.package_controller = PackageController(package_tab)
        self.pdfreader_controller = PDFReaderController(pdfreader_tab)
        self.setting_controller = SettingsController(settings_tab)

        tabs.addTab(package_tab, 'Пакет документов')
        tabs.addTab(pdfreader_tab, 'Сверка с pdf')
        tabs.addTab(settings_tab, 'Настройки')
        tabs.addTab(calculator_tab, 'Калькулятор')

        layout.addWidget(tabs)
        self.setLayout(layout)

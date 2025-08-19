from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from controllers.package_controller import PackageController
from controllers.settings_controller import SettingsController
from ui.tabs.package_tab import PackageTab
from ui.tabs.settings_tab import SettingsTab

# from ui.tabs.statement_tab import StatementTab


class DocPrepApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DocPrep')
        self.resize(600, 500)
        self.setting_controller = None
        self.package_controller = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        package_tab = PackageTab()
        settings_tab = SettingsTab()
        # statement_tab = StatementTab()

        # Контроллеры
        self.package_controller = PackageController(package_tab)
        self.setting_controller = SettingsController(settings_tab)

        tabs.addTab(package_tab, 'Пакет документов')
        tabs.addTab(settings_tab, 'Настройки')
        # tabs.addTab(statement_tab, "Заявление")

        layout.addWidget(tabs)
        self.setLayout(layout)

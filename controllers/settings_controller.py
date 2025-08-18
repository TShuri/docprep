from PyQt6.QtWidgets import QFileDialog

from utils.settings_utils import load_work_directory, save_work_directory


class SettingsController:
    def __init__(self, view, on_work_dir_changed=None):
        """
        :param view: экземпляр SettingsTab
        :param on_work_dir_changed: опциональный callback, который вызывается при изменении рабочей директории
        """
        self.view = view
        self.on_work_dir_changed = on_work_dir_changed

        # Подписка на сигналы View
        self.view.save_clicked.connect(self.handle_save_clicked)
        self.view.browse_clicked.connect(self.handle_browse_clicked)

        # Инициализация рабочего пути
        folder_path = load_work_directory()
        if folder_path:
            self.view.set_work_dir(folder_path)

    def handle_browse_clicked(self):
        folder = QFileDialog.getExistingDirectory(self.view, "Выберите рабочую папку")
        if folder:
            self.view.set_work_dir(folder)
            self.save_work_directory()  # Автосохранение после выбора

    def handle_save_clicked(self):
        folder_path = self.view.get_work_dir()
        if folder_path:
            save_work_directory(folder_path)
            # Если есть callback, уведомляем другие вкладки о смене директории
            if self.on_work_dir_changed:
                self.on_work_dir_changed(folder_path)

    def load_work_directory(self) -> str | None:
        """
        Загружает путь к рабочей папке из настроек.
        :return: Путь к рабочей папке или None, если не задано.
        """
        return load_work_directory()

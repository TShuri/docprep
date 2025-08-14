from pathlib import Path

from core import docx_tools, file_tools
from utils.settings_utils import load_work_directory, save_work_directory
from utils.text_utils import sanitize_filename


class DocPrepController:
    def __init__(self):
        pass

    def load_work_directory(self) -> str | None:
        """
        Загружает путь к рабочей папке из настроек.
        :return: Путь к рабочей папке или None, если не задано.
        """
        return load_work_directory()

    def package_formation(self, folder_path: str) -> list[str]:
        """
        Главная функция обработки рабочей папки.
        Возвращает список статусов (логов), которые потом можно показывать в GUI.
        """
        try:
            logs = []

            folder = Path(folder_path)
            if not folder.exists() or not folder.is_dir():
                logs.append('Указанная папка не существует.')
                return logs

            save_work_directory(str(folder))  # Сохраняем рабочую директорию

            path_rtk_doc = file_tools.find_rtk_doc(folder)  # Путь к документу РТК
            fio_debtor = docx_tools.extract_fio_debtor(path_rtk_doc)  # Извлечение ФИО должника
            case_number = docx_tools.extract_case_number(path_rtk_doc)  # Извлечение номера дела

            path_dossier_archive = file_tools.find_dossier_archive(folder)  # Путь к архиву досье
            path_extract_dossier_archive = folder / fio_debtor  # Папка для распаковки архива досье
            path_dossier = file_tools.unzip_archive(
                archive_path=path_dossier_archive,
                extract_to=path_extract_dossier_archive,
            )  # Распаковка архива досье
            file_tools.unzip_all_nested_archives(
                path_dossier
            )  # Распаковка вложенных архивов в досье
            file_tools.delete_file(path_dossier_archive)  # Удаление архива досье после распаковки

            file_tools.move_file(
                src=path_rtk_doc,
                dst=path_dossier,
            )  # Перемещение документа РТК в папку досье

            arbitter_folder = path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}'
            path_arbitter_folder = file_tools.ensure_folder(
                arbitter_folder
            )  # Создание папки для арбитражного дела

            paths_obligations = file_tools.find_folders_obligations(
                path_dossier
            )  # Поиск папок обязательств
            for path_obligation in paths_obligations:
                if path_obligation == path_arbitter_folder:
                    continue
                file_tools.copy_folder(
                    src=path_obligation,
                    dst=path_arbitter_folder,
                )

            logs.append('Пакет документов сформирован.')

            return logs
        except Exception as e:
            return [f'Произошла ошибка: {e}']

from pathlib import Path

from core import docx_tools, file_tools
from utils.settings_utils import load_work_directory
from utils.text_utils import sanitize_filename


class PackageController:
    def __init__(self, view):
        self.view = view
        self.view.process_clicked.connect(self.handle_process_clicked)
        self.view.reset_clicked.connect(self.handle_reset_clicked)

        self.current_path_rtk = None  # Путь к документу РТК
        self.update_bank_requisites()
        
        
    def update_bank_requisites(self):
        banks = docx_tools.get_bank_list()
        self.view.set_bank_list(banks)
        
        
    def handle_reset_clicked(self):
        self.view.reset_bank()
        self.view.reset()
        self.current_path_rtk = None
        
        
    def handle_process_clicked(self):
        self.view.reset()
        self.current_path_rtk = None
        folder_path = load_work_directory()
        
        if not folder_path:
            self.view.append_log("Пожалуйста, укажите путь к рабочей папке.")
            return
        
        if self.view.bank_selector.currentText() == "— выберите банк —":
            self.view.append_log("Выберите банк перед продолжением.")
            return

        self._form_package(folder_path) # Формирование пакета документов
        
        if not self.current_path_rtk:
            self.view.append_log("Не удалось найти документ РТК в указанной папке.")
            return
        
        self._proccess_statement(self.current_path_rtk)  # Обработка заявления на включение требований в реестр
        
        
    def _form_package(self, folder_path: str) -> list[str]:
        folder = Path(folder_path)
        
        if not folder.exists() or not folder.is_dir():
            self.view.append_log('Указанная папка не существует.')
            return
            
        try:
            # 1️⃣ Найти документ РТК и извлечь данные должника
            path_rtk_doc = file_tools.find_rtk_doc(folder)  # Путь к документу РТК
            fio_debtor = docx_tools.extract_fio_debtor(path_rtk_doc)  # Извлечение ФИО должника
            case_number = docx_tools.extract_case_number(path_rtk_doc)  # Извлечение номера дела

            # 2️⃣ Разархивировать досье
            path_dossier_archive = file_tools.find_dossier_archive(folder)  # Путь к архиву досье
            path_extract_dossier_archive = folder / fio_debtor  # Папка для распаковки архива досье
            path_dossier = file_tools.unzip_archive(path_dossier_archive, path_extract_dossier_archive)  # Распаковка архива досье
            file_tools.unzip_all_nested_archives(path_dossier)  # Распаковка вложенных архивов в досье
            file_tools.delete_file(path_dossier_archive)  # Удаление архива досье после распаковки

            # 3️⃣ Переместить документ РТК в папку досье
            self.current_path_rtk = file_tools.move_file(path_rtk_doc, path_dossier)

            # 4️⃣ Создать папку арбитражного дела
            arbitter_folder = path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}'
            path_arbitter_folder = file_tools.ensure_folder(arbitter_folder)

            # 5️⃣ Скопировать папки обязательств в папку арбитражного дела
            # Исключая папку арбитражного дела, если она уже существует
            paths_obligations = file_tools.find_folders_obligations(path_dossier)  # Поиск папок обязательств
            for path_obligation in paths_obligations:
                if path_obligation == path_arbitter_folder:
                    continue
                file_tools.copy_folder(path_obligation, path_arbitter_folder)

            self.view.set_current_case(f'{case_number} {fio_debtor}')
            self.view.append_log('Пакет документов сформирован.')

        except Exception as e:
            self.view.append_log(f'Произошла ошибка: {e}')
            
    def _proccess_statement(self, path_statement: Path) -> None:
        # 1️⃣ Форматирование списка приложений
        docx_tools.format_appendices(path_statement)
        # 2️⃣ Вставка реквизитов банка в таблицу
        docx_tools.insert_bank_table(path_statement, self.view.bank_selector.currentText())
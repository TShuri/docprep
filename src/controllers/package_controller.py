from pathlib import Path

from src.core import docx_tools
from src.core.workflow import (form_package, insert_statement,
                               proccess_statement, unpack_package_no_statement)
from src.utils.settings_utils import load_work_directory
from src.utils.templates_utils import load_bank_requisites


class PackageController:
    def __init__(self, view):
        # Подключение view
        self.view = view
        self.view.checkbox_no_statement.stateChanged.connect(self.handle_checkbox_no_statement)
        self.view.process_clicked.connect(self.handle_process_clicked)
        self.view.unpack_clicked.connect(self.handle_unpack_clicked)
        self.view.insert_clicked.connect(self.handle_insert_clicked)
        self.view.reset_clicked.connect(self.handle_reset_clicked)

        # Инициализация необходимых параметров
        self.current_path_doc = None  # Путь к документу РТК
        self.current_path_dossier = None  # Путь к папке досье, при распаковке без заявления
        self.have_bank_requisites = False  # Флаг наличия реквизитов банков
        self.update_bank_requisites()

    def handle_checkbox_no_statement(self, state):
        enabled = state == 0  # 0 = unchecked, 2 = checked
        self.view.btn_process.setVisible(enabled)  # видимость
        self.view.btn_process.setEnabled(enabled)  # активность

        self.view.btn_unpack.setVisible(not enabled)  # видимость
        self.view.btn_unpack.setEnabled(not enabled)  # активность

        self.view.btn_insert.setVisible(not enabled)  # видимость
        self.view.btn_insert.setEnabled(not enabled)  # активность

    def handle_process_clicked(self):
        """Формирование пакета документов"""
        self.view.reset()
        self.current_path_doc = None
        self.current_path_dossier = None

        folder = self.get_work_folder()
        if not folder:  # Проверяем выбрана ли рабочая директория
            return

        # Если банковские реквизиты подгружены, то проверяем выбранный банк для вставки реквизитов
        selected_bank = None
        if self.have_bank_requisites:
            selected_bank = self.get_selected_bank()
            if selected_bank is None:
                return
        
        save_base_statement = False
        if self.view.checkbox_base_statement.isChecked():
            save_base_statement = True

        try:  # Формируем пакет (распаковку)
            self.current_path_doc, fio_debtor, case_number = form_package(folder, save_base_statement)
            self.view.set_current_case(f'{case_number} {fio_debtor}')
        except Exception as e:
            self.view.append_log(f'Ошибка формирования пакета: {e}')
            return

        if self.current_path_doc:
            try:  # Обрабатываем заявление
                proccess_statement(self.current_path_doc, selected_bank)
                self.view.append_log('Пакет документов сформирован.')
            except Exception as e:
                self.view.append_log(f'Пакет документов сформирован без обработки заявления: {e}')
        
        self.view.reset_bank()
                
    def handle_unpack_clicked(self):
        """Распаковка архива пакета документов"""
        self.view.reset()
        self.current_path_doc = None
        self.current_path_dossier = None

        folder = self.get_work_folder()
        if not folder:  # Проверяем выбрана ли рабочая директория
            return
        
        try:  # Распаковка архива
            self.current_path_dossier, case_number = unpack_package_no_statement(folder)
            self.view.set_current_case(f'{case_number} без заявления')
            self.view.append_log('Архив документов распакован')
        except Exception as e:
            self.view.append_log(f'Ошибка формирования пакета: {e}')
            return
        
    def handle_insert_clicked(self):
        """Перемещение заявления в разархивированный пакет документов"""
        self.current_path_doc = None
        
        folder = self.get_work_folder()
        if not folder:  # Проверяем выбрана ли рабочая директория
            return
        
        # Если банковские реквизиты подгружены, то проверяем выбранный банк для вставки реквизитов
        selected_bank = None
        if self.have_bank_requisites:
            selected_bank = self.get_selected_bank()
            if selected_bank is None:
                return
            
        save_base_statement = False
        if self.view.checkbox_base_statement.isChecked():
            save_base_statement = True
        
        self.view.reset()
        try: # Формируем пакет
            self.current_path_doc, fio_debtor, case_number = insert_statement(folder, self.current_path_dossier, save_base_statement)
            self.view.set_current_case(f'{case_number} {fio_debtor}')
        except Exception as e:
            self.view.append_log(f'Ошибка формирования пакета: {e}')
            return
        
        if self.current_path_doc:
            try:  # Обрабатываем заявление
                proccess_statement(self.current_path_doc, selected_bank)
                self.view.append_log('Пакет документов сформирован.')
            except Exception as e:
                self.view.append_log(f'Пакет документов сформирован без обработки заявления: {e}')
        
        self.view.reset_bank()

    def handle_reset_clicked(self):
        """Сбросить"""
        self.view.reset_bank()
        self.view.reset()
        self.current_path_doc = None
        self.current_path_dossier = None

    def update_bank_requisites(self):
        """Подгружает список банков при первоначальном запуске"""
        doc_requisites = load_bank_requisites()
        if not doc_requisites:
            self.view.append_log('Файл с реквизитами банков не найден.')
        else:
            self.have_bank_requisites = True
            banks = docx_tools.get_bank_list(doc_requisites)
            self.view.set_bank_list(banks)

    def get_work_folder(self) -> Path | None:
        """Получает путь рабочей директории"""
        folder_path = load_work_directory()
        if folder_path is None:
            self.view.append_log('Пожалуйста, укажите путь к рабочей папке.')
        return folder_path

    def get_selected_bank(self) -> str | None:
        """Получает выбранный банк"""
        bank_name = self.view.bank_selector.currentText()
        if bank_name == '— выберите банк —':
            self.view.append_log('Выберите банк перед продолжением.')
            return None
        return bank_name

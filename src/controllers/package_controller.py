from pathlib import Path

from src.core import docx_tools
from src.core.workflow import form_package, proccess_statement
from src.utils.settings_utils import load_work_directory
from src.utils.templates_utils import load_bank_requisites
from src.utils.text_utils import sanitize_filename


class PackageController:
    def __init__(self, view):
        self.view = view
        self.view.process_clicked.connect(self.handle_process_clicked)
        self.view.reset_clicked.connect(self.handle_reset_clicked)

        self.current_path_doc = None  # Путь к документу РТК
        self.current_path_dossier = None  # Путь к папке досье, при распаковке без заявления
        self.have_bank_requisites = False  # Флаг наличия реквизитов банков
        self.update_bank_requisites()

    def handle_process_clicked(self):
        """Формирование пакета документов"""
        self.view.reset()
        self.current_path_doc = None
        self.current_path_dossier = None

        folder = self._get_work_folder()
        if not folder:  # Проверяем выбрана ли рабочая директория
            return

        # Если банковские реквизиты подгружены, то проверяем выбранный банк для вставки реквизитов
        selected_bank = None
        if self.have_bank_requisites:
            selected_bank = self._get_selected_bank()
            if selected_bank is None: 
                return

        try: # Формируем пакет (распаковку)
            self.current_path_doc, fio_debtor, case_number = form_package(folder)
            self.view.set_current_case(f'{case_number} {fio_debtor}')
        except Exception as e:
            self.view.append_log(f'Ошибка формирования пакета: {e}')
            return
            
        if self.current_path_doc:
            try: # Обрабатываем заявление
                proccess_statement(self.current_path_doc, selected_bank)
                self.view.append_log('Пакет документов сформирован.')
            except Exception as e:
                self.view.append_log(f'Пакет документов сформирован без обработки заявления: {e}')

    def handle_reset_clicked(self):
        """Сбросить"""
        self.view.reset_bank()
        self.view.reset()
        self.current_path_doc = None
        self.current_path_dossier = None

    def handle_checkbox_toggled(self, state):
        enabled = state == 0  # 0 = unchecked, 2 = checked
        self.view.btn_insert_statement.setVisible(not enabled)  # видимость
        self.view.btn_insert_statement.setEnabled(not enabled)  # активность

    def update_bank_requisites(self):
        """Подгружает список банков при первоначальном запуске"""
        doc_requisites = load_bank_requisites()
        if not doc_requisites:
            self.view.append_log('Файл с реквизитами банков не найден.')
        else:
            self.have_bank_requisites = True
            banks = docx_tools.get_bank_list(doc_requisites)
            self.view.set_bank_list(banks)

    def _get_work_folder(self) -> Path | None:
        """Получает путь рабочей директории"""
        folder_path = load_work_directory()
        if folder_path is None:
            self.view.append_log('Пожалуйста, укажите путь к рабочей папке.')
        return folder_path

    def _get_selected_bank(self) -> str | None:
        """Получает выбранный банк"""
        bank_name = self.view.bank_selector.currentText()
        if bank_name == '— выберите банк —':
            self.view.append_log('Выберите банк перед продолжением.')
            return None
        return bank_name
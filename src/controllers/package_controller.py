import traceback
from pathlib import Path

from src.core import docx_tools
from src.core.workflow import (
    insert_statement,
    procces_package,
    unpack_package,
)
from src.utils.settings_utils import (
    load_all_in_arbitter,
    load_arbitter_name,
    load_format_header,
    load_work_directory,
    save_all_in_arbitter,
)
from src.utils.templates_utils import load_bank_requisites, load_path_signa


class PackageController:
    def __init__(self, view):
        # Подключение view
        self.view = view
        self.view.checkbox_no_statement.stateChanged.connect(self.handle_checkbox_no_statement)
        self.view.process_clicked.connect(self.handle_process_clicked)
        self.view.unpack_clicked.connect(self.handle_unpack_clicked)
        self.view.insert_clicked.connect(self.handle_insert_clicked)
        self.view.reset_clicked.connect(self.handle_reset_clicked)
        self.view.checkbox_all_in_arbitter.stateChanged.connect(self.handle_all_in_arbitter_clicked)

        # Инициализация необходимых параметров
        self.have_bank_requisites = False  # Флаг наличия реквизитов банков
        self._update_bank_requisites()
        self._check_signa()
        self.arbitter_name = self._load_arbitter_name()
        self._load_setting_all_in_arbitter()
        self.format_header = self._load_format_header()

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

        folder = self.get_work_folder()
        if not folder:  # Проверяем выбрана ли рабочая директория
            return

        # Если банковские реквизиты подгружены, то проверяем выбранный банк для вставки реквизитов
        selected_bank = None
        if self.have_bank_requisites:
            selected_bank = self.get_selected_bank()
            if selected_bank is None:
                return

        save_orig = False  # Сохранять ли исходное заявление
        if self.view.checkbox_base_statement.isChecked():
            save_orig = True

        have_signa = self.view.radio_yes.isChecked()  # Вставить подпись или нет
        all_in_arb = self.view.checkbox_all_in_arbitter.isChecked()  # Объединить все обязательства в одну папку

        try:  # Формируем пакет
            fio_debtor, case_number = procces_package(
                folder_path=folder,
                signa=have_signa,
                bank=selected_bank,
                save_orig=save_orig,
                all_in_arb=all_in_arb,
                arb_name=self.arbitter_name,
                format_header=self.format_header,
            )
            self.view.set_current_case(f'{case_number} {fio_debtor}')
            self.view.append_log('Пакет документов сформирован.')
        except Exception as e:
            self.view.append_log(f'Ошибка формирования пакета: {e}\n{traceback.format_exc()}')
            return

        self.view.reset_bank()

    def handle_unpack_clicked(self):
        """Распаковка архива пакета документов без заявления"""
        self.view.reset()

        folder = self.get_work_folder()
        if not folder:  # Проверяем выбрана ли рабочая директория
            return

        try:  # Распаковка архива
            case_number = unpack_package(folder)
            self.view.set_current_case(f'{case_number} без заявления')
            self.view.append_log('Архив документов распакован')
        except Exception as e:
            self.view.append_log(f'Ошибка распаковки архива: {e}\n{traceback.format_exc()}')
            return

    def handle_insert_clicked(self):
        """Перемещение заявления в разархивированный пакет документов"""

        folder = self.get_work_folder()
        if not folder:  # Проверяем выбрана ли рабочая директория
            return

        # Если банковские реквизиты подгружены, то проверяем выбранный банк для вставки реквизитов
        selected_bank = None
        if self.have_bank_requisites:
            selected_bank = self.get_selected_bank()
            if selected_bank is None:
                return

        save_orig = False  # Сохранять ли исходное заявление
        if self.view.checkbox_base_statement.isChecked():
            save_orig = True

        have_signa = self.view.radio_yes.isChecked()  # Вставлять ли подпись
        all_in_arb = self.view.checkbox_all_in_arbitter.isChecked()  # Объединить все обязательства в одну папку

        self.view.reset()
        try:  # Формируем пакет
            fio_debtor, case_number = insert_statement(
                folder_path=folder,
                signa=have_signa,
                bank=selected_bank,
                save_orig=save_orig,
                all_in_arb=all_in_arb,
                arb_name=self.arbitter_name,
                format_header=self.format_header,
            )
            self.view.set_current_case(f'{case_number} {fio_debtor}')
            self.view.append_log('Пакет документов сформирован.')
        except Exception as e:
            self.view.append_log(f'Ошибка формирования пакета: {e}\n{traceback.format_exc()}')
            return

        self.view.reset_bank()

    def handle_all_in_arbitter_clicked(self):
        """Объединить содержимое папок всех обязательств в одну папку"""
        value = self.view.checkbox_all_in_arbitter.isChecked()
        save_all_in_arbitter(value)

    def handle_reset_clicked(self):
        """Сбросить"""
        self.view.reset_bank()
        self.view.reset()

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

    def _update_bank_requisites(self):
        """Подгружает список банков при первоначальном запуске"""
        doc_requisites = load_bank_requisites()
        if not doc_requisites:
            self.view.append_log('Файл с реквизитами банков не найден.')
            self.view.group2.setEnabled(False)
        else:
            self.have_bank_requisites = True
            banks = docx_tools.get_bank_list(doc_requisites)
            self.view.set_bank_list(banks)

    def _check_signa(self):
        """Получаем путь к подписи если он есть"""
        if load_path_signa() is None:
            self.view.append_log('Подпись не загружена.')
            self.view.radio_no.setChecked(True)
            self.view.group3.setEnabled(False)

    def _load_setting_all_in_arbitter(self):
        value = load_all_in_arbitter()
        if value:
            self.view.checkbox_all_in_arbitter.setChecked(value)

    def _load_arbitter_name(self):
        value = load_arbitter_name()
        if value:
            return value
        else:
            return None

    def _load_format_header(self):
        value = load_format_header()
        if value:
            return value
        else:
            return None

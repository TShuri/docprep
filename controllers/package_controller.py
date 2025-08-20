from pathlib import Path

from core import docx_tools, file_tools
from utils.settings_utils import load_bank_requisites_directory, load_work_directory
from utils.templates_utils import load_del_paragraphs, load_del_words, get_gosposhlina_template
from utils.text_utils import get_case_number_from_filename, sanitize_filename


class PackageController:
    def __init__(self, view):
        self.view = view
        self.view.process_clicked.connect(self.handle_process_clicked)
        self.view.reset_clicked.connect(self.handle_reset_clicked)
        self.view.checkbox_statement.stateChanged.connect(self.handle_checkbox_toggled)
        self.view.insert_statement_clicked.connect(self.handle_insert_statement)

        self.current_path_doc = None  # Путь к документу РТК
        self.current_path_dossier = None  # Путь к папке досье
        self.have_bank_requisites = False  # Флаг наличия реквизитов банков
        self.update_bank_requisites()

    def update_bank_requisites(self):
        path_requirities = load_bank_requisites_directory()
        if not path_requirities:
            self.view.append_log('Файл с реквизитами банков не найден.')
        else:
            self.have_bank_requisites = True
            doc_requirities = docx_tools.open_docx(path_requirities)
            banks = docx_tools.get_bank_list(doc_requirities)
            self.view.set_bank_list(banks)

    def handle_checkbox_toggled(self, state):
        enabled = state == 0  # 0 = unchecked, 2 = checked
        self.view.btn_insert_statement.setVisible(not enabled)  # видимость
        self.view.btn_insert_statement.setEnabled(not enabled)  # активность

    def handle_reset_clicked(self):
        self.view.reset_bank()
        self.view.reset()
        self.current_path_doc = None
        self.current_path_dossier = None

    def handle_process_clicked(self):
        self.view.reset()
        self.current_path_doc = None
        self.current_path_dossier = None
        folder_path = Path(load_work_directory())

        if not folder_path.exists() or not folder_path.is_dir():
            self.view.append_log('Пожалуйста, укажите путь к рабочей папке.')
            return

        if self.view.checkbox_statement.isChecked():
            self._form_package_without_statement(folder_path)  # Формирование пакета документов без заявления
            return

        if self.view.bank_selector.currentText() == '— выберите банк —':
            self.view.append_log('Выберите банк перед продолжением.')
            return

        self._form_package(folder_path)  # Формирование пакета документов
        if not self.current_path_doc:
            self.view.append_log('Не удалось найти документ РТК в указанной папке.')
            return
        self._proccess_statement(self.current_path_doc)  # Обработка заявления на включение требований в реестр

        self.view.append_log('Пакет документов сформирован.')

    def handle_insert_statement(self):
        if self.view.bank_selector.currentText() == '— выберите банк —':
            self.view.append_log('Выберите банк перед продолжением.')
            return

        self.view.reset()
        self.current_path_doc = None
        folder_path = Path(load_work_directory())

        if not folder_path.exists() or not folder_path.is_dir():
            self.view.append_log('Пожалуйста, укажите путь к рабочей папке.')
            return

        self._insert_statement(folder_path)  # Вставка заявления в пакет документов
        if not self.current_path_doc:
            self.view.append_log('Не удалось найти Заявление в указанной папке.')
            return
        self._proccess_statement(self.current_path_doc)  # Обработка заявления на включение требований в реестр

        self.view.append_log('Пакет документов сформирован.')

    def _form_package(self, folder_path: str):
        """Формирование пакета документов по банкротству"""
        folder = Path(folder_path)
        try:
            # 1️⃣ Найти документ РТК и извлечь данные должника
            path_doc = file_tools.find_rtk_doc(folder)  # Путь к документу РТК
            doc = docx_tools.open_docx(path_doc)  # Открытие документа РТК
            fio_debtor = docx_tools.extract_fio_debtor(doc)  # Извлечение ФИО должника
            case_number = docx_tools.extract_case_number(doc)  # Извлечение номера дела

            # 2️⃣ Разархивировать досье
            path_archive = file_tools.find_dossier_archive(folder)  # Путь к архиву досье
            path_extract = folder / fio_debtor  # Папка для распаковки архива досье
            path_dossier = file_tools.unzip_archive(path_archive, path_extract)  # Распаковка архива досье
            file_tools.unzip_all_nested_archives(path_dossier)  # Распаковка вложенных архивов в досье
            file_tools.delete_file(path_archive)  # Удаление архива досье после распаковки

            # 3️⃣ Переместить документ РТК в папку досье
            self.current_path_doc = file_tools.move_file(path_doc, path_dossier)

            # 4️⃣ Создать папку арбитражного дела
            name_arbitter = path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}'
            path_arbitter = file_tools.ensure_folder(name_arbitter)

            # 5️⃣ Скопировать папки обязательств в папку арбитражного дела
            # Исключая папку арбитражного дела, если она уже существует
            paths_obligations = file_tools.find_folders_obligations(path_dossier)  # Поиск папок обязательств
            for path_oblig in paths_obligations:
                if path_oblig == path_arbitter:
                    continue
                file_tools.copy_folder(path_oblig, path_arbitter)

            self.view.set_current_case(f'{case_number} {fio_debtor}')

        except Exception as e:
            self.view.append_log(f'Произошла ошибка: {e}')

    def _form_package_without_statement(self, folder_path: str):
        """Формирование пакета документов без заявления"""
        folder = Path(folder_path)
        try:
            path_archive = file_tools.find_dossier_archive(folder)  # Путь к архиву досье
            case_number = get_case_number_from_filename(path_archive.name)  # Извлечение номера дела из имени архива
            path_extract = f'{folder / case_number} без заявления'  # Папка для распаковки архива досье
            path_dossier = file_tools.unzip_archive(path_archive, path_extract)  # Распаковка архива досье
            self.current_path_dossier = path_dossier  # Сохраняем путь к папке досье
            file_tools.unzip_all_nested_archives(path_dossier)  # Распаковка вложенных архивов в досье
            file_tools.delete_file(path_archive)  # Удаление архива досье после распаковки

            self.view.set_current_case(f'{case_number} без заявления')
            self.view.append_log('Пакет документов сформирован без заявления.')
        except Exception as e:
            self.view.append_log(f'Произошла ошибка: {e}')

    def _proccess_statement(self, path_doc: Path) -> None:
        """Обработка заявления"""
        doc = docx_tools.open_docx(path_doc)

        def _step(step_name: str, func: callable, *args):
            try:
                func(*args)
                doc.save(path_doc)
            except Exception as e:
                self.view.append_log(f'{step_name}: ошибка — {e}')

        # Удаление слов из документа
        del_words = load_del_words()
        if del_words:
            _step('Удаление слов', docx_tools.delete_words, doc, del_words)

        # Удаление параграфов из документа
        del_paragraphs = load_del_paragraphs()
        if del_paragraphs:
            _step('Удаление параграфов', docx_tools.delete_paragraphs, doc, del_paragraphs)

        # Вставка шаблона госпошлины
        gosposhlina_temp = get_gosposhlina_template()
        if gosposhlina_temp:
            _step('Вставка шаблона госпошлины', docx_tools.insert_gosposhlina, doc, gosposhlina_temp)

        # Форматирование списка приложений
        _step('Форматирование приложений', docx_tools.format_appendices, doc)

        # Вставка реквизитов банка в таблицу
        if self.have_bank_requisites:
            path_requisites = load_bank_requisites_directory()
            doc_requisities = docx_tools.open_docx(path_requisites)
            _step(
                'Вставка реквизитов банка',
                docx_tools.insert_bank_table,
                doc,
                doc_requisities,
                self.view.bank_selector.currentText(),
            )
        else:
            self.view.append_log('Банковские реквизиты не заменены')

    def _insert_statement(self, folder_path: str) -> None:
        """Вставка заявления в пакет документов"""
        folder = Path(folder_path)
        try:
            # 1️⃣ Найти документ РТК и извлечь данные должника
            path_doc = file_tools.find_rtk_doc(folder)  # Путь к документу РТК
            doc = docx_tools.open_docx(path_doc)  # Открытие документа РТК
            fio_debtor = docx_tools.extract_fio_debtor(doc)  # Извлечение ФИО должника
            case_number = docx_tools.extract_case_number(doc)  # Извлечение номера дела

            # 2️⃣ Поиск и переименование папки досье
            path_dossier = self.current_path_dossier
            path_dossier = file_tools.rename_folder(path_dossier, fio_debtor)  # Переименование папки досье

            # 3️⃣ Переместить документ РТК в папку досье
            self.current_path_doc = file_tools.move_file(path_doc, path_dossier)

            # 4️⃣ Создать папку арбитражного дела
            name_arbitter = path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}'
            path_arbitter = file_tools.ensure_folder(name_arbitter)

            # 5️⃣ Скопировать папки обязательств в папку арбитражного дела
            # Исключая папку арбитражного дела, если она уже существует
            paths_obligations = file_tools.find_folders_obligations(path_dossier)  # Поиск папок обязательств
            for path_oblig in paths_obligations:
                if path_oblig == path_arbitter:
                    continue
                file_tools.copy_folder(path_oblig, path_arbitter)

            self.view.set_current_case(f'{case_number} {fio_debtor}')
        except Exception as e:
            self.view.append_log(f'Ошибка при добавлении заявления: {e}')

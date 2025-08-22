from pathlib import Path

from src.core import docx_tools, file_tools
from src.utils.settings_utils import load_work_directory
from src.utils.templates_utils import (
    load_bank_requisites,
    load_del_paragraphs_appendices,
    load_del_paragraphs_gosposhlina,
    load_del_paragraphs_obyazatelstv,
    load_del_words_obyazatelstv,
    load_gosposhlina_template,
    load_zalog_contacts_template,
)
from src.utils.text_utils import sanitize_filename


def form_package(folder_path: str):
    """
    Формирование пакета документов по банкротству
    Архив + Заявление
    """
    folder = Path(folder_path)
    try:
        # 1 Найти документ РТК и извлечь данные должника
        path_doc = file_tools.find_rtk_doc(folder)  # Путь к документу РТК
        doc = docx_tools.open_docx(path_doc)  # Открытие документа РТК
        fio_debtor = docx_tools.extract_fio_debtor(doc)  # Извлечение ФИО должника
        case_number = docx_tools.extract_case_number(doc)  # Извлечение номера дела

        # 2 Разархивировать досье
        path_archive = file_tools.find_dossier_archive(folder)  # Путь к архиву досье
        path_extract = folder / fio_debtor  # Папка для распаковки архива досье
        path_dossier = file_tools.unzip_archive(path_archive, path_extract)  # Распаковка архива досье
        file_tools.unzip_all_nested_archives(path_dossier)  # Распаковка вложенных архивов в досье
        file_tools.delete_file(path_archive)  # Удаление архива досье после распаковки

        # 3 Переместить документ РТК в папку досье
        current_path_doc = file_tools.move_file(path_doc, path_dossier)

        # 4 Создать папку арбитражного дела
        name_arbitter = path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}'
        path_arbitter = file_tools.ensure_folder(name_arbitter)

        # 5 Скопировать папки обязательств в папку арбитражного дела
        # Исключая папку арбитражного дела, если она уже существует
        paths_obligations = file_tools.find_folders_obligations(path_dossier)  # Поиск папок обязательств
        for path_oblig in paths_obligations:
            if path_oblig == path_arbitter:
                continue
            file_tools.copy_folder(path_oblig, path_arbitter)

        return current_path_doc, fio_debtor, case_number

    except Exception as e:
        raise e


def proccess_statement(path_doc: Path, bank):
    """Обработка заявления"""
    doc = docx_tools.open_docx(path_doc)

    def _step(step_name: str, func: callable, *args):  # Функция для выполнения каждого шага обработки
        try:
            func(*args)
            doc.save(path_doc)
        except Exception as e:
            raise RuntimeError(f'Ошибка шага "{step_name}": {e}') from e
            # self.view.append_log(f'{step_name}: ошибка — {e}')

    # === Обработка Обязательств ===
    # Удаление слов из документа
    del_words_obyaz = load_del_words_obyazatelstv()
    if del_words_obyaz:
        _step('Удаление слов в Обязательствах', docx_tools.delete_words_in_obyazatelstvo, doc, del_words_obyaz)

    # Удаление параграфов из документа
    del_paragraphs_obyaz = load_del_paragraphs_obyazatelstv()
    if del_paragraphs_obyaz:
        _step('Удаление абзацев в Обязательствах', docx_tools.delete_paragraphs_in_obyazatelstvo, doc, del_paragraphs_obyaz)

    # === Обработка части ПРОСИТ СУД ===
    # Удаление параграфов из документа
    del_paragraphs_gosposhlina = load_del_paragraphs_gosposhlina()
    if del_paragraphs_gosposhlina:
        _step('Удаление пунктов в ПРОСИТ СУД', docx_tools.delete_paragraphs_in_gosposhlina, doc, del_paragraphs_gosposhlina)

    # Вставка шаблона госпошлины
    gosposhlina_temp = load_gosposhlina_template()
    if gosposhlina_temp:
        _step('Вставка шаблона госпошлины', docx_tools.insert_gosposhlina, doc, gosposhlina_temp)

    # === Обработка части Приложения ===
    del_paragraphs_appendices = load_del_paragraphs_appendices()
    if del_paragraphs_appendices:
        _step('Удаление пунктов в Приложения', docx_tools.delete_paragraphs_in_appendices, doc, del_paragraphs_appendices)

    # Форматирование списка приложений
    _step('Форматирование приложений', docx_tools.format_appendices, doc)

    # === Обработка части Реквизиты ===
    # Вставка реквизитов банка в таблицу
    if bank:
        doc_requisities = load_bank_requisites()
        _step('Вставка реквизитов банка', docx_tools.insert_bank_table, doc, doc_requisities, bank)

    # === Обработка контактов ===
    # Вставка залоговых контактов
    zalog_contacts_temp = load_zalog_contacts_template()
    if zalog_contacts_temp:
        _step('Вставка залоговых контактов ', docx_tools.insert_zalog_contacts, doc, zalog_contacts_temp)

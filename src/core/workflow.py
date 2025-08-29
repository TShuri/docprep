import os
from pathlib import Path

from src.core import docx_tools, file_tools, pdf_tools
from src.utils.templates_utils import (
    load_bank_requisites,
    load_del_paragraphs_appendices,
    load_del_paragraphs_gosposhlina,
    load_del_paragraphs_obyazatelstv,
    load_del_words_obyazatelstv,
    load_gosposhlina_template,
    load_path_signa,
    load_zalog_contacts_template,
)
from src.utils.text_utils import (
    get_case_number_from_filename,
    get_number_obligation_from_foldername,
    sanitize_filename,
    to_iso_date,
)


def form_package(folder_path: str, save_base_statement=False, all_in_arbitter=False):
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

        # Если выбрано сохранение исходного заявления
        if save_base_statement:
            dst_path = current_path_doc.parent / f'Исходное заявление{current_path_doc.suffix}'
            file_tools.copy_file(current_path_doc, dst_path)

        # 4 Создать папку арбитражного дела
        name_arbitter = path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}'
        path_arbitter = file_tools.ensure_folder(name_arbitter)

        # 5 Скопировать папки обязательств в папку арбитражного дела
        # Исключая папку арбитражного дела, если она уже существует
        paths_obligations = file_tools.find_folders_obligations(path_dossier)  # Поиск папок обязательств
        if not all_in_arbitter:
            for path_oblig in paths_obligations:
                if path_oblig == path_arbitter:
                    continue
                file_tools.copy_folder(path_oblig, path_arbitter)
        else:
            for path_oblig in paths_obligations:
                if path_oblig == path_arbitter:
                    continue
                folder_name = os.path.basename(path_oblig)
                num_oblig = get_number_obligation_from_foldername(folder_name)

                if num_oblig:
                    file_tools.copy_contents_with_num(path_oblig, path_arbitter, num_oblig)
                else:  # Если номер не найден, копируем папку целиком
                    file_tools.copy_folder(path_oblig, path_arbitter)

        return current_path_doc, fio_debtor, case_number

    except Exception as e:
        raise e


def unpack_package_no_statement(folder_path: str):
    """
    Распаковка пакета документов по банкротству
    Архив без Заявления
    """
    folder = Path(folder_path)
    try:
        # 1 Разархивировать досье
        path_archive = file_tools.find_dossier_archive(folder)  # Путь к архиву досье
        case_number = get_case_number_from_filename(str(path_archive))
        path_extract = folder / f'{sanitize_filename(case_number)} без заявления'  # Папка для распаковки архива досье
        current_path_dossier = file_tools.unzip_archive(path_archive, path_extract)  # Распаковка архива досье
        file_tools.unzip_all_nested_archives(current_path_dossier)  # Распаковка вложенных архивов в досье
        file_tools.delete_file(path_archive)  # Удаление архива досье после распаковки

        return current_path_dossier, case_number

    except Exception as e:
        raise e


def insert_statement(folder_path: str, path_dossier: str, save_base_statement=False, all_in_arbitter=False):
    """
    Перемещение заявление в распакованный пакет документов по банкротству
    Архив без Заявления
    """
    folder = Path(folder_path)
    try:
        # 1 Найти документ РТК и извлечь данные должника
        path_doc = file_tools.find_rtk_doc(folder)  # Путь к документу РТК
        doc = docx_tools.open_docx(path_doc)  # Открытие документа РТК
        fio_debtor = docx_tools.extract_fio_debtor(doc)  # Извлечение ФИО должника
        case_number = docx_tools.extract_case_number(doc)  # Извлечение номера дела

        # 2 Переименовывание папки досье
        path_dossier = file_tools.rename_folder(path_dossier, fio_debtor)

        # 3 Переместить документ РТК в папку досье
        current_path_doc = file_tools.move_file(path_doc, path_dossier)

        # Если выбрано сохранение исходного заявления
        if save_base_statement:
            dst_path = current_path_doc.parent / f'Исходное заявление{current_path_doc.suffix}'
            file_tools.copy_file(current_path_doc, dst_path)

        # 4 Создать папку арбитражного дела
        name_arbitter = path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}'
        path_arbitter = file_tools.ensure_folder(name_arbitter)

        # 5 Скопировать папки обязательств в папку арбитражного дела
        # Исключая папку арбитражного дела, если она уже существует
        paths_obligations = file_tools.find_folders_obligations(path_dossier)  # Поиск папок обязательств
        if not all_in_arbitter:
            for path_oblig in paths_obligations:
                if path_oblig == path_arbitter:
                    continue
                file_tools.copy_folder(path_oblig, path_arbitter)
        else:
            for path_oblig in paths_obligations:
                if path_oblig == path_arbitter:
                    continue
                folder_name = os.path.basename(path_oblig)
                num_oblig = get_number_obligation_from_foldername(folder_name)

                if num_oblig:
                    file_tools.copy_contents_with_num(path_oblig, path_arbitter, num_oblig)
                else:  # Если номер не найден, копируем папку целиком
                    file_tools.copy_folder(path_oblig, path_arbitter)

        return current_path_doc, fio_debtor, case_number

    except Exception as e:
        raise e


def proccess_statement(path_doc: Path, bank, signa):
    """Обработка заявления"""
    doc = docx_tools.open_docx(path_doc)

    def _step(step_name: str, func: callable, *args):  # Функция для выполнения каждого шага обработки
        try:
            func(*args)
            doc.save(path_doc)
        except Exception as e:
            raise RuntimeError(f'Ошибка шага "{step_name}": {e}') from e

    # === Обработка Обязательств ===
    # Удаление слов из документа
    del_words_obyaz = load_del_words_obyazatelstv()
    if del_words_obyaz:
        _step('Удаление слов в Обязательствах', docx_tools.delete_words_in_obyazatelstvo, doc, del_words_obyaz)

    # Удаление параграфов из документа
    del_paragraphs_obyaz = load_del_paragraphs_obyazatelstv()
    if del_paragraphs_obyaz:
        _step(
            'Удаление абзацев в Обязательствах',
            docx_tools.delete_paragraphs_in_obyazatelstvo,
            doc,
            del_paragraphs_obyaz,
        )

    # === Обработка части ПРОСИТ СУД ===
    # Удаление параграфов из документа
    del_paragraphs_gosposhlina = load_del_paragraphs_gosposhlina()
    if del_paragraphs_gosposhlina:
        _step(
            'Удаление пунктов в ПРОСИТ СУД',
            docx_tools.delete_paragraphs_in_gosposhlina,
            doc,
            del_paragraphs_gosposhlina,
        )

    # Вставка шаблона госпошлины
    gosposhlina_temp = load_gosposhlina_template()
    if gosposhlina_temp:
        _step('Вставка шаблона госпошлины', docx_tools.insert_gosposhlina, doc, gosposhlina_temp)

    # === Обработка части Приложения ===
    del_paragraphs_appendices = load_del_paragraphs_appendices()
    if del_paragraphs_appendices:
        _step(
            'Удаление пунктов в Приложения', docx_tools.delete_paragraphs_in_appendices, doc, del_paragraphs_appendices
        )

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

    # Вставка подписи
    if signa:
        path_signa = load_path_signa()
        _step('Вставка подписи', docx_tools.insert_signature, doc, path_signa)


def check_docx_fields_in_publikaciya(path_docx: Path, path_pdf):
    """
    Проверяет, что данные из docx присутствуют в PDF:
    - Номер дела
    - ФИО должника
    - ФИО финансового управляющего
    - Дата решения
    """
    # Данные с заявления
    try:
        docx_info = {}
        doc = docx_tools.open_docx(path_docx)  # Открытие документа РТК
        docx_info['fio_debtor'] = docx_tools.extract_fio_debtor(doc)  # Извлечение ФИО должника
        docx_info['fio_manager'] = docx_tools.extract_fio_financial_manager(doc)  # Извлечение ФИО финуправляющего
        docx_info['case_number'] = docx_tools.extract_case_number(doc)  # Извлечение номера дела
        docx_info['date'] = docx_tools.extract_date(doc)
    except Exception as e:
        raise RuntimeError(f'Ошибка при извлечении данных с Заявления": {e}') from e

    # Данные с публикации
    text_pdf = pdf_tools.extract_text_from_pdf(path_pdf)
    pdf_info = {}
    try:  # Проверка ФИО должника
        pdf_info['fio_debtor'] = pdf_tools.find_debtor_in_publikatsiya(text_pdf)
    except Exception:
        pdf_info['fio_debtor'] = None

    try:  # Проверка ФИО финансового управляющего
        pdf_info['fio_manager'] = pdf_tools.find_manager_in_publikatsiya(text_pdf)
    except Exception:
        pdf_info['fio_manager'] = None

    try:  # Проверка номера дела
        pdf_info['case_number'] = pdf_tools.find_case_in_publikatsiya(text_pdf)
    except Exception:
        pdf_info['case_number'] = None

    try:  # Проверка даты решения
        pdf_info['date'] = pdf_tools.find_date_in_publikatsiya(text_pdf)
    except Exception:
        pdf_info['date'] = None

    # Сравнение данных из заявления и публикации
    result = {}

    for key in docx_info.keys():
        docx_val = docx_info.get(key)
        pdf_val = pdf_info.get(key)

        if not docx_val or not pdf_val:
            result[key] = None
        else:
            if key == 'date':
                try:
                    result[key] = to_iso_date(docx_val).lower() == pdf_val.lower()
                except Exception:
                    result[key] = None  # если дата не преобразовалась
            else:
                result[key] = docx_val.lower() == pdf_val.lower()

    return docx_info, pdf_info, result

import os
from pathlib import Path

from src.core import docx_tools, file_tools
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
from src.utils.text_utils import get_case_number_from_filename, get_number_obligation_from_foldername, sanitize_filename


def _get_debtor_info(path_folder: Path) -> tuple[str, str, Path]:
    """
    Находит документ РТК и извлекает ФИО должника и номер дела.
    Возвращает (fio_debtor, case_number, path_doc)
    """
    path_doc = file_tools.find_rtk_doc(path_folder)
    doc = docx_tools.open_docx(path_doc)
    fio_debtor = docx_tools.extract_fio_debtor(doc)
    case_number = docx_tools.extract_case_number(doc)
    return path_doc, fio_debtor, case_number


def _extract_dossier(path_folder: Path, path_extract: Path = None) -> Path:
    """
    Находит архив досье и распаковывает его.
    Если задан path_extract, то распакует туда, иначе в папку с '<ФИО> без заявления'.
    Удаляет исходный архив после распаковки.
    """
    path_archive = file_tools.find_dossier_archive(path_folder)
    case_number = get_case_number_from_filename(str(path_archive.stem))
    if path_extract:
        path_dossier = file_tools.unzip_archive(path_archive, path_extract)
    else:
        path_extract = path_folder / f'{sanitize_filename(case_number)} без заявления'
        path_dossier = file_tools.unzip_archive(path_archive, path_extract)
    file_tools.delete_file(path_archive)
    return path_dossier, case_number


def _get_dossier_no_statement(path_folder: Path, fio_debtor: str, case_number: str):
    """Находит распакованную папку досье по его номеру дела и переименовывает ее"""
    case_number = sanitize_filename(case_number)
    path = file_tools.find_dossier_no_statement_folder(path_folder, case_number)
    new_path = file_tools.rename_folder(path, fio_debtor)
    return new_path


def _extract_all_nested_archives(path_folder: Path) -> None:
    """Распаковка вложенных архивов в папке"""
    file_tools.unzip_all_nested_archives(path_folder)


def _move_rtk_doc(path_doc: Path, path_dossier: Path, save_orig=False) -> Path:
    """Перемещение Заявления в папку"""
    current_path_doc = file_tools.move_file(path_doc, path_dossier)
    if save_orig:
        dst_path = current_path_doc.parent / f'Исходное заявление{current_path_doc.suffix}'
        file_tools.copy_file(current_path_doc, dst_path)
    return current_path_doc


def _prepare_arbiter_folder(
    path_dossier: Path, case_number: str, fio_debtor: str, all_in_arb=False, arb_name: str = None
):
    """Формирование папки арбитр"""
    paths_obligations = file_tools.find_folders_obligations(path_dossier)
    if arb_name == '<Номер дела> <ФИО>':
        path_arbitter = file_tools.ensure_folder(path_dossier / f'{sanitize_filename(case_number)} {fio_debtor}')
    elif arb_name == 'Арбитр <ФИО>':
        path_arbitter = file_tools.ensure_folder(path_dossier / f'Арбитр {fio_debtor}')
    else:
        path_arbitter = file_tools.ensure_folder(path_dossier / f'А {fio_debtor}')

    for path_oblig in paths_obligations:
        if all_in_arb:
            folder_name = os.path.basename(path_oblig)
            num_oblig = get_number_obligation_from_foldername(folder_name)
            if num_oblig:
                file_tools.copy_contents_with_num(path_oblig, path_arbitter, num_oblig)
            else:
                file_tools.copy_folder(path_oblig, path_arbitter)
        else:
            file_tools.copy_folder(path_oblig, path_arbitter)

    return path_arbitter


# ==== Функции для контроллера ====
def procces_package(folder_path: str, signa, bank, save_orig=False, all_in_arb=False, arb_name=None):
    """Распаковка архива досье и обработка заявления"""
    folder = Path(folder_path)  # Рабочая директория
    path_doc, fio_debtor, case_number = _get_debtor_info(folder)  # Получение инфо с заявления

    _path_extract = folder / fio_debtor  # Создаём путь для распаковки
    path_dossier, _case_number = _extract_dossier(folder, _path_extract)  # Получаем путь к распакованному архиву

    current_path_doc = _move_rtk_doc(path_doc, path_dossier, save_orig)  # Получаем путь к перемещенному заявлению
    proccess_statement(current_path_doc, bank, signa)  # Обрабатываем заявление

    _extract_all_nested_archives(path_dossier)  # Распаковываем вложенные архивы
    _prepare_arbiter_folder(path_dossier, case_number, fio_debtor, all_in_arb, arb_name)  # Формируем папку арбитр

    return fio_debtor, case_number


def unpack_package(folder_path: str, save_orig=False):
    """Распаковка архива досье без заявления"""
    folder = Path(folder_path)  # Рабочая директория
    path, case_number = _extract_dossier(folder)  # Распаковываем архив
    return case_number


def insert_statement(folder_path: str, signa, bank, save_orig=False, all_in_arb=False, arb_name=None):
    """Вставка заявления в распакованную папку архива досье без заявления"""
    folder = Path(folder_path)  # Рабочая директория
    path_doc, fio_debtor, case_number = _get_debtor_info(folder)  # Получение инфо с заявления

    path_dossier = _get_dossier_no_statement(folder, fio_debtor, case_number)  # Получаем путь к папке досье

    current_path_doc = _move_rtk_doc(path_doc, path_dossier, save_orig)  # Получаем путь к перемещенному заявлению
    proccess_statement(current_path_doc, bank, signa)  # Обрабатываем заявление

    _extract_all_nested_archives(path_dossier)  # Распаковываем вложенные архивы
    _prepare_arbiter_folder(path_dossier, case_number, fio_debtor, all_in_arb, arb_name)  # Формируем папку арбитр

    return fio_debtor, case_number


def proccess_statement(path_doc: Path, bank, signa):
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

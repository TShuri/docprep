from pathlib import Path

from core.docx_tools import open_docx
from core.file_tools import copy_file

# ==== Шаблоны для блока Обязательство ====
DEL_WORDS_OBYAZATELSTVO_PATH = 'templates/obyazatelstvo/del_words.txt'


def load_del_words_obyazatelstv() -> list[str]:
    """Загрузка слов для удаления в частях Обязательств"""
    try:
        with open(DEL_WORDS_OBYAZATELSTVO_PATH, 'r', encoding='utf-8') as file:
            words = [line.strip('\n') for line in file if line.strip()]
        return words
    except FileNotFoundError:
        return None


DEL_PARAGRAPHS_OBYAZATELSTVO_PATH = 'templates/obyazatelstvo/del_paragraphs.txt'


def load_del_paragraphs_obyazatelstv() -> list[str]:
    """Загрузка параграфов для удаления в частях Обязательств"""
    try:
        with open(DEL_PARAGRAPHS_OBYAZATELSTVO_PATH, 'r', encoding='utf-8') as file:
            paragraphs = [line.strip('\n') for line in file if line.strip()]
        return paragraphs
    except FileNotFoundError:
        return None


# ==== Шаблоны для блока ПРОСИТ СУД ====
GOSPOSHLINA_TEMPLATE_PATH = 'templates/gosposhlina/add_gosposhlina.docx'


def load_gosposhlina_template():
    """Загрузка шаблона вставки госпошлины"""
    try:
        gp_temp = open_docx(GOSPOSHLINA_TEMPLATE_PATH)
        return gp_temp
    except FileNotFoundError:
        return None


DEL_PARAGRAPHS_GOSPOSHLINA_PATH = 'templates/gosposhlina/del_paragraphs.txt'


def load_del_paragraphs_gosposhlina():
    """Загрузка параграфов для удаления в блоке ПРОСИТ СУД"""
    try:
        with open(DEL_PARAGRAPHS_GOSPOSHLINA_PATH, 'r', encoding='utf-8') as file:
            paragraphs = [line.strip('\n') for line in file if line.strip()]
        return paragraphs
    except FileNotFoundError:
        return None


# ==== Шаблоны для блока Приложения ====


DEL_PARAGRAPHS_APPENDICES_PATH = 'templates/appendices/del_paragraphs.txt'


def load_del_paragraphs_appendices():
    """Загрузка параграфов для удаления в блоке Приложения"""
    try:
        with open(DEL_PARAGRAPHS_APPENDICES_PATH, 'r', encoding='utf-8') as file:
            paragraphs = [line.strip('\n') for line in file if line.strip()]
        return paragraphs
    except FileNotFoundError:
        return None


# ==== Шаблоны для блока Реквизиты ====
BANK_REQUISITES_FILE = Path('templates/bank_requisites.docx')


def save_bank_requisites_directory(path: str) -> None:
    """
    Сохраняет путь к файлу с реквизитами банка в templates/bank_requisites.docx
    """
    copy_file(path, BANK_REQUISITES_FILE)


def load_bank_requisites_directory() -> str | None:
    """
    Загружает путь к файлу с реквизитами банка из templates/bank_requisites.docx
    :return: Путь к файлу с реквизитами или None, если файл не существует
    """
    if not BANK_REQUISITES_FILE.exists():
        return None

    return str(BANK_REQUISITES_FILE.resolve())


# ==== Шаблоны для блока Контакты ====
ZALOG_CONTACTS_TEMPLATE_PATH = 'templates/zalog_contacts.docx'


def load_zalog_contacts_template():
    """Загрузка шаблона вставки залоговых контактов"""
    try:
        z_contacts = open_docx(ZALOG_CONTACTS_TEMPLATE_PATH)
        return z_contacts
    except FileNotFoundError:
        return None


if __name__ == '__main__':
    load_del_paragraphs_gosposhlina()

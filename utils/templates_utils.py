from pathlib import Path

from core.docx_tools import open_docx
from core.file_tools import copy_file

DEL_WORDS_PATH = 'templates/del_words.txt'


def load_del_words() -> list[str]:
    """Загрузка слов для удаления из файла"""
    try:
        with open(DEL_WORDS_PATH, 'r', encoding='utf-8') as file:
            words = [line.strip('\n') for line in file if line.strip()]
        return words
    except FileNotFoundError:
        return None


DEL_PARAGRAPHS_PATH = 'templates/del_paragraphs.txt'


def load_del_paragraphs() -> list[str]:
    """Загрузка параграфов для удаления из файла"""
    try:
        with open(DEL_PARAGRAPHS_PATH, 'r', encoding='utf-8') as file:
            paragraphs = [line.strip('\n') for line in file if line.strip()]
        return paragraphs
    except FileNotFoundError:
        return None


GOSPOSHLINA_TEMPLATE_PATH = 'templates/gosposhlina.docx'


def get_gosposhlina_template():
    try:
        gp_temp = open_docx(GOSPOSHLINA_TEMPLATE_PATH)
        return gp_temp
    except FileNotFoundError:
        return None


ZALOG_CONTACTS_TEMPLATE_PATH = 'templates/zalog_contacts.docx'


def get_zalog_contacts_template():
    try:
        z_contacts = open_docx(ZALOG_CONTACTS_TEMPLATE_PATH)
        return z_contacts
    except FileNotFoundError:
        return None


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


if __name__ == '__main__':
    # Пример использования
    words = load_del_words()
    print(words)

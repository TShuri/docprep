from pathlib import Path

from core.file_tools import copy_file

SETTINGS_FILE_WORK_DIR = Path("settings/work_directory.txt")

def save_work_directory(path: str) -> None:
    """
    Сохраняет путь к рабочей папке в settings/work_directory.txt
    """
    SETTINGS_FILE_WORK_DIR.parent.mkdir(exist_ok=True)  # создаём папку settings, если нет
    with open(SETTINGS_FILE_WORK_DIR, "w", encoding="utf-8") as f:
        f.write(path)


def load_work_directory() -> str | None:
    """
    Загружает путь к рабочей папке из settings/work_directory.txt
    :return: Путь к рабочей папке или None, если файл пустой/не существует
    """
    if not SETTINGS_FILE_WORK_DIR.exists():
        return None

    path = SETTINGS_FILE_WORK_DIR.read_text(encoding="utf-8").strip()
    return path if path else None


BANK_REQUISITES_FILE = Path("settings/bank_requisites.docx")

def save_bank_requisites_directory(path: str) -> None:
    """
    Сохраняет путь к файлу с реквизитами банка в settings/bank_requisites.docx
    """
    copy_file(path, BANK_REQUISITES_FILE)

def load_bank_requisites_directory() -> str | None:
    """
    Загружает путь к файлу с реквизитами банка из settings/bank_requisites.docx
    :return: Путь к файлу с реквизитами или None, если файл не существует
    """
    if not BANK_REQUISITES_FILE.exists():
        return None

    return str(BANK_REQUISITES_FILE.resolve())

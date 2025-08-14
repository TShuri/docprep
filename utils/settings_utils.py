from pathlib import Path

SETTINGS_FILE = Path("settings/work_directory.txt")

def save_work_directory(path: str) -> None:
    """
    Сохраняет путь к рабочей папке в settings/work_directory.txt
    """
    SETTINGS_FILE.parent.mkdir(exist_ok=True)  # создаём папку settings, если нет
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write(path)


def load_work_directory() -> str | None:
    """
    Загружает путь к рабочей папке из settings/work_directory.txt
    :return: Путь к рабочей папке или None, если файл пустой/не существует
    """
    if not SETTINGS_FILE.exists():
        return None

    path = SETTINGS_FILE.read_text(encoding="utf-8").strip()
    return path if path else None

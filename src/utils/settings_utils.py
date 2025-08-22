import json
from pathlib import Path

SETTINGS_FILE = Path("src/settings.json")


def save_work_directory(path: str) -> None:
    """
    Сохраняет путь к рабочей папке в settings.json под ключом 'work_directory'
    """
    SETTINGS_FILE.parent.mkdir(exist_ok=True)

    settings = {}
    if SETTINGS_FILE.exists():
        try:
            settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            settings = {}

    settings["work_directory"] = path

    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def load_work_directory() -> Path | None:
    """
    Загружает путь к рабочей папке из settings.json.
    Возвращает Path, если путь задан и существует на диске, иначе None.
    """
    if not SETTINGS_FILE.exists():
        return None

    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    path_str = settings.get("work_directory")
    if not path_str:
        return None

    folder_path = Path(path_str)
    if not folder_path.exists() or not folder_path.is_dir():
        return None

    return folder_path

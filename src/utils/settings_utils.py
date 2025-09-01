import json
from pathlib import Path
from typing import Any

SETTINGS_FILE = Path('src/settings.json')


# --- Базовые(универсальные) функции ---


def _load_settings() -> dict:
    """
    Загружает все настройки из файла.
    Если файла нет или он поврежден, возвращает пустой словарь.
    """
    if not SETTINGS_FILE.exists():
        return {}

    try:
        return json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def _save_settings(settings: dict) -> None:
    """Сохраняет словарь в файл настроек"""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(settings, indent=4, ensure_ascii=False), encoding='utf-8')


def set_setting(key: str, value: Any) -> None:
    """
    Универсальная функция: сохраняет значение по ключу.
    """
    settings = _load_settings()
    settings[key] = value
    _save_settings(settings)


def get_setting(key: str, default: Any = None) -> Any:
    """
    Универсальная функция: загружает значение по ключу.
    Возвращает default, если ключа нет.
    """
    settings = _load_settings()
    return settings.get(key, default)


# --- специальные функции поверх универсальных ---


# Рабочая директория
def save_work_directory(path: str) -> None:
    """Сохраняет путь к рабочей папке в settings.json под ключом 'work_directory'"""
    set_setting('work_directory', path)


def load_work_directory() -> Path | None:
    """
    Загружает путь к рабочей папке из settings.json.
    Возвращает Path, если путь задан и существует на диске, иначе None.
    """
    path_str = get_setting('work_directory')
    if not path_str:
        return None

    folder_path = Path(path_str)
    if not folder_path.exists() or not folder_path.is_dir():
        return None

    return folder_path


# Пересохранение РЦИ
def save_resave_rci(value: bool) -> None:
    """Сохраняет в настройках 'Пересохранение РЦИ после расчета'"""
    set_setting('resave_rci', value)


def load_resave_rci() -> bool | None:
    """
    Загружает флаг 'Пересохранение РЦИ' из settings.json.
    Возвращает Path, если путь задан и существует на диске, иначе None.
    """
    value = get_setting('resave_rci')
    if not value:
        return False

    return value

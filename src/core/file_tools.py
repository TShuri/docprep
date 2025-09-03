import os
import re
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional

import rarfile


def _safe_path(path: Path) -> str:
    """
    Возвращает путь, безопасный для Windows (поддержка длинных путей).
    На других ОС просто возвращает str(path).
    """
    p = str(path.resolve())
    if os.name == 'nt' and not p.startswith('\\\\?\\'):
        return '\\\\?\\' + p
    return p


def find_rtk_doc(folder: str | Path) -> Path:
    """
    Ищет **один** docx-файл, название которого начинается с
    'Заявление на включение в требований в РТК' только в указанной папке.

    :param folder: Папка для поиска
    :return: Путь к найденному docx-файлу
    :raises FileNotFoundError: если файл не найден
    :raises ValueError: если найдено несколько файлов
    """
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f'Папка {folder} не существует')

    pattern = 'Заявление на включение требований*.docx'
    files = list(folder.glob(pattern))  # только текущая папка

    if not files:
        raise FileNotFoundError("Документ 'Заявление на включение в требований' не найден")
    if len(files) > 1:
        raise ValueError(f'Найдено несколько документов: {[str(f) for f in files]}')

    return Path(_safe_path(files[0]))


def find_dossier_archive(folder: str | Path) -> Path:
    """
    Ищет архив, название которого начинается с 'Досье по банкротству'
    только в указанной папке. Архив должен быть только один.

    :param folder: Папка для поиска
    :return: Путь к найденному архиву
    :raises FileNotFoundError: если архив не найден
    :raises ValueError: если найдено несколько архивов
    """
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f'Папка {folder} не существует')

    pattern = 'Досье по банкротству*.zip'
    files = list(folder.glob(pattern))  # только текущая папка

    if not files:
        raise FileNotFoundError("Архив 'Досье по банкротству' не найден")
    if len(files) > 1:
        raise ValueError(f'Найдено несколько архивов: {[str(f) for f in files]}')

    return Path(_safe_path(files[0]))


def find_dossier_no_statement_folder(folder: str | Path, case_number: str) -> Path:
    """
    Ищет папку с названием "<номер дела> без заявления" только в указанной папке.
    Папка должна быть только одна.

    :param folder: Папка для поиска
    :param case_number: Номер дела, который должен быть в имени папки
    :return: Путь к найденной папке
    :raises FileNotFoundError: если папка не найдена
    :raises ValueError: если найдено несколько папок
    """
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f'Папка {folder} не существует')

    case_number_suffix = case_number[1:]
    pattern = re.compile(rf'.*{re.escape(case_number_suffix)} без заявления.*', re.IGNORECASE)
    folders = [f for f in folder.iterdir() if f.is_dir() and pattern.match(f.name)]

    if not folders:
        raise FileNotFoundError(f"Папка для дела '{case_number} без заявления' не найдена")
    if len(folders) > 1:
        raise ValueError(f'Найдено несколько папок для дела {case_number}: {[str(f) for f in folders]}')

    return Path(_safe_path(folders[0]))


def unzip_archive(archive_path: str | Path, extract_to: Optional[str | Path] = None) -> Path:
    """
    Безопасная распаковка ZIP или RAR архива с учётом Windows длинных путей.
    """
    archive_path = Path(archive_path)

    if not archive_path.exists():
        raise FileNotFoundError(f'Архив {archive_path} не найден')

    if extract_to is None:
        extract_to = archive_path.parent / archive_path.stem
    else:
        extract_to = Path(extract_to)

    extract_to.mkdir(parents=True, exist_ok=True)

    suffix = archive_path.suffix.lower()

    archive_str = _safe_path(archive_path)
    extract_str = _safe_path(extract_to)

    if suffix == '.zip':
        with zipfile.ZipFile(archive_str, 'r') as zip_ref:
            for member in zip_ref.namelist():
                try:
                    zip_ref.extract(member, extract_str)
                except Exception as e:
                    raise RuntimeError(f'Ошибка при распаковке {member}: {e}') from e
    elif suffix == '.rar':
        with rarfile.RarFile(archive_str) as rar_ref:
            for member in rar_ref.namelist():
                try:
                    rar_ref.extract(member, extract_str)
                except Exception as e:
                    raise RuntimeError(f'Ошибка при распаковке {member}: {e}') from e
    else:
        raise ValueError(f'Неподдерживаемый формат архива: {archive_path.suffix}')

    return extract_to


def unzip_all_nested_archives(folder: str | Path) -> None:
    """
    Рекурсивно разархивирует все ZIP и RAR файлы в папке.
    Каждый архив распаковывается в подпапку с именем архива.
    Бросает RuntimeError при ошибках распаковки конкретного файла.
    """
    folder = Path(folder)

    for archive_file in folder.rglob('*'):
        if archive_file.suffix.lower() not in ('.zip', '.rar'):
            continue  # Ищем только ZIP и RAR

        extract_to = archive_file.parent / archive_file.stem
        extract_to.mkdir(parents=True, exist_ok=True)

        try:
            unzip_archive(archive_file, extract_to)
        except Exception as e:
            raise RuntimeError(f'Ошибка при распаковке архива {archive_file}: {e}') from e

        # Рекурсивно проверяем новую папку на вложенные архивы
        try:
            unzip_all_nested_archives(extract_to)
        except Exception as e:
            raise RuntimeError(f'Ошибка при рекурсивной распаковке {extract_to}: {e}') from e


def delete_file(path: str | Path) -> None:
    """
    Удаляет файл.
    :param path: Путь к файлу.
    :raises FileNotFoundError: если файл не существует
    :raises IsADirectoryError: если путь указывает на папку
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f'Файл {p} не найден')
    if not p.is_file():
        raise IsADirectoryError(f'Путь {p} не является файлом')
    os.remove(_safe_path(p))  # <-- безопасно для длинных путей


def delete_folder(path: str | Path) -> None:
    """
    Рекурсивно удаляет папку со всем содержимым.
    :param path: Путь к папке.
    :raises FileNotFoundError: если папка не существует
    :raises NotADirectoryError: если путь не папка
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f'Папка {p} не найдена')
    if not p.is_dir():
        raise NotADirectoryError(f'Путь {p} не является папкой')
    shutil.rmtree(_safe_path(p))


def rename_file(path: str | Path, new_name: str) -> Path:
    """
    Переименовывает файл.
    :param path: Путь к файлу.
    :param new_name: Новое имя файла (только имя, без пути).
    :return: Новый путь к файлу.
    :raises FileNotFoundError: если файл не существует
    :raises IsADirectoryError: если путь не файл
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f'Файл {p} не найден')
    if not p.is_file():
        raise IsADirectoryError(f'Путь {p} не является файлом')
    new_path = p.with_name(new_name)
    os.rename(_safe_path(p), _safe_path(new_path))
    return new_path


def rename_folder(path: str | Path, new_name: str) -> Path:
    """
    Переименовывает папку.
    :param path: Путь к папке.
    :param new_name: Новое имя папки (только имя, без пути).
    :return: Новый путь к папке.
    :raises FileNotFoundError: если папка не существует
    :raises NotADirectoryError: если путь не папка
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f'Папка {p} не найдена')
    if not p.is_dir():
        raise NotADirectoryError(f'Путь {p} не является папкой')
    new_path = p.with_name(new_name)
    os.rename(_safe_path(p), _safe_path(new_path))
    return new_path


def copy_file(src: str | Path, dst: str | Path) -> Path:
    """
    Копирует файл в указанное место.
    :param src: Исходный файл
    :param dst: Папка назначения или полный путь нового файла
    :return: Путь к скопированному файлу
    """
    src = Path(src)
    dst = Path(dst)

    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f'Файл {src} не найден')

    if dst.is_dir():
        dst = dst / src.name

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_safe_path(src), _safe_path(dst))
    return dst


def copy_folder(src: str | Path, dst: str | Path) -> Path:
    """
    Копирует папку рекурсивно в указанное место.
    :param src: Исходная папка
    :param dst: Папка назначения
    :return: Путь к скопированной папке
    """
    src = Path(src)
    dst = Path(dst)

    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f'Папка {src} не найдена')

    dst = dst / src.name
    shutil.copytree(_safe_path(src), _safe_path(dst))
    return dst


def move_file(src: str | Path, dst: str | Path) -> Path:
    """
    Перемещает файл в указанное место.
    :param src: Исходный файл
    :param dst: Папка назначения или полный путь нового файла
    :return: Путь к перемещённому файлу
    """
    src = Path(src)
    dst = Path(dst)

    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f'Файл {src} не найден')

    if dst.is_dir():
        dst = dst / src.name

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(_safe_path(src), _safe_path(dst))
    return dst


def move_folder(src: str | Path, dst: str | Path) -> Path:
    """
    Перемещает папку рекурсивно в указанное место.
    :param src: Исходная папка
    :param dst: Папка назначения
    :return: Путь к перемещённой папке
    """
    src = Path(src)
    dst = Path(dst)

    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f'Папка {src} не найдена')

    dst = dst / src.name
    shutil.move(_safe_path(src), _safe_path(dst))
    return dst


def ensure_folder(path: str | Path) -> Path:
    """
    Создаёт папку, если она не существует.
    :param path: Путь к папке
    :return: Путь к созданной или существующей папке
    """
    p = Path(path)
    p_str = _safe_path(p)  # безопасный путь для Windows
    Path(p_str).mkdir(parents=True, exist_ok=True)
    return p


def find_folders_obligations(folder: str | Path) -> List[Path]:
    """
    Возвращает все папки в указанной директории, за исключением папки
    'Документы по банкротству'.

    :param folder: Папка для поиска
    :return: Список путей к найденным папкам
    """
    folder = Path(folder)
    folder_str = _safe_path(folder)

    if not Path(folder_str).exists() or not Path(folder_str).is_dir():
        raise NotADirectoryError(f'Папка {folder} не существует')

    return [
        subfolder
        for subfolder in Path(folder_str).iterdir()
        if subfolder.is_dir() and subfolder.name != 'Документы о банкротстве'
    ]


def copy_contents_with_num(src_folder: str, target_folder: str, num_oblig: str):
    """Копирует содержимое src_folder в target_folder.
    Если имя файла/папки не содержит num_oblig, добавляет его в имя.
    """
    src_folder = Path(src_folder)
    target_folder = Path(target_folder)

    for item in src_folder.iterdir():
        src_path = item
        item_name = item.name

        # Добавляем num_oblig к имени, если его там нет
        if num_oblig not in item_name:
            base, ext = os.path.splitext(item_name)
            item_name = f'{base}_{num_oblig}{ext}'

        dst_path = target_folder / item_name

        if src_path.is_dir():
            copy_contents_with_num(src_path, target_folder, num_oblig)
        else:
            counter = 1
            orig_dst = dst_path
            while dst_path.exists():
                base, ext = os.path.splitext(item_name)
                dst_path = target_folder / f'{base}_{counter}{ext}'
                counter += 1
            shutil.copy2(_safe_path(src_path), _safe_path(dst_path))


# if __name__ == '__main__':
#     # Пример использования
#     try:
#         path = find_dossier_archive('C:\Projects\sber\programs\docprep')
#         print(f'Найден архив: {path}')
#     except Exception as e:
#         print(f'Ошибка: {e}')

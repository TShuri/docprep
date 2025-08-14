import shutil
import zipfile
from pathlib import Path
from typing import List, Optional


def unzip_archive(archive_path: str | Path, extract_to: Optional[str | Path] = None) -> Path:
    """
    Разархивирует ZIP-архив в указанную папку.
    Если extract_to не указан, распаковывает в той же папке, где архив.

    :param archive_path: Путь к ZIP-файлу.
    :param extract_to: Папка, куда распаковать.
    :return: Путь к папке, в которую был извлечён архив.
    """
    archive_path = Path(archive_path)

    if not archive_path.exists():
        raise FileNotFoundError(f'Архив {archive_path} не найден')

    if archive_path.suffix.lower() != '.zip':
        raise ValueError(f'Неподдерживаемый формат архива: {archive_path.suffix}')

    if extract_to is None:  # Если extract_to не задан, распаковываем в той же папке, где архив
        extract_to = archive_path.parent / archive_path.stem
    else:
        extract_to = Path(extract_to)

    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    return extract_to


def unzip_all_nested_archives(folder: str | Path) -> None:
    """
    Рекурсивно разархивирует все ZIP-файлы в папке.
    Каждый архив распаковывается в подпапку с именем архива.
    """
    folder = Path(folder)

    for zip_file in folder.rglob('*.zip'):  # Ищем все ZIP в папке и подпапках
        extract_to = zip_file.parent / zip_file.stem
        unzip_archive(zip_file, extract_to)
        # После распаковки можно рекурсивно проверить новую папку на вложенные архивы
        unzip_all_nested_archives(extract_to)


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
    p.unlink()


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
    shutil.rmtree(p)


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
    p.rename(new_path)
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
    p.rename(new_path)
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
    shutil.copy2(src, dst)
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
    shutil.copytree(src, dst)
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
    shutil.move(str(src), str(dst))
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
    shutil.move(str(src), str(dst))
    return dst


def ensure_folder(path: str | Path) -> Path:
    """
    Создаёт папку, если она не существует.
    :param path: Путь к папке
    :return: Путь к созданной или существующей папке
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


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

    return files[0]


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

    return files[0]


def find_folders_obligations(folder: str | Path) -> List[Path]:
    """
    Возвращает все папки в указанной директории, за исключением папки
    'Документы по банкротству'.

    :param folder: Папка для поиска
    :return: Список путей к найденным папкам
    """
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f'Папка {folder} не существует')

    return [
        subfolder
        for subfolder in folder.iterdir()
        if subfolder.is_dir() and subfolder.name != 'Документы о банкротстве'
    ]


# if __name__ == '__main__':
#     # Пример использования
#     try:
#         path = find_dossier_archive('C:\Projects\sber\programs\docprep')
#         print(f'Найден архив: {path}')
#     except Exception as e:
#         print(f'Ошибка: {e}')

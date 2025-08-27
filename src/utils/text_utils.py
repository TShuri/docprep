import re
from typing import Optional


def sanitize_filename(name: str) -> str:
    """
    Заменяет недопустимые символы в имени файла.
    Сейчас заменяет '/' на '-'.

    :param name: Исходная строка
    :return: Строка, безопасная для использования в имени файла
    """
    if not isinstance(name, str):
        raise TypeError('name должен быть строкой')

    sanitized = name.replace('/', '-')
    return sanitized


def get_case_number_from_filename(filename: str) -> str:
    """
    Извлекает номер дела из имени файла.
    Разбивает имя файла по пробелам и ищет подстроку,
    содержащую символы '-' и '_'.

    :param filename: Имя файла
    :return: Номер дела или пустая строка, если не найден
    """
    for part in filename.split():
        if '-' in part and '_' in part:
            return part
    return ''

def get_number_obligation_from_foldername(foldername: str) -> Optional[str]:
    """Извлекает номер обязательства из названия папки обязательства.
    Возвращает None, если номер не найден или формат некорректный.
    """
    if not foldername:  # пустая строка или None
        return None

    parts = foldername.split()
    if len(parts) < 3:
        return None

    candidate = parts[-3].strip()
    # Проверка: есть ли хотя бы одна цифра
    if re.search(r"\d", candidate):
        return candidate

    return None


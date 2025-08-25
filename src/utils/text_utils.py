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

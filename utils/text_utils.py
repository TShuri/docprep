def sanitize_filename(name: str) -> str:
    """
    Заменяет недопустимые символы в имени файла.
    Сейчас заменяет '/' на '-'.

    :param name: Исходная строка
    :return: Строка, безопасная для использования в имени файла
    """
    if not isinstance(name, str):
        raise TypeError("name должен быть строкой")
    
    sanitized = name.replace("/", "-")
    return sanitized

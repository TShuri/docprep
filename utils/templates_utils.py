from core.docx_tools import open_docx

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


if __name__ == '__main__':
    # Пример использования
    words = load_del_words()
    print(words)

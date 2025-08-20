DEL_WORDS_PATH = 'templates/del_words.txt'

def load_del_words() -> list[str]:
    """Загрузка слов для удаления из файла"""
    try:
        with open(DEL_WORDS_PATH, 'r', encoding='utf-8') as file:
            words = [line.strip('\n') for line in file if line.strip()]
        return words
    except FileNotFoundError:
        print(f"Файл {DEL_WORDS_PATH} не найден.")
        
if __name__ == "__main__":
    # Пример использования
    words = load_del_words()
    print(words)
import fitz  # PyMuPDF


def extract_text_from_pdf(path_pdf: str) -> str:
    """
    Извлекает весь текст из PDF.
    Возвращает строку с текстом всех страниц.
    """
    doc = fitz.open(path_pdf)
    text_chunks = []
    for page in doc:
        text_chunks.append(page.get_text('text'))
    return '\n'.join(text_chunks)

# === Поиск полей в публикации ===
def find_debtor_in_publikatsiya(text_pdf: str, fio_debtor: str) -> bool:
    """
    Ищет ФИО должника в тексте PDF.
    Находит абзац с текстом "ФИО должника" и проверяет,
    встречается ли fio_debtor в следующем абзаце.

    text_pdf: текст PDF (вся строка, с разделением абзацев \n)
    fio_debtor: строка с ФИО должника

    Возвращает True, если найдено, иначе False.
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    for i, para in enumerate(paragraphs[:-1]):  # кроме последнего
        if 'ФИО должника' in para:
            next_para = paragraphs[i + 1]
            return fio_debtor in next_para
        else:
            return False

    return False


def find_manager_in_publikatsiya(text_pdf: str, fio_manager: str) -> bool:
    """
    Ищет ФИО финансового управляющего в тексте PDF.
    Находит абзац с текстом "управляющий" и проверяет,
    встречается ли fio_manager в следующем абзаце.

    text_pdf: текст PDF (вся строка, с разделением абзацев \n)
    fio_manager: строка с ФИО финасового управляющего

    Возвращает True, если найдено, иначе False.
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    for i, para in enumerate(paragraphs[:-1]):  # кроме последнего
        if 'управляющий' in para:
            next_para = paragraphs[i + 1]
            return fio_manager in next_para
        else:
            return False

    return False


def find_case_in_publikatsiya(text_pdf: str, case_number: str) -> bool:
    """
    Ищет номер дела в тексте PDF.
    Находит абзац с текстом "# дела" и проверяет,
    встречается ли case_number в следующем абзаце.

    text_pdf: текст PDF (вся строка, с разделением абзацев \n)
    case_number: строка с номером дела

    Возвращает True, если найдено, иначе False.
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    for i, para in enumerate(paragraphs[:-1]):  # кроме последнего
        if '# дела' in para:
            next_para = paragraphs[i + 1]
            return case_number in next_para
        else:
            return False

    return False

def find_date_in_publikatsiya(text_pdf: str, date: str) -> bool:
    """
    Ищет дату решения в тексте PDF.
    Находит абзац с текстом "Дата решения" и проверяет,
    встречается ли date через 3 абзаца.

    text_pdf: текст PDF (вся строка, с разделением абзацев \n)
    date: строка с датой решения

    Возвращает True, если найдено, иначе False.
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    for i, para in enumerate(paragraphs[:-3]):  # кроме последнего
        if 'Дата решения' in para:
            next_para = paragraphs[i + 3]
            return date in next_para
        else:
            return False

    return False

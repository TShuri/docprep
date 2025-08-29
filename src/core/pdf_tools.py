import re

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
def find_debtor_in_publikatsiya(text_pdf: str):
    """
    Ищет ФИО должника в тексте PDF и возвращает
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    for i, para in enumerate(paragraphs[:-1]):  # кроме последнего
        if 'ФИО должника' in para:
            next_para = paragraphs[i + 1]
            return next_para

    return None


def find_manager_in_publikatsiya(text_pdf: str):
    """
    Ищет ФИО финансового управляющего в тексте PDF и возвращает.
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    for i, para in enumerate(paragraphs[:-1]):  # кроме последнего
        if 'управляющий' in para:
            next_para = paragraphs[i + 1]

            fio = next_para.split("(", 1)[0].strip() # Убираем лишнее в строке
            return fio if fio else None

    return None


def find_case_in_publikatsiya(text_pdf: str):
    """
    Ищет номер дела в тексте PDF и возвращает.
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    for i, para in enumerate(paragraphs[:-1]):  # кроме последнего
        if '# дела' in para:
            next_para = paragraphs[i + 1]
            return next_para

    return None


def find_date_in_publikatsiya(text_pdf: str) -> str | None:
    """
    Ищет дату решения в тексте PDF.
    Дата ищется в блоке текста между абзацами:
      "Публикуемые сведения"  и  "Текст:".
    Формат даты: YYYY-MM-DD.
    """
    paragraphs = [p.strip() for p in text_pdf.split('\n') if p.strip()]

    try:
        start_idx = next(i for i, p in enumerate(paragraphs) if 'Публикуемые сведения' in p)
        end_idx = next(i for i, p in enumerate(paragraphs) if 'Текст:' in p)
    except StopIteration:
        return None  # если не нашли границы блока

    block = paragraphs[start_idx:end_idx]

    # Ищем дату по регулярке
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    for para in block:
        match = date_pattern.search(para)
        if match:
            return match.group(0)

    return None

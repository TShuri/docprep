import fitz  # PyMuPDF
from rapidfuzz import fuzz


def _extract_text_from_pdf(pdf_path: str) -> str:
    """
    Извлекает весь текст из PDF.
    Возвращает строку с текстом всех страниц.
    """
    doc = fitz.open(pdf_path)
    text_chunks = []
    for page in doc:
        text_chunks.append(page.get_text("text"))
    return " ".join(text_chunks)


def _check_field_in_pdf(value: str, pdf_text: str, threshold: int = 80) -> bool:
    """
    Проверяет, встречается ли value в pdf_text.
    Использует fuzzy-поиск, чтобы учитывать переносы/разрывы.
    threshold — минимальный процент совпадения.
    """
    if not value:
        return False
    score = fuzz.partial_ratio(value, pdf_text)
    return score >= threshold


def check_fields_in_pdf(fields: dict, pdf_path: str, threshold: int = 80) -> dict:
    """
    Проверяет все поля из docx в PDF.
    fields: dict = {"debtor": str, "manager": str, "case": str, "date": str}
    Возвращает словарь вида {"debtor": True/False, ...}
    """
    pdf_text = _extract_text_from_pdf(pdf_path)
    results = {}
    for key, value in fields.items():
        results[key] = _check_field_in_pdf(value, pdf_text, threshold)
    return results

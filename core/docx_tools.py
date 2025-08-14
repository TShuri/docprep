import re
from pathlib import Path
from typing import Optional

from docx import Document


def _open_docx(path: str | Path) -> Document:
    """
    Открывает существующий документ Word.
    :param path: Путь к файлу docx
    :return: Объект Document
    """
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f'Файл {path} не найден')
    return Document(path)


def _extract_after_label(doc: Document, label: str) -> Optional[str]:
    """
    Поиск метки (label) и возвращение текста следующего абзаца после неё
    """

    for i, para in enumerate(doc.paragraphs):
        if label in para.text:
            if i + 1 < len(doc.paragraphs):
                return doc.paragraphs[i + 1].text.strip()
            else:
                return None
    return None


def extract_fio_debtor(docx_path: Path) -> Optional[str]:
    """
    Извлечение ФИО должника. Метка: 'Должник:'
    """
    doc = _open_docx(docx_path)
    return _extract_after_label(doc, 'Должник:')


# def extract_fio_financial_manager(docx_path: Path) -> Optional[str]:
#     """
#     Извлечение ФИО фин. управляющего. Метка: 'Финансовый управляющий:'
#     """
#     doc = _open_docx(docx_path)
#     return _extract_after_label(doc, 'Финансовый управляющий:')


def extract_case_number(docx_path: Path) -> Optional[str]:
    """
    Извлечение номера дела. Формат: Дело № A33-12345/2024
    """
    doc = _open_docx(docx_path)
    pattern = r'Дело\s+№\s*([AА]\d{2}-\d+/\d{4})'

    for para in doc.paragraphs:
        match = re.search(pattern, para.text)
        if match:
            return match.group(1)

    return None

if __name__ == '__main__':
    # Пример использования
    try:
        doc_path = Path('заявление на включение требований в РТК_2rsfdofiswdf.docx.docx')  # Замените на ваш путь к файлу
        print(f'ФИО должника: {extract_fio_debtor(doc_path)}')
        print(f'Номер дела: {extract_case_number(doc_path)}')
    except Exception as e:
        print(f'Ошибка: {e}')
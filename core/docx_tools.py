import re
from pathlib import Path
from typing import Optional

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


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


def format_appendices(docx_path: Path) -> None:
    """
    Форматирует блок "ПРИЛОЖЕНИЯ:" в документе как нумерованный список.
    Убирает старые цифры перед созданием формата списка.
    """
    doc = _open_docx(docx_path)
    appendices_start = None
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip().upper() == "ПРИЛОЖЕНИЯ:" and any(run.bold for run in para.runs):
            appendices_start = i + 1
            break

    if appendices_start is None:
        return  # Блок не найден

    num_id = 1  # id нумерации Word, можно оставить 1 для простого случая

    for para in doc.paragraphs[appendices_start:]:
        text = para.text.strip()
        if text and re.match(r'^\d+\.\s+', text):
            run_formats = [(run.font.name, run.font.size, run.font.bold, run.font.italic) for run in para.runs]

            para.text = re.sub(r'^\d+\.\s+', '', text)

            p = para._p
            pPr = p.get_or_add_pPr()
            numPr = OxmlElement('w:numPr')

            ilvl = OxmlElement('w:ilvl')
            ilvl.set(qn('w:val'), '0')
            numPr.append(ilvl)

            numId = OxmlElement('w:numId')
            numId.set(qn('w:val'), str(num_id))
            numPr.append(numId)

            pPr.append(numPr)

            for run, (name, size, bold, italic) in zip(para.runs, run_formats):
                run.font.name = name
                run.font.size = size
                run.font.bold = bold
                run.font.italic = italic
        else:
            break
    doc.save(docx_path)

if __name__ == '__main__':
    # Пример использования
    try:
        doc_path = Path('заявление на включение требований в РТК_2rsfdofiswdf.docx.docx')
        
        format_appendices(doc_path)
        
    except Exception as e:
        print(f'Ошибка: {e}')

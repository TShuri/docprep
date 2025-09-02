from pathlib import Path

from openpyxl import load_workbook


def resave_files(files):
    """
    Пересохраняет файлы Excel (убирает вычисляемые формулы, пересобирает структуру).
    """
    logs = []
    for file in files:
        try:
            wb = load_workbook(file, data_only=True)
            wb.save(file)
        except Exception as e:
            logs.append(f'<b>Ошибка при пересохранении файла {Path(file).name}: {e}</b>')
        finally:
            try:
                wb.close()
            except Exception:
                pass
    logs.append('<b>Все файлы пересохранены</b>')
    return '\n'.join(logs)

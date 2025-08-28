from pathlib import Path

from src.core.workflow import check_docx_fields_in_pdf


class PDFReaderController:
    def __init__(self, view):
        # Подключение view
        self.view = view

        # Инициализация необходимых параметров
        self.files = {'zayavlenie': None, 'publikaciya': None, 'reshenie': None}

        # Подписываемся на сигналы из DragDropLabel
        self.view.label_zayavlenie.file_dropped.connect(self.update_file)
        self.view.label_publikaciya.file_dropped.connect(self.update_file)
        self.view.label_reshenie.file_dropped.connect(self.update_file)

        # Сигналы кнопок
        self.view.process_clicked.connect(self.handle_process_clicked)
        self.view.reset_clicked.connect(self.handle_reset_clicked)

    def handle_process_clicked(self):
        """Сверка документов"""
        self.view.reset_log()

        zayavlenie_path = self.files.get('zayavlenie')
        publikaciya_path = self.files.get('publikaciya')
        resh_path = self.files.get('reshenie')

        # Проверка выбора файлов
        if not zayavlenie_path or not zayavlenie_path.lower().endswith('.docx'):
            self.view.log('Не выбран файл заявления (.docx)')
            return

        if publikaciya_path:
            res = check_docx_fields_in_pdf(zayavlenie_path, publikaciya_path)
            self.print_result(res, 'publikaciya')
        else:
            self.view.log('PDF файл с публикацией не выбран', 'publikaciya')

        if resh_path:
            res = check_docx_fields_in_pdf(zayavlenie_path, resh_path)
            self.print_result(res, 'reshenie')
        else:
            self.view.log('PDF файл с решением суда не выбран', 'reshenie')

    def handle_reset_clicked(self):
        self.view.label_zayavlenie.setText('Перетащите Заявление (.docx)')
        self.view.label_publikaciya.setText('Перетащите публикацию (.pdf)')
        self.view.label_reshenie.setText('Перетащите решение суда (.pdf)')
        self.view.reset_log()

    def update_file(self, key, path):
        """Обновляем данные в контроллере по событию из UI"""
        self.files[key] = path

    def print_result(self, result: dict, log):
        """
        Выводит результат сверки в лог.
        result: dict = {"fio_debtor": True/False, "case_number": True/False, ...}
        """
        # словарь соответствий ключей и человеко-читаемых названий
        field_names = {
            "fio_debtor": "ФИО должника",
            "manager": "ФИО финансового управляющего",
            "case_number": "Номер дела",
            "date": "Дата решения",
        }

        for key, found in result.items():
            name = field_names.get(key, key)  # если ключ неизвестен, оставляем как есть
            status = "✅ найдено" if found else "❌ не найдено"
            self.view.log(f"{name}: {status}", log)

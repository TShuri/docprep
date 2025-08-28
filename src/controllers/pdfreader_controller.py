from src.core.workflow import check_docx_fields_in_publikaciya


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

        self.field_names = {  # словарь соответствий ключей и человеко-читаемых названий
            'fio_debtor': 'ФИО должника',
            'fio_manager': 'ФИО финансового управляющего',
            'case_number': 'Номер дела',
            'date': 'Дата решения',
        }

    def handle_process_clicked(self):
        """Сверка документов"""
        self.view.reset_log()

        zayavlenie_path = self.files.get('zayavlenie')
        publikaciya_path = self.files.get('publikaciya')
        resh_path = self.files.get('reshenie')

        # Проверка выбора файлов
        if not zayavlenie_path or not zayavlenie_path.lower().endswith('.docx'):
            self.view.log('Не выбран файл заявления (.docx)', 'zayavlenie')
            return

        if publikaciya_path:
            docx_info, pdf_info, result = check_docx_fields_in_publikaciya(zayavlenie_path, publikaciya_path)
            self.print_docx_info(docx_info, 'zayavlenie')
            self.print_result(pdf_info, result, 'publikaciya')
        else:
            self.view.log('PDF файл с публикацией не выбран', 'publikaciya')

        if resh_path:
            pass
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

    def print_docx_info(self, info, log):
        """
        Выводит данные в лог.
        """
        for key, value in info.items():
            name = self.field_names.get(key, key)  # если ключ неизвестен, оставляем как есть
            if not value:
                self.view.log(f'{name}: не найдено', log)
            else:
                self.view.log(f'{name}: {value}', log)

    def print_result(self, info: dict, result: dict, log):
        """
        Выводит результат сверки в лог.
        info: dict = {'fio_debtor': value}
        result: dict = {"fio_debtor": True/False/None, "case_number": True/False/None, ...}
        """
        for key, found in result.items():
            name = self.field_names.get(key, key)  # если ключ неизвестен, оставляем как есть
            value = info.get(key, key)

            if found is True:
                status = '✅ совпадает'
            elif found is False:
                status = '❌ не совпадает'
            elif not found and value is None:
                status = '⚠️ не найдено'
                value = ''
            else:  # None
                status = '⚠️ ошибка обработки'

            self.view.log(f'{status}/{name}: {value}', log)

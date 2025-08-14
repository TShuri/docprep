# main.py
import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import DocPrepApp  # Импортируем GUI


def main():
    """
    Точка входа для запуска программы DocPrep.
    """
    app = QApplication(sys.argv)
    window = DocPrepApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

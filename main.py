import sys
from PySide6.QtWidgets import QApplication
from window import FramelessWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())

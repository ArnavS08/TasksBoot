import sys
import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from window import FramelessWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "taskbootlogo.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())

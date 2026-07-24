import os
import sys
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPoint


class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()

        font_path = os.path.join(os.path.dirname(__file__), "assets", "PressStart2P-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"path: {font_path}")
            font_family = "Arial"
        else:
            families = QFontDatabase.applicationFontFamilies(font_id)
            font_family = families[0] if families else "Arial"

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_StyledBackground, True) 
        self._old_pos = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # title label
        self.title_label = QLabel("TasksBoot", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.title_label.setObjectName("titleLabel")
        
       
        # Close button
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.close)

        layout.addWidget(self.title_label)
         # tasks
        self.list_tasks = self.read_data(self.get_data())
        for task in self.list_tasks:
                    task_label = QLabel(task, self)
                    task_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
                    task_label.setObjectName("taskLabel")
                    layout.addWidget(task_label)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.resize(400, 200)
        
        # QSS styling
        style = f"""
            QWidget {{
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 10px;
            }}
            #titleLabel {{
                color: white;
                font-family: "{font_family}";
                font-size: 16px;
                padding: 8px;
            }}
            #closeButton {{
                background-color: transparent;
                color: white;
                font-size: 14px;
                border: none;
                padding: 5px;
            }}
            #closeButton:hover {{
                background-color: #ff5555;
                border-radius: 5px;
            }}
            #taskLabel {{
                color: white;
                font-family: "Comfortaa";
                font-size: 14px;
                padding: 5px;
                bold: true;
            }}
        """
        self.setStyleSheet(style)
       
        
    # Dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._old_pos = None
        
    # get data from tasks.json
    def get_data(self) -> str | None:
        try:
            with open("tasks.json", "r") as f:
                data = f.read()
                return data
        except FileNotFoundError:
            return None
    def read_data(self, data) -> list[str]:
        if data is None:
            return []
        try:
            import json
            tasks_data = json.loads(data)
            if isinstance(tasks_data, dict) and "tasks" in tasks_data:
                tasks = tasks_data["tasks"]
            elif isinstance(tasks_data, list):
                tasks = tasks_data
            else:
                return []

            list_of_tasks = []
            for task in tasks:
                if isinstance(task, dict):
                    if "name" in task:
                        list_of_tasks.append(task["name"])
                    elif "task" in task:
                        list_of_tasks.append(task["task"])
            return list_of_tasks
        except json.JSONDecodeError:
            return []
    
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())

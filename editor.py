from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QListWidget, QPushButton, QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
import os

from storage import load_tasks_from_file, save_tasks_to_file


class TaskEditorWindow(QWidget):
    def __init__(self, tasks_path: str, font_family: str | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Editor")
        self.setWindowFlag(Qt.Window)
        
        comfortaa_path = os.path.join(os.path.dirname(__file__), "assets", "Comfortaa-Regular.ttf")
        comfortaa_id = QFontDatabase.addApplicationFont(comfortaa_path)
        if comfortaa_id == -1:
            comfortaa_path_alt = os.path.join(os.path.dirname(__file__), "assets", "Comfortaa", "Comfortaa-Regular.ttf")
            comfortaa_id = QFontDatabase.addApplicationFont(comfortaa_path_alt)
        
        if comfortaa_id != -1:
            families = QFontDatabase.applicationFontFamilies(comfortaa_id)
            self.font_family = families[0] if families else "Comfortaa"
        else:
            self.font_family = "Comfortaa"
            
        self.tasks_path = tasks_path
        self.tasks = []
        self.resize(560, 460)

        layout = QVBoxLayout(self)
        row_layout = QHBoxLayout()

        self.task_list = QListWidget(self)
        self.task_list.currentRowChanged.connect(self.load_task_into_form)
        row_layout.addWidget(self.task_list, 1)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Task name:"))
        self.name_input = QLineEdit(self)
        form_layout.addWidget(self.name_input)

        form_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit(self)
        self.description_input.setFixedHeight(120)
        form_layout.addWidget(self.description_input)

        form_layout.addWidget(QLabel("Priority:"))
        self.priority_input = QComboBox(self)
        self.priority_input.addItems(["low", "medium", "high"])
        form_layout.addWidget(self.priority_input)

        # Focused Checkbox
        from PySide6.QtWidgets import QCheckBox
        self.focused_input = QCheckBox("Mark as Focused (only one task will be focused)", self)
        form_layout.addWidget(self.focused_input)

        button_layout = QHBoxLayout()
        self.new_btn = QPushButton("New Task", self)
        self.new_btn.clicked.connect(self.clear_form)
        self.add_btn = QPushButton("Add / Save task", self)
        self.add_btn.clicked.connect(self.add_or_update_task)
        self.remove_btn = QPushButton("Remove selected", self)
        self.remove_btn.clicked.connect(self.remove_task)
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.remove_btn)
        form_layout.addLayout(button_layout)

        row_layout.addLayout(form_layout, 2)
        layout.addLayout(row_layout)

        self.save_btn = QPushButton("Reload tasks", self)
        self.save_btn.clicked.connect(self.save_tasks)
        layout.addWidget(self.save_btn)
        self.apply_styles()
        self.load_tasks()

    def clear_form(self):
        self.task_list.setCurrentRow(-1)
        self.task_list.clearSelection()
        self.name_input.clear()
        self.description_input.clear()
        self.priority_input.setCurrentIndex(1)
        self.focused_input.setChecked(False)

    def load_tasks(self):
        self.tasks = load_tasks_from_file(self.tasks_path)
        self.task_list.clear()
        for task in self.tasks:
            label = task.get("task") or task.get("name") or "Untitled"
            priority = task.get("priority", "medium")
            focused_str = " *FOCUSED*" if task.get("focused", False) else ""
            self.task_list.addItem(f"[{priority}] {label}{focused_str}")

    def load_task_into_form(self, index: int):
        if index < 0 or index >= len(self.tasks):
            self.name_input.clear()
            self.description_input.clear()
            self.priority_input.setCurrentIndex(1)
            self.focused_input.setChecked(False)
            return

        entry = self.tasks[index]
        self.name_input.setText(entry.get("task") or entry.get("name") or "")
        self.description_input.setPlainText(entry.get("description", ""))
        priority = entry.get("priority", "medium")
        idx = self.priority_input.findText(priority)
        self.priority_input.setCurrentIndex(idx if idx >= 0 else 1)
        self.focused_input.setChecked(entry.get("focused", False))

    def add_or_update_task(self):
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        priority = self.priority_input.currentText()
        is_focused = self.focused_input.isChecked()

        if not name:
            QMessageBox.warning(self, "Missing name", "Please enter a task name.")
            return

        # If marking this task as focused, clear focused status from all other tasks
        if is_focused:
            for task in self.tasks:
                task["focused"] = False

        current = self.task_list.currentRow()
        if current >= 0 and current < len(self.tasks):
            existing_task = self.tasks[current]
            existing_task["task"] = name
            existing_task["description"] = description
            existing_task["priority"] = priority
            existing_task["focused"] = is_focused
        else:
            task_obj = {
                "task": name,
                "description": description,
                "priority": priority,
                "focused": is_focused
            }
            self.tasks.append(task_obj)
            current = len(self.tasks) - 1

        # Re-render list display to show *FOCUSED* tags correctly
        self.task_list.clear()
        for task in self.tasks:
            lbl = task.get("task") or task.get("name") or "Untitled"
            pri = task.get("priority", "medium")
            focused_str = " *FOCUSED*" if task.get("focused", False) else ""
            self.task_list.addItem(f"[{pri}] {lbl}{focused_str}")
        self.task_list.setCurrentRow(current)

    def remove_task(self):
        current = self.task_list.currentRow()
        if current < 0 or current >= len(self.tasks):
            return
        self.tasks.pop(current)
        self.task_list.takeItem(current)
        self.load_task_into_form(self.task_list.currentRow())

    def save_tasks(self):
        from window import FramelessWindow

        try:
            save_tasks_to_file(self.tasks_path, self.tasks)
            QMessageBox.information(self, "Saved", "Tasks saved successfully.")
            # notify any FramelessWindow instances to reload tasks
            for w in QApplication.topLevelWidgets():
                try:
                    if isinstance(w, FramelessWindow):
                        w.reload_tasks()
                except Exception:
                    pass
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", f"Unable to save tasks:\n{exc}")

    def apply_styles(self):
        style = f"""
        QWidget {{
            background-color: #2b2b2b;
            color: white;
            font-family: '{self.font_family}';
        }}
        QListWidget {{
            background-color: #3c3c3c;
            border: 1px solid #555;
        }}
        QLabel, QLineEdit, QTextEdit, QComboBox, QListWidget, QPushButton {{
            color: white;
            font-family: '{self.font_family}';
        }}
        QPushButton {{
            background-color: #555;
            border: none;
            padding: 5px;
        }}
        QTextEdit {{
            background-color: #333;
            border: 1px solid #444;
        }}
        """
        self.setStyleSheet(style)


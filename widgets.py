from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer


class TaskItem(QWidget):
    """A small widget that encapsulates a task label and its animations."""

    def __init__(self, task_data: str | dict, font_family: str | None = None, parent=None):
        super().__init__(parent)
        self.font_family = font_family
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        if isinstance(task_data, dict):
            self.task_data = task_data
            text = task_data.get("task") or task_data.get("name") or ""
            self.focused = task_data.get("focused", False)
        else:
            self.task_data = {"task": task_data, "focused": False}
            text = task_data
            self.focused = False

        self.label = QLabel(text, self)
        self.label.setObjectName("taskLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.update_style()

        self._layout.addWidget(self.label)

        # opacity effect for fade animations
        self.opacity = QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity)

        self.animation = QPropertyAnimation(self.opacity, b"opacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def update_style(self):
        font_style = f"font-family: '{self.font_family}';" if self.font_family else ""
        if self.focused:
            self.label.setStyleSheet(f"{font_style} color: #55ff55;")
        else:
            self.label.setStyleSheet(f"{font_style} color: white;")

    def set_highlighted(self, highlighted: bool):
        font_style = f"font-family: '{self.font_family}';" if self.font_family else ""
        if highlighted:
            self.label.setStyleSheet(f"{font_style} color: #55ff55;")
        else:
            self.label.setStyleSheet(f"{font_style} color: white;")

    def animate_in(self, delay_ms: int = 0):
        if delay_ms <= 0:
            self.animation.start()
        else:
            QTimer.singleShot(delay_ms, self.animation.start)

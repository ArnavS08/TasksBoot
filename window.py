import os

from PySide6.QtGui import QFontDatabase, QIcon, QPixmap, QColor, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication, QSystemTrayIcon, QMenu, QFrame
from PySide6.QtCore import Qt, QTimer, Slot, QPoint

from storage import get_data, read_data, load_tasks_from_file, save_tasks_to_file, get_tasks_storage_path
from widgets import TaskItem
from editor import TaskEditorWindow


class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()

        font_path = os.path.join(os.path.dirname(__file__), "assets", "PressStart2P-Regular.ttf")
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "taskbootlogo.ico")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"path: {font_path}")
            font_family = "Arial"
        else:
            families = QFontDatabase.applicationFontFamilies(font_id)
            font_family = families[0] if families else "Arial"

        comfortaa_path = os.path.join(os.path.dirname(__file__), "assets", "Comfortaa-Regular.ttf")
        comfortaa_id = QFontDatabase.addApplicationFont(comfortaa_path)
        if comfortaa_id == -1:
            task_font_family = "Arial"
        else:
            comfortaa_families = QFontDatabase.applicationFontFamilies(comfortaa_id)
            task_font_family = comfortaa_families[0] if comfortaa_families else "Arial"

        self.font_family = font_family
        self.task_font_family = task_font_family
        self.setWindowIcon(QIcon(icon_path))
        # Position window in the top-right corner of the screen
        screen = QApplication.primaryScreen().geometry()
        self.resize(400, 200)
        x = screen.width() - self.width() - 40
        y = 40
        self.move(x, y)

        # Set stay-on-top window flags initially
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._old_pos = None
        self.preview_popup = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title bar widgetd
        class TitleBar(QWidget):
            def __init__(self, parent_window):
                super().__init__(parent_window)
                self.parent_window = parent_window
                h = QHBoxLayout(self)
                h.setContentsMargins(8, 4, 8, 4)
                self.title = QLabel("TasksBoot", self)
                self.title.setObjectName("titleLabel")
                self.title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
                h.addWidget(self.title)

            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton:
                    self.parent_window._old_pos = event.globalPosition().toPoint()

            def mouseMoveEvent(self, event):
                if self.parent_window._old_pos is not None:
                    delta = event.globalPosition().toPoint() - self.parent_window._old_pos
                    self.parent_window.move(self.parent_window.x() + delta.x(), self.parent_window.y() + delta.y())
                    self.parent_window._old_pos = event.globalPosition().toPoint()

            def mouseReleaseEvent(self, event):
                self.parent_window._old_pos = None

        self.title_bar = TitleBar(self)
        self.tasks_path = get_tasks_storage_path()
        if not os.path.exists(self.tasks_path):
            bundled_tasks = os.path.join(os.path.dirname(__file__), "tasks.json")
            try:
                import shutil
                shutil.copyfile(bundled_tasks, self.tasks_path)
            except Exception:
                pass
        self.list_tasks = load_tasks_from_file(self.tasks_path)
        self.task_items = []
        layout.addWidget(self.title_bar)
        for index, task in enumerate(self.list_tasks):
            item = TaskItem(task, self.task_font_family, self)
            self.task_items.append(item)
            layout.addWidget(item)
            item.animate_in(index * 150)

        # Footer Layout with Close and Editor buttons
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(0)

        self.close_btn = QPushButton("✕ Hide", self)
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.hide)

        self.editor_btn = QPushButton("⚙ Editor", self)
        self.editor_btn.setObjectName("editorButton")
        self.editor_btn.clicked.connect(self.open_task_editor)

        self.footer_layout.addWidget(self.close_btn)
        self.footer_layout.addWidget(self.editor_btn)
        layout.addLayout(self.footer_layout)

        # create editor as a top-level window so it can receive focus normally
        self.editor_window = TaskEditorWindow(self.tasks_path, self.font_family, None)
        self.tray_icon = self.create_tray_icon()

        self.setLayout(layout)
        self.apply_styles()
        QTimer.singleShot(1000, self.run_focus_animation_sequence)

        try:
            import keyboard
            from PySide6.QtCore import QMetaObject, Slot
    
            keyboard.add_hotkey('alt+t', lambda: QMetaObject.invokeMethod(self, "toggle_window_slot"))
            keyboard.add_hotkey('alt+e', lambda: QMetaObject.invokeMethod(self, "open_task_editor_slot"))
        except Exception as e:
            print("ok")

    def ensure_preview_popup(self):
        if self.preview_popup is not None:
            return self.preview_popup

        popup = QFrame(None, Qt.ToolTip | Qt.FramelessWindowHint)
        popup.setObjectName("taskPreviewPopup")
        popup.setAttribute(Qt.WA_ShowWithoutActivating, True)
        popup.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        popup.setFrameShape(QFrame.Shape.StyledPanel)
        popup.setFrameShadow(QFrame.Shadow.Plain)

        layout = QVBoxLayout(popup)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(0)

        title = QLabel("Task description", popup)
        title.setObjectName("taskPreviewTitle")
        body = QLabel("", popup)
        body.setObjectName("taskPreviewBody")
        body.setWordWrap(True)
        body.setMinimumWidth(220)
        body.setMaximumWidth(280)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(title)
        layout.addWidget(body)
        popup.title_label = title
        popup.body_label = body
        popup.hide()
        self.preview_popup = popup
        return popup

    def show_task_preview(self, task_item, description: str):
        popup = self.ensure_preview_popup()
        popup.title_label.setText(task_item.label.text())
        popup.body_label.setText(description or "No description provided.")
        popup.adjustSize()

        offset = QPoint(18, 0)
        global_pos = task_item.mapToGlobal(task_item.rect().topLeft())
        popup_width = popup.sizeHint().width()
        x = global_pos.x() - popup_width - offset.x()
        y = global_pos.y() + offset.y() - 6
        if x < 10:
            x = global_pos.x() + task_item.width() + offset.x()
        popup.move(x, y)
        popup.show()
        popup.raise_()

    def hide_task_preview(self):
        if self.preview_popup is not None:
            self.preview_popup.hide()
    
    @Slot()
    def toggle_window_slot(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_normal()

    @Slot()
    def open_task_editor_slot(self):
        self.open_task_editor()

    def toggle_window(self):
        self.toggle_window_slot()

    def apply_styles(self):
        style = f"""
            QWidget {{
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 10px;
            }}
            #titleLabel {{
                color: white;
                font-family: "{self.font_family}";
                font-size: 16px;
                padding: 8px;
            }}
            #closeButton, #editorButton {{
                background-color: #3a3a3a;
                color: #aaaaaa;
                font-size: 13px;
                border: none;
                border-top: 1px solid #555;
                border-radius: 0px;
                padding: 6px;
            }}
            #closeButton {{
                border-right: 1px solid #555;
                border-bottom-left-radius: 8px;
            }}
            #editorButton {{
                border-bottom-right-radius: 8px;
            }}
            #closeButton:hover {{
                background-color: #ff5555;
                color: white;
            }}
            #editorButton:hover {{
                background-color: #55ff55;
                color: #2b2b2b;
            }}
            #taskLabel {{
                color: white;
                font-family: "{self.task_font_family}", sans-serif;
                font-size: 14px;
                padding: 5px;
                font-weight: bold;
            }}
            #taskPreviewPopup {{
                background-color: #202020;
                border: 1px solid #555;
                border-radius: 8px;
            }}
            #taskPreviewTitle {{
                color: #55ff55;
                font-family: "{self.font_family}";
                font-size: 11px;
                padding-bottom: 4px;
            }}
            #taskPreviewBody {{
                color: #f2f2f2;
                font-family: "{self.task_font_family}", sans-serif;
                font-size: 12px;
            }}
        """
        self.setStyleSheet(style)

    def run_focus_animation_sequence(self):
        # Keep window on top during animations
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint)
        self.show()

        # Cancel any active timers
        if hasattr(self, 'ladder_timer') and self.ladder_timer.isActive():
            self.ladder_timer.stop()
        if hasattr(self, 'shuffle_timer') and self.shuffle_timer.isActive():
            self.shuffle_timer.stop()

        focused_indices = [idx for idx, item in enumerate(self.task_items) if item.focused]

        if len(focused_indices) == 1:
            self.perform_ladder_animation(focused_indices[0])
        else:
            # If multiple tasks are focused or none are, clear all and run shuffle
            for item in self.task_items:
                item.focused = False
                item.set_highlighted(False)
            self.save_current_tasks_state()
            self.perform_shuffle_animation()

    def perform_ladder_animation(self, start_idx: int):
        if start_idx <= 0:
            if len(self.task_items) > 0:
                self.task_items[0].focused = True
                self.task_items[0].set_highlighted(True)
                self.save_current_tasks_state()
            # Clear stay on top flag since animation has finished
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
            self.show()
            return

        self.climbing_idx = start_idx
        self.ladder_timer = QTimer(self)
        self.task_items[self.climbing_idx].set_highlighted(True)

        def step():
            if self.climbing_idx > 0:
                idx = self.climbing_idx
                self.task_items[idx], self.task_items[idx-1] = self.task_items[idx-1], self.task_items[idx]
                widget = self.task_items[idx-1]
                self.layout().removeWidget(widget)
                self.layout().insertWidget(idx, widget)
                self.climbing_idx -= 1
            else:
                self.ladder_timer.stop()
                self.task_items[0].focused = True
                self.task_items[0].set_highlighted(True)
                self.save_current_tasks_state()
                # Clear stay on top flag since animation has finished
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
                self.show()

        self.ladder_timer.timeout.connect(step)
        self.ladder_timer.start(1000)

    def perform_shuffle_animation(self):
        import random
        if not self.task_items:
            return

        target_idx = random.randint(0, len(self.task_items) - 1)
        self.shuffle_steps = 12
        self.shuffle_current_step = 0
        self.shuffle_last_highlighted = -1
        self.shuffle_timer = QTimer(self)

        def step():
            import random
            if self.shuffle_last_highlighted != -1:
                self.task_items[self.shuffle_last_highlighted].set_highlighted(False)

            if self.shuffle_current_step < self.shuffle_steps:
                highlight_idx = random.randint(0, len(self.task_items) - 1)
                self.task_items[highlight_idx].set_highlighted(True)
                self.shuffle_last_highlighted = highlight_idx
                self.shuffle_current_step += 1
            else:
                self.shuffle_timer.stop()
                for item in self.task_items:
                    item.focused = False
                    item.set_highlighted(False)
                
                target_item = self.task_items[target_idx]
                target_item.focused = True
                target_item.set_highlighted(True)
                self.perform_ladder_animation(target_idx)

        self.shuffle_timer.timeout.connect(step)
        self.shuffle_timer.start(350)  # Slower step (350ms) for a more gradual, clear shuffle

    def save_current_tasks_state(self):
        updated_tasks = []
        for item in self.task_items:
            task_dict = dict(item.task_data)
            task_dict["focused"] = item.focused
            updated_tasks.append(task_dict)
        save_tasks_to_file(self.tasks_path, updated_tasks)

    def reload_tasks(self):
        # Cancel any active timers
        if hasattr(self, 'ladder_timer') and self.ladder_timer.isActive():
            self.ladder_timer.stop()
        if hasattr(self, 'shuffle_timer') and self.shuffle_timer.isActive():
            self.shuffle_timer.stop()

        for item in self.task_items:
            item.deleteLater()
        self.task_items.clear()

        from storage import load_tasks_from_file
        self.list_tasks = load_tasks_from_file(self.tasks_path)
        for index, task in enumerate(self.list_tasks):
            item = TaskItem(task, self.task_font_family, self)
            self.task_items.append(item)
            self.layout().insertWidget(index + 1, item)
            item.animate_in(index * 150)

        QTimer.singleShot(1000, self.run_focus_animation_sequence)

    def create_tray_icon(self) -> QSystemTrayIcon:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "taskbootlogo.ico")
        icon = QIcon(icon_path)

        tray = QSystemTrayIcon(icon, self)
        menu = QMenu(self)

        show_action = QAction("Show tasks", self)
        show_action.triggered.connect(self.show_normal)
        edit_action = QAction("Open task editor", self)
        edit_action.triggered.connect(self.open_task_editor)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.clean_exit)

        menu.addAction(show_action)
        menu.addAction(edit_action)
        menu.addSeparator()
        menu.addAction(exit_action)

        tray.setContextMenu(menu)
        tray.activated.connect(self.on_tray_activated)
        tray.show()
        return tray

    def clean_exit(self):
        try:
            import keyboard
            keyboard.unhook_all()
        except Exception:
            pass
        self.editor_window.close()
        self.close()
        QApplication.instance().quit()

    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def open_task_editor(self):
        self.editor_window.load_tasks()
        self.editor_window.show()
        self.editor_window.raise_()
        self.editor_window.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_normal()

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

import json
import os
import sys


def get_tasks_storage_path() -> str:
    app_data = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
    if not app_data:
        app_data = os.path.expanduser("~")

    tasks_dir = os.path.join(app_data, "TasksBoot")
    os.makedirs(tasks_dir, exist_ok=True)
    return os.path.join(tasks_dir, "tasks.json")


def get_startup_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
    return f'"{sys.executable}" "{script_path}"'


def is_startup_enabled() -> bool:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            value, _ = winreg.QueryValueEx(key, "TasksBoot")
            return value == get_startup_command()
    except Exception:
        return False


def set_startup_enabled(enabled: bool) -> None:
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            if enabled:
                winreg.SetValueEx(key, "TasksBoot", 0, winreg.REG_SZ, get_startup_command())
            else:
                try:
                    winreg.DeleteValue(key, "TasksBoot")
                except FileNotFoundError:
                    pass
    except Exception:
        pass


def get_data(path: str) -> str | None:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


def read_data(data: str | None, type: str) -> list[str]:
    if data is None:
        return []
    try:
        tasks_data = json.loads(data)
        if isinstance(tasks_data, dict) and "tasks" in tasks_data:
            tasks = tasks_data["tasks"]
        elif isinstance(tasks_data, list):
            tasks = tasks_data
        else:
            return []
        if type == "task":
            list_of_tasks = []
            for task in tasks:
                if isinstance(task, dict):
                    if "name" in task:
                        list_of_tasks.append(task["name"])
                    elif "task" in task:
                        list_of_tasks.append(task["task"])
                    return list_of_tasks
        elif type == "description":
            list_of_descriptions = []
            for task in tasks:
                if isinstance(task, dict) and "description" in task:
                    list_of_descriptions.append(task["description"])
            return list_of_descriptions
        
    except json.JSONDecodeError:
        return []

    

def load_tasks_from_file(path: str) -> list[dict]:
    """Load the full task list (as dicts) from the tasks file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"tasks": []}

    tasks = []
    if isinstance(data, dict):
        tasks = data.get("tasks", [])
    elif isinstance(data, list):
        tasks = data

    if isinstance(tasks, list):
        for task in tasks:
            if isinstance(task, dict) and "focused" not in task:
                task["focused"] = False
        return tasks
    return []


def save_tasks_to_file(path: str, tasks: list[dict]) -> None:
    """Save the full task list (as dicts) to the tasks file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks}, f, indent=4)

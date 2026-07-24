import json


def get_data(path: str) -> str | None:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


def read_data(data: str | None) -> list[str]:
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

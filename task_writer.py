from model import TaskList
import csv

class TaskWriter:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def write_list(self, task_list: TaskList) -> None:

        with open(self._file_path, "w", encoding="UTF-8", newline="") as f:
            writer = csv.writer(f)

            data = []

            for task in task_list.get_all_tasks():
                data.append(task.get_as_csv())

            writer.writerows(data)
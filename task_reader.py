from model import Task, TaskList
import csv

class TaskReader:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def read_list(self) -> TaskList:

        with open(self._file_path, "r", encoding="UTF-8") as f:
            reader = csv.reader(f)

            tasks = []

            for line in reader:
                tasks.append(Task.create_from_csv(line))

            return TaskList(tasks)
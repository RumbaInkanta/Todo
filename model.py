from datetime import date
import uuid

class Task:
    def __init__(self, title: str, due_date: date, description =''):
        self.title = title
        self.checked = False
        self.due_date = due_date
        self.description = description
        self.id = uuid.uuid4()

    def __repr__(self) -> str:
        output = self.title

        if self.checked:
            output = "[DONE] " + output

        return output
    
    def check(self):
        self.checked = True

    def uncheck(self):
        self.checked = False

    def change_description(self, description: str):
        self.description = description
    
    def change_title(self, title: str):
        self.title = title

    def change_due_date(self, due_date: date):
        self.due_date = due_date


class TaskList:
    def __init__(self, tasks = None):
        if tasks is None:
            self.tasks = []
        else:
            self.tasks = tasks

    def __repr__(self) -> str:
        return '\n'.join(repr(task) for task in self.tasks)

    def _find_index(self, id: uuid) -> int:
        for idx, task in enumerate(self.tasks):
            if (task.id == id):
                return idx

        return -1
    
    def add(self, task):
        self.tasks.append(task)

    def remove(self, id: uuid) -> bool:
        index = self._find_index(id)
        if (index < 0):
            return False
        else:
            self.tasks.pop(index)
            return True

    def get_undone(self):
        undone = filter(lambda x: not x.checked, self.tasks)
        return TaskList(list(undone))

    def get_done(self):
        done = filter(lambda x: x.checked, self.tasks)
        return TaskList(list(done))

    def get_today(self):
        return self.get_on_date(date.today())

    def get_on_date(self, on_date: date):
        tasks = filter(lambda x: x.due_date == on_date, self.tasks)
        return TaskList(list(tasks))
    
    def get_sort_date(self):
        tasks = self.tasks.copy()
        tasks.sort(key = lambda task: task.due_date)
        return TaskList(tasks)
    
    def get_count(self) -> int:
        return len(self.tasks)

    def get_all_tasks(self):
        return self.tasks.copy()
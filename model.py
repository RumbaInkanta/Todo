from datetime import date, timedelta
import uuid, itertools
from utils import *

class Task:
    def __init__(self, title: str, due_date: date, description='', checked=False, created_date=date.today(), project_id=None, id=None):
        self.title = title
        self.checked = checked
        self.due_date = due_date
        self.description = description
        self.id = id if id else uuid.uuid4()
        self._created_date = created_date
        self.project_id = project_id

    def __repr__(self) -> str:
        output = self.title

        if self.checked:
            output = "[DONE] " + output

        return output
    
    @property
    def created_date(self):
        return self._created_date
    
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

    def get_as_csv(self):
        return [ self.title, self.checked, self.due_date, self.description, self.id, self._created_date ]

    @staticmethod
    def create_from_csv(collection):
        task = Task(title=collection[0], due_date=date.fromisoformat(collection[2]), description=collection[3])
        task.checked = str2bool(collection[1])
        task.id = uuid.UUID(collection[4])
        task._created_date = date.fromisoformat(collection[5])
        return task

def merge_task_lists(task_lists: []):
    tasks = []
    
    for lst in task_lists:
        tasks.extend(lst.get_all_tasks())

    return TaskList(tasks)

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

    def add_task(self, title: str, due: date, description: str = "") -> Task:
        task = Task(title, due, description)
        self.add(task)
        return task

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

    def get_today_or_overdue(self):
        tasks = filter(lambda x: x.due_date <= date.today(), self.tasks)
        return TaskList(list(tasks))

    def get_soon(self):
        soon_days = date.today() + timedelta(weeks=2)
        tasks = filter(lambda x: x.due_date > date.today() and x.due_date <= soon_days, self.tasks)
        return TaskList(list(tasks))

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


class Project:
    def __init__(self, project_title: str, task_list: TaskList = None, id: uuid = None):
        self._project_title = project_title
        self.id = id if id else uuid.uuid4()
        
        if task_list is None:
            self._task_list = TaskList()
        else:
            self._task_list = task_list

    @property
    def project_title(self) -> str:
        return self._project_title

    @project_title.setter
    def project_title(self, value: str):
        self._project_title = value

    @property
    def task_list(self) -> TaskList:
        return self._task_list
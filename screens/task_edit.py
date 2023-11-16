from kivy.uix.screenmanager import Screen
from screens.main import TaskListItem, MainScreen
import model as md


class TaskEditScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_task_values(self, task_title, task_description, due_date, created_date):
        self.ids.edit_task_title.text = task_title
        self.ids.edit_task_description.text = task_description
        self.ids.edit_task_due_date.text = str(due_date)
        self.ids.edit_task_created_date.text = str(created_date)
    
    def change_task(self):
        pass
    
    def cancel_click(self):
        self.manager.current = 'main'
import os
import sys
from datetime import date, datetime
from task_writer import TaskWriter
from task_reader import TaskReader
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
from kivy.clock import mainthread
import model as md
import keyboard
import db_connection as db


def path_parse():
    return sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_writer(project: md.Project) -> TaskWriter:
    return TaskWriter(os.path.join(path_parse(), project.project_title + '.csv'))

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        keyboard.add_hotkey('ctrl+enter', self.on_new_task)
        self.project_id = None
        self._selected_project = None

    def fill_data(self):
        self.projects = self._read_all_projects()
        self.ids.datetime_label.text = f"Сегодня: {date.today().strftime('%d.%m.%Y')}"

        for p in self.projects:
            self.ids.projects.add_widget(ProjectListItem(project=p, main_screen=self, is_dynamic=False, text=p.project_title, on_release=lambda x: x.on_click()))

        self.update_dynamic_projects()

    def open_edit(self):
        self.manager.current = 'task_edit'

    def update_dynamic_projects(self):
        today_lists = []
        soon_list = []

        for p in self.projects:
            today_lists.append(p.task_list.get_today_or_overdue().get_undone())
            soon_list.append(p.task_list.get_soon().get_undone())

        today_proj = md.Project(project_title='Сегодня', task_list=md.merge_task_lists(today_lists))
        soon_proj = md.Project(project_title='Скоро', task_list=md.merge_task_lists(soon_list))


        self.ids.dynamic_projects.clear_widgets()

        self.ids.dynamic_projects.add_widget(ProjectListItem(project=today_proj, main_screen=self, is_dynamic=True, text=today_proj.project_title, on_release=lambda x: x.on_click()))
        self.ids.dynamic_projects.add_widget(ProjectListItem(project=soon_proj, main_screen=self, is_dynamic=True, text=soon_proj.project_title, on_release=lambda x: x.on_click()))
    
    @mainthread
    def on_new_task(self):

        str = self.ids.new_task_title.text.splitlines()
        if str:
            txt = str[0]
            
            if len(str) > 1:
                descr = ' '.join(str[1:])
            else:
                descr = ''
            
            db_connection = db.DatabaseConnection()            
            db_connection.insert_task(txt, 0, due_date=date.today(), description=descr, project_id=MainScreen.project_id)
            db_connection.disconnect()

            self._selected_project.project.task_list.add_task(txt, due=date.today(), description=descr)
            self._selected_project.render_tasks()
            self._write_project_to_file(self._selected_project.project)
            self.ids.new_task_title.text = ''
            self.ids.new_task_title.focus = False

            self.update_dynamic_projects()
        else:
            self.ids.new_task_title.text = "Введите название"
    
    def schedule_on_new_task(self, *args):
        Clock.schedule_once(self.on_new_task, 0)

    def on_key_down(self, window, keycode, scancode, codepoint, modifier):
 
        if self.ids.new_task_title.focus and 'ctrl' in modifier and keycode == 40:  # Код клавиши Enter
            self.schedule_on_new_task()

    def on_task_change(self):
        self._selected_project.render_tasks()
        self._write_project_to_file(self._selected_project.project)
        self.update_dynamic_projects()

    def on_task_delete(self, task: md.Task):
        removed = self._selected_project.project.task_list.remove(task.id)

        if not removed:
            print(f'Cannot find task {task.id}')
            return
        
        db_connection = db.DatabaseConnection()
        db_connection.delete_task(task.id)
        db_connection.disconnect()

        self.on_task_change()

    def on_new_project(self):

        project_title=self.ids.new_project_title.text

        db_connection = db.DatabaseConnection()

        if not db_connection.table_exists('projects'):
            db_connection.create_tables()

        project_id = db_connection.get_project_id_by_title(project_title)

        if not project_id:
            project_id = db_connection.insert_project(project_title)

        self.project_id = project_id

        db_connection.disconnect()

        if project_title:
            proj = md.Project(project_title)
            self.projects.append(proj)
            self.ids.projects.add_widget(ProjectListItem(proj, main_screen=self, is_dynamic=False, text=proj.project_title, on_release=lambda x: x.on_click()))
            self.ids.new_project_title.text = ''
            self.ids.tasks.clear_widgets()
        else:
            self.ids.new_project_title.hint_text = "Введите название"

    def _write_project_to_file(self, project: md.Project) -> None:
        writer = create_writer(project)
        writer.write_list(project.task_list)

    def _read_all_projects(self) -> []:
        db_connection = db.DatabaseConnection()

        if not db_connection.table_exists("projects"):
            db_connection.disconnect()
            return []

        db_connection.execute_query("SELECT * FROM projects")
        projects_data = db_connection.fetch_all()

        projects = []
        for project_data in projects_data:
            project_id, project_title = project_data

            db_connection.execute_query("SELECT * FROM tasks WHERE project_id = ?", (project_id,))
            tasks_data = db_connection.fetch_all()

            tasks = []
            for task_data in tasks_data:
                task_id, title, checked, due_date, description, created_date, _ = task_data
                task = md.Task(id=task_id, title=title, checked=bool(checked), due_date=date.fromisoformat(due_date),
                            description=description, created_date=datetime.strptime(created_date, "%Y-%m-%d %H:%M:%S.%f").date())
                tasks.append(task)

            project = md.Project(project_title, task_list=md.TaskList(tasks))
            projects.append(project)

        db_connection.disconnect()
        return projects


class ProjectListItem(OneLineListItem):
    def __init__(self, project: md.Project, main_screen: MainScreen, is_dynamic: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        self._task_list_container = main_screen.ids.tasks
        self._main_screen = main_screen
        self._is_dynamic = is_dynamic

    def on_click(self):
        self._set_current_project()
        self.render_tasks()
        self._main_screen.ids.new_task_title.disabled = self._is_dynamic
        self._main_screen.ids.new_task_button.disabled = self._is_dynamic

    def _set_current_project(self):
        self._main_screen._selected_project = self
        db_connection = db.DatabaseConnection()
        MainScreen.project_id = db_connection.get_project_id_by_title(self._main_screen._selected_project.project.project_title)
        db_connection.disconnect()

    def _task_change_callback(self):
        writer = create_writer(self.project)
        writer.write_list(self.project.task_list)
        self._main_screen.update_dynamic_projects()

    def render_tasks(self):
        self._task_list_container.clear_widgets()

        change_callback = None

        if not self._is_dynamic:
            change_callback = self._task_change_callback
              
        all_tasks = self.project.task_list.get_all_tasks()

        sorted_tasks = sorted(all_tasks, key=lambda x: (x.checked, x.due_date))

        for t in sorted_tasks:
            self._task_list_container.add_widget(TaskListItem(task=t, main_screen=self._main_screen, is_dynamic=self._is_dynamic, on_change=change_callback))

class TaskListItem(BoxLayout):

    def __init__(self, task: md.Task, main_screen: MainScreen, is_dynamic: bool, on_change=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = task
        self._main_screen = main_screen
        
        if not is_dynamic:
            self.add_widget(TaskCheckbox(task=task, on_change=on_change, disabled=is_dynamic, width='48dp', size_hint=(.15,1)))

        self.add_widget(TwoLineListItem(text=task.title, secondary_text=task.description, on_press=self.switch_to_edit))
        
        self.add_widget(MDLabel(text=str(task.due_date), size_hint=(.30,1)))

        if not is_dynamic:
            self.add_widget(MDIconButton(icon='pencil', on_press=self.switch_to_edit))

    def switch_to_edit(self, instance):
        task_edit_screen = self._main_screen.manager.get_screen('task_edit')
        task_edit_screen.set_task(self._task)
        self._main_screen.manager.current = 'task_edit'
    

class TaskCheckbox(IRightBodyTouch, MDCheckbox):

    _on_change = None
    
    def __init__(self, task: md.Task, on_change=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = task
        self.active = task.checked
        self._on_change = on_change

    def on_active(self, *args) -> None:
        super().on_active(*args)
        self._task.checked = self.active

        if self._on_change:
            self._on_change()
            db_connection = db.DatabaseConnection()
            db_connection.update_task_checked(self.active, self._task.id)
            db_connection.disconnect()


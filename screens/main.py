import os
import sys
from datetime import date, datetime
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
from kivy.clock import mainthread
import model as md
import keyboard
import db_connection as db


def path_parse():
    return sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        keyboard.add_hotkey('ctrl+enter', self.on_new_task)
        self._selected_project = None

        db.DatabaseConnection().ensure_schema_created()

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
            
            task = self._selected_project.project.task_list.add_task(txt, due=date.today(), description=descr)

            db_connection = db.DatabaseConnection()            
            db_connection.insert_task(project=self._selected_project.project, task=task)

            self._selected_project.render_tasks()
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
        self.update_dynamic_projects()

    def on_task_delete(self, task: md.Task):
        removed = self._selected_project.project.task_list.remove(task.id)

        if not removed:
            print(f'Cannot find task {task.id}')
            return
        
        db_connection = db.DatabaseConnection()
        db_connection.delete_task(task.id)

        self.on_task_change()

    def on_new_project(self):

        project_title=self.ids.new_project_title.text

        if project_title:
            
            proj = md.Project(project_title=project_title)

            db_connection = db.DatabaseConnection()
            db_connection.insert_project(proj)

            self.projects.append(proj)
            item = ProjectListItem(proj, main_screen=self, is_dynamic=False, text=proj.project_title, on_release=lambda x: x.on_click())
            self.ids.projects.add_widget(item)
            self.ids.new_project_title.text = ''
            item.on_click()
        else:
            self.ids.new_project_title.hint_text = "Введите название"

    def _read_all_projects(self) -> []:
        db_connection = db.DatabaseConnection()
        projects = db_connection.get_all_projects()
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

    def _task_change_callback(self):
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
import os
import sys
from datetime import date
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

def path_parse():
    return sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_writer(project: md.Project) -> TaskWriter:
    return TaskWriter(os.path.join(path_parse(), project.project_title + '.csv'))

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        keyboard.add_hotkey('ctrl+enter', self.on_new_task)

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

        for p in self.projects:
            today_lists.append(p.task_list.get_today().get_undone())

        today_proj = md.Project(project_title='Сегодня', task_list=md.merge_task_lists(today_lists))

        self.ids.dynamic_projects.clear_widgets()

        self.ids.dynamic_projects.add_widget(ProjectListItem(project=today_proj, main_screen=self, is_dynamic=True, text=today_proj.project_title, on_release=lambda x: x.on_click()))
    
    @mainthread
    def on_new_task(self):

        str = self.ids.new_task_title.text.splitlines()
        if str:
            txt = str[0]
            
            if len(str) > 1:
                descr = ' '.join(str[1:])
            else:
                descr = ''
            
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
        # Проверка, что TextInput активен
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

        self.on_task_change()

    def on_new_project(self):

        project_title=self.ids.new_project_title.text
        
        if project_title:
            proj = md.Project(project_title)
            self.projects.append(proj)
            self.ids.projects.add_widget(ProjectListItem(proj, main_screen=self, is_dynamic=False, text=proj.project_title, on_release=lambda x: x.on_click()))
            self.ids.new_project_title.text = ''
        else:
            self.ids.new_project_title.hint_text = "Введите название"
            

    def _write_project_to_file(self, project: md.Project) -> None:
        writer = create_writer(project)
        writer.write_list(project.task_list)

    def _read_all_projects(self) -> []:
        
        csv_files = [f for f in os.listdir(path_parse()) if f.endswith('.csv')]

        projects = []

        for csv in csv_files:
            project_title, _ = os.path.splitext(csv)
            reader = TaskReader(os.path.join(path_parse(), csv))
            task_list = reader.read_list()
            project = md.Project(project_title, task_list=task_list)
            projects.append(project)

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
        writer = create_writer(self.project)
        writer.write_list(self.project.task_list)
        self._main_screen.update_dynamic_projects()

    def render_tasks(self):
        self._task_list_container.clear_widgets()

        change_callback = None

        if not self._is_dynamic:
            change_callback = self._task_change_callback
        
        for t in self.project.task_list.get_all_tasks():
            self._task_list_container.add_widget(TaskListItem(task=t, main_screen=self._main_screen, is_dynamic=self._is_dynamic, on_change=change_callback))

class TaskListItem(BoxLayout):

    def __init__(self, task: md.Task, main_screen: MainScreen, is_dynamic: bool, on_change=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = task
        self._main_screen = main_screen
        
        if not is_dynamic:
            self.add_widget(TaskCheckbox(task=task, on_change=on_change, disabled=is_dynamic, width='48dp', size_hint=(.15,1)))

        self.add_widget(TwoLineListItem(text=task.title, secondary_text=task.description))
        self.add_widget(MDLabel(text=task.due_date.strftime('%d.%m.%Y'), size_hint=(.30,1)))

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


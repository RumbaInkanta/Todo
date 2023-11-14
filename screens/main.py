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
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
import model as md

def path_parse():
    return sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_writer(project: md.Project) -> TaskWriter:
    return TaskWriter(os.path.join(path_parse(), project.project_title + '.csv'))

class MainScreen(Screen):

    def fill_data(self):
        self.projects = self._read_all_projects()
        self.ids.datetime_label.text = f"Сегодня: {date.today().strftime('%d-%m-%Y')}"

        for p in self.projects:
            self.ids.projects.add_widget(ProjectListItem(project=p, main_screen=self, text=p.project_title, on_release=lambda x: x.on_click()))

    def open_edit(self):
        self.manager.current = 'task_edit'

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
        else:
            self.ids.new_task_title.text = "Введите название"
    
    def on_new_project(self):

        project_title=self.ids.new_project_title.text
        
        if project_title:
            proj = md.Project(project_title)
            self.projects.append(proj)
            self.ids.projects.add_widget(ProjectListItem(proj, main_screen=self, text=proj.project_title, on_release=lambda x: x.on_click()))
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
    def __init__(self, project: md.Project, main_screen: MainScreen, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        self._task_list_container = main_screen.ids.tasks
        self._main_screen = main_screen

    def on_click(self):
        self._set_current_project()
        self.render_tasks()
        self._main_screen.ids.new_task_title.disabled = False
        self._main_screen.ids.new_task_button.disabled = False

    def _set_current_project(self):
        self._main_screen._selected_project = self

    def render_tasks(self):
        self._task_list_container.clear_widgets()

        writer = create_writer(self.project)
        
        for t in self.project.task_list.get_all_tasks():
            self._task_list_container.add_widget(TaskListItem(task=t, main_screen=self._main_screen, on_change=lambda: writer.write_list(self.project.task_list)))

class TaskListItem(BoxLayout):

    def __init__(self, task: md.Task, main_screen: MainScreen, on_change=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = task
        self._main_screen = main_screen
        
        self.add_widget(TaskCheckbox(task=task, on_change=on_change, width='48dp', size_hint=(.15,1)))
        self.add_widget(TwoLineListItem(text=task.title, secondary_text=task.description))
        self.add_widget(MDIconButton(icon='pencil', on_press=self.switch_to_edit))

    def switch_to_edit(self, instance):
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


import os
import sys
from datetime import date
from model import Task, TaskList, Project
from task_writer import TaskWriter
from task_reader import TaskReader
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox


class TodoApp(MDApp):

    def on_start(self):
        
        self.projects = self._read_all_projects()

        for p in self.projects:
            self.root.ids.projects.add_widget(ProjectListItem(project=p, app=self, text=p.project_title, on_release=lambda x: x.on_click()))

    def path_parse(self):
        return sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

    def _read_all_projects(self) -> []:
        
        csv_files = [f for f in os.listdir(self.path_parse()) if f.endswith('.csv')]

        projects = []

        for csv in csv_files:
            project_title, _ = os.path.splitext(csv)
            reader = TaskReader(os.path.join(self.path_parse(), csv))
            task_list = reader.read_list()
            project = Project(project_title, task_list=task_list)
            projects.append(project)

        return projects
        

    def on_new_task(self):

        str = self.root.ids.new_task_title.text.splitlines()
        txt = str[0]
        
        if len(str) > 1:
            descr = " ".join(str[1:])
        else:
            descr = ""
        
        self._selected_project.project.task_list.add_task(txt, due=date.today(), description=descr)
        self._selected_project.render_tasks()
        self._write_project_to_file(self._selected_project.project)
        self.root.ids.new_task_title.text = ''
    
    def on_new_project(self):

        project_title=self.root.ids.new_project_title.text
        
        if project_title:
            proj = Project(project_title)
            self.projects.append(proj)
            self.root.ids.projects.add_widget(ProjectListItem(proj, app=self, text=proj.project_title, on_release=lambda x: x.on_click()))
            self.root.ids.new_project_title.text = ''
        else:
            self.root.ids.new_project_title.hint_text = 'Введите название'
            

    def _write_project_to_file(self, project: Project) -> None:
        writer = TaskWriter(os.path.join(self.path_parse(), project.project_title + ".csv"))
        writer.write_list(project.task_list)


class ProjectListItem(OneLineListItem):
    def __init__(self, project: Project, app: TodoApp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        self._task_list_container = app.root.ids.tasks
        self._app = app

    def on_click(self):
        self._set_current_project()
        self.render_tasks()
        self._app.root.ids.new_task_title.disabled = False
        self._app.root.ids.new_task_button.disabled = False

    def _set_current_project(self):
        self._app._selected_project = self

    def render_tasks(self):
        self._task_list_container.clear_widgets()
        
        for t in self.project.task_list.get_all_tasks():
            self._task_list_container.add_widget(TwoLineListItem(text=t.title, secondary_text=t.description))


if __name__ == '__main__':
        
    TodoApp().run()
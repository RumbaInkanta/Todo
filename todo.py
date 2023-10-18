from datetime import date
from model import Task, TaskList, Project
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.scrollview import ScrollView

class TodoApp(MDApp):

    def on_start(self):

        projects = []

        projects.append(Project(project_title="Project 1"))
        projects.append(Project(project_title="Project 2"))
        projects.append(Project(project_title="Project 3"))

        projects_dic = {p.project_title: p for p in projects}

        projects_dic["Project 1"].task_list.add_task("Task 1", date.today())
        projects_dic["Project 1"].task_list.add_task("Task 2", date.today())
        projects_dic["Project 2"].task_list.add_task("Task 3", date.today())
        projects_dic["Project 3"].task_list.add_task("Task 4", date.today())

        for p in projects:
            self.root.ids.projects.add_widget(OneLineListItem(text=p.project_title, on_release=lambda x: print(f"Вы выбрали проект '{x.text}' (Количество задач: {projects_dic[x.text].task_list.get_count()})")))

if __name__ == '__main__':
    TodoApp().run()

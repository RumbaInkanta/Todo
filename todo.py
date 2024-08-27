import os
import sys
from datetime import date
from model import Task, TaskList, Project
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from screens.main import MainScreen
from screens.task_edit import TaskEditScreen
from screens.calendar import CalendarScreen
from screens.auth import AuthScreen



class TodoApp(MDApp):

    def build(self):
        kv_file_path = resource_path("todo.kv")
        Builder.load_file(kv_file_path)
        return super().build()

    def on_start(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Orange'
        self.title = "Список задач"
        self.root.current = 'auth'

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
        
    TodoApp().run()
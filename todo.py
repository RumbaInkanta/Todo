import os
import sys
from datetime import date
from model import Task, TaskList, Project
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
from screens.main import MainScreen
from screens.task_edit import TaskEditScreen


class TodoApp(MDApp):

    kv_loaded = False

    def on_start(self):
        if not self.kv_loaded:
            Builder.load_file('todo.kv')
            self.kv_loaded = True

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightGreen"

        self.root.get_screen("main").fill_data()






if __name__ == '__main__':
        
    TodoApp().run()
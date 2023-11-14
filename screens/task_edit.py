from kivy.uix.screenmanager import Screen


class TaskEditScreen(Screen):
    def cancel_click(self):
        self.manager.current = 'main'
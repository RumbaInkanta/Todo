from kivy.uix.screenmanager import Screen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton
from screens.main import TaskListItem, MainScreen
import model as md


class TaskEditScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmation_dialog = None 

    def set_task_values(self, task_title, task_description, due_date):
        self.ids.edit_task_title.text = task_title
        self.ids.edit_task_description.text = task_description
        self.ids.edit_task_due_date.text = str(due_date)
    
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.ids.edit_task_due_date.text = str(value)

    def show_confirmation_dialog(self):
        self.confirmation_dialog = MDDialog(
            text="Вы уверены, что хотите удалить задачу?",
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda *args: self.confirmation_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Подтвердить",
                    on_release=lambda *args: self.confirmation_callback()
                ),
            ],
        )
        self.confirmation_dialog.open()

    def confirmation_callback(self):
        print("Пиши логику е-мае")
        self.manager.current = 'main'
        self.confirmation_dialog.dismiss()

    def change_task(self):
        pass
    
    def cancel_click(self):
        self.manager.current = 'main'
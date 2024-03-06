from kivy.uix.screenmanager import Screen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.selectioncontrol import MDCheckbox
from screens.main import TaskListItem, MainScreen
import model as md
import db_connection as db
from datetime import date


class TaskEditScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmation_dialog = None

    def set_task(self, task: md.Task):
        self._task = task
        self.ids.edit_task_title.text = task.title
        self.ids.edit_task_description.text = task.description
        self.ids.edit_task_due_date.text = str(task.due_date)
        checkbox_mapping = {
            0: 'chb_single',
            1: 'chb_week',
            2: 'chb_month',
            3: 'chb_quarter',
        }
        selected_checkbox_id = checkbox_mapping.get(task.period, 'chb_single')
        self.ids[selected_checkbox_id].active = True
        self.ids.chb_checked.active = task.checked

    
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
        self.get_main_screen().on_task_delete(self._task)
        self.switch_to_main()
        self.confirmation_dialog.dismiss()

    def update_period(self, checkbox, checkbox_id):
        period_mapping = {'chb_single': 0, 'chb_week': 1, 'chb_month': 2, 'chb_quarter': 3}
        self._task.period = period_mapping.get(checkbox_id, 0)

    def on_task_active(self):
        self._task.checked = self.ids.chb_checked.active

    def change_task(self):
        self._task.title = self.ids.edit_task_title.text
        self._task.description = self.ids.edit_task_description.text
        self._task.due_date = date.fromisoformat(self.ids.edit_task_due_date.text)
        self.get_main_screen().db_connection.update_task(self._task.id, self._task.title, self._task.checked, self._task.due_date, self._task.description, self._task.period, self.get_main_screen()._selected_project.project.id)
        
        self.get_main_screen().set_period_task(self.get_main_screen()._selected_project, self._task)
        self.get_main_screen().on_task_change()
        self.switch_to_main()
    
    def cancel_click(self):
        self.switch_to_main()

    def get_main_screen(self):
        main_screen = self.manager.get_screen('main')
        return main_screen

    def switch_to_main(self):
        self.manager.current = 'main'
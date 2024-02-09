from kivy.uix.screenmanager import ScreenManager, Screen
import db_connection as db

class AuthScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def auth(self):
        pw = self.ids.auth_text_field.text
        db_connection = db.DatabaseConnection()
        
        if pw == '000':
            self.manager.current = 'main'
        else:
            self.ids.true_label.text = 'Введен неверный пароль, попробуйте снова:'
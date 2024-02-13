from kivy.uix.screenmanager import ScreenManager, Screen
import db_connection as db

class AuthScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def auth(self):
        pw = self.ids.auth_text_field.text
        db_connection = db.DatabaseConnection(password=pw)
        main_screen = self.manager.get_screen('main')
        main_screen.set_dbconnection(db_connection)
        main_screen.fill_data()
        self.manager.current = 'main'

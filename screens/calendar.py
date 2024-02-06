from kivy.uix.screenmanager import Screen
from screens.main import MainScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.tab import MDTabsBase
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import calendar

class CalendarScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def switch_to_main(self):
        self.manager.current = 'main'
    
    def on_start_calendar(self):
        for month_num in range(1, 13):
            month_name = calendar.month_name[month_num]
            self.ids.tabs.add_widget(Tab(title=month_name))
    
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        instance_tab.on_enter()


class Tab(MDFloatLayout, MDTabsBase):
    def on_enter(self, *args):
        calendar_layout = self.ids.calendar_layout
        calendar_layout.clear_widgets()

        # Добавление дней недели в первый ряд
        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for day in days_of_week:
            calendar_layout.add_widget(Label(text=day))

        # Добавление чисел в календарь
        for i in range(1, 32):
            btn = Button(text=str(i), size_hint_y=None, height=40)
            btn_label = Label(text='Label')

            # Создание BoxLayout для размещения числа и label внутри кнопки
            btn_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=60)
            btn_layout.add_widget(btn_label)
            btn_layout.add_widget(btn)

            calendar_layout.add_widget(btn_layout)
import unittest
from datetime import date, timedelta
from model import Task

class TaskTests(unittest.TestCase):
    def test_change_description_element_contains(self):
        today = date.today()
        task = Task("Test task1", today, "Test task1 description")

        task.change_description("test task1 changed description")

        self.assertEqual(task.description, "test task1 changed description")
    
    def test_change_title_element_contains(self):
        today = date.today()
        task = Task("Test task1", today, "Test task1 description")

        task.change_title("Test task1 changed title")

        self.assertEqual(task.title, "Test task1 changed title")
    
    def test_change_date_element_contains(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        task = Task("Test task1", today, "Test task1 description")

        task.change_due_date(tomorrow)

        self.assertEqual(task.due_date, tomorrow)
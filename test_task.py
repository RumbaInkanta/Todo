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

    def test_task_serialize(self):
        today = date.today()
        task = Task(title="Test task", due_date=today, description="Yoba task")
        collection = task.get_as_csv()

        self.assertEqual(len(collection), 6)

        self.assertEqual(collection[0], task.title)
        self.assertEqual(collection[1], task.checked)
        self.assertEqual(collection[2], task.due_date)
        self.assertEqual(collection[3], task.description)
        self.assertEqual(collection[4], task.id)
        self.assertEqual(collection[5], task.created_date)

        collection_str = list(map(lambda x: str(x), collection))

        new_task = Task.create_from_csv(collection_str)
        collection2 = new_task.get_as_csv()

        self.assertListEqual(collection, collection2)
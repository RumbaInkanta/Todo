from datetime import date, timedelta
import unittest
import os
from model import Task, TaskList
from task_writer import TaskWriter
from task_reader import TaskReader

class StorageTests(unittest.TestCase):
    def test_write_read_to_csv(self):
        file_path = "data.csv"

        if os.path.exists(file_path):
            os.remove(file_path)

        today = date.today()
        tomorrow = today + timedelta(days=1)
        task1 = Task(title="Test task 1", due_date=today, description="Desc 1")
        task2 = Task(title="Test task 2", due_date=tomorrow, description="Desc 2")

        task_list = TaskList([task1, task2])

        task_writer = TaskWriter(file_path)
        task_writer.write_list(task_list)

        task_reader = TaskReader(file_path)
        new_task_list = task_reader.read_list()

        self.assertEqual(2, new_task_list.get_count())

        new_tasks = new_task_list.get_all_tasks()

        self.assertListEqual(task1.get_as_csv(), new_tasks[0].get_as_csv())
        self.assertListEqual(task2.get_as_csv(), new_tasks[1].get_as_csv())
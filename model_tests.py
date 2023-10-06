import unittest
from datetime import date, timedelta
from model import Task, TaskList

class TaskListTests(unittest.TestCase):
    def test_create_tasklist_add_element_contains_elements(self):
        today = date.today()
        task = Task("Test task", today)
        task_list = TaskList()
        task_list.add(task)
        self.assertEqual(task_list.get_count(), 1)

    def test_three_todays_tasks_returned_correctly(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        task_list = TaskList()

        task_list.add(Task("Yesterday task 1", yesterday))
        task_list.add(Task("Yesterday task 2", yesterday))

        task_list.add(Task("Today task 1", today))
        task_list.add(Task("Today task 2", today))
        task_list.add(Task("Today task 3", today))

        task_list.add(Task("Tomorrow task 1", tomorrow))
        task_list.add(Task("Tomorrow task 2", tomorrow))

        todays_list = task_list.get_today()
        self.assertEqual(todays_list.get_count(), 3)

        for task in todays_list.get_all_tasks():
            self.assertRegex(task.title, "Today task \\d")

    def test_two_done_two_undone_returns_done_tasks(self):
        task_list = TaskList()

        done1 = Task("Task 1", date.today())
        done2 = Task("Task 2", date.today())

        done1.check()
        done2.check()

        undone1 = Task("Task 3", date.today())
        undone2 = Task("Task 4", date.today())

        task_list.add(done1)
        task_list.add(done2)
        task_list.add(undone1)
        task_list.add(undone2)

        done_list = task_list.get_done()

        self.assertEqual(done_list.get_count(), 2)

        done_tasks = done_list.get_all_tasks()

        self.assertEqual(done_tasks[0].title, "Task 1")
        self.assertEqual(done_tasks[1].title, "Task 2")

    def test_three_tasks_remove_one_two_remain(self):
        today = date.today()
        task1 = Task("Task 1", today)
        task2 = Task("Task 2", today)
        task3 = Task("Task 3", today)

        task_list = TaskList([task1, task2, task3])

        self.assertEqual(task_list.get_count(), 3)

        task_list.remove(task2.id)

        self.assertEqual(task_list.get_count(), 2)

        tasks = task_list.get_all_tasks()

        self.assertEqual(tasks[0].title, "Task 1")
        self.assertEqual(tasks[1].title, "Task 3")

    def test_remove_multiple_times(self):
        today = date.today()
        task1 = Task("Task 1", today)
        task2 = Task("Task 2", today)
        task3 = Task("Task 3", today)

        task_list = TaskList([task1, task2, task3])

        self.assertTrue(task_list.remove(task2.id))
        self.assertFalse(task_list.remove(task2.id))

        self.assertEqual(task_list.get_count(), 2)


if __name__ == "__main__":
    unittest.main()
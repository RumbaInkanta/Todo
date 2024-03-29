import unittest
from datetime import date, timedelta
from model import Task, TaskList, merge_task_lists

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
    
    def test_sorting_tasks(self):
        task_list = self._create_test_list()

        tasks = task_list.get_sort_date().get_all_tasks()

        self.assertEqual(tasks[0].title, "Task 2")
        self.assertEqual(tasks[1].title, "Task 5")
        self.assertEqual(tasks[2].title, "Task 1")
        self.assertEqual(tasks[3].title, "Task 6")
        self.assertEqual(tasks[4].title, "Task 3")
        self.assertEqual(tasks[5].title, "Task 4")

    def test_merge_tasks(self):
        list_1 = self._create_test_list()
        list_2 = self._create_test_list()
        list_3 = self._create_test_list()

        merged_list = merge_task_lists([list_1, list_2, list_3])

        self.assertEqual(merged_list.get_count(), 18)

    def _create_test_list(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        task1 = Task("Task 1", today)
        task2 = Task("Task 2", yesterday)
        task3 = Task("Task 3", tomorrow)
        task4 = Task("Task 4", tomorrow)
        task5 = Task("Task 5", yesterday)
        task6 = Task("Task 6", today)

        return TaskList([task1, task2, task3, task4, task5, task6])

if __name__ == "__main__":
    unittest.main()
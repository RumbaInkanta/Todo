from datetime import date
from model import Task, TaskList

if __name__ == "__main__":
    taskList = TaskList()

    today = date.fromisoformat("2023-10-04")
    tomorrow = date.fromisoformat("2023-10-05")

    taskList.add(Task("Test task 1", tomorrow))
    taskList.add(Task("Test task 2", tomorrow))

    thirdTask = Task("Test task 3", tomorrow)
    thirdTask.check()

    taskList.add(thirdTask)
    taskList.add(Task("Test task 4", today))

    print("Today tasks:\n")
    print(taskList.get_today())

    print("\n")

    print("Tomorrow tasks:\n")
    print(taskList.get_on_date(tomorrow))
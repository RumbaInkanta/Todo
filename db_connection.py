import sqlite3
import uuid
from datetime import date, datetime
import model as md

class DatabaseConnection:
    def __init__(self, db_name='tasks.db'):
        self.db_name = db_name

    def execute_non_query(self, query, parameters = None):
        self._execute_query(query=query, reader_func=None, commit=True, parameters=parameters)

    def execute_scalar(self, query, parameters = None):
        return self._execute_query(query=query, reader_func=lambda cur: cur.fetchone(), commit=False, parameters=parameters)

    def execute_table_query(self, query, parameters = None):
        return self._execute_query(query=query, reader_func=lambda cur: cur.fetchall(), commit=False, parameters=parameters)

    def _execute_query(self, query, reader_func, commit: bool, parameters):
        with sqlite3.connect(self.db_name) as connection:
            
            cursor = connection.cursor()

            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            result = None

            if reader_func:
                result = reader_func(cursor)

            if commit:
                connection.commit()

            return result

    def ensure_schema_created(self):
        if not self.table_exists('projects'):
            self.create_tables()

    def get_all_projects(self):
        query = "SELECT * FROM projects"
        projects_data = self.execute_table_query(query)

        projects = []
        for project_data in projects_data:
            project_id, project_title = project_data

            tasks_data = self.execute_table_query("SELECT * FROM tasks WHERE project_id = ?", (project_id,))

            tasks = []
            for task_data in tasks_data:
                task_id, title, checked, due_date, description, created_date, _ = task_data
                task = md.Task(id=task_id, title=title, checked=bool(checked), due_date=date.fromisoformat(due_date),
                            description=description, created_date=datetime.strptime(created_date, "%Y-%m-%d").date())
                tasks.append(task)

            project = md.Project(id=project_id, project_title=project_title, task_list=md.TaskList(tasks))
            projects.append(project)

        return projects

    def table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        return bool(self.execute_scalar(query, (table_name,)))

    def create_tables(self):
        projects_table_query = '''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                project_title TEXT,
                CONSTRAINT id_unique UNIQUE (id)
            )
        '''
        tasks_table_query = '''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT,
                checked INTEGER,
                due_date TEXT,
                description TEXT,
                created_date TEXT,
                project_id TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                CONSTRAINT id_unique UNIQUE (id)
            )
        '''
        self.execute_non_query(projects_table_query)
        self.execute_non_query(tasks_table_query)

    def insert_project(self, project: md.Project):
        query = "INSERT INTO projects (id, project_title) VALUES (?, ?)"
        self.execute_non_query(query, (str(project.id), project.project_title))

    def insert_task(self, project: md.Project, task: md.Task):
        task_id = str(task.id)
        created_date = str(task.created_date)
        project_id = str(project.id)
        query = "INSERT INTO tasks (id, title, checked, due_date, description, created_date, project_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.execute_non_query(query, (task_id, task.title, task.checked, task.due_date, task.description, created_date, project_id))
    
    def update_project(self, project_id, new_project_title):
        query = "UPDATE projects SET project_title = ? WHERE id = ?"
        self.execute_non_query(query, (new_project_title, project_id))

    def update_task(self, task_id, title, checked, due_date, description, project_id):
        query = "UPDATE tasks SET title = ?, checked = ?, due_date = ?, description = ?, project_id = ? WHERE id = ?"
        self.execute_non_query(query, (title, checked, due_date, description, project_id, task_id))

    def update_task_checked(self, checked, task_id):
        query = "UPDATE tasks SET checked = ? WHERE id = ?"
        self.execute_non_query(query, (checked, str(task_id)))
    
    def delete_task(self, task_id):
        query = "DELETE FROM tasks WHERE id = ?"
        self.execute_non_query(query, (task_id,))
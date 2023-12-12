import sqlite3
import uuid
from datetime import datetime

class DatabaseConnection:
    def __init__(self, db_name='tasks.db'):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, parameters=None):
        if not self.connection:
            self.connect()

        if parameters:
            self.cursor.execute(query, parameters)
        else:
            self.cursor.execute(query)

    def commit(self):
        if self.connection:
            self.connection.commit()

    def fetch_all(self):
        if self.cursor:
            return self.cursor.fetchall()

    def fetch_one(self):
        if self.cursor:
            return self.cursor.fetchone()

    def table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        self.execute_query(query, (table_name,))
        return bool(self.fetch_one())

    def create_tables(self):
        projects_table_query = '''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                project_title TEXT
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
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        '''
        self.execute_query(projects_table_query)
        self.execute_query(tasks_table_query)
        self.commit()

    def insert_project(self, project_title):
        project_id = str(uuid.uuid4())
        query = "INSERT INTO projects (id, project_title) VALUES (?, ?)"
        self.execute_query(query, (project_id, project_title))
        self.commit()
        return project_id

    def insert_task(self, title, checked, due_date, description, project_id):
        task_id = str(uuid.uuid4())
        created_date = str(datetime.now())
        query = "INSERT INTO tasks (id, title, checked, due_date, description, created_date, project_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (task_id, title, checked, due_date, description, created_date, project_id))
        self.commit()
        return task_id
    
    def get_project_id_by_title(self, project_title):
        query = "SELECT id FROM projects WHERE project_title = ?"
        self.execute_query(query, (project_title,))
        result = self.fetch_one()
        return result[0] if result else None
    
    def update_project(self, project_id, new_project_title):
        query = "UPDATE projects SET project_title = ? WHERE id = ?"
        self.execute_query(query, (new_project_title, project_id))
        self.commit()

    def update_task(self, task_id, title, checked, due_date, description, project_id):

        query_task_exists = "SELECT 1 FROM tasks WHERE id = ?"
        self.execute_query(query_task_exists, (task_id,))
        task_exists = bool(self.fetch_one())

        if not task_exists:
            print("Задача с ID {} не существует.".format(task_id))
            return

        query_project_exists = "SELECT 1 FROM projects WHERE id = ?"
        self.execute_query(query_project_exists, (project_id,))
        project_exists = bool(self.fetch_one())

        if not project_exists:
            print("Проект с ID {} не существует.".format(project_id))
            return
        query = "UPDATE tasks SET title = ?, checked = ?, due_date = ?, description = ?, project_id = ? WHERE id = ?"
        self.execute_query(query, (title, checked, due_date, description, project_id, task_id))
        self.commit()

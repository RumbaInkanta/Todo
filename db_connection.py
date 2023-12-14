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
        query = """
            SELECT p.id AS project_id, p.project_title, t.id AS task_id, t.title, t.checked, t.due_date, 
                t.description, t.created_date
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
        """
        data = self.execute_table_query(query)

        projects_dict = {}
        for row in data:
            project_id, project_title, task_id, title, checked, due_date, description, created_date = row

            if project_id not in projects_dict:
                projects_dict[project_id] = {'project_title': project_title, 'tasks': []}

            if task_id is not None:
                task = md.Task(id=task_id, title=title, checked=bool(checked), due_date=date.fromisoformat(due_date),
                            description=description, created_date=datetime.strptime(created_date, "%Y-%m-%d").date())
                projects_dict[project_id]['tasks'].append(task)

        projects = [md.Project(id=proj_id, project_title=proj_data['project_title'], 
                            task_list=md.TaskList(proj_data['tasks']))
                    for proj_id, proj_data in projects_dict.items()]

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
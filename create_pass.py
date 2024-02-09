import sqlite3

def create_database():
    connection = sqlite3.connect('tasks.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password TEXT
        )
    ''')
    cursor.execute("INSERT INTO pass (password) VALUES (?)", ('000',))

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_database()

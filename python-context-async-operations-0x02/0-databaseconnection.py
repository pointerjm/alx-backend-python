import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

def main():
    # Assuming a database with a 'users' table exists
    with DatabaseConnection('users.db') as cursor:
        cursor.execute('SELECT * FROM users')
        results = cursor.fetchall()
        for row in results:
            print(row)

if __name__ == "__main__":
    main()
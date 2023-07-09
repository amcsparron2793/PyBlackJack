import os
import sqlite3
from os.path import isfile

db_full_path = '../MiscProjectFiles/PyBlackJack.db'


def InitializeNewDB(script_path='../MiscProjectFiles/InitializeNewDB.sql'):
    def _ReadAndCreateDB():
        conn = sqlite3.connect(db_full_path)
        print(f"database {db_full_path} created.")
        cursor = conn.cursor()

        with open(script_path) as sql_file:
            sql_script = sql_file.read()

        cursor.executescript(sql_script)
        conn.commit()
        return conn

    if isfile(db_full_path):  # and os.stat(db_full_path).st_ctime:
        while True:
            warn = input(f"DB file ({db_full_path}) already exists. "
                         f"Are you sure you want to reinitialize the database? (y/n/q): ").lower()
            if warn == 'y':
                os.remove(db_full_path)
                print("Database removed!")
                conn = _ReadAndCreateDB()
                return conn
            elif warn == 'n':
                print("Database NOT removed or recreated.")
                break
            elif warn == 'q':
                print("Ok Quitting!")
                exit(0)
            else:
                print("Please choose \'y\', \'n\', or \'q\'")
    else:
        conn = _ReadAndCreateDB()
        return conn


if __name__ == "__main__":
    InitializeNewDB()
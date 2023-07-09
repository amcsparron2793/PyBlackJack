import ConfigFunctions as cf
import sqlite3
from os import remove
from os.path import isfile

# globals
default_config_location = '../cfg/sqliteDB_config.ini'
default_config = [
    {'DEFAULT':
        {
            'db_path': '../MiscProjectFiles/PyBlackJack.db',
            'script_path': '../MiscProjectFiles/InitializeNewDB.sql'
        }
    }
]

if isfile(default_config_location):
    current_config = cf.get_config(config_location=default_config_location)
else:
    current_config = cf.get_config(config_location=default_config_location,
                                   config_list_dict=default_config)

db_path = current_config['DEFAULT']['db_path']
setup_script_path = current_config['DEFAULT']['script_path']


def InitializeNewDB(script_path, db_full_path):
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
                remove(db_full_path)
                print("Database removed!")
                conn = _ReadAndCreateDB()
                return conn
            elif warn == 'n':
                print("Database NOT removed or recreated.")
                conn = sqlite3.connect(db_full_path)
                return conn
            elif warn == 'q':
                print("Ok Quitting!")
                exit(0)
            else:
                print("Please choose \'y\', \'n\', or \'q\'")
    else:
        conn = _ReadAndCreateDB()
        return conn


def GetSQLliteConn(SQLlite_db_path=db_path):
    conn = sqlite3.connect(SQLlite_db_path)
    print(f"Connection to {SQLlite_db_path} established")
    return conn

# TODO: add to db (add player and bank account) and query for preexisting players

if __name__ == "__main__":
    InitializeNewDB(script_path=setup_script_path,
                    db_full_path=db_path)

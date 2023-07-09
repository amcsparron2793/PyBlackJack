import ConfigFunctions as cf
import sqlite3
from os import remove
from os.path import isfile
from AndrewLogger import AndrewsLogger as alogger

# globals
default_config_location = '../cfg/sqliteDB_config.ini'
default_config = [
    {'DEFAULT':
        {
            'db_path': '../MiscProjectFiles/PyBlackJack.db',
            'setupDB_script_path': '../MiscProjectFiles/InitializeNewDB.sql',
            'new_player_setup': '../MiscProjectFiles/NewPlayerSetup.sql'
        }
    }
]

if isfile(default_config_location):
    current_config = cf.get_config(config_location=default_config_location)
else:
    current_config = cf.get_config(config_location=default_config_location,
                                   config_list_dict=default_config)

db_path = current_config['DEFAULT']['db_path']
setupDB_script_path = current_config['DEFAULT']['setupDB_script_path']
NewPlayerSetupScript = current_config['DEFAULT']['new_player_setup']


def InitializeNewDB(script_path, db_full_path, logger: alogger = None):
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


def PlayerInfoLookup(conn: sqlite3.Connection, **kwargs):
    sql_query_text = None
    if ('player_first_name' in kwargs
            and 'player_last_name' in kwargs
            and 'player_id' in kwargs):
        raise AttributeError('please only enter a name OR a player_id')
    elif ('player_first_name' in kwargs
          and 'player_last_name' in kwargs):
        p_first = kwargs['player_first_name']
        p_last = kwargs['player_last_name']
        where_text = (p_first + ' ' + p_last)
        sql_query_text = f"select id from Players where player_full_name = '{where_text}'"
    elif 'player_id' in kwargs:
        p_id = kwargs['player_id']
        where_text = int(p_id)
        sql_query_text = f"select id from Players where id = {where_text}"

    cursor = conn.cursor()
    cursor.execute(sql_query_text)
    res = cursor.fetchone()

    if res is None:
        print('No matching Players found')
    else:
        print(res[0])


def NewPlayerSetup(cxn: sqlite3.Connection,
                   new_player_dict: dict,
                   new_player_script=NewPlayerSetupScript,
                   logger: alogger = None):
    new_player_string = ' '.join(new_player_dict.values()).replace('\'', '')
    print(f"Setting up new player '{new_player_string}'.")
    try:
        with open(new_player_script) as sql_file:
            sql_script = sql_file.read()
            sql_script = sql_script.replace(':fname',
                                            new_player_dict['fname']
                                            ).replace(':lname',
                                                      new_player_dict['lname'])
            print('SQL script ready.')
    except FileNotFoundError as e:
        logger.logger.error(e, exc_info=True)
        raise e

    try:
        cursor = cxn.cursor()
        print('Cursor ready.')
        cursor.executescript(sql_script)
        print(f"New Player \'{new_player_string}\' added to database!")
    except sqlite3.IntegrityError as e:
        if e.args[0].startswith('UNIQUE constraint failed'):
            logger.logger.warning(f"Player {new_player_string} already exists in the database.")
        else:
            logger.logger.error(e, exc_info=True)
            raise e
    except sqlite3.Error as e:
        logger.logger.error(e, exc_info=True)


# TODO: add to db (add player and bank account) and query for preexisting players


if __name__ == "__main__":
    main_logger = alogger()
    main_logger.FinalInit()

    cn = GetSQLliteConn()
    #NewPlayerSetup(cn, {'fname': '\'Default\'', 'lname': '\'Player\''}, logger=main_logger)
    player_name_dict = {'player_first_name': 'Andrew', 'player_last_name': 'McSparron'}
    player_id_dict = {'player_id': 1}
    PlayerInfoLookup(cn, **player_name_dict)# **player_id_dict)

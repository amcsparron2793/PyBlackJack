import ConfigFunctions as cf
from SQLLite3HelperClass import SQLlite3Helper
from pathlib import Path


class PyBlackJackSQLLite(SQLlite3Helper):
    def __init__(self, db_file_path: str = None, config: cf.PyBlackJackConfig = None):
        self.config = config or cf.PyBlackJackConfig(config_filename=cf.DEFAULT_CONFIG_LOCATION.name,
                              config_dir=cf.DEFAULT_CONFIG_LOCATION.parent)
        self.db_file_path = Path(db_file_path) or Path(self.config.get('DEFAULT', 'db_file_path'))
        self.setup_database_script_path = Path(self.config.get('DEFAULT', 'setup_database_script_path'))
        self.setup_new_player_script_path = Path(self.config.get('DEFAULT', 'setup_new_player_script_path'))
        super().__init__(self.db_file_path)
        self.GetConnectionAndCursor()

        if not self.db_file_path.is_file():
            self.initialize_new_db()


    def initialize_new_db(self):
        with open(self.setup_database_script_path) as sql_file:
            sql_script = sql_file.read()

            self._cursor.executescript(sql_script)
            self._connection.commit()

    def new_player_setup(self, new_player_dict: dict):
       new_player_string = ' '.join(new_player_dict.values()).replace('\'', '')
       print(f"Setting up new player '{new_player_string}'.")
       try:
           with open(self.setup_new_player_script_path) as sql_file:
               sql_script = sql_file.read()
               sql_script = sql_script.replace(':fname',
                                               new_player_dict['fname']
                                               ).replace(':lname',
                                                         new_player_dict['lname'])
               print('SQL script ready.')
       except FileNotFoundError as e:
           raise e

       self._cursor.executescript(sql_script)
       self._connection.commit()
       print(f"New Player \'{new_player_string}\' added to database!")

    def PlayerInfoLookup(self, **kwargs):
        sql_query_text = None
        player_first_name = kwargs.get('player_first_name', None)
        player_last_name = kwargs.get('player_last_name', None)
        player_id = kwargs.get('player_id', None)
        if all([player_first_name, player_last_name, player_id]):
            raise AttributeError('please only enter a name OR a player_id')
        elif player_first_name and player_last_name:
            where_text = (player_first_name + ' ' + player_last_name)
            sql_query_text = f"select id from Players where player_full_name = '{where_text}'"
        elif player_id:
            p_id = kwargs['player_id']
            where_text = int(p_id)
            sql_query_text = f"select id from Players where id = {where_text}"

        self.Query(sql_query_text)

        if self.query_results is None:
            print('No matching Players found')
        else:
            print(self.query_results[0][0])
            return self.query_results[0][0]


# TODO: add to db (add player and bank account) and query for preexisting players


if __name__ == "__main__":
    ...
    # main_logger = alogger()
    # main_logger.FinalInit()
    #
    # cn = GetSQLliteConn()
    # #NewPlayerSetup(cn, {'fname': '\'Default\'', 'lname': '\'Player\''}, logger=main_logger)
    # player_name_dict = {'player_first_name': 'Andrew', 'player_last_name': 'McSparron'}
    # player_id_dict = {'player_id': 1}
    # PlayerInfoLookup(cn, **player_name_dict)# **player_id_dict)

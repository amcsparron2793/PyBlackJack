import ConfigFunctions as cf
from SQLLite3HelperClass import SQLlite3Helper
from pathlib import Path


class PyBlackJackSQLLite(SQLlite3Helper):
    """
    Provides functionalities for managing players and their information in a
    BlackJack game application using an SQLite database.

    This class extends the `SQLlite3Helper` and provides additional features for
    initializing a database, managing player data, and retrieving player information.
    It is tightly coupled with the `PyBlackJackConfig` class, from which it sources
    configuration details such as database file paths and script paths.

    :ivar config: Configuration object used to retrieve settings and paths for the database.
    :type config: PyBlackJackConfig
    :ivar setup_database_script_path: Path to the SQL script used for setting up the database.
    :type setup_database_script_path: Path
    :ivar setup_new_player_script_path: Path to the SQL script for adding a new player to the database.
    :type setup_new_player_script_path: Path
    """
    def __init__(self, db_file_path: str = None, config: cf.PyBlackJackConfig = None):
        self.config = config or cf.PyBlackJackConfig(config_filename=cf.DEFAULT_CONFIG_LOCATION.name,
                              config_dir=cf.DEFAULT_CONFIG_LOCATION.parent)
        self.config.GetConfig()

        self._db_file_path = db_file_path
        self.setup_database_script_path = Path(self.config.get('DEFAULT', 'setup_database_script_path'))
        self.setup_new_player_script_path = Path(self.config.get('DEFAULT', 'setup_new_player_script_path'))

        super().__init__(self.db_file_path)
        self.GetConnectionAndCursor()


    @property
    def db_file_path(self):
        self._db_file_path = self._db_file_path or Path(self.config.get('DEFAULT', 'db_file_path'))
        if not self._db_file_path.is_file():
            self.initialize_new_db()
        return self._db_file_path



    def initialize_new_db(self):
        """
        Initializes a new database using the provided SQL script.

        This method reads an SQL script from the file specified by
        `setup_database_script_path` and executes it to initialize or
        setup a database. Upon successful execution of the script,
        all changes are committed to the database.

        :raises FileNotFoundError: If the file specified by
            `setup_database_script_path` does not exist.
        :raises sqlite3.DatabaseError: If there is an issue with the execution
            of the SQL script on the database.

        :return: None
        """
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
       return new_player_dict

    def PlayerIDLookup(self, player_first_name, player_last_name):
        where_text = ' '.join([player_first_name, player_last_name])
        sql_query_text = f"select id from Players where player_full_name = '{where_text}'"

        self.Query(sql_query_text)
        if self.query_results:
            return self.query_results[0][0]
        else:
            print(f"Player {where_text} not found in database.")
            return None

    def PlayerInfoLookup(self, player_id):
        """
        Performs a lookup for player information in the PlayerBanksFull database.

        This method queries the PlayerBanksFull table to retrieve player information,
        including PlayerID, PlayerName, AccountID, and account balance, based on the
        given player_id. If the player_id is not provided, an exception is raised.
        If a matching player is found, the relevant details are returned. Otherwise,
        the method prints a message indicating that the player was not found and
        returns None.

        :param player_id: The ID of the player to look up.
        :type player_id: int
        :raises ValueError: If player_id is not provided.
        :return: A dictionary containing player information if found, otherwise None.
        :rtype: Optional[dict]
        """

        bank_account_query = (f"select PlayerID, PlayerName, AccountID, account_balance "
                              f"from PlayerBanksFull where PlayerID = {player_id}")
        if not player_id:
            raise ValueError("player_id must be provided to perform a lookup.")
        self.Query(bank_account_query)
        if self.query_results:
            return self.list_dict_results[0]
        else:
            print(f"Player with ID {player_id} not found in database.")
            return None




# TODO: add to db (add player and bank account) and query for preexisting players


if __name__ == "__main__":
    pbj_db = PyBlackJackSQLLite()
    p_info = pbj_db.PlayerInfoLookup(pbj_db.PlayerIDLookup(player_first_name='Andrew', player_last_name='McSparron'))
    print(p_info)

from sqlite3 import DatabaseError, OperationalError, IntegrityError

from Backend.settings import Settings
from SQLLite3HelperClass import SQLlite3Helper
from pathlib import Path


class PlayerExistsError(IntegrityError):
    ...


class PlayerDoesNotExistError(Exception):
    ...


class PyBlackJackSQLLite(SQLlite3Helper):
    """
    Provides functionalities for managing players and their information in a
    BlackJack game application using an SQLite database.

    This class extends the `SQLlite3Helper` and provides additional features for
    initializing a database, managing player data, and retrieving player information.
    It is tightly coupled with the `PyBlackJackConfig` class, from which it sources
    configuration details such as database file paths and script paths.

    :ivar setup_database_script_path: Path to the SQL script used for setting up the database.
    :type setup_database_script_path: Path
    :ivar setup_new_player_script_path: Path to the SQL script for adding a new player to the database.
    :type setup_new_player_script_path: Path
    """
    NEW_PLAYER_DICT_KEYS = ['fname', 'lname']

    def __init__(self, db_file_path: str = None, **kwargs):
        self.settings = kwargs.get('settings', Settings())
        self._db_initialized = None


        self.db_file_path = db_file_path or Path(self.settings.db_file_path)
        self.setup_database_script_path = Path(self.settings.setup_database_script_path)
        self.setup_new_player_script_path = Path(self.settings.setup_new_player_script_path)

        super().__init__(self.db_file_path)
        if self.db_file_path.exists() and not isinstance(self.db_file_path, Path):
            self.db_file_path = Path(self.db_file_path)
        self.GetConnectionAndCursor()


    @property
    def db_initialized(self):
        if not self._db_initialized:
            if not hasattr(self, '_cursor'):
                self._db_initialized = False
            else:
                try:
                    self.Query("SELECT name FROM sqlite_master WHERE type='table';")
                    if self.query_results:
                        self._db_initialized = True
                    else:
                        self._db_initialized = False
                except OperationalError:
                    self._db_initialized = False
        return self._db_initialized

    def check_initialization(self):
        if not self.db_initialized:
            raise DatabaseError("Database not initialized. Please initialize the database first.")

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
            print("Database initialized successfully.")

    def new_player_setup(self, new_player_dict: dict):
        """
        Sets up a new player in the database using the provided dictionary of
        player details. The method reads an SQL script, replaces placeholders
        with actual player data, and executes the script to add the player
        to the database.

        :param new_player_dict: Dictionary containing details of the new player.
            Keys must match the expected fields defined within the system.
        :type new_player_dict: dict
        :return: The same dictionary provided as input upon successful setup of the player.
        :rtype: dict
        :raises FileNotFoundError: If the SQL script file for setting up a new player cannot
            be found at the specified script path.
        :raises PlayerExistsError: If the player already exists in the database. This error
            specifically occurs when the database enforces uniqueness constraints.
        :raises IntegrityError: If any other database integrity error occurs during the execution
            of the SQL script.
        """
        self.check_initialization()
        new_player_string = ' '.join(new_player_dict.values()).replace('\'', '')
        print(f"Setting up new player '{new_player_string}'.")
        try:
            with open(self.setup_new_player_script_path) as sql_file:
                sql_script = sql_file.read()

                new_fname = f'\'{new_player_dict[PyBlackJackSQLLite.NEW_PLAYER_DICT_KEYS[0]]}\''
                new_lname = f'\'{new_player_dict[PyBlackJackSQLLite.NEW_PLAYER_DICT_KEYS[1]]}\''

                sql_script = sql_script.replace(f':{PyBlackJackSQLLite.NEW_PLAYER_DICT_KEYS[0]}', new_fname
                                                ).replace(f':{PyBlackJackSQLLite.NEW_PLAYER_DICT_KEYS[1]}', new_lname)
                print('SQL script ready.')
        except FileNotFoundError as e:
           raise e
        try:
            self._cursor.executescript(sql_script)
            self._connection.commit()

            self.Query(f"SELECT id FROM Players WHERE player_first_name = {new_fname} AND player_last_name = {new_lname}")
            new_player_id = self.query_results[0][0]
            print(f"New Player \'{new_player_string}\' added to database!")
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                raise PlayerExistsError(f"Player \'{new_player_string}\' already exists in database.") from None
            else:
                raise e
        return new_player_id

    def PlayerIDLookup(self, player_first_name, player_last_name):
        """
        Searches the database for a player's ID based on their first and last name. The method
        executes a SQL query against the 'Players' table using the full name of the player
        and retrieves the player's ID if it exists in the database. If no player is found,
        it prints a message to the console and returns None.

        :param player_first_name: The first name of the player to look up
        :type player_first_name: str
        :param player_last_name: The last name of the player to look up
        :type player_last_name: str
        :return: The ID of the player if found, or None if the player does not exist in the database
        :rtype: int or None
        """
        self.check_initialization()
        where_text = ' '.join([player_first_name, player_last_name])
        sql_query_text = f"select id from Players where player_full_name = '{where_text}'"

        self.Query(sql_query_text)
        if self.query_results:
            return self.query_results[0][0]
        else:
            print(f"Player {where_text} not found in database.")
            return None

    def PlayerInfoLookup(self, player_id):
        def _no_pid(pid):
            print(f"Player with ID {pid} not found in database.")
            return None
        """
        Looks up player information in the database and retrieves corresponding player
        and bank account details based on the provided player ID. Ensures initialization
        has been performed before executing the query. Returns the first matching record
        if found; otherwise, logs a message and returns None.

        :param player_id: The unique identifier of the player whose information is
            being retrieved.
        :type player_id: int
        :raises ValueError: If `player_id` is not provided.
        :return: A dictionary containing player and bank account details if a match
            is found; otherwise, None.
        :rtype: dict or None
        """
        self.check_initialization()

        bank_account_query = (f"select PlayerID as player_id, PlayerName as player_name,"
                              f" AccountID as account_id, account_balance as account_balance "
                              f"from PlayerBanksFull where PlayerID = {player_id}")
        if not player_id:
            return _no_pid(player_id)

        self.Query(bank_account_query)

        if self.query_results:
            return self.list_dict_results[0]
        else:
            return _no_pid(player_id)

    def GetPlayerPasswordHash(self, player_id):
        self.Query(f"select hash from PlayerHashes where player_id = {player_id}")
        if self.query_results:
            return self.query_results[0][0]
        else:
            raise PlayerDoesNotExistError(f"Player with ID {player_id} does not exist in database.")

    def update_player_account_balance(self, new_balance: int, account_id: int):
        """
        Updates the player's account balance to the specified value in the database. This method
        executes an update query on the `BankAccounts` table and commits the transaction. A confirmation
        message is printed after the update completes.

        :param new_balance: The new balance to be updated in the player's account.
        :type new_balance: int
        :param account_id: The unique identifier of the player's bank account.
        :type account_id: int
        :return: None
        """

        self.check_initialization()
        sql_str = f"""update BankAccounts set account_balance = {new_balance} where id = {account_id}"""
        self.Query(sql_str)
        self._connection.commit()
        print(f'updated BankAccount ID {account_id} with new balance ({new_balance}).')




# TODO: add to db (add player and bank account) and query for preexisting players


if __name__ == "__main__":
    pbj_db = PyBlackJackSQLLite()
    #pbj_db.initialize_new_db()
    #pbj_db.new_player_setup({'fname': 'Andrew', 'lname': 'McSparron'})
    #p_info = pbj_db.PlayerInfoLookup(pbj_db.PlayerIDLookup(player_first_name='Andrew', player_last_name='McSparron'))

    #print(p_info)

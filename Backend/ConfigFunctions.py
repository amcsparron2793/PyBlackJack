from logging import Logger
from typing import List
from pathlib import Path
from Backend.settings import GAME_ROOT_FOLDER
from BetterConfigAJM import BetterConfigAJM

DEFAULT_CONFIG_LOCATION = Path(GAME_ROOT_FOLDER, 'cfg/sqliteDB_config.ini')


class PyBlackJackConfig(BetterConfigAJM):
    DEFAULT_DB_PATH = Path(GAME_ROOT_FOLDER, 'MiscProjectFiles/PyBlackJack.db')
    SETUP_DATABASE_SCRIPT_PATH = Path(GAME_ROOT_FOLDER, 'MiscProjectFiles/InitializeNewDB.sql')
    SETUP_NEW_PLAYER_SCRIPT_PATH = Path(GAME_ROOT_FOLDER, 'MiscProjectFiles/NewPlayerSetup.sql')
    def __init__(self, config_filename, config_dir, config_list_dict: List[dict] = None, logger: Logger = None):
        super().__init__(config_filename, config_dir, config_list_dict, logger)
        self.default_config = [
            {
                'DEFAULT':
                    {
                        'db_file_path': PyBlackJackConfig.DEFAULT_DB_PATH,
                        'setup_database_script_path': PyBlackJackConfig.SETUP_DATABASE_SCRIPT_PATH,
                        'setup_new_player_script_path': PyBlackJackConfig.SETUP_NEW_PLAYER_SCRIPT_PATH
                    }
             }
        ]
        if self.config_list_dict:
            pass
        else:
            self.config_list_dict = self.default_config
        # making this resolve to an absolute path
        self.config_location = Path(self.config_location).resolve()

if __name__ == "__main__":
    config = PyBlackJackConfig(config_filename='sqliteDB_config.ini', config_dir='../cfg')
    config.GetConfig()
    print(config['DEFAULT']['db_path'])
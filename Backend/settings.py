from logging import Logger
from typing import List
from pathlib import Path
from BetterConfigAJM import BetterConfigAJM

class Settings:
    GAME_ROOT_FOLDER = Path(__file__).parent.parent
    DEFAULT_CONFIG_LOCATION = Path(GAME_ROOT_FOLDER, 'cfg/PyBlackjackConfig.ini')
    def __init__(self, config=None):
        self.starting_chips = 250
        self.config = config or PyBlackJackConfig(config_filename=Settings.DEFAULT_CONFIG_LOCATION.name,
                              config_dir=Settings.DEFAULT_CONFIG_LOCATION.parent)

        self.config.GetConfig()

        self.db_file_path = Path(self.config.get('DEFAULT', 'db_file_path'))
        self.setup_database_script_path = Path(self.config.get('DEFAULT',
                                                               'setup_database_script_path'))
        self.setup_new_player_script_path = Path(self.config.get('DEFAULT',
                                                                 'setup_new_player_script_path'))
        self.use_unicode_cards = self.config.getboolean('CARD', 'use_unicode')
        self.shoe_runout_warning_threshold = self.config.getint('DECK', 'shoe_runout_warning_threshold')


class PyBlackJackConfig(BetterConfigAJM):
    DEFAULT_DB_PATH = Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/PyBlackJack.db')
    SETUP_DATABASE_SCRIPT_PATH = Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/InitializeNewDB.sql')
    SETUP_NEW_PLAYER_SCRIPT_PATH = Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/NewPlayerSetup.sql')
    def __init__(self, config_filename, config_dir, config_list_dict: List[dict] = None, logger: Logger = None):
        super().__init__(config_filename, config_dir, config_list_dict, logger)
        self.default_config = [
            {
                'DEFAULT':
                    {
                        'db_file_path': PyBlackJackConfig.DEFAULT_DB_PATH,
                        'setup_database_script_path': PyBlackJackConfig.SETUP_DATABASE_SCRIPT_PATH,
                        'setup_new_player_script_path': PyBlackJackConfig.SETUP_NEW_PLAYER_SCRIPT_PATH
                    },
                'CARD':
                    {
                        'use_unicode': True,
                    },
                'DECK':
                    {'shoe_runout_warning_threshold': 15}
             }
        ]
        if self.config_list_dict:
            pass
        else:
            self.config_list_dict = self.default_config
        # making this resolve to an absolute path
        self.config_location = Path(self.config_location).resolve()








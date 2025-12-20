from logging import Logger
from typing import List
from pathlib import Path
from BetterConfigAJM import BetterConfigAJM
from pygame import font

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
        self.use_database = self.config.getboolean('DEFAULT', 'use_database')
        self.player_name = self.config.get('DEFAULT', 'player_name')


class PyGameSettings(Settings):
    GREEN_RGB = (0, 128, 0)
    WHITE_RGB = (255, 255, 255)
    BLACK_RGB = (0, 0, 0)
    def __init__(self, config=None):
        super().__init__(config)
        self.game_screen_bg_color = self.parse_tuple_from_config(self.config.get('PYGAME', 'game_screen_bg_color'))
        self.start_screen_bg_color = self.parse_tuple_from_config(self.config.get('PYGAME','start_screen_bg_color'))
        self.game_over_screen_bg_color = self.parse_tuple_from_config(self.config.get('PYGAME','game_over_screen_bg_color'))
        self.game_font_color = self.parse_tuple_from_config(self.config.get('PYGAME','game_font_color'))

        self.screen_size = (self.config.getint('PYGAME', 'screen_size_width'),
                            self.config.getint('PYGAME', 'screen_size_height'))
        self.font = font.Font(None, 36)

        # Resolve card asset locations, preferring the project's SVG-cards-1.3 when available
        cfg_dir = Path(self.config.get('PYGAME', 'card_dir_location'))
        default_dir = PyBlackJackConfig.CARD_SVG_DEFAULT_PATH
        # Pick configured directory if it exists; otherwise fall back to default
        self.card_dir_location = (cfg_dir if cfg_dir.exists() and cfg_dir.is_dir() else default_dir).resolve()

        cfg_back = Path(self.config.get('PYGAME', 'card_back_location'))
        default_back = PyBlackJackConfig.CARD_BACK_SVG_DEFAULT_PATH
        # Pick configured back if it exists; otherwise fall back to default
        self.card_back_location = (cfg_back if cfg_back.exists() and cfg_back.is_file() else default_back).resolve()

        def _build_map(from_dir: Path):
            try:
                return {
                    ' '.join(x.stem.split('_of_')): x.resolve()
                    for x in from_dir.iterdir()
                    if x.suffix.lower() == '.svg'
                    and not x.stem.endswith('2')
                    and not x.stem.endswith('_joker')
                }
            except Exception:
                return {}

        self.card_svg_path_list = _build_map(self.card_dir_location)
        # If the configured directory didn't yield any cards, try default path as a fallback
        if not self.card_svg_path_list and default_dir.exists():
            self.card_svg_path_list = _build_map(default_dir.resolve())
            self.card_dir_location = default_dir.resolve()

    @staticmethod
    def parse_tuple_from_config(config_value):
        # Removing parentheses and splitting the string by commas
        parsed_values = config_value.strip("()").split(",")
        # Converting each value to an integer and creating a tuple
        return tuple(map(int, parsed_values))


class PyBlackJackConfig(BetterConfigAJM):
    DEFAULT_DB_PATH = Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/PyBlackJack.db')
    SETUP_DATABASE_SCRIPT_PATH = Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/InitializeNewDB.sql')
    SETUP_NEW_PLAYER_SCRIPT_PATH = Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/NewPlayerSetup.sql')
    CARD_SVG_DEFAULT_PATH = Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/PlayingCards/SVG-cards-1.3')
    CARD_BACK_SVG_DEFAULT_PATH = CARD_SVG_DEFAULT_PATH.parent / 'card_back.svg' #Path(Settings.GAME_ROOT_FOLDER, 'MiscProjectFiles/PlayingCards/card_back.svg')

    DEFAULT_SCREEN_SIZE = (800, 600)

    def __init__(self, config_filename, config_dir, config_list_dict: List[dict] = None, logger: Logger = None):
        super().__init__(config_filename, config_dir, config_list_dict, logger)
        self.default_config = [
            {
                'DEFAULT':
                    {
                        'db_file_path': PyBlackJackConfig.DEFAULT_DB_PATH,
                        'setup_database_script_path': PyBlackJackConfig.SETUP_DATABASE_SCRIPT_PATH,
                        'setup_new_player_script_path': PyBlackJackConfig.SETUP_NEW_PLAYER_SCRIPT_PATH,
                        'use_database': 'False',
                        'player_name': ''
                    },
                'CARD':
                    {
                        'use_unicode': 'True',
                    },
                'DECK':
                    {'shoe_runout_warning_threshold': '15'},
                'PYGAME':
                    {
                        'game_screen_bg_color': PyGameSettings.GREEN_RGB,
                        'start_screen_bg_color': PyGameSettings.GREEN_RGB,
                        'game_over_screen_bg_color': PyGameSettings.BLACK_RGB,
                        'game_font_color': PyGameSettings.WHITE_RGB,
                        'screen_size_width': PyBlackJackConfig.DEFAULT_SCREEN_SIZE[0],
                        'screen_size_height': PyBlackJackConfig.DEFAULT_SCREEN_SIZE[1],
                        'card_dir_location': PyBlackJackConfig.CARD_SVG_DEFAULT_PATH,
                        'card_back_location': PyBlackJackConfig.CARD_BACK_SVG_DEFAULT_PATH
                    }
             }
        ]
        if self.config_list_dict:
            pass
        else:
            self.config_list_dict = self.default_config
        # making this resolve to an absolute path
        self.config_location = Path(self.config_location).resolve()








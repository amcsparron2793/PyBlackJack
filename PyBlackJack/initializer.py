from Backend.PlayerCashRecordDB import PyBlackJackSQLLite
from Backend.settings import Settings
from PyBlackJack.Bank.Cage import Cage, DatabaseCage
from PyBlackJack.Deck.DeckOfCards import Deck
from PyBlackJack.Players.Players import Player, Dealer, DatabasePlayer


class BlackJackInitializer:
    NON_DATABASE_PLAYER_CLASS = Player
    NON_DATABASE_CAGE_CLASS = Cage
    NON_DATABASE_DEALER_CLASS = Dealer
    DATABASE_PLAYER_CLASS = DatabasePlayer
    DATABASE_CAGE_CLASS = DatabaseCage
    DATABASE_DEALER_CLASS = Dealer

    def __init__(self, **kwargs):
        self.banker = None
        self.player = None
        self.db = None
        self.dealer = None
        self.game_deck = None

        self.game_settings = kwargs.get('game_settings', Settings())

        self.use_database = kwargs.get('use_database', self.game_settings.use_database)
        self.player_name = kwargs.get('player_name', self.game_settings.player_name)
        self.player_id = kwargs.get('player_id', None)

        self.initialize_game(**kwargs)

    def _shared_initialization(self, **kwargs):
        self.game_deck = Deck(settings=self.game_settings)
        self.game_deck.shuffle_deck()
        dealer_class = kwargs.get('dealer_class', self.__class__.NON_DATABASE_DEALER_CLASS)
        self.dealer = dealer_class(chosen_card_back=self.game_deck.card_back)

    def _setup_non_database(self, **kwargs):
        non_database_player_class = kwargs.get('non_database_player_class', self.__class__.NON_DATABASE_PLAYER_CLASS)
        non_database_cage_class = kwargs.get('non_database_cage_class', self.__class__.NON_DATABASE_CAGE_CLASS)
        self.player = non_database_player_class(settings=self.game_settings)

        self.banker = non_database_cage_class(settings=self.game_settings)

    def _setup_database(self, **kwargs):
        self.db = kwargs.get('db', PyBlackJackSQLLite(settings=self.game_settings))

        database_player_class = kwargs.get('database_player_class', self.__class__.DATABASE_PLAYER_CLASS)
        self.player = database_player_class(player_id=self.player_id,
                                         player_name=self.player_name,
                                         settings=self.game_settings)

        cage_class = kwargs.get('database_cage_class', self.__class__.DATABASE_CAGE_CLASS)
        self.banker = cage_class(self.db, settings=self.game_settings)

    def initialize_game(self, **kwargs):
        """
        Initializes the game by setting up the necessary components such as deck,
        player, dealer, and banker. It handles both database-enabled and non-database
        scenarios based on the provided keyword arguments.

        :param kwargs: Optional keyword arguments to customize game initialization:
            - ``use_database`` (bool): Indicates if the game should use a database. Defaults to the
              value defined in game_settings.
            - ``player_name`` (str): The player's name. Defaults to the value defined in game_settings.
            - ``player_id`` (Optional[int]): The player's unique identifier. Defaults to None.
            - ``db`` (Optional[object]): The database instance if a custom database should be used.
              Required if ``use_database`` is True.
        :return: None
        """
        self._shared_initialization()

        if not self.use_database:
            self._setup_non_database(**kwargs)

        elif self.use_database:
            self._setup_database(**kwargs)

        # initialize player chips and dealer chips
        self.banker.pay_in(self.player)
        self.banker.pay_in(self.dealer)
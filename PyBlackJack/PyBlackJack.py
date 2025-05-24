#! python3
"""
PyBlackJack
"""

import pygame
from PyGameBlackJack.GameScreens import StartScreen, GameOverScreen, GameScreen
from os import system
from Backend.settings import Settings, PyGameSettings
from Deck.DeckOfCards import Deck
from Players.Players import Player, Dealer, DatabasePlayer
from Bank.Cage import Cage, DatabaseCage
from Backend import yes_no
from Backend.PlayerCashRecordDB import PyBlackJackSQLLite


class Game:
    """
    Game class for managing and executing a blackjack game.

    The Game class encapsulates the logic and data required for managing a game
    of blackjack, including initializing players, handling turns, gameplay, and
    managing bets and chips. It interacts with player, dealer, and banker objects
    to ensure proper game flow.

    :ivar banker: Reference to the banker or cage responsible for handling chips.
    :type banker: Cage | DatabaseCage | None
    :ivar player: The primary player participating in the game.
    :type player: Player | DatabasePlayer | None
    :ivar db: Database connection or object, if the game uses a database.
    :type db: PyBlackJackSQLLite | None
    :ivar dealer: The dealer in the game interacting with the player and banker.
    :type dealer: Dealer | None
    :ivar game_deck: The deck of cards used during the game.
    :type game_deck: Deck | None
    :ivar game_settings: The configuration and settings for the game.
    :type game_settings: Settings
    """
    def __init__(self, **kwargs):
        self.banker = None
        self.player = None
        self.db = None
        self.dealer = None
        self.game_deck = None

        self.game_settings = kwargs.get('game_settings', Settings())

        #self._start_screen()

        self._initialize_game(**kwargs)


    def _initialize_game(self, **kwargs):
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
        self.use_database = kwargs.get('use_database', self.game_settings.use_database)
        self.player_name = kwargs.get('player_name', self.game_settings.player_name)
        self.player_id = kwargs.get('player_id', None)
        self.game_deck = Deck(settings=self.game_settings)
        self.game_deck.shuffle_deck()

        if not self.use_database:
            self.banker = Cage(settings=self.game_settings)
            self.player = Player(settings=self.game_settings)
        else:
            self.db = kwargs.get('db', PyBlackJackSQLLite(settings=self.game_settings))
            self.banker = DatabaseCage(self.db, settings=self.game_settings)
            self.player = DatabasePlayer(player_id=self.player_id,
                                         player_name=self.player_name,
                                         settings=self.game_settings)

        self.dealer = Dealer(chosen_card_back=self.game_deck.card_back)
        # initialize player chips and dealer chips
        self.banker.pay_in(self.player)
        self.banker.pay_in(self.dealer)

    def play(self):
        """
        Handles the execution of the primary loop of the application and manages its interruption.

        This method repeatedly executes the `hand_loop` function to perform the necessary
        tasks. If the user interrupts the process manually via a keyboard interrupt (Ctrl+C),
        the function acknowledges the action, displays a quitting message, and terminates
        the program with an exit code of -1.

        :raises KeyboardInterrupt: When the user interrupts the application manually.
        """
        try:
            self.hand_loop()
        except KeyboardInterrupt:
            print("Ok Quitting")
            exit(-1)

    def _get_suits_string(self):
        """
        Generates a string representation of card suits based on the game settings.

        This method checks the game settings to determine whether Unicode card symbols
        should be used. If so, it constructs a string containing all Unicode card suit
        symbols, separated by spaces. If Unicode symbols are not used, an empty string
        is returned.

        :return: A string of card suits based on the game settings.
        :rtype: str
        """
        if self.game_settings.use_unicode_cards:
            suits = Deck.UNICODE_SUITS
        else:
            suits = ''
        suits_string = ''

        for x in suits:
            suits_string += f"{x} "
        return suits_string

    def _start_screen(self):
        """
        Starts the initial screen for the PyBlackJack game, presenting the welcome message
        with decorative suits and prompting the user to start the game. Repeatedly displays
        the screen until the user chooses to begin by providing a "yes" response or chooses
        to exit the application.

        :raises KeyboardInterrupt: Raised if the user produces an interrupt signal (e.g.,
            Control-C) during the prompt. This results in gracefully exiting the application.
        :return: None
        """
        while True:
            system('cls')
            print(f"{self._get_suits_string() * 4} Welcome to PyBlackJack! {self._get_suits_string() * 4}")
            try:
                if yes_no("Ready to play?"):
                    system('cls')
                    break
                else:
                    print("Ok, goodbye!")
                    exit(0)
            except KeyboardInterrupt:
                print("Ok Quitting")
                exit(-1)

    def deal(self):
        """
        Draws a hand of cards from the deck.

        This method draws two cards from the game deck and returns them as a hand.
        The method ensures that the number of cards drawn matches the expected
        hand size for this operation.

        :return: A list containing two cards drawn from the game deck.
        :rtype: list
        """
        hand = [self.game_deck.draw(), self.game_deck.draw()]
        return hand

    def check_bust(self, player: Player):
        """
        Checks if the given player's hand value exceeds 21 and marks them as busted if so.

        :param player: The player whose hand value is being evaluated.
        :type player: Player
        :return: The player object, with their bust status potentially updated.
        :rtype: Player
        """
        if player.get_hand_value() > 21:
            self.is_bust(player)
            return player
        else:
            return player

    def hit(self, player: Player):
        """
        Processes the player's decision to hit (draw a card from the deck) in the
        game. This function adds a card to the player's hand, checks if the player
        has exceeded the allowable score (busted), and handles the setup for a new
        hand if necessary. If the player is not busted, their last move is updated
        to reflect the hit action.

        :param player: An instance of the Player class. Represents the player
            taking the action of hitting.
        :return: The updated Player instance after processing the hit action.
            Includes updates to the player's hand, bust status, and last move.
        """
        print(f"Player: {player.player_display_name} Decided to hit!")
        player.hand.append(self.game_deck.draw())
        self.check_bust(player)
        if player.busted:
            if self.new_hand():
                self.setup_new_hand()
                return player
            else:
                exit(0)
        player.last_move = 'hit'
        return player

    @staticmethod
    def stay(player):
        """
        Provides a static method to handle a player's decision to "stay" during gameplay.

        This method updates the player's last move to "stay" and logs the decision.

        :param player: Instance of the player who chooses to stay.
        :type player: Player
        :return: The updated player object with 'last_move' set to 'stay'.
        :rtype: Player
        """
        print(f"Player: {player.player_display_name} Decided to stay!")
        player.last_move = 'stay'
        return player

    def player_turn(self):
        """
        Executes the player's turn in the game. It provides the player with two
        choices: to either "Hit" or "Stay". Based on the player's input, it calls
        the corresponding method to proceed with the game. Ensures that the input
        is valid before proceeding.

        :raises ValueError: If the player's input is invalid and neither corresponds to
            "Hit" nor "Stay".
        """
        choices = {1: 'Hit',
                   2: 'Stay'}

        pretty_choices = [(x, y) for x, y in [x for x in choices.items()]]
        while True:
            c = input(f"Would you like to \n{pretty_choices[0][0]}. {pretty_choices[0][1]}"
                      f"\n{pretty_choices[1][0]}. {pretty_choices[1][1]}\n: ").lower()
            if c == '1' or c == 'hit':
                self.hit(self.player)
                break
            elif c == '2' or c == 'stay':
                self.stay(self.player)
                break
            else:
                print("Please choose hit or stay.")

    def is_bust(self, player: Player):
        """
        Determines if a player has gone over the permissible score threshold,
        marking them as "busted", and ends the current hand. This function
        modifies the player's status to "busted" and triggers the necessary
        post-bust actions, such as calling the `end_hand` method.

        :param player: The player object whose score is being evaluated.
        :type player: Player
        :return: The modified player object with an updated "busted" status.
        :rtype: Player
        """
        print(f"Player {player.player_display_name} Busted! Game over.")
        player.busted = True
        self.end_hand()
        return player

    def display_winner(self):
        """
        Determines the winner of the game by comparing the hand values of the player and
        the dealer. Awards the winning hand's value to the respective party through the
        banker.

        The method first checks if either the player or the dealer has gone "busted".
        If so, the other party is declared the winner. If both player and dealer are
        still valid, their hand values are compared to decide the winner. In both cases,
        the winner’s hand value is awarded via the banker.

        :return: None
        """
        if self.player.busted:
            print(f"{self.dealer.player_display_name} Wins!!!!!!!!")
            self.banker.award_hand_value(self.dealer)

        elif self.dealer.busted:
            print(f"Player {self.player.player_display_name} Wins!!!!!!!")
            self.banker.award_hand_value(self.player)

        elif self.player.get_hand_value() < self.dealer.get_hand_value():
            print(f"{self.dealer.player_display_name} Wins!!!!!!!!")
            self.banker.award_hand_value(self.dealer)

        elif self.player.get_hand_value() > self.dealer.get_hand_value():
            print(f"Player {self.player.player_display_name} Wins!!!!!!!")
            self.banker.award_hand_value(self.player)

    def setup_new_hand(self):
        """
        Prepares a new hand for the player and dealer by reinitializing their attributes and dealing
        new cards from the game deck.

        This method reinitializes the player's attributes based on its type (either `DatabasePlayer`
        or `Player`) and assigns a new hand of cards. Similarly, it reinitializes the dealer's
        attributes, assigns a new hand, and sets up its hidden hand state.

        :raises TypeError: If the type of player is not recognized.

        :param self: The instance of the class that owns this method.
        :return: None
        """
        if isinstance(self.player, DatabasePlayer):
            self.player.__init__(self.player.player_id)
        elif isinstance(self.player, Player):
            self.player.__init__(self.player.chips)
        self.player.hand = self.deal()
        self.dealer.__init__(chosen_card_back=self.game_deck.card_back, player_chips=self.dealer.chips)
        self.dealer.hand = self.deal()
        self.dealer.hidden_hand_setup()

    def hand_loop(self):
        """
        Executes the main game loop for handling a single hand in the blackjack game.
        This loop manages the player's and dealer's actions for betting, hitting, staying,
        and ultimately concludes the round when appropriate conditions are met, such as both
        sides staying or a participant busting. Once a hand ends, it facilitates the
        setup for a new hand or concludes the game based on player input.

        :return: None
        """
        self.setup_new_hand()
        while True:
            # game.hit(player_one)
            self.player.print_hand()
            self.dealer.print_hand()
            # TODO: figure out how to make betting work for dealer also
            if not self.player.has_bet:  # and not self.dealer.has_bet
                self.bet_question(self.player)
                self.player.has_bet = True
            else:
                pass

            self.player_turn()

            if ((self.dealer.last_move == 'stay'
                 and self.player.last_move == 'stay') or
                    (self.dealer.busted or self.player.busted)):
                print("---------------")
                self.end_hand()
                new = self.new_hand()
                if new:
                    self.setup_new_hand()
                    continue
                else:
                    break
            print("---------------")

            # print(f"last moves were {self.dealer.last_move, self.player.last_move}")
            if self.dealer.should_stay():
                self.stay(self.dealer)
            else:
                self.hit(self.dealer)
                self.dealer.hidden_hand_update()

    def end_hand(self):
        """
        Ends the current hand of gameplay, displaying final scores and determining the
        winner. This method prints the player's hand, reveals the dealer's hand,
        determines the winner, and updates the player's account balance if both the
        banker and player are database-backed entities.

        :raises TypeError: if `banker` or `player` is not initialized or of incorrect
            types.
        :return: None
        """
        print("FINAL SCORE:")
        self.player.print_hand()
        self.dealer.reveal_hand()
        self.display_winner()
        if isinstance(self.banker, DatabaseCage) and isinstance(self.player, DatabasePlayer):
            self.banker.write_new_account_balance(self.player)
        # self.banker.write_new_account_balance(self.dealer)

    @staticmethod
    def new_hand():
        """
        Prompts the user to decide whether to play another hand or not. The function continuously
        accepts user input until a valid response is provided, where 'y' indicates playing
        another hand and 'n' indicates exiting the game. If 'y' is selected, the screen is
        cleared and the function returns True. If 'n' is selected, the function returns False.

        :return:
            True if the user decides to play another hand.
            False if the user decides not to play another hand.
        :rtype: bool
        """
        while True:
            play_again = input("\nPlay Another Hand? (y/n): ").lower()
            if play_again == 'y':
                system('cls')
                return True
            elif play_again == 'n':
                return False
            else:
                pass

    def bet_question(self, player: Player):
        """
        Prompts the player to place a bet and processes the betting transaction through the banker.
        Handles edge cases where the player might be bankrupt or needs a bank pay-in.

        :param player: The player instance who is placing the bet.
        :type player: Player
        :return: The updated player instance after the betting process.
        :rtype: Player
        """
        if player.chips <= 0:
            player.bankrupt()
            if player.needs_pay_in:
                self.banker.pay_in(player)
        else:
            pass
        while True:
            bet_amount = input(f"How much would you like to bet? (${player.chips:,} available): ")
            if bet_amount.isnumeric():
                bet_amount = int(bet_amount)
                break
            else:
                print("Bet amount must be an integer.")

        player.bet_amount = bet_amount
        player = self.banker.take_bet(player)
        return player


class PyGameBlackJack(Game):
    START = "START"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"
    GAME_STATES = [START, PLAYING, GAME_OVER]

    def __init__(self, **kwargs):
        pygame.init()
        self.game_settings = kwargs.pop('game_settings', PyGameSettings())

        pygame.display.set_caption("PyBlackJack")

        self.screen = pygame.display.set_mode(size=self.game_settings.screen_size)
        self.clock = pygame.time.Clock()

        self.running = True

        self._state = PyGameBlackJack.START  # Game states: START, PLAYING, GAME_OVER
        self.start_screen = StartScreen(self.game_settings, screen=self.screen)
        self.game_over_screen = GameOverScreen(self.game_settings, screen=self.screen)
        self.game_screen = GameScreen(self.game_settings, screen=self.screen, player_name=self.game_settings.player_name)

        super().__init__(game_settings=self.game_settings, **kwargs)

        # FIXME: This is a hacky workaround - need to figure out how to easily parse tuples from config
        self.game_settings.game_screen_bg_color = PyGameSettings.GREEN_RGB
        self.game_settings.game_over_screen_bg_color = PyGameSettings.BLACK_RGB

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value in PyGameBlackJack.GAME_STATES:
            self._state = value
        else:
            raise ValueError(f"Invalid game state: {value}")

    def _keydown_events(self, event):
        if event.key == pygame.K_SPACE:
            print("space")
            # self.play()
        elif event.key == pygame.K_ESCAPE:
            # self.running = False
            self.state = PyGameBlackJack.GAME_OVER
        elif event.key == pygame.K_h:  # Example: Player hits
            print("Player hits (logic under development)")
        elif event.key == pygame.K_s:  # Example: Player stays
            print("Player stays (logic under development)")

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = PyGameBlackJack.GAME_OVER
            elif event.type == pygame.KEYDOWN:
                self._keydown_events(event)

    def _start_screen(self):
        """
        Render the start screen.
        """
        self.start_screen.draw(self.screen)
        pygame.display.flip()  # Update the screen

        # Wait for the player to press any key to continue
        self._wait_for_key()

    def _wait_for_key(self):
        """
        Wait for a key press to continue.
        """
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def play(self):
        """
        Main game loop.
        """
        while self.running:
            # Handle game states
            if self.state == PyGameBlackJack.START:
                self._start_screen()
                self.state = PyGameBlackJack.PLAYING  # Transition to the playing state

            elif self.state == PyGameBlackJack.PLAYING:
                self._game_loop()

            elif self.state == PyGameBlackJack.GAME_OVER:
                self._game_over_screen()
                self.running = False  # Exit loop after displaying game over

        self._quit_game()

    def _game_loop(self):
        """
        The main game-playing loop.
        """
        while self.state == PyGameBlackJack.PLAYING:
            # Event handling
            self.check_events()

            # Update game logic
            # Add functionality such as checking for a bust, dealer actions, etc.

            # Render game screen
            self._render_game_screen()

            # Limit frame rate to 60 FPS
            self.clock.tick(60)

    def _render_game_screen(self):
        """
        Render the main game playing screen.
        """
        self.game_screen.draw(self.screen)
        pygame.display.flip()  # Update the display

    def _game_over_screen(self):
        """
        Display the game over screen.
        """
        self.game_over_screen.draw(self.screen)
        pygame.display.flip()  # Update the screen

        # Wait for the player to press any key to continue
        self._wait_for_key()

    def _quit_game(self):
        """
        Properly shut down the game.
        """
        pygame.quit()
        exit()




if __name__ == '__main__':
    game = PyGameBlackJack()#Game()
    game.play()


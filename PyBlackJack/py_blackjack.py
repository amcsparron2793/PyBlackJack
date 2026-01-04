#! python3
"""
PyBlackJack
"""

from os import system
from Backend.settings import Settings
from PyBlackJack.Deck.DeckOfCards import Deck, CardSuits
from PyBlackJack.Players.Players import Player, Dealer, DatabasePlayer
from PyBlackJack.Bank.Cage import Cage, DatabaseCage
from Backend import yes_no
from Backend.PlayerCashRecordDB import PyBlackJackSQLLite
from PyBlackJack.initializer import BlackJackInitializer


class Game(BlackJackInitializer):
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
            self._start_screen()
            self.hand_loop()
        except KeyboardInterrupt:
            print("Ok Quitting")
            exit(-1)


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
            print(self.get_welcome_message())
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

        # TODO: redo with enum TurnChoices
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

    @staticmethod
    def get_winner_string(winner):
        return f"{winner} Wins!!!!!!!!"

    def _print_and_award_winner(self, player: Player):
        print(self.get_winner_string(player.player_display_name))
        self.banker.award_hand_value(player)

    def _calculate_winner(self):
        dealer_high = (self.player.get_hand_value() < self.dealer.get_hand_value())
        player_high = (self.player.get_hand_value() > self.dealer.get_hand_value())
        tie = (self.player.get_hand_value() == self.dealer.get_hand_value())

        if self.dealer.busted:
            player_win = True
            dealer_win = False
        elif self.player.busted:
            dealer_win = True
            player_win = False
        else:
            player_win = player_high or tie
            dealer_win = dealer_high
        return player_win, dealer_win

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
        player_win, dealer_win = self._calculate_winner()

        if dealer_win:
            self._print_and_award_winner(self.dealer)

        elif player_win:
            self._print_and_award_winner(self.player)

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


if __name__ == '__main__':
    game = Game()
    game.play()


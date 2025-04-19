#! python3
"""
PyBlackJack
"""

import itertools
import random
from os import system


# classes
class EmptyShoeError(BaseException):
    """
    Exception raised when attempting to interact with an empty shoe in a card game or similar context.

    The `EmptyShoeError` is a user-defined exception that extends BaseException. It is intended to signal issues related
    to operations involving an empty shoe, such as attempting to draw cards when none are available.

    :noindex:
    """
    def __init__(self, *args):
        super().__init__(*args)

    def with_traceback(self, tb):
        """
        Exception.with_traceback(tb) --
            set self.__traceback__ to tb and return self.
        """
        self.__traceback__ = tb
        return self


class Cards:
    """
    Represents a deck of playing cards with support for Unicode and plaintext representations.

    This class provides attributes to define card suit symbols, card back designs, and
    values for the cards. Users can choose between Unicode or plaintext representation
    by specifying the parameter during initialization. By default, Unicode is used, and
    appropriate card back and suit symbols are set accordingly.

    :ivar UNICODE_SUITS: Predefined list of Unicode symbols representing card suits.
    :type UNICODE_SUITS: list[str]
    :ivar PLAINTEXT_SUITS: Predefined list of plaintext names for card suits.
    :type PLAINTEXT_SUITS: list[str]
    :ivar UNICODE_CARD_BACK: Unicode character representing the back of a card.
    :type UNICODE_CARD_BACK: str
    :ivar PLAINTEXT_CARD_BACK: String representing the plaintext card back design.
    :type PLAINTEXT_CARD_BACK: str
    :ivar card_back: Current card back symbol based on the chosen representation.
    :type card_back: str
    :ivar suit: Current card suits set based on the chosen representation.
    :type suit: list[str]
    :ivar value: Numeric values representing cards in the deck.
    :type value: range
    """
    UNICODE_SUITS = ['\u2664', '\u2661', '\u2662', '\u2667']
    PLAINTEXT_SUITS = ['Spade', 'Heart', 'Diamond', 'Club']
    UNICODE_CARD_BACK = '\U0001F0A0'
    PLAINTEXT_CARD_BACK = 'xxxx'

    def __init__(self, use_unicode=True, card_back: str = None):
        self.card_back = card_back

        if use_unicode:
            if self.card_back is None:
                # three leading zeros made this code work
                self.card_back = Cards.UNICODE_CARD_BACK
            else:
                self.card_back = self.card_back
            self.suit = Cards.UNICODE_SUITS
        else:
            self.card_back = Cards.PLAINTEXT_CARD_BACK
            self.suit = Cards.PLAINTEXT_SUITS

        self.value = range(1, 14)


class Deck(Cards):
    """
    Represents a standard deck of cards.

    This class is designed to create, manage, and manipulate a deck of cards.
    It provides functionality to shuffle, draw, and reload the deck, ensuring
    that the deck's state and integrity are properly maintained.

    :ivar deck: A list representing the current deck of cards, created as
        combinations of card values and suits.
    :type deck: list
    """

    SHOE_RUNOUT_WARNING_THRESHOLD = 15
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deck = list(itertools.product(self.value, self.suit))

    def shuffle_deck(self):
        """
        Shuffles the deck of cards to randomize the order.

        This method randomizes the order of the deck list using the shuffle function
        from the random module. It modifies the existing deck attribute in place and
        returns the shuffled deck.

        :return: The shuffled list of cards.
        :rtype: list
        """
        random.shuffle(self.deck)
        return self.deck

    def draw(self):
        """
        Draws the top card from the deck.

        This method removes and returns the first card from the deck. It also checks
        the current size of the deck and provides warnings if the number of cards
        left is less than or equal to 15. If there are no cards left in the deck,
        an `EmptyShoeError` is raised.

        :raises EmptyShoeError: If the deck has run out of cards.
        :return: The top card of the deck.
        """
        if len(self.deck) <= Deck.SHOE_RUNOUT_WARNING_THRESHOLD:
            print(f"{len(self.deck)} cards left to draw from.")
        if len(self.deck) <= 0:
            raise EmptyShoeError("Deck has run out of cards")
        else:
            return self.deck.pop(0)

    def reload_deck(self):
        """
        Reloads the deck of cards by reinitializing and shuffling it, or raises an
        exception if the user indicates not to reload the deck.

        This method keeps prompting the user to choose whether to reload the deck
        or not. If the user chooses to reload the deck, the deck is reinitialized
        and shuffled. If the user chooses not to reload, an EmptyShoeError is raised.
        Invalid inputs are ignored, and the prompt repeats until a valid response
        is provided.

        :raises EmptyShoeError: If the user declines to reload the deck.
        :return: The reloaded and shuffled deck of cards.
        """
        while True:
            r = input("Would you like to reload the deck? (y/n): ").lower()
            if r == 'y':
                self.__init__()
                self.shuffle_deck()
                return self.deck
            elif r == 'n':
                raise EmptyShoeError("Deck has run out of cards")
            else:
                pass


class Player:
    """
    Represents a player in a card game.

    The Player class models a participant in the game, capable of performing various
    actions such as placing bets, calculating hand values, printing their hand, and
    managing game-related states like bankrupt status. It includes attributes to store
    the player's hand, chips, betting status, and other relevant gameplay details.

    :ivar hand: Represents the cards currently in the player's possession.
    :type hand: list
    :ivar is_player: Indicates whether the instance represents an actual player or the dealer.
    :type is_player: bool
    :ivar player_number: Identifies the player with a unique number or a special 'Dealer' identifier.
    :type player_number: int or str
    :ivar last_move: Stores the last move made by the player. Defaults to None.
    :type last_move: Any
    :ivar busted: Tracks whether the player has exceeded the game's card limit.
    :type busted: bool
    :ivar bet_amount: Represents the amount the player has bet.
    :type bet_amount: int
    :ivar has_bet: Indicates whether the player has placed a bet in the current game.
    :type has_bet: bool
    :ivar chips: The total chips the player currently has.
    :type chips: int
    """
    def __init__(self, player_chips: int = None,):
        self.hand = []
        self.is_player = True
        self.player_number = self.set_player_number()
        self.last_move = None
        self.busted = False
        self.bet_amount: int = 0
        self.has_bet = False
        self.chips: int = player_chips or Cage.STARTING_CHIPS

    def bankrupt(self):
        """
        Indicates that the player has gone bankrupt and exits the program.

        The method prints a message indicating that the player is bankrupt,
        displays a system pause, and subsequently terminates the program. It
        does not return any value and is primarily used to handle player
        bankruptcy scenarios during the game.

        :return: None
        """
        print(f"Player {self.player_number} is bankrupt! goodbye!")
        system("pause")
        exit(0)

    @staticmethod
    def get_print_hand(hand):
        """
        Converts the numeric representation of card ranks in a hand to their corresponding name
        representation for better readability. Cards with rank identifiers 1, 11, 12, and 13 are
        replaced with their respective names ('Ace', 'Jack', 'Queen', 'King'), while all other
        cards remain unchanged in the output.

        :param hand: A list of tuples representing the cards of a hand. Each tuple consists of
                     two elements: the rank and suit where the rank is an integer and the suit
                     is typically a string or another integer.

        :return: A list of tuples where card ranks 1, 11, 12, and 13 are replaced with their
                 corresponding name representation ('Ace', 'Jack', 'Queen', or 'King'). Other
                 ranks remain unchanged along with the associated suit.
        """
        p_hand = []
        for x in hand:
            if x[0] == 1:
                p_hand.append(('Ace', x[1]))
            elif x[0] == 11:
                p_hand.append(('Jack', x[1]))
            elif x[0] == 12:
                p_hand.append(('Queen', x[1]))
            elif x[0] == 13:
                p_hand.append(('King', x[1]))
            else:
                p_hand.append(x)
        return p_hand

    def set_player_number(self):
        """
        Determines and sets the identifier for the current entity, which can be a
        player or a dealer. The identifier will be used for tracking and managing
        data within the database such as available cash or other relevant
        attributes.

        :raises AttributeError: If the `is_player` attribute is not defined in the
            calling context or is missing.
        :return: Returns the identifier of the entity. It will return an integer (1)
            if the entity is a player, or a string ("Dealer") if it is the dealer.
        :rtype: Union[int, str]
        """
        # TODO: change this to player name and use it as part of db tracking of available cash etc
        if self.is_player:
            player_id = 1
        else:
            player_id = "Dealer"
        return player_id

    def print_hand(self):
        """
        Print the current hand of the player in a readable format.

        This method retrieves the current hand representation of the player
        and prints it to the console, including the player's number for
        identification.

        :return: None
        """
        print_hand = self.get_print_hand(self.hand)
        print(f"Player {self.player_number}: {print_hand}")

    def get_hand_value(self):
        """
        Calculates the total value of the player's hand in a card game.

        This method iterates through the player's hand, evaluates the value of each card,
        and determines the total hand value while considering the special case for Aces.
        Cards with a rank of 11 or higher are valued as 10. If an Ace (value 1) exists
        in the hand, its value will be adjusted to 11 if it does not cause the hand
        value to exceed 21.

        :return: The total value of the hand as an integer.
        :rtype: int
        """
        value = []
        for c in self.hand:
            if c[0] >= 11:
                value.append(10)
            else:
                value.append(c[0])
            if 1 in value:
                if sum(value) + 10 > 21:
                    pass
                else:
                    value.append(10)
        return sum(value)


class Dealer(Player):
    """
    Represents a Dealer in the game, inheriting from the Player class.

    The Dealer class extends the Player class to implement specific behaviors and
    attributes for a game dealer. It includes unique functionality such as managing
    a hidden hand, revealing the cards, and determining whether the dealer should
    stay based on a certain set of conditions. This class is specifically designed
    to follow game-specific rules for dealer behavior.

    :ivar is_player: Indicates whether the instance is a player or not.
                     Always False for a dealer.
    :type is_player: bool
    :ivar player_number: The player number assigned to the dealer through the
                         ``set_player_number`` method.
    :type player_number: Any
    :ivar hidden_hand: Represents the dealer's hand with one or more cards
                       intentionally hidden.
    :type hidden_hand: list
    """
    def __init__(self, player_chips: int = None):
        super().__init__(player_chips)
        self.is_player = False
        self.player_number = self.set_player_number()
        self.hidden_hand = []

    def print_hand(self):
        """
        Prints the player's hand in a readable format, including the player number.
        The hand is determined using the `get_print_hand` method and is internally
        formatted before being printed.

        :return: None
        :rtype: None
        """
        print_hand = self.get_print_hand(self.hidden_hand)
        print(f"{self.player_number}: {print_hand}")

    def hidden_hand_setup(self):
        """
        Creates a hidden representation of the player's hand by modifying the current
        hand. This involves copying the hand, then replacing the first card with the
        back of the card from the game's deck.

        :raises AttributeError: If any of the required attributes (hand or
            game_deck.card_back) are missing or not correctly initialized.
        :return: None
        """
        self.hidden_hand = [x for x in self.hand]
        self.hidden_hand.pop(0)
        self.hidden_hand.insert(0, game.game_deck.card_back)

    def hidden_hand_update(self):
        """
        Updates the `hidden_hand` list with the last card from the `hand` list if the
        length of `hand` is greater than the length of `hidden_hand`. Otherwise, no
        changes are made. Returns the updated `hidden_hand`.

        :return: The updated list of `hidden_hand`.
        :rtype: list
        """
        if len(self.hand) > len(self.hidden_hand):
            self.hidden_hand.append(self.hand[-1])
        else:
            pass
        return self.hidden_hand

    def reveal_hand(self):
        """
        Displays the player's hand in a human-readable format along with the player's number.
        This function retrieves the string representation of the player's hand using the
        `get_print_hand` method and displays the result along with the player number.

        :return: None
        :rtype: NoneType
        """
        print_hand = self.get_print_hand(self.hand)
        print(f"{self.player_number}: {print_hand}")

    def should_stay(self):
        """
        Determines whether the player should stay based on the current hand value and
        a degree of randomness.

        This method evaluates the player's hand value and decides if the player should
        stay in the current game. When the hand value is greater than or equal to 15,
        a randomized decision-making element is introduced with an approximately 50/50
        chance. Similarly, if the hand value is less than or equal to 16, the decision
        is randomized but more likely false. Otherwise, when the hand value doesn't
        fall within these ranges, the decision will default to staying in the game.

        :raises TypeError: If the hand value or randomness has unexpected types.

        :return: A boolean value indicating whether the player should stay in the game.
                 True to stay, False otherwise. The decision may include elements of
                 randomness.
        :rtype: bool
        """
        if self.get_hand_value() >= 15:
            # this should be True without randomness
            return bool(random.Random().randint(1, 100) % 2)
        elif self.get_hand_value() <= 16:
            # this should be False without randomness
            return bool(random.Random().randint(1, 100) % 2)
        else:
            return True


class Cage:
    """
    Manages the chip interactions between the bank (Cage) and players, such as initiating
    chips for new players, handling bets, and awarding winnings.

    This class handles chips-related operations specific to a card game. It includes mechanisms
    to set initial chip values for players, manage bets, and calculate and distribute winnings.

    :ivar hand_value: The total value of chips collected from all bets during a hand.
    :type hand_value: int
    :cvar STARTING_CHIPS: The number of chips each player starts with.
    :cvar CHIP_VALUES: The list of predefined chip values available in the game.
    """
    STARTING_CHIPS = 250
    CHIP_VALUES = [5, 15, 25, 50]
    def __init__(self):
        self.hand_value: int = 0

    def pay_in(self, player: Player):
        player.chips = Cage.STARTING_CHIPS
        return player

    def take_bet(self, player: Player):
        if player.chips <= 0:
            player.bankrupt()
        if 0 < player.bet_amount <= player.chips:
            self.hand_value += player.bet_amount
            player.chips -= player.bet_amount
            return player
        else:
            raise ValueError("Bet amount cannot exceed players available chips, or be zero.")

    def award_hand_value(self, player: Player):
        player.chips += (self.hand_value * 2)
        self.hand_value = 0
        return player


class Game:
    def __init__(self):
        self.game_deck = Deck()
        self.game_deck.shuffle_deck()
        self.banker = Cage()
        self.player = Player()
        self.dealer = Dealer()
        # initialize player chips and dealer chips
        self.banker.pay_in(self.player)
        self.banker.pay_in(self.dealer)

    def deal(self):
        hand = [self.game_deck.draw(), self.game_deck.draw()]
        return hand

    def check_bust(self, player: Player):
        if player.get_hand_value() > 21:
            self.is_bust(player)
            return player
        else:
            return player

    def hit(self, player: Player):
        print(f"Player: {player.player_number} Decided to hit!")
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
        print(f"Player: {player.player_number} Decided to stay!")
        player.last_move = 'stay'
        return player

    def player_turn(self):
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
        print(f"Player {player.player_number} Busted! Game over.")
        player.busted = True
        self.display_winner()
        return player

    def display_winner(self):
        if self.player.busted:
            print(f"{self.dealer.set_player_number()} Wins!!!!!!!!")
            self.banker.award_hand_value(self.dealer)

        elif self.dealer.busted:
            print(f"Player {self.player.set_player_number()} Wins!!!!!!!")
            self.banker.award_hand_value(self.player)

        elif self.player.get_hand_value() < self.dealer.get_hand_value():
            print(f"{self.dealer.set_player_number()} Wins!!!!!!!!")
            self.banker.award_hand_value(self.dealer)

        elif self.player.get_hand_value() > self.dealer.get_hand_value():
            print(f"Player {self.player.set_player_number()} Wins!!!!!!!")
            self.banker.award_hand_value(self.player)

    def setup_new_hand(self):
        self.player.__init__(self.player.chips)
        self.player.hand = game.deal()
        self.dealer.__init__(self.dealer.chips)
        self.dealer.hand = game.deal()
        self.dealer.hidden_hand_setup()

    def hand_loop(self):
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
        print("FINAL SCORE:")
        self.player.print_hand()
        self.dealer.reveal_hand()
        self.display_winner()

    @staticmethod
    def new_hand():
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
        if player.chips <= 0:
            player.bankrupt()
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
    try:
        game.hand_loop()
    except KeyboardInterrupt:
        print("Ok Quitting")
        exit(-1)

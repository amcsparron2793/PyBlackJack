import itertools
import random

# TODO: use settings class
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
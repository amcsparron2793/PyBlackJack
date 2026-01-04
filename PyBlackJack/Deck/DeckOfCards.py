import itertools
import random
from Backend.enum import CardSuits, CardValues
from Backend.settings import Settings


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


class _Card:
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
    UNICODE_CARD_BACK = '\U0001F0A0'
    PLAINTEXT_CARD_BACK = 'xxxx'

    def __init__(self, suit, value, ** kwargs):#, use_unicode=True, card_back: str = None):
        self.settings = kwargs.pop('settings', Settings())
        self._card_suit = None
        self._card_value = None

        # noinspection PyTypeChecker
        self.card_back = kwargs.get('card_back', None)
        self.card_suit = suit
        self.card_value = value


        self.setup_cards()


    # TODO: MAKE A _PYGAMECARD CLASS GIVE THIS A PNGFILEPATH property

    def __str__(self):
        return f"{self.card_value.name} of {self.card_suit.name}S"

    @property
    def card_suit(self):
        return self._card_suit

    @card_suit.setter
    def card_suit(self, suit:CardSuits):
        if isinstance(suit, CardSuits):
            self._card_suit = suit
        else:
            raise AttributeError(f"Suit must be a CardSuits enum value. NOT \'{type(suit)}\'")

    @property
    def card_value(self):
        return self._card_value

    @card_value.setter
    def card_value(self, value:CardValues):
        if isinstance(value, CardValues):
            self._card_value = value
        else:
            raise AttributeError("Value must be a CardValues enum value.")

    def _setup_unicode_cardback_and_suit(self):
        if self.card_back is None:
            # three leading zeros made this code work
            self.card_back = self.__class__.UNICODE_CARD_BACK
        else:
            self.card_back = self.card_back
        #self.suit = [x.value for x in CardSuits]

    def _setup_plaintext_cardback_and_suit(self):
        self.card_back = self.__class__.PLAINTEXT_CARD_BACK
        self.suit = [x.name for x in CardSuits]

    def setup_cards(self):
        if self.settings.use_unicode_cards:
            self._setup_unicode_cardback_and_suit()
        else:
            self._setup_plaintext_cardback_and_suit()
        #self.value = [x.value for x in CardValues]

class Deck:
    """
    Represents a standard deck of cards.

    This class is designed to create, manage, and manipulate a deck of cards.
    It provides functionality to shuffle, draw, and reload the deck, ensuring
    that the deck's state and integrity are properly maintained.

    :ivar deck: A list representing the current deck of cards, created as
        combinations of card values and suits.
    :type deck: list
    """

    DEFAULT_SHOE_RUNOUT_WARNING_THRESHOLD = 15
    def __init__(self, **kwargs):
        self.settings = kwargs.pop('settings', Settings())
        self.shoe_runout_warning_threshold = kwargs.pop('shoe_runout_warning_threshold',
                                                        self.settings.shoe_runout_warning_threshold)
                                                        #Deck.DEFAULT_SHOE_RUNOUT_WARNING_THRESHOLD)
        super().__init__(**kwargs)
        self.deck = []
        self._populate_deck(**kwargs)


        self.card_back = self.deck[0].card_back
        # self.deck = list(itertools.product(self.value, self.suit))

    @property
    def is_running_low(self):
        return len(self.deck) <= self.shoe_runout_warning_threshold

    @property
    def is_empty(self):
        return len(self.deck) <= 0

    def print_as_populating(self, card: _Card):
        # TODO: make this flashy - alternate blackish with red?
        print(card)

    def _populate_deck(self, **kwargs):
        while len(self.deck) < 52:
            for card_val, card_suit in itertools.product(CardValues, CardSuits):
                card = _Card(suit=card_suit, value=card_val, **kwargs)
                self.print_as_populating(card)
                self.deck.append(card)

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
        if self.is_running_low:
            print(f"{len(self.deck)} cards left to draw from.")
        if self.is_empty:
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
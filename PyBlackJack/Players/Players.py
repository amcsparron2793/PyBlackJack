import random
from os import system
from Backend import yes_no
from Backend.settings import Settings
from Backend.PlayerCashRecordDB import PyBlackJackSQLLite, PlayerDoesNotExistError


class Player:
    """
    Represents a player in a card game.

    The Player class models a participant in the game, capable of performing various
    actions such as placing bets, calculating hand values, printing their hand, and
    managing game-related states like bankrupt status. It includes attributes to store
    the player's hand, chips, betting status, and other relevant gameplay details.

    :ivar hand: Represents the cards currently in the player's possession.
    :type hand: list
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

    BANKRUPT_BUY_IN_TEXT = "Player is bankrupt. Would you like to buy back in and play again?"

    def __init__(self, player_chips: int = None, **kwargs):
        # TODO: implement more?
        self.settings = kwargs.get('settings', Settings())
        self.hand = []
        self.chips = player_chips
        self.last_move = None
        self.busted = False
        self.bet_amount: int = 0
        self.has_bet = False
        self.needs_pay_in = False
        if isinstance(self.chips, int) and self.chips == 0:
            self.bankrupt()

    def bankrupt(self):
        """
        Handles the scenario where a player becomes bankrupt during a game.

        The method checks whether the player has already been marked as "busted".
        If not, it prompts the player with the option to buy back into the game
        and continue playing. If the player agrees, their chips are reset to
        the defined starting value. If the player declines, the game exits for
        that player with a farewell message.

        :return: None
        """
        if self.busted:
            pass
        else:
            if yes_no(Player.BANKRUPT_BUY_IN_TEXT):
                self.chips = self.settings.starting_chips
                self.needs_pay_in = True
                return self.needs_pay_in

        print(f"Player {self.player_display_name} is bankrupt! goodbye!")
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

    @property
    def player_display_name(self):
        """
        Returns the display name of the player.

        This method determines the display name based on the class of the object. If the
        object is not a subclass of the Dealer class, it returns a generic identifier.
        Otherwise, it identifies the object as a "Dealer". It is intended to facilitate
        database tracking of player-specific information such as available cash.

        :return: The display name of the player.
        :rtype: Union[str, int]
        """
        if not issubclass(self.__class__, Dealer):
            return 1
        else:
            return "Dealer"

    def print_hand(self):
        """
        Print the current hand of the player in a readable format.

        This method retrieves the current hand representation of the player
        and prints it to the console, including the player's number for
        identification.

        :return: None
        """
        print_hand = self.get_print_hand(self.hand)
        print(f"Player {self.player_display_name}: {print_hand}")

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

    :ivar hidden_hand: Represents the dealer's hand with one or more cards
                       intentionally hidden.
    :type hidden_hand: list
    """

    def __init__(self, chosen_card_back, player_chips: int = None):
        super().__init__(player_chips)
        self.hidden_hand = []
        self.chosen_card_back = chosen_card_back

    def print_hand(self):
        """
        Prints the player's hand in a readable format, including the player number.
        The hand is determined using the `get_print_hand` method and is internally
        formatted before being printed.

        :return: None
        :rtype: None
        """
        print_hand = self.get_print_hand(self.hidden_hand)
        print(f"{self.player_display_name}: {print_hand}")

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
        self.hidden_hand.insert(0, self.chosen_card_back)

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
        print(f"{self.player_display_name}: {print_hand}")

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


class DatabasePlayer(Player):
    """
    Represents a player whose data is retrieved and managed via a database.

    This class extends the `Player` class by adding functionality to interact with
    a SQLite database for retrieving and updating player information. It initializes
    with player-specific data such as account balance, player name, and account ID,
    while leveraging database operations to manage and update these details.

    :ivar account_balance: The current account balance of the player.
    :type account_balance: Optional[int]
    :ivar player_name: The name of the player.
    :type player_name: Optional[str]
    :ivar account_id: The unique identifier for the player's account.
    :type account_id: Optional[int]
    :ivar player_id: The unique identifier for the player, used to query the database.
    :type player_id: Optional[int]
    :ivar db: The database connection and cursor object for managing database operations.
    :type db: PyBlackJackSQLLite
    """

    def __init__(self, player_id=None, player_name=None, **kwargs):
        self.settings = kwargs.get('settings', Settings())
        self.account_balance = None
        self.player_name = player_name
        self.account_id = None
        self.player_id = player_id
        if all([self.player_id, self.player_name]):
            raise AttributeError("Cannot initialize with both player_id and player_name.")

        self.db = PyBlackJackSQLLite()
        self.db.GetConnectionAndCursor()

        self.get_player()

        super().__init__(player_chips=self.account_balance)

    def bankrupt(self):
        # TODO
        super().bankrupt()

    @property
    def player_display_name(self):
        if issubclass(self.__class__, DatabasePlayer):
            return self.player_name
        else:
            return super().player_display_name

    def get_player(self):
        if not self.player_id:
            if self.player_name:
                self.player_id = self.db.PlayerIDLookup(player_first_name=self.player_name.split()[0].capitalize(),
                                                        player_last_name=self.player_name.split()[1].capitalize())
            else:
                fn = self._get_new_player_name('first')
                ln = self._get_new_player_name('last')
                self.player_id = self.db.PlayerIDLookup(player_first_name=fn.capitalize(),
                                                        player_last_name=ln.capitalize())

        player_attrs = self.db.PlayerInfoLookup(self.player_id)
        if not player_attrs:
            np_dict = self.build_player_dict()
            np_id = self.db.new_player_setup(np_dict)
            self.player_id = np_id
            player_attrs = self.db.PlayerInfoLookup(self.player_id)

        for name, attr in player_attrs.items():
            setattr(self, name, attr)

    @staticmethod
    def _get_new_player_name(get_first_or_last_name: str):
        if get_first_or_last_name.lower() in ['first', 'last']:
            pass
        else:
            raise AttributeError('get_first_or_last_name must be either "first" or "last"')

        while True:
            name = input(f"Enter {get_first_or_last_name} name: ").title()
            if name.isalpha():
                return name
            else:
                print("Please enter a valid name.")

    def build_player_dict(self):
        if yes_no("Player does not exist in database. Would you like to create a new player?"):
            fn = self._get_new_player_name('first')
            ln = self._get_new_player_name('last')
            return {self.db.NEW_PLAYER_DICT_KEYS[0]: fn, self.db.NEW_PLAYER_DICT_KEYS[1]: ln}
        else:
            raise PlayerDoesNotExistError("Player does not exist in database.")


if __name__ == "__main__":
    p = DatabasePlayer(1)
    p.chips = 100
    print(p.account_balance)

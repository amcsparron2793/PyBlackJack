from Backend.settings import Settings


class Cage:
    """
    Manages the chip interactions between the bank (Cage) and players, such as initiating
    chips for new players, handling bets, and awarding winnings.

    This class handles chips-related operations specific to a card game. It includes mechanisms
    to set initial chip values for players, manage bets, and calculate and distribute winnings.

    :ivar hand_value: The total value of chips collected from all bets during a hand.
    :type hand_value: int
    :cvar CHIP_VALUES: The list of predefined chip values available in the game.
    """
    CHIP_VALUES = [5, 15, 25, 50]
    def __init__(self):
        self.hand_value: int = 0
        self.settings = Settings()

    def pay_in(self, player: 'Player'):
        player.chips = self.settings.starting_chips
        return player

    def take_bet(self, player: 'Player'):
        if player.chips <= 0:
            player.bankrupt()
        if 0 < player.bet_amount <= player.chips:
            self.hand_value += player.bet_amount
            player.chips -= player.bet_amount
            return player
        else:
            raise ValueError("Bet amount cannot exceed players available chips, or be zero.")

    def award_hand_value(self, player: 'Player'):
        player.chips += (self.hand_value * 2)
        self.hand_value = 0
        return player


class DatabaseCage(Cage):
    def __init__(self, db:'PyBlackJackSQLLite'):
        super().__init__()
        self.db = db

    def write_new_account_balance(self, player: 'Player'):
        if player.chips != player.account_balance:
            self.db.update_player_account_balance(player.chips, player.account_id)
            player.account_balance = player.chips
            print(f"New balance: {player.account_balance}")
        else:
            print("No change in balance")

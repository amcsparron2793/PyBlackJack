#! python3
"""
PyBlackJack
"""
from os import system
from Backend.settings import Settings
from Deck.DeckOfCards import Deck
from Players.Players import Player, Dealer, DatabasePlayer
from Bank.Cage import Cage, DatabaseCage
from Backend import yes_no
from Backend.PlayerCashRecordDB import PyBlackJackSQLLite


class Game:
    def __init__(self, use_database=False, **kwargs):
        self.game_settings = kwargs.get('game_settings', Settings())

        self.game_deck = Deck(settings=self.game_settings)
        self.game_deck.shuffle_deck()

        if not use_database:
            self.banker = Cage(settings=self.game_settings)
            self.player = Player(settings=self.game_settings)
        else:
            self.db = kwargs.get('db', PyBlackJackSQLLite(settings=self.game_settings))
            self.banker = DatabaseCage(self.db, settings=self.game_settings)
            self.player = DatabasePlayer(kwargs.get('player_id', 1), settings=self.game_settings)

        self.dealer = Dealer(chosen_card_back=self.game_deck.card_back)
        # initialize player chips and dealer chips
        self.banker.pay_in(self.player)
        self.banker.pay_in(self.dealer)

    @staticmethod
    def start_screen():
        while True:
            system('cls')
            print("Welcome to PyBlackJack!")
            if yes_no("Ready to play?"):
                system('cls')
                break
            else:
                print("Ok, goodbye!")
                exit(0)

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
        print(f"Player: {player.player_display_name} Decided to stay!")
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
        print(f"Player {player.player_display_name} Busted! Game over.")
        player.busted = True
        self.end_hand()
        return player

    def display_winner(self):
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
        if isinstance(self.player, DatabasePlayer):
            self.player.__init__(self.player.player_id)
        elif isinstance(self.player, Player):
            self.player.__init__(self.player.chips)
        self.player.hand = game.deal()
        self.dealer.__init__(chosen_card_back=game.game_deck.card_back, player_chips=self.dealer.chips)
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
        if isinstance(self.banker, DatabaseCage) and isinstance(self.player, DatabasePlayer):
            self.banker.write_new_account_balance(self.player)
        # self.banker.write_new_account_balance(self.dealer)

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
    game = Game(use_database=True)
    game.start_screen()
    try:
        game.hand_loop()
    except KeyboardInterrupt:
        print("Ok Quitting")
        exit(-1)

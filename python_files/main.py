#! python3
"""
PyBlackJack
"""

import logging
import itertools
import random
from os import system


# classes
class EmptyShoeError(BaseException):
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
    def __init__(self, use_unicode=True, card_back: str = None):
        self.card_back = card_back

        self.unicode_suits = ['\u2664', '\u2661', '\u2662', '\u2667']
        self.plaintext_suits = ['Spade', 'Heart', 'Diamond', 'Club']

        if use_unicode:
            if self.card_back is None:
                # three leading zeros made this code work
                self.card_back = '\U0001F0A0'
            else:
                self.card_back = self.card_back
            self.suit = self.unicode_suits
        else:
            self.card_back = 'xxxx'
            self.suit = self.plaintext_suits

        self.value = range(1, 14)


class Deck(Cards):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deck = list(itertools.product(self.value, self.suit))

    def shuffle_deck(self):
        random.shuffle(self.deck)
        return self.deck

    def draw(self):
        """Draw a card from the deck, make sure it is removed when it is drawn."""
        if len(self.deck) <= 15:
            print(f"{len(self.deck)} cards left to draw from.")
        if len(self.deck) <= 0:
            raise EmptyShoeError("Deck has run out of cards")
        else:
            return self.deck.pop(0)

    def reload_deck(self):
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
    def __init__(self):
        self.hand = []
        self.is_player = True
        self.player_number = self.set_player_number()
        self.last_move = None
        self.busted = False
        self.bet_amount: int = 0
        self.has_bet = False

    def bankrupt(self):
        print(f"Player {self.player_number} is bankrupt! goodbye!")
        system("pause")
        exit(0)

    @staticmethod
    def get_print_hand(hand):
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
        # TODO: change this to player name and use it as part of db tracking of available cash etc
        if self.is_player:
            player_id = 1
        else:
            player_id = "Dealer"
        return player_id

    def print_hand(self):
        print_hand = self.get_print_hand(self.hand)
        print(f"Player {self.player_number}: {print_hand}")

    def get_hand_value(self):
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
    def __init__(self):
        super().__init__()
        self.is_player = False
        self.player_number = self.set_player_number()
        self.hidden_hand = []

    def print_hand(self):
        print_hand = self.get_print_hand(self.hidden_hand)
        print(f"{self.player_number}: {print_hand}")

    def hidden_hand_setup(self):
        self.hidden_hand = [x for x in self.hand]
        self.hidden_hand.pop(0)
        self.hidden_hand.insert(0, game.game_deck.card_back)

    def hidden_hand_update(self):
        if len(self.hand) > len(self.hidden_hand):
            self.hidden_hand.append(self.hand[-1])
        else:
            pass
        return self.hidden_hand

    def reveal_hand(self):
        print_hand = self.get_print_hand(self.hand)
        print(f"{self.player_number}: {print_hand}")

    def should_stay(self):
        if self.get_hand_value() >= 15:
            # this should be True without randomness
            return bool(random.Random().randint(1, 100) % 2)
        elif self.get_hand_value() <= 16:
            # this should be False without randomness
            return bool(random.Random().randint(1, 100) % 2)
        else:
            return True


class Cage:
    def __init__(self):
        self.starting_chips = 250
        self.chip_values = [5, 15, 25, 50]
        self.hand_value: int = 0

    def pay_in(self, player: Player):
        player.chips = self.starting_chips
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
        self.player.__init__()
        self.player.hand = game.deal()
        self.dealer.__init__()
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
            bet_amount = input(f"How much would you like to bet? (${player.chips} available): ")
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

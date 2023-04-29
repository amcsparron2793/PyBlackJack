#! python3
"""
PyBlackJack
"""
import logging
import itertools
import random


# classes

class Cards:
    def __init__(self):
        self.suit = ['Spade', 'Heart', 'Diamond', 'Club']
        self.value = range(1, 14)


class Deck(Cards):
    def __init__(self):
        super().__init__()
        self.deck = list(itertools.product(self.value, self.suit))

    def shuffle_deck(self):
        random.shuffle(self.deck)
        return self.deck

    def draw(self):
        """Draw a card from the deck, make sure it is removed when it is drawn."""
        return self.deck.pop(0)


class Player:
    def __init__(self):
        self.hand = []
        self.is_player = True
        self.player_number = self.set_player_number()
        self.last_move = None

    def set_player_number(self):
        if self.is_player:
            player_id = 1
        else:
            player_id = "Dealer"
        return player_id

    def print_hand(self):
        print(f"Player {self.player_number}: {self.hand}")

    def get_hand_value(self):
        value = []
        for c in self.hand:
            if c[0] >= 11:
                value.append(10)
            else:
                value.append(c[0])
        return sum(value)


class Dealer(Player):
    def __init__(self):
        super().__init__()
        self.is_player = False
        self.player_number = self.set_player_number()
        self.hidden_hand = []

    def print_hand(self):
        print(f"{self.player_number}: {self.hidden_hand}")

    def hidden_hand_setup(self):
        # FIXME: this needs to be fixed, when the cpu hits,
        #  the new hand isn't SHOWN properly, it works, just a display issue
        self.hidden_hand = [x for x in self.hand]
        self.hidden_hand.pop(0)
        self.hidden_hand.insert(0, ('xxxx', 'xxxx'))
        print(self.hand, self.hidden_hand)

    def reveal_hand(self):
        print(f"{self.player_number}: {self.hand}")

    def should_stay(self):
        if self.get_hand_value() >= 15:
            return True
        elif self.get_hand_value() <= 16:
            return False
        else:
            return True


class Game:
    def __init__(self):
        self.game_deck = Deck()
        self.game_deck.shuffle_deck()

    def deal(self):
        hand = [self.game_deck.draw(), self.game_deck.draw()]
        return hand

    def check_bust(self, player: Player):
        if player.get_hand_value() > 21:
            self.is_bust(player)
        else:
            return player

    def hit(self, player: Player):
        print(f"Player: {player.player_number} Decided to hit!")
        player.hand.append(self.game_deck.draw())
        self.check_bust(player)
        player.last_move = 'hit'
        return player

    def stay(self, player):
        print(f"Player: {player.player_number} Decided to stay!")
        player.last_move = 'stay'
        return player

    def player_turn(self, player: Player):
        choices = {1: 'hit',
                   2: 'stay'}
        # print(choices.items())
        c = int(input(f"please make a choice {[(x,y) for x, y in choices.items()]}: "))
        if c == 1:
            self.hit(player)
        elif c == 2:
            self.stay(player)
        else:
            print("Please choose 1 or 2")

    @staticmethod
    def is_bust(player: Player):
        print(f"Player {player.player_number} Busted! Game over.")
        exit(0)

    @staticmethod
    def display_winner(player: Player, cpu: Dealer):
        if player.get_hand_value() < cpu.get_hand_value():
            print(f"{cpu.set_player_number()} Wins!!!!!!!!")
            exit(0)
        else:
            print(f"Player {player.set_player_number()} Wins!!!!!!!")
            exit(0)


if __name__ == '__main__':
    game = Game()
    dealer = Dealer()
    player_one = Player()

    dealer.hand = game.deal()
    player_one.hand = game.deal()
    dealer.hidden_hand_setup()

    while True:
        # game.hit(player_one)
        player_one.print_hand()
        dealer.print_hand()
        game.player_turn(player_one)
        if (dealer.last_move == 'stay'
                and player_one.last_move == 'stay'):
            print("---------------")
            break
        print("---------------")
        print(f"last moves were {dealer.last_move, player_one.last_move}")
        if dealer.should_stay():
            game.stay(dealer)
        else:
            game.hit(dealer)

    print("FINALS:")
    player_one.print_hand()
    dealer.reveal_hand()
    game.display_winner(player_one, dealer)


    #while True:
    #final_eval(player_hand=game.player.hand, dealer_hand=game.dealer.hand)



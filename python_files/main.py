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



class Game:
    def __init__(self):
        super().__init__()
        self.game_deck = Deck()
        self.game_deck.shuffle_deck()
        # TODO: this needs to happen outside of the game class, so each player can hit or stay independently
        self.dealer = Player()
        self.player = Player()
        self.dealer.hand = self.deal()
        self.player.hand = self.deal()

    def deal(self):
        hand = [self.game_deck.draw(), self.game_deck.draw()]
        return hand
    def hit(self):
        ...



def final_eval(player_hand, dealer_hand):
    if sum([x[0] for x in dealer_hand]) > 21:
        print("Dealer Busts, Player Wins!")
        return Player
    elif sum([x[0] for x in player_hand]) > 21:
        print("Player Busts, Dealer Wins!")
        return Player

    if sum([x[0] for x in dealer_hand]) > sum([x[0] for x in player_hand]):
        print(f"Dealer Wins with {sum([x[0] for x in dealer_hand])}, "
              f"over players {sum([x[0] for x in player_hand])}")
    elif sum([x[0] for x in dealer_hand]) < sum([x[0] for x in player_hand]):
        print(f"Player Wins with {sum([x[0] for x in player_hand])}, "
              f"over Dealers {sum([x[0] for x in dealer_hand])}")


if __name__ == '__main__':
    game = Game()

    #while True:
    final_eval(player_hand=game.player.hand, dealer_hand=game.dealer.hand)



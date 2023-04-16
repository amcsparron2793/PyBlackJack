#! python3
"""
PyBlackJack
"""
import logging


# classes
class Deck:
    def __init__(self):
        self.card_suits = {1: 'hearts', 2: 'spades', 3: 'clubs', 4: 'diamonds'}
        self.card_value_range = (1, 14)
        self.deck = []
        self.deck = self.make_deck()
        print(self.deck)

    def make_deck(self):
        values = [x for x in range(self.card_value_range[0], self.card_value_range[1])]
        for x in self.card_suits:
            self.deck.append({x: values})
        return self.deck

    def draw(self):
        ...


class Card(Deck):
    def __init__(self):
        super().__init__()
        self.suit = None
        self.value = None


if __name__ == '__main__':
    Deck()

#! python3
"""
PyBlackJack
"""
import logging
import itertools
import random

# globals
face_card_dict = {1: 'Ace',
                  11: 'Jack',
                  12: 'Queen',
                  13: 'King'}


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
        """for card in self.hidden_hand:
            if card[0] in [1, 11, 12, 13]:
                print(face_card_dict[card[0]])
            else:
                print(card)"""
        print(f"{self.player_number}: {self.hidden_hand}")

    def hidden_hand_setup(self):
        self.hidden_hand = [x for x in self.hand]
        self.hidden_hand.pop(0)
        self.hidden_hand.insert(0, ('xxxx', 'xxxx'))

    def hidden_hand_update(self):
        if len(self.hand) > len(self.hidden_hand):
            self.hidden_hand.append(self.hand[-1])
        else:
            pass
        return self.hidden_hand

    def reveal_hand(self):
        print(f"{self.player_number}: {self.hand}")

    def should_stay(self):
        if self.get_hand_value() >= 15:
            # this should be True without randomness
            return bool(random.Random().randint(1, 100) % 2)
        elif self.get_hand_value() <= 16:
            # this should be False without randomness
            return bool(random.Random().randint(1, 100) % 2)
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

    @staticmethod
    def stay(player):
        print(f"Player: {player.player_number} Decided to stay!")
        player.last_move = 'stay'
        return player

    def player_turn(self, player: Player):
        choices = {1: 'Hit',
                   2: 'Stay'}

        pretty_choices = [(x, y) for x, y in [x for x in choices.items()]]
        while True:
            c = input(f"Would you like to \n{pretty_choices[0][0]}. {pretty_choices[0][1]}"
                      f"\n{pretty_choices[1][0]}. {pretty_choices[1][1]}\n: ").lower()
            if c == '1' or c == 'hit':
                self.hit(player)
                break
            elif c == '2' or c == 'stay':
                self.stay(player)
                break
            else:
                print("Please choose hit or stay.")

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


def hand_loop():
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
            dealer.hidden_hand_update()
    print("FINAL SCORE:")
    player_one.print_hand()
    dealer.reveal_hand()
    game.display_winner(player_one, dealer)


def new_hand():
    play_again = input("Play Another Hand? (y/n): ").lower()
    if play_again == 'y':
        return True
    elif play_again == 'n':
        return False
    else:
        return False


if __name__ == '__main__':
    game = Game()
    dealer = Dealer()
    player_one = Player()

    dealer.hand = game.deal()
    player_one.hand = game.deal()
    dealer.hidden_hand_setup()
    #while True:
    try:
        hand_loop()
    except KeyboardInterrupt:
        print("Ok Quitting")
        exit(-1)
    #play_again = new_hand()
    #if play_again:
    #pass
    #else:
    #break


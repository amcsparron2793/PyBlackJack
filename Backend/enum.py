from enum import Enum

class FaceCard(Enum):
    ACE = 1
    JACK = 11
    QUEEN = 12
    KING = 13

class GameStates(Enum):
    START = "START"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"

class CardValues(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


class CardSuits(Enum):
    HEART = '\u2661'
    DIAMOND = '\u2662'
    CLUB = '\u2667'
    SPADE = '\u2664'
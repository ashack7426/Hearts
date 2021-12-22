import pygame
from constants import *


class Card:
    def __init__(self, suit, rank):
        self.suits = ['H', 'S', 'D', 'C']
        self.ranks = ['2', '3', '4', '5', '6', '7',
                      '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.__suit = self.suits[suit]
        self.__rank = self.ranks[rank]

        self.__show = True

    def isHeart(self):
        if self.__suit == 'H':
            return True
        return False

    def show(self):
        return self.__show

    def hide(self):
        self.__show = False

    def reveal(self):
        self.__show = True

    def is2ofC(self):
        if self.__suit == 'C' and self.__rank == '2':
            return True
        return False

    def isQofS(self):
        if self.__suit == 'S' and self.__rank == 'Q':
            return True
        return False

    def getSuit(self):
        return self.__suit

    def getSuitIndex(self):
        suit = self.__suit
        return self.suits.index(suit)

    def getRank(self):
        return self.__rank

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__suit == other.__suit and self.__rank == other.__rank
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    # If postive then the first one has a higher rank
    # If negative then the second one has a lower rank
    def compareRanks(self, other):
        return self._getRankIndex() - other._getRankIndex()

    def _getRankIndex(self):
        rank = self.__rank
        return self.ranks.index(rank)

    def __str__(self):
        if self.__show:
            return self.__suit + self.__rank
        return '?'

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self._getRankIndex() < other._getRankIndex()

    """ def render(self, win, x, y):
        # Width and height need to be determined by screen size
        # lets do 3 to 2 so length of card is 3 and width is 2
        # the width of screen = 13 * card_width + 2 * card length
        # height of screen = 13 * card_width + 2 * card length
        # Screen is a box
        # 3/2 = card_length / card_width => card_length = 3/2 * card_width
        # Box size = 13 * card_Width + 3 * card_width = 16 * card width
        # card_Width = Box size / 16
        # card_length = card_width * 3/2 = 3/2 * (Box Size / 16) = 3 * BoxSize / 32
        font = pygame.font.Font(None, 25)
        color = None

        if self.__suit == 'H' or self.__suit == 'D':
            color = RED
        else:
            color = BLACK

        text = font.render(str(self), True, color)
        card_width = SIZE / 16
        card_length = 3 * SIZE / 32
        #pygame.draw.rect(win, WHITE, (x, y, card_width, card_length))
        win.blit(text, ((x + card_width) / 2, (y + card_length) / 2)) """

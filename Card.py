
from constants import *
import pygame, sys
from pygame.locals import *

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
    
    def draw(self,win,x,y):
        WHITE = (255,255,255)
        BLUE = (0,128,255)
        font = pygame.font.SysFont('Arial', 25)

        if(self.__show):
            pygame.draw.rect(win,WHITE,(x,y,50,80))
            color = (255,0,0)

            if(self.__suit == 'S' or self.__suit == 'C'):
                color = (0,0,0)
            win.blit(font.render(str(self), True, color), (x + 4,y + 20))
        else:
            pygame.draw.rect(win,BLUE,(x,y,50,80))
            win.blit(font.render(str(self), True, WHITE), (x + 4,y + 20))
        



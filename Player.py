from Card import Card


class Player:
    def __init__(self, startingHand, score, number):
        self.__score = score
        self.__hand = startingHand
        self.__cardsWon = []
        self.__number = number
        self.__prevScore = score
        self.__type = None  # Comp = 1, player = 2, unknown = 3
        self.__level = None
        self.__showCards = True
        self.__handLen = min(13, len(self.__hand))

        self.__playerknownHands = {
            1: [[], {'H': True,
                     'D': True,
                     'C': True,
                     'S': True}],
            2: [[], {'H': True,
                     'D': True,
                     'C': True,
                     'S': True}],
            -1: [[], {'H': True,
                      'D': True,
                      'C': True,
                      'S': True}],
            0: [[], {'H': True,
                     'D': True,
                     'C': True,
                     'S': True}]
        }

    # Only matters for players that arent unknown
    def getNumOfSuit(self, suit):
        cnt = 0

        for c in self.__hand:
            if c.getSuit() == suit:
                cnt += 1

        return cnt

    # Comp = 1, player = 2, unknown = 3
    def changeType(self, type):
        self.__type = type

    def getType(self):
        return self.__type

    def changeLevel(self, level):
        self.__level = level

    def getLevel(self):
        return self.__level

    def getHandLen(self):
        return self.__handLen

    def hideCards(self):
        self.__showCards = False

    def revealCards(self):
        self.__showCards = True

    def show(self):
        return self.__showCards

    def noOtherPlayerHas(self, suit):
        for key, val in self.__playerknownHands.items():
            if key != 0:
                val[1][suit] = False

    def getPlayerKnownHands(self, num, i):
        return self.__playerknownHands[num][i]

    def updatePlayerKnownHands(self, num, cards):
        self.__playerknownHands[num][0] = cards

    def addToWonCards(self, pile):
        for c in pile:
            self.__cardsWon.append(c)

    def clearCards(self):
        self.__hand = []
        self.__cardsWon = []

        self.__playerknownHands = {
            1: [[], {'H': True,
                     'D': True,
                     'C': True,
                     'S': True}],
            2: [[], {'H': True,
                     'D': True,
                     'C': True,
                     'S': True}],
            -1: [[], {'H': True,
                      'D': True,
                      'C': True,
                      'S': True}],
            0: [[], {'H': True,
                     'D': True,
                     'C': True,
                     'S': True}]
        }

        self.__handLen = 0

    def getPrevScore(self):
        return self.__prevScore

    def order_players_by_restrictions(self, possible_cards):
        nums = {}
        knownCards = []

        for key, val in self.__playerknownHands.items():
            if key != 0:
                if val[0]:
                    knownCards = val[0]

        for key, val in self.__playerknownHands.items():
            if key != 0:
                # Has cards
                cards = []

                for c in possible_cards:
                    cards.append(c)

                for c in knownCards:
                    cards.remove(c)

                # Put those cards at the start of the list
                if val[0]:
                    for c in knownCards:
                        cards.insert(0, c)

                for k, v in val[1].items():
                    if not v:
                        for c in cards:
                            if c.getSuit() == k:
                                cards.remove(c)

                # Go from key to player index
                index = (-1 + self.getNumber() + key) % 4
                nums[index] = cards

        nums_sorted = sorted(nums.items(), key=lambda item: len(item[1]))

        return nums_sorted

    def changeHandLen(self, num):
        self.__handLen = num

    def incrScore(self, incr):
        self.__prevScore = self.__score
        self.__score += incr

    def getScore(self):
        return self.__score

    # Not for unknown players
    def cntHeartsInHand(self):
        cnt = 0

        for c in self.__hand:
            if c.isHeart():
                cnt += 1

        return cnt

    def addCardToHand(self, card):
        self.__hand.insert(0, card)
        if self.__handLen < 13:
            self.__handLen += 1

    def removeCardFromHand(self, card, turn):
        for c in self.__hand:
            if c == card:
                self.__hand.remove(c)

                # This is for unknown players
                if turn + 1 == self.getNumber():
                    self.__handLen -= 1
                break

    def has2ofC(self):
        for c in self.__hand:
            if c.is2ofC():
                return True
        return False

    def hasQofS(self, pile):
        for c in pile:
            if c.isQofS():
                return True
        return False

    def changeHand(self, lst):
        self.__hand = lst
        self.__handLen = len(lst)

    def getHand(self):
        return self.__hand

    def getWonHand(self):
        return self.__cardsWon

    def getNumber(self):
        return self.__number

    def getCurrentScore(self):
        num = 0

        for c in self.__cardsWon:
            if c.isHeart():
                num += 1
            elif c.isQofS():
                num += 13

        return num

    def organizeHand(self, lst):
        hand = []
        QS = Card(1, 10)

        if self.hasQofS(lst):
            hand.append(QS)

        for i in range(4):
            suitGroup = []
            for c in lst:
                if c.getSuitIndex() == i and not c.isQofS():
                    suitGroup.append(c)

            sorted(suitGroup)
            for c in suitGroup:
                hand.append(c)

        return hand

    def __str__(self):
        txt = 'Player ' + str(self.__number) + ' stats:\n'
        txt += 'Player Level: ' + str(self.__level) + '\n'
        txt += 'Player Hand: ' + str(self.getHand()[:self.__handLen]) + '\n'
        txt += 'Hand Len: ' + str(self.__handLen) + '\n'
        txt += 'Player Cards Won this round: ' + str(self.getWonHand()) + '\n'
        txt += 'Player current Score: ' + str(self.getCurrentScore()) + '\n'
        txt += 'Player total Score: ' + str(self.getScore())
        return txt

    def __eq__(self, other):
        return self.__number == other.__number

    def __lt__(self, other):
        return self.__score + self.getCurrentScore() < other.__score +  other.getCurrentScore()

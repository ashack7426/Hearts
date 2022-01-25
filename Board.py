
from matplotlib.pyplot import show
from Card import Card
from Player import Player
import random
import numpy as np
from math import comb, fabs
from constants import *
import copy


class Board:
    def __init__(self, max):
        self.__deck = self.__initDeck()
        self.__round = -1
        self.__passNum = -1
        self.__pile = []
        self.__players = self.__initPlayers()
        self.__limit = max
        self.__cnt = 0
        self.__playerTurn = -1
        self.__brokeHearts = False
        self.maxCard = None
        self.__knownSuitsinGame = {
            'H': 13,
            'C': 13,
            'D': 13,
            'S': 13
        }

    def changePlayerTurn(self, turn):
        self.__playerTurn = turn

    def getDeck(self):
        return self.__deck

    def changePassNum(self, num):
        self.__passNum = num

    def getPassNum(self):
        return self.__passNum

    def getMCPass(self, player, max):
        pass_num = self.__passNum
        action_num = 10
        sims = 5

        # No Pass
        if pass_num == 3:
            # random number between 0 and 285 inclusive
            action = random.randint(0, 285)

            cc = self.prepassCards(
                self.__players[player].getNumber() - 1, action)

            return [action, cc]

        player_hand = self.__players[player].getHand()
        other_hands = []

        for c in self.__deck:
            if c not in player_hand:
                other_hands.append(c)

        max_action = 0
        max_reward = float('-inf')
        max_cards = []

        min_action = 0
        min_reward = float('inf')
        min_cards = []

        for action in range(action_num):
            # different action everytime
            action = random.randint(0, 285)
            cc = self.prepassCards(
                self.__players[player].getNumber() - 1, action)
            reward_avg = 0.0
            for _ in range(sims):
                # 100 different deck shuffles
                random.shuffle(other_hands)
                r = 0.0
                for _ in range(sims):
                    # 10 different test games
                    copy_game = copy.deepcopy(self)

                    # Change hands to other_hands
                    i = 0
                    for p in copy_game.__players:
                        if p.getNumber() != player + 1:
                            hand = []
                            for _ in range(13):
                                hand.append(other_hands[i])
                                i += 1

                            p.changeHand(hand)
                            p.changeType(2)  # Regular Human

                    cards = []
                    for p in copy_game.getPlayers():
                        if p.getNumber() != player + 1:
                            cards.append(copy_game.prepassCards(
                                p.getNumber() - 1, None))
                        else:
                            cards.append(copy_game.prepassCards(
                                p.getNumber() - 1, action))

                    copy_game.passCards(cards)

                    # Finish the Round
                    round_over = False
                    while not round_over:
                        round_over = copy_game.playCard(None)

                    r += copy_game.getReward(player)

                r /= sims

                reward_avg += r

            reward_avg /= sims
            print('Action: ' + str(action) + ' Average Reward: ' +
                  str(reward_avg) + ', ' + str(cc))

            if reward_avg > max_reward:
                max_reward = reward_avg
                max_action = action
                max_cards = cc

            if reward_avg < min_reward:
                min_reward = reward_avg
                min_action = action
                min_cards = cc

        if max:
            return [max_action, max_cards]
        return [min_action, min_cards]

    def mcRoundHelp(self, other_cards, player):
        done = False
        while not done:
            hands = []
            random.shuffle(other_cards)
            pp = self.__players[player]
            potentialCards = pp.order_players_by_restrictions(other_cards)
            players = []

            for k, v in potentialCards:
                p = self.__players[k]
                players.append(p)

                hand = []
                l = p.getHandLen()

                for c in v:
                    if len(hand) < l:
                        found = False
                        for lst in hands:
                            if c in lst:
                                found = True
                                break

                        if not found:
                            hand.append(c)
                    else:
                        break

                if len(hand) == l:
                    hands.append(hand)
                else:
                    break

            if len(hands) == 3:
                done = True

        for i in range(3):
            lst = hands[i]
            p = players[i]
            p.changeHand(lst)
            p.changeType(2)  # Change to human

    def getMCRound(self, player, max):
        not_in_others = []
        others = []
        sims = 5

        # Get all of the cards that the other players could have
        # For each player make a list of cards that they could have
        # Then starting with the player with the least amount of cards randomly choose n cards for them
        # Remove those cards chosen from the other 2 lists, start the process

        # (Is there anyway that makes this happen such that i have to redo this ? )
        # The first thing we know is that there is at least one way that this works
        # Does this process guareentee a solution ?

        # Well lets say that the lowest person has n different cards to chose from and they need x cards
        # then the next lowest person has n cards and another person has n cards as well
        # Each person needs x1, x2, and x3 cards when all the x are <= n
        # The first person takes x1 cards and the x1 cards are removed from the other piles leaving at worst
        # All of the other players have at least n - x1 cards in hand

        # At this point in time is it possible that we dont have enough cards ?
        # Wait but if the cards only show up in that persons hand then we should know idk this sounds like it should work to me
        # Just make a list of all the possible cards for each person while also giving them the guareenteed cards at the start

        for c in self.__players[player].getHand():
            not_in_others.append(c)

        for p in self.__players:
            for c in p.getWonHand():
                not_in_others.append(c)

        for c in self.__pile:
            not_in_others.append(c)

        for c in self.__deck:
            if c not in not_in_others:
                c.reveal()
                others.append(c)

        max_action = 0
        max_reward = float('-inf')
        valid = self.validCards(self.__players[player])

        min_action = 0
        min_reward = float('inf')

        if len(valid) == 1:
            return 0

        for action in range(len(valid)):
            # different action everytime
            reward_avg = 0.0
            print(action)

            for _ in range(sims):
                # 100 different deck shuffles
                random.shuffle(others)
                r = 0.0
                for _ in range(sims):
                    # 10 different test games
                    copy_game = copy.deepcopy(self)
                    copy_game.mcRoundHelp(others, player)
                    round_over = copy_game.playCard(action)

                    # Finish the round
                    # time_start = datetime.datetime.now()
                    while not round_over:
                        round_over = copy_game.playCard(None)
                        # if datetime.datetime.now() - time_start > datetime.timedelta(seconds=20):
                        # print('???????)

                    r += copy_game.getReward(player)

                r /= sims
                reward_avg += r

            reward_avg /= sims
            print('Average Reward: ' + str(reward_avg))

            if reward_avg > max_reward:
                max_reward = reward_avg
                max_action = action

            if reward_avg < min_reward:
                min_reward = reward_avg
                min_action = action

        if max:
            return max_action
        return min_action

    def __initDeck(self):
        cards = []

        for suit in range(4):
            for rank in range(13):
                c = Card(suit, rank)
                cards.append(c)

        return cards

    def __initPlayers(self):
        P1 = Player([], 0, 1)
        P2 = Player([], 0, 2)
        P3 = Player([], 0, 3)
        P4 = Player([], 0, 4)
        return [P1, P2, P3, P4]

    def getPlayers(self):
        return self.__players

    def getPlayerTurn(self):
        return self.__playerTurn

    def gameOver(self):
        for p in self.__players:
            if p.getScore() >= self.__limit:
                return True
        return False

    # only should be called at end of rounds
    def getReward(self, player):
        p = self.__players[player]
        rankedPlayers = sorted(self.__players)

        for i in range(4):
            if rankedPlayers[i] == p:
                break

        if not self.gameOver():
            return -1 * (p.getScore() + 100 * i)

        if p.getScore() == rankedPlayers[0].getScore():  # First place
            # Big bonus for winning
            # always postive
            return abs(self.__limit - p.getScore()) * 100000000
        else:
            return -1 * (self.__limit + p.getScore() + 100 * i) * 100000000

    def roundOver(self):
        if self.__cnt < 52:
            return False
        self.__resetRound()
        return True

    def __resetRound(self):
        self.__cnt = 0

        # Calc player scores
        scores = []
        for p in self.__players:
            scores.append(p.getCurrentScore())

        # Did a player shoot the moon?
        try:
            moon = scores.index(26)
            scores = [26, 26, 26, 26]
            scores[moon] = 0
        except ValueError:
            pass

        for i in range(4):
            self.__players[i].incrScore(scores[i])

        for j in range(4):
            self.__players[j].clearCards()

    # Shuffle the cards and pass out Cards
    def startRound(self):
        random.shuffle(self.__deck)
        others = []
        found = False
        i = 0

        for p in self.__players:
            if p.getType() != 3:  # Normal just add 13 cards
                while len(p.getHand()) < 13:
                    # make sure card isnt already in another hand
                    found2 = False
                    for pp in self.__players:
                        hand = pp.getHand()
                        if self.__deck[i] in hand:
                            found2 = True
                            break

                    if not found2:
                        p.addCardToHand(self.__deck[i])
                    i += 1
            else:
                found = True

        if found:  # Unknown Players exist
            while i < 52:
                found = False
                for p in self.__players:
                    if self.__deck[i] in p.getHand():
                        found = True
                        break

                if not found:
                    others.append(self.__deck[i])
                i += 1

            for p in self.__players:
                if p.getType() == 3:  # Unknown Player
                    for c in others:
                        p.addCardToHand(c)

        for p in self.__players:
            # Organize hands
            # Start with Queen of spades if available
            # Go over all hearts then spades then diamonds then clubs
            # Order by rank
            p.changeHand(p.organizeHand(p.getHand()))

            if p.getType() != 3 and p.has2ofC():
                self.__playerTurn = p.getNumber() - 1

        self.__brokeHearts = False
        self.maxCard = None
        self.__round += 1
        self.__playerTurn = -1
        self.__passNum = (self.__passNum + 1) % 4
        self.__knownSuitsinGame = {
            'H': 13,
            'C': 13,
            'D': 13,
            'S': 13
        }

    def startOfRound(self):
        for p in self.__players:
            if p.getHandLen() < 13:
                return False
        return True

    def getRankings(self, player):
        ranked = sorted(self.__players)
        ranks = []
        i = 1
        num = 0

        while i < 4:
            cnt = 1
            while ranked[i] == ranked[i-1]:
                cnt += 1
                i += 1

            for _ in range(cnt):
                ranks.append(num)

            num += cnt
            i += 1

        if len(ranks) < 4:
            ranks.append(num)

        for i in range(4):
            if ranked[i] == player:
                return ranks[i]

        return None

    def validCards(self, p):
        C2 = Card(3, 0)
        valid = []
        hand = p.getHand()

        if p.has2ofC():
            return [C2]

        cnt = 0
        for pp in self.__players:
            if pp.getType() == 3:
                cnt += 1

        if len(self.__pile) > 0:
            startCard = self.__pile[0]
        else:
            startCard = None

        if not startCard:
            # If hearts are broken then can start with anything
            if self.__brokeHearts:
                return hand
            # If hearts are not broken then cannot start with a heart card
            else:
                for c in hand:
                    if not c.isHeart():
                        valid.append(c)
                # Only had hearts in hand
                if not valid:
                    return hand
                return valid

        if p.getType() == 3:
            suit = startCard.getSuit()
            h = p.getPlayerKnownHands(0, 0)
            found = False

            for c in h:
                if c.getSuit() == suit:
                    found = True
                    break

            if found:
                for c in hand:
                    if c.getSuit() == suit:
                        valid.append(c)

            if len(valid) > 0:
                return valid
            return hand

        # Can only play cards with the same suit
        for c in hand:
            if c.getSuit() == startCard.getSuit():
                valid.append(c)

        # Do not have the suit
        if len(valid) == 0:
            # if startcard is 2C then no hearts or QS
            if startCard.is2ofC():
                for c in hand:
                    if not (c.isHeart() or c.isQofS()):
                        valid.append(c)

            elif not self.__brokeHearts:
                for c in hand:
                    if not c.isHeart():
                        valid.append(c)

            if len(valid) == 0:
                return hand

        return valid

    def getBoardState(self, p):
        state = []
        valid = self.validCards(p)
        maxCard = self.maxCard

        if maxCard:
            state.append(maxCard.getSuitIndex())
        else:
            state.append(4)

        state.append(p.getCurrentScore())
        state.append(p.getScore())

        # Num of hearts in hand
        state.append(p.cntHeartsInHand())

        # Has Queen of spades in hand
        if p.hasQofS(p.getHand()):
            state.append(1)
        else:
            state.append(0)

        # Have a same suit card with higher rank(2)
        found = False
        for c in valid:
            if not maxCard or (maxCard.compareRanks(c) < 0 and c.getSuit() == maxCard.getSuit()):
                state.append(1)
                found = True
                break

        if not found:
            state.append(0)

        # Have a same suit card with lower rank(2)
        found = False
        for c in valid:
            if maxCard and maxCard.compareRanks(c) > 0 and c.getSuit() == maxCard.getSuit():
                state.append(1)
                found = True
                break

        if not found:
            state.append(0)

        # Broke Hearts (2)
        if self.__brokeHearts:
            state.append(1)
        else:
            state.append(0)

        cards = []
        total = 0
        for suit in ['C', 'D', 'H', 'S']:
            num = 0
            for c in p.getHand():
                if c.getSuit() == suit:
                    num += 1

            total += num
            cards.append(num)

        cards.append(13 - total)
        ind = C135.index(tuple(cards))
        state.append(ind)

        return np.array(state)

    def getPassState(self, p):
        state = []
        pass_num = self.__passNum
        state.append(pass_num)

        # Has Queen of spades in hand
        if p.hasQofS(p.getHand()):
            state.append(1)
        else:
            state.append(0)

        # Num of hearts in hand
        state.append(p.cntHeartsInHand())

        # Player Score
        state.append(p.getScore())

        # Hand
        cards = []
        for suit in ['C', 'D', 'H', 'S']:
            num = 0
            for c in p.getHand():
                if c.getSuit() == suit:
                    num += 1

            cards.append(num)

        ind = C134.index(tuple(cards))
        state.append(ind)

        return np.array(state)

    def prepassCards(self, player, action):
        cards = []
        p = self.__players[player]

        if action == None:
            # Random Cards to pass to next person
            nums = random.sample(range(len(p.getHand())), 3)
            for n in nums:
                c = p.getHand()[n]
                cards.append(c)

        else:
            nums = self.__actionToNums(action)
            for n in nums:
                c = p.getHand()[n]
                cards.append(c)

        return cards

    def passCards(self, cards):
        pass_num = self.__passNum
        passArr = [1, -1, 2, 0]
        passing = passArr[pass_num]
        lst = []
        C2 = Card(3, 0)

        for i in range(4):
            for c in cards[i]:
                p = self.__players[i]
                next_p = self.__players[(i + passing) % 4]
                p.removeCardFromHand(c, -1)

                if c not in next_p.getHand():
                    if next_p.getType() != 3:  # Normal player
                        c.reveal()
                    next_p.addCardToHand(c)

                if next_p.getType() != 3:  # Normal player
                    lst.append(c)

                if p.getType() != 3:
                    if next_p.getType() != 3:  # normal to normal (remove those cards from all weird hands)
                        for pp in self.__players:
                            if pp.getType() == 3:
                                pp.removeCardFromHand(c, -1)

                    # normal to weird (remove from other weird hands)
                    else:
                        for pp in self.__players:
                            if pp != next_p and pp.getType() == 3:
                                pp.removeCardFromHand(c, -1)
                else:
                    # weird to normal (remove from all weird hands)
                    if next_p.getType() != 3:
                        for pp in self.__players:
                            if pp.getType() == 3:
                                pp.removeCardFromHand(c, -1)

                    # weird to weird (do not remove from any weird hands since we have no idea what cards they passed)
                    else:
                        if c not in p.getHand():
                            p.addCardToHand(c)

            if pass_num != 3:
                # if normal to normal update
                # if normal to weird update
                # if weird to normal update
                # if weird to weird do not update
                if p.getType() != 3 or next_p.getType() != 3:
                    p.updatePlayerKnownHands(passing, cards[i])

                    if next_p.getType() == 3:
                        next_p.updatePlayerKnownHands(0, cards[i])

        for p in self.__players:
            if len(p.getHand()) == 13:
                p.updatePlayerKnownHands(0, p.getHand())

        cnt = 0
        index = -1
        for p in self.__players:
            if (p.getType() != 3 or C2 in lst) and p.has2ofC():
                self.__playerTurn = p.getNumber() - 1
                break
            elif p.getType() == 3:
                cnt += 1
                index = p.getNumber() - 1

        # if the number of unknown humans is one then its just that guy
        if self.__playerTurn == -1 and cnt == 1:
            self.__playerTurn = index

        for p in self.__players:
            p.changeHandLen(13)

            if not p.show():
                for c in p.getHand():
                    c.hide()
                    pass

   # Action space & _action to number
    # Need a mapping of (x,y,z) such that 0 <= x < y < z <= 12
    # Go from number to mapping N = xC1 + yC2 + zC3

    def __actionToNums(self, action):
        for x in range(13):
            for y in range(x + 1, 13):
                for z in range(y + 1, 13):
                    num = comb(x, 1) + comb(y, 2) + comb(z, 3)

                    if num == action:
                        return [x, y, z]
        return []

    def numsToAction(self, x, y, z):
        return comb(x, 1) + comb(y, 2) + comb(z, 3)

    # 2 options either a card is being removed twice or more from a pile
    # Or a player is going 2 times during a round?

    def playCard(self, action):
        if self.roundOver():
            return True

        p = self.__players[self.__playerTurn]
        valid = self.validCards(p)

        # Random Action
        if action == None or action >= len(valid):
            card = random.choice(valid)
        # Specific Action
        else:
            card = valid[action]

        if card.isHeart():
            self.__brokeHearts = True

        # Add to pile
        card.reveal()
        self.__pile.append(card)
        # Remove From Hand
        p.removeCardFromHand(card, self.__playerTurn)
        self.__cnt += 1

        if len(p.getHand()) == 1:
            c = p.getHand()[0]
            for pp in self.__players:
                if p != pp and pp.getType() == 3:
                    pp.removeCardFromHand(c, self.__playerTurn)

            run = True
            while run:
                found = False
                for pp in self.__players:
                    if p != pp and pp.getHandLen() == 1:
                        c = pp.getHand()[0]

                        for ppp in self.__players:
                            if ppp != pp and ppp.getType() == 3 and c in ppp.getHand():
                                ppp.removeCardFromHand(c, self.__playerTurn)
                                found = True
                if not found:
                    run = False
        else:
            # The unknown human players
            for pp in self.__players:
                if pp.getType() == 3:
                    pp.removeCardFromHand(card, self.__playerTurn)

        # Decrement total Suit count
        self.__knownSuitsinGame[card.getSuit()] -= 1

        # Does it equal 0? No one has this suit anymore
        if self.__knownSuitsinGame[card.getSuit()] == 0:
            val = card.getSuit()

            for x in self.__players:
                # No other player has this suit
                x.noOtherPlayerHas(val)

        # If suit of card played is different from the startCard suit then everyone now knows that this player does not have that suit
        if self.maxCard and card.getSuit() != self.maxCard.getSuit():
            for pp in self.__players:
                num = p.getNumber() - pp.getNumber()
                if num != 0:
                    num = p.getNumber() - pp.getNumber()

                    if abs(num) == 2:
                        num = 2

                    if abs(num) == 3:
                        num /= -3

                    pp.getPlayerKnownHands(
                        num, 1)[self.maxCard.getSuit()] = False

            if p.getType() == 3:
                p.getPlayerKnownHands(
                    0, 1)[self.maxCard.getSuit()] = False

                lst = copy.deepcopy(p.getHand())
                for c in lst:
                    if c.getSuit() == self.maxCard.getSuit():
                        c.reveal()
                        p.removeCardFromHand(c, -2)
                        c.hide()

                unknowns = 0
                no_suits = 0
                found_player = None
                for pp in self.__players:
                    if pp.getType() == 3:
                        unknowns += 1

                        if not pp.getPlayerKnownHands(
                                0, 1)[self.maxCard.getSuit()]:
                            no_suits += 1

                        else:
                            found_player = pp

                if found_player and unknowns - no_suits == 1:
                    l = found_player.getPlayerKnownHands(
                        0, 0)

                    for c in found_player.getHand():
                        if c.getSuit() == self.maxCard.getSuit() and c not in l:
                            l.append(c)

                    found_player.updatePlayerKnownHands(0, l)

        # If the number of suits availble is equal to the number of suits that you have then you now know that nobody else has this suit
        if self.__knownSuitsinGame[card.getSuit()] > 0:
            val = self.__knownSuitsinGame[card.getSuit()]
            if val == p.getNumOfSuit(card.getSuit()) and p.getType() != 3:
                # No other player has this suit
                p.noOtherPlayerHas(card.getSuit())

        # Update Know Cards in Hand ?:
        pass_num = self.__passNum
        passArr = [1, -1, 2, 0]
        passing = passArr[pass_num]

        if passing != 0:
            # The guy that passed to this current player would be the one who is updating there player card knowledge
            # If passing is 1 then the guy who passed to me is (self.__playerTurn - 1) % 4
            # If passing is -1 then the guy who passed to me is (self.__playerTurn + 1) % 4
            # If passing is 2 then the guy who passed to me was (self.__playerTurn - 2) % 4
            player_that_passed_to_me = self.__players[(
                self.__playerTurn - passing) % 4]
            cards = player_that_passed_to_me.getPlayerKnownHands(
                passing, 0)

            if card in cards:
                cards.remove(card)

        # Is this card the new maxCard ?
        if not self.maxCard or (card.getSuit() == self.maxCard.getSuit() and card.compareRanks(self.maxCard) > 0):
            self.maxCard = card

        if len(self.__pile) == 4:
            # We have a certain turn at this point so in this case index 3 is self.__playerTurn

            for i in range(4):
                c = self.__pile[i]
                if c == self.maxCard:
                    self.__playerTurn = (self.__playerTurn + i + 1) % 4
                    # Add cards to hands won
                    p = self.__players[self.__playerTurn]
                    p.addToWonCards(self.__pile)
                    self.maxCard = None
                    self.__pile = []
                    break
        else:
            self.__playerTurn = (self.__playerTurn + 1) % 4

        return False

    def showGame(self):
        first_player = self.getPlayerTurn()
        pp = self.getPlayers()[first_player]

        # Show the cards in the other players hand
        pass_num = self.__passNum
        passArr = [1, -1, 2, 0]
        cards = []

        for j in passArr:
            if j != 0 and pp.getType() != 3:
                cards = pp.getPlayerKnownHands(j, 0)

                if len(cards) > 0:
                    p = self.getPlayers()[(first_player + j) % 4]
                    for cc in p.getHand():
                        if cc in cards:
                            cc.reveal()

        # 4 options

        # player knows hand (show on turn dont show anyother time)
        # player doesnt know hand (never show)
        # computer show hand (show all the time)
        # computer dont show hand (only show on turn)

        for i in range(4):
            turn = (first_player + i) % 4
            p = self.getPlayers()[turn]

            if p.getType() == 3:  # Unknown Player
                for c in p.getHand():
                    if c not in cards:
                        c.hide()

            # show my cards if show
            if p.show() or (pp == p and p.getType() != 3):  # if show card or pp is the current player
                for c in pp.getHand():
                    c.reveal()

            print(str(p))

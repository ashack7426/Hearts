from copy import deepcopy
from Board import Board
import random
import numpy as np
from tensorflow import keras
import copy
import pygame

from constants import SIZE, WHITE


# Passing does very little need to adjust this hand differently for passing

gameModel = keras.models.load_model('gameModel')
passModel = keras.models.load_model('passModel')


def getRoundAction(board, player, level):
    # Very easy: Min MC - 80% 4th, 10% 2nd, and 10% 3rd
    if level == 0:
        return board.getMCRound(player, 0)
    # Easy: Random - 25 % win rate
    elif level == 1:
        return None
    # Medium: 5/14 Max MC and 9/14 Random - 50% first, 18% second, 16% third and fourth (in theory)
    elif level == 2:
        num = random.randint(1, 14)

        # Random
        if num > 6:
            return None
        # Max MC
        else:
            return board.getMCRound(player, 1)

    # Hard: 17/27 Max MC and 10/27 Heart AI - 75% first, 13.5% second, 7.7% third, 3.7% last (in theory)
    elif level == 3:
        num = random.randint(1, 27)

        # Heart Ai
        if num > 10:
            state = list(board.getBoardState(board.getPlayers()[0]))
            state = np.array([[state]])
            obs = gameModel.predict(state)
            return (obs.argmax(axis=0))[0]

        # Max MC
        else:
            return board.getMCRound(player, 1)

    # Very Hard: Max MC - 95 % win rate 5% second place
    else:
        return board.getMCRound(player, 1)


def getPassAction(board, player, level):
    # Very easy: Min MC - 80% 4th, 10% 2nd, and 10% 3rd
    if level == 0:
        return board.getMCPass(player, 0)[0]
    # Easy: Random - 25 % win rate
    elif level == 1:
        return None
    # Medium: 5/14 Max MC and 9/14 Random - 50% first, 18% second, 16% third and fourth (in theory)
    elif level == 2:
        num = random.randint(1, 14)

        # Random
        if num > 6:
            return None
        # Max MC
        else:
            return board.getMCPass(player, 1)[0]

    # Hard: 17/27 Max MC and 10/27 Heart AI - 75% first, 13.5% second, 7.7% third, 3.7% last (in theory)
    elif level == 3:
        num = random.randint(1, 27)

        # Heart Ai
        if num > 10:
            state = list(board.getPassState(board.getPlayers()[0]))
            state = np.array([[state]])
            obs = passModel.predict(state)
            return (obs.argmax(axis=0))[0]

        # Max MC
        else:
            return board.getMCPass(player, 1)[0]

    # Very Hard: Max MC - 95 % win rate 5% second place
    else:
        return board.getMCPass(player, 1)[0]


def __addCards(b, i):
    # Do you know this guys hand?
    num_cards = int(input('How many cards do you know in this hand? (0-13): '))

    for j in range(num_cards):
        run = True

        while run:
            card = input('Card ' + str(j + 1) + ': ')

            found = False
            for c in b.getDeck():
                if str(c) == card and card != '?':
                    found = True
                    # insert card to hand
                    repeat = False
                    for pp in b.getPlayers():
                        hand = pp.getHand()
                        if c in hand:
                            repeat = True
                            print(
                                'Card is already in another hand. Try Again!')
                            break

                    if not repeat and found:
                        b.getPlayers()[i].addCardToHand(c)
                        run = False
                        break

            if not found:
                print('Not Valid Card. Try Again!')


def chooseSettings():
    board = Board(100)
    has_computers = False

    for i in range(4):
        print('Player ' + str(i + 1) + ':')
        choice = int(
            input('Press 0 computer, 1 for human, and 2 for unknown: '))

        if choice == 0:
            has_computers = True
            board.getPlayers()[i].changeType(1)

            # Choose diffuculty
            level = int(
                input('Press 0(very easy), 1(easy), 2(medium), 3(hard), 4(very hard): '))

            board.getPlayers()[i].changeLevel(level)
            __addCards(board, i)

        # Human player
        elif choice == 1:
            __addCards(board, i)
            board.getPlayers()[i].changeType(2)

        # Unknown Player
        else:
            board.getPlayers()[i].changeType(3)
            board.getPlayers()[i].hideCards()

    if has_computers:
        print('Do you want to show computer cards? ')
        choice = int(input('Press 1 for yes and 0 for no: '))

        # default is that they are shown
        if choice == 0:
            for p in board.getPlayers():
                if p.getType() == 1:  # is computer player
                    p.hideCards()

    return board


def playGame():
    board = chooseSettings()
    play = True
    pygame.init()
    win = pygame.display.set_mode([SIZE, SIZE])
    win.fill(WHITE)
    pygame.display.set_caption('Hearts')

    while play:
        pygame.display.update()
        b = copy.deepcopy(board)

        while not b.gameOver():
            b.startRound()
            if b.startOfRound():
                cards = []
                b.showGame()
                # Ask to change the pass
                print('What is the pass of this round?')
                passing = int(
                    input('0(left), 1(right), 2(across), 3(no pass), 4(default(' + str(b.getPassNum()) + ')): '))

                # change passing num
                if passing != 4:
                    b.changePassNum(passing)

                if passing != 0:
                    l = []
                    for p in b.getPlayers():
                        # Compute player
                        if p.getType() == 1:  # computer player
                            a = getPassAction(
                                b, p.getNumber() - 1, p.getLevel())
                            lst = b.prepassCards(
                                p.getNumber() - 1, a)

                            cards.append(lst)
                            print(lst)

                            for c in lst:
                                l.append(c)

                        # Player character
                        else:
                            if p.getType() == 2:  # Human Player
                                print('Player ' + str(p.getNumber()))

                                print('What is the first card you want to pass?')
                                print(str(p.getHand()))
                                card1 = int(input('Choose a card from 0-12: '))

                                print('What is the second card you want to pass?')
                                print(str(p.getHand()))
                                card2 = int(input('Choose a card from 0-12: '))

                                while card2 == card1:
                                    print(
                                        'Needs to be a different index. Try Again!')
                                    print(str(p.getHand()))
                                    card2 = int(
                                        input('Choose a card from 0-12: '))

                                print('What is the third card you want to pass?')
                                print(str(p.getHand()))
                                card3 = int(input('Choose a card from 0-12: '))

                                while card3 == card1 or card3 == card2:
                                    print(
                                        'Needs to be a different index. Try Again!')
                                    print(str(p.getHand()))
                                    card3 = int(
                                        input('Choose a card from 0-12: '))

                                # Go from 3 numbers to an action
                                a = b.numsToAction(card1, card2, card3)

                                lst = b.prepassCards(
                                    p.getNumber() - 1, a)

                                cards.append(lst)

                                for c in lst:
                                    l.append(c)

                            # Unknown player
                            else:
                                # Passing to a computer or a regular human
                                passArr = [1, -1, 2, 0]
                                passing = passArr[b.getPassNum()]
                                num = (p.getNumber() - 1 + passing) % 4
                                next_p = b.getPlayers()[num]

                                # next is normal human or computer
                                if next_p.getType() != 3:
                                    found = False
                                    while not found:
                                        lst = []
                                        print('You are Player ' +
                                              str(next_p.getNumber()))

                                        unknowns = []
                                        for c in p.getHand():
                                            if str(c) == '?':
                                                c.reveal()
                                                unknowns.append(c)

                                        for i in range(3):
                                            run = True
                                            while run:
                                                print(str(p.getHand()))
                                                c = input(
                                                    'Card ' + str(i + 1) + ' you got from the Player ' + str(p.getNumber()) + ': ')

                                                # is this a valid card?
                                                for cc in b.getDeck():
                                                    if str(cc) == c:
                                                        if cc in p.getHand() and cc not in lst and cc not in l:
                                                            lst.append(cc)
                                                            run = False
                                                            break

                                                if run:
                                                    print(
                                                        'Invalid Card. Try Again')

                                        cards.append(lst)
                                        for c in lst:
                                            l.append(c)
                                        found = True

                                        for c in p.getHand():
                                            if c in unknowns:
                                                c.hide()

                                # next_p is a unknown player
                                else:
                                    lst = b.prepassCards(
                                        p.getNumber() - 1, None)

                                    okay = False
                                    while not okay:
                                        found = False
                                        for c in lst:
                                            if c in l:
                                                lst = b.prepassCards(
                                                    p.getNumber() - 1, None)
                                                found = True
                                                break
                                        if not found:
                                            okay = True

                                    cards.append(lst)

                    print(cards)
                    b.passCards(cards)

                    for p in b.getPlayers():
                        print(str(p))

            # If more than 2 unknown_humans and the other players do not have the 2 of c
            if -1 == b.getPlayerTurn():
                lst = []
                for p in b.getPlayers():
                    if p.getType() == 3:  # Unknown Player
                        lst.append(p.getNumber() - 1)
                turn = int(input('Who has the 2C? ' + str(lst) + str(': ')))
                b.changePlayerTurn(turn)

            # Finish the Round
            round_over = False
            while not round_over:
                b.showBoard(win)
                turn = b.getPlayerTurn()
                p = b.getPlayers()[turn]
                print('Player ' + str(p.getNumber()) + ' turn:')
                b.showGame()

                if p.getType() == 1:  # Compute player
                    valid = b.validCards(p)
                    print('Player ' + str(p.getNumber()))
                    print('Valid Cards: ' + str(valid))
                    a = getRoundAction(b, turn, p.getLevel())
                    print(str(a))
                    round_over = b.playCard(a)

                # Human or unknown Player
                else:
                    valid = b.validCards(p)

                    for c in valid:
                        c.reveal()

                    print('Player ' + str(p.getNumber()))
                    print('Valid Cards: ' + str(valid))

                    if p.getType() == 3:  # Unknown Player
                        for c in valid:
                            c.hide()

                    a = None
                    # Only worry about this if theres more than 1 valid card to play
                    # For unknown human players their whole hand is valid since if there are more than 2,
                    # We do not know what their hand is
                    if len(valid) > 1:
                        card = input('What is the valid Card you want? ')

                        for i in range(len(valid)):
                            c = valid[i]
                            show = False

                            if not c.show():
                                c.reveal()
                                show = True

                            if str(c) == card:
                                a = i
                                break

                            if show:
                                c.hide()

                    print(str(a))
                    round_over = b.playCard(a)

            if not b.gameOver():
                b.showRankings(0, win)  # show current rankings
                for i in range(4):
                    p = b.getPlayers()[i]
                    hand = copy.deepcopy(board.getPlayers()[i].getHand())
                    p.changeHand(hand)

        # Do you want to play again, adjust settings, or quit
        rankedPlayers = sorted(b.getPlayers())
        for p in rankedPlayers:
            print(str(p))

        b.showRankings(1, win)  # show final rankings

        choice = int(
            input('Do you want to play again(1), adjust settings(2), or quit(3): '))

        if choice == 2:
            board = chooseSettings()
        elif choice == 3:
            play = False
            pygame.quit()
        else:
            random.shuffle(board.getDeck())


def main():
    playGame()


if __name__ == "__main__":
    main()


# Tests
# 4 normals (good) (done)
# 1 weird and 3 normals (good) (done)
# (2 weird humans + 2 normals) (good) (done)
# (3 weird humans 1 human) (good) (done)
# 4 weird humans (good) (done)

# 4 computers (good) (done)
# 3 computers + (1 normal or 1 weird) (good) (done)
# 2 computers + (2 normal or 2 weird or 1 of each) (nope)
# 1 computer + (1 normal & 2 weird or 2 normal & 1 weird or 3 normal or 3 weird) (nope)

# Make sure the scores add up to 26 where are the hearts ?
# add comments and organize
# post to git


# Play the game

# The pygame will just have these settings the toggle and a pass number at the start

# Players will see the valid cards


# Get this whole setup in the console then just add a gui to it


# The settings shoulh have 4 players

# Each player is either a human or computer
# If a player is a human then you can check ythe option of show hand or not
# This is meant so that if i am playing against malone or something then I can manually type in my cards
# If its a human and its show hand then before the game starts the human show players need to
# type in what their hands are at the start

# The other one is computer with 5 different diffculties


# At the start of each round I can also change the pass, the default will be the order but just in case it can change


# Min MC - 80% 4th, 10% 2nd, and 10% 3rd
# Random - 25 % win rate
# Bot - 41% 1st, 28 %second, 21% third, 10% 4th
# Max MC - 95 % win rate 5% second place

# Test bots and make guis
# Computer Levels:
# Very easy: Min MC - 80% 4th, 10% 2nd, and 10% 3rd
# Easy: Random - 25 % win rate
# Medium: 5/14 Max MC and 9/14 Random - 50% first, 18% second, 16% third and fourth (in theory)
# Hard: 17/27 Max MC and 10/27 Heart AI - 75% first, 13.5% second, 7.7% third, 3.7% last (in theory)
# Very Hard: Max MC - 95 % win rate 5% second place

from tensorflow import keras
from Board import Board
import numpy as np
import itertools

from constants import C134, C135
import matplotlib.pyplot as plt


def display_rankings(ranks, num_of_games):
    print('Number of times and percentage of time AI got each rank: ')

    for i in range(4):
        print(str(i + 1) + '. Number: ' +
              str(ranks[i]) + ' Percentage: ' + str(100 * ranks[i] / num_of_games) + '%')

    # Display Chart
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    placements = ['1st', '2nd', '3rd', '4th']
    percents = []

    for r in ranks:
        percents.append(r / num_of_games)

    ax.bar(placements, percents)
    plt.show()


def playGamewithAI(num_of_games):
    ranks = [0.0, 0.0, 0.0, 0.0]
    boardModel = keras.models.load_model('boardModel')
    passModel = keras.models.load_model('passModel')

    for i in range(num_of_games):
        board = Board(100)
        board.startRound()

        while not board.gameOver():

            # Pass Cards
            if board.startOfRound():
                cards = []
                for p in board.getPlayers():
                    # game.render()
                    if p.getNumber() != 1:
                        cards.append(board.prepassCards(
                            p.getNumber() - 1, None))
                    else:
                        state = list(board.getPassState(board.getPlayers()[0]))
                        state = np.array([[state]])
                        obs = passModel.predict(state)
                        a = (obs.argmax(axis=0))[0]
                        cards.append(board.prepassCards(p.getNumber() - 1, a))

                board.passCards(cards)
                # game.render()

            # Finish the Round
            round_over = False
            while not round_over:
                board.showBoard()
                turn = board.getPlayerTurn()
                # game.render()

                if turn != 0:
                    round_over = board.playCard(None)
                else:
                    state = list(board.getBoardState(board.getPlayers()[0]))
                    state = np.array([[state]])
                    obs = boardModel.predict(state)
                    a = (obs.argmax(axis=0))[0]
                    round_over = board.playCard(a)

        # Update Rankings
        # game.render()
        index = board.getRankings(board.getPlayers()[0])
        ranks[index] += 1
        print('Game ' + str(i + 1) + ' Over!')
        print(ranks)

    display_rankings(ranks, num_of_games)


def main():
    playGamewithAI(100)


if __name__ == "__main__":
    main()

""" 
def get13C5():
    perms = []

    for a in range(14):
        for b in range(14):
            for c in range(14):
                for d in range(14):
                    for e in range(14):
                        if a + b + c + d + e == 13:
                            p = list(itertools.permutations([a, b, c, d, e]))
                            p = list(set(p))  # Remove duplicates

                            for pp in p:
                                perms.append(pp)

    return perms


def get13C4():
    perms = []

    for a in range(14):
        for b in range(14):
            for c in range(14):
                for d in range(14):
                    if a + b + c + d == 13:
                        p = list(itertools.permutations([a, b, c, d]))
                        p = list(set(p))  # Remove duplicates

                        for pp in p:
                            perms.append(pp)

    return perms


file1 = open('C134.txt', "w")
file2 = open('C135.txt', "w")

file1.write(str(get13C4()))
file2.write(str(get13C5()))

file1.close()
file2.close()
 """

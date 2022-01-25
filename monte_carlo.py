
from Board import Board
import matplotlib.pyplot as plt
import random


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


def PlayWithMonteCarlo(num_of_games, max, player_num):
    ranks = [0.0, 0.0, 0.0, 0.0]

    for i in range(num_of_games):
        board = Board(100)

        while not board.gameOver():
            board.startRound()
            # Pass Cards
            if board.startOfRound():
                cards = []

                for p in board.getPlayers():
                    # game.render()
                    if p.getNumber() != player_num:
                        cards.append(board.prepassCards(
                            p.getNumber() - 1, None))
                    else:
                        a = board.getMCPass(0, max)
                        cards.append(board.prepassCards(
                            p.getNumber() - 1, a[0]))

                        if max:
                            print('Max Pass: ' +
                                  str(a[0]) + ', ' + str(a[1]))
                        else:
                            print('Min Pass: ' +
                                  str(a[0]) + ', ' + str(a[1]))

                board.passCards(cards)

            # Finish the Round
            round_over = False
            while not round_over:
                board.showBoard()
                turn = board.getPlayerTurn()
                # game.render()

                if turn != player_num - 1:
                    round_over = board.playCard(None)
                else:
                    a = board.getMCRound(0, max)
                    round_over = board.playCard(a)

                    if max:
                        print('Max Move: ' + str(a))
                    else:
                        print('Min Move: ' + str(a))

            rankedPlayers = sorted(board.getPlayers())
            for p in rankedPlayers:
                print(str(p))

        # Update Rankings
        index = board.getRankings(board.getPlayers()[0])
        ranks[index] += 1
        print('Game ' + str(i + 1) + ' Over!')
        print(ranks)

    display_rankings(ranks, num_of_games)


def main():
    PlayWithMonteCarlo(10, 1, 1)


if __name__ == "__main__":
    main()

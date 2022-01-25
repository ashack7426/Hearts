
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


# Last things
# Why does it randoming pause for long times sometimes (investigate with time function)
# IF it is taking more then this amount of time then do something check


# Geneal Notes
# Add better print statements with max reward score and ones checked
# Make each round check on average be 5 seconds or less
# Try to make pass check less than 20 seconds

# Pass Notes
# Limit pass action checks (can cut down on combos since some permutations are the same) (done)
# Since there are so many different combos at the start (39C13 + 26C13 + 13C13 = 8132826045 different combos)
# if for each possible pass we run 10k different combos 1k times then the percentage of combos we cover is .03%
# Thus the chance of getting a repeat combo is so low we might as well not check if it is a repeat
# With no pass the passing bot doesnt need to be checked (done)

# Round Notes
# if only 1 card left no point in doing any of this (done)
# Only check valid options (done)
# We also know 3 cards that are next person has with the pass (done)


# Can get information about whether a player has clubs or diamonds or hearts or spades (done)
# Check the updates for the suits then try to implement in the combos (done)


# Check min of (100, number of possible combos of opponents) (this might just be overenginered at this point ? )
# Monte Carlo is nice since its random i wont contiye


# Max MC Win Rates:
# 95 % is 1st place and 5 % 2nd place

# Min MC win Rates:
#


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

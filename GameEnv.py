
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam


from gym.spaces.multi_discrete import MultiDiscrete
from Board import Board
from gym import Env
from gym.spaces import Discrete, MultiDiscrete
import numpy as np

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory


class BoardEnv(Env):
    def __init__(self):
        self.board = Board(100)

        # Actions are just play cards 1-13:
        self.action_space = Discrete(13)

        # Starting suit (5 vals)
        # Current game Score (0-25)
        # Total player score (0-max-1)

        # Number of hearts? (14 vals)
        # Has queen of spades in hand (2 vals)
        # Have a same suit card with higher rank(2)
        # Have a same suit card with lower rank(2)
        # Broke Hearts (2)
        # Number of Cards in Hand (clubs, diamonds, hearts, spades, None(could have less than 13 cards in hand))
        self.observation_space = MultiDiscrete(
            [5, 26, 100, 14, 2, 2, 2, 2, 141300])

        # play a trick?
        # Deal out all cards no passing in this
        # Play game until we get to P1
        self.board.startRound()

        cards = []
        for p in self.board.getPlayers():
            cards.append(self.board.prepassCards(p.getNumber() - 1, None))

        self.board.passCards(cards)

        # Somehow figire out what the state is at this point
        self.state = self.board.getBoardState(self.board.getPlayers()[0])

    def step(self, action):
        info = {}
        done = False
        # self.game.displayGame(False)

        if self.board.gameOver():
            done = True
            self.state = self.board.getBoardState(self.board.getPlayers()[0])
            reward = self.board.getReward(0)
            return self.state, reward, done, info

        turn = self.board.getPlayerTurn()

        while turn != 0:
            self.board.playCard(None)
            # self.game.displayGame(False)
            turn = self.board.getPlayerTurn()

        self.state = self.board.getBoardState(self.board.getPlayers()[0])
        self.board.playCard(action - 1)
        reward = self.board.getReward(0)
        return self.state, reward, done, info

    def render(self):
        self.board.showBoard()

    def reset(self):
        self.board = Board(100)
        self.board.startRound()

        cards = []
        for p in self.board.getPlayers():
            cards.append(self.board.prepassCards(p.getNumber() - 1, None))

        self.board.passCards(cards)

        # Somehow figire out what the state is at this point
        self.state = self.board.getBoardState(self.board.getPlayers()[0])
        return self.state


def build_model(actions):
    model = Sequential()
    model.add(Dense(24, activation='relu', input_shape=(1, 9)))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    model.add(Flatten(input_shape=(1, 1, 13)))
    return model


def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=50000, target_model_update=1e-2)
    return dqn


def main():
    env = BoardEnv()
    print(env.action_space.sample())
    print(env.observation_space.sample())
    episodes = 10

    for ep in range(1, episodes + 1):
        state = env.reset()
        done = False
        score = 0
        final_score = 0

        while not done:
            action = env.action_space.sample()
            n_state, reward, done, info = env.step(action)
            score += reward
            final_score = reward

        print('Episode: {} Score {} Final Score {} '.format(ep, score, final_score))

    states = env.observation_space.shape
    actions = env.action_space.n

    print(states)
    print(actions)

    boardModel = build_model(actions)
    boardModel.summary()

    dqn = build_agent(boardModel, actions)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])

    dqn.fit(env, nb_steps=1000000, visualize=False,
            verbose=1)
    scores = dqn.test(env, nb_episodes=100, visualize=False)
    print(np.mean(scores.history['episode_reward']))

    boardModel.save('boardModel', overwrite=True)
    state = env.observation_space.sample().reshape((1, 1, 9))
    print(state)
    print(boardModel.predict(state))


if __name__ == "__main__":
    main()

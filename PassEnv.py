from tensorflow import keras
import numpy as np
from gym import Env
from gym.spaces import Discrete, MultiDiscrete
from Board import Board


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory


class PassEnv(Env):
    def __init__(self):
        self.boardModel = keras.models.load_model('boardModel')
        self.board = Board(100)

        # play a trick?
        # Deal out all cards no passing in this
        # Play game until we get to P1
        self.board.startRound()

        # Pass_num
        # Has Queen of Spades
        # Number of Hearts
        # Player total score
        # Number of Cards in Hand (clubs, diamonds, hearts, spades)
        self.observation_space = MultiDiscrete([4, 2, 14, 100, 9728])
        self.action_space = Discrete(286)
        self.state = self.board.getPassState(self.board.getPlayers()[0])

    def step(self, action):
        info = {}
        done = False

        if self.board.gameOver():
            done = True
            reward = self.board.getReward(0)
            self.state = self.board.getPassState(self.board.getPlayers()[0])
            return self.state, reward, done, info

        # Pass Cards
        if self.board.startOfRound():
            cards = []
            for p in self.board.getPlayers():
                if p.getNumber() != 1:
                    cards.append(self.board.prepassCards(
                        p.getNumber() - 1, None))
                else:
                    cards.append(self.board.prepassCards(
                        p.getNumber() - 1, action))
            self.board.passCards(cards)

        # Finish the Round
        round_over = False
        while not round_over:
            turn = self.board.getPlayerTurn()

            if turn != 0:
                round_over = self.board.playCard(None)
            else:
                state = list(self.board.getBoardState(
                    self.board.getPlayers()[0]))
                state = np.array([[state]])
                obs = self.boardModel.predict(state)
                a = (obs.argmax(axis=0))[0]
                round_over = self.board.playCard(a)

        self.state = self.board.getPassState(self.board.getPlayers()[0])
        reward = self.board.getReward(0)
        return self.state, reward, done, info

    def render(self):
        pass

    def reset(self):
        # play a trick?
        # Deal out all cards no passing in this
        # Play game until we get to P1
        self.board = Board(100)
        self.board.startRound()
        self.state = self.board.getPassState(
            self.board.getPlayers()[0])

        return self.state


def build_model(actions):
    model = Sequential()
    model.add(Dense(24, activation='relu', input_shape=(1, 5)))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    model.add(Flatten(input_shape=(1, 1, 13)))
    return model


def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=10000, target_model_update=1e-2)
    return dqn


def main():
    env = PassEnv()

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

    passModel = build_model(actions)
    passModel.summary()

    dqn = build_agent(passModel, actions)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])

    dqn.fit(env, nb_steps=100000, visualize=False,
            verbose=1)
    scores = dqn.test(env, nb_episodes=100, visualize=False)
    print(np.mean(scores.history['episode_reward']))

    passModel.save('passModel', overwrite=True)
    state = env.observation_space.sample().reshape((1, 1, 5))
    print(state)
    print(passModel.predict(state))


if __name__ == "__main__":
    main()

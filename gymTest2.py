import gym
import numpy as np

env = gym.make("MountainCar-v0")
env.reset()

LEARNING_RATE = 0.1
DISCOUNT = 0.95  # how much we value future actions over current
EPISODES = 25000

SHOW_EVERY = 2000

print(env.observation_space.high)  # print maximum position, velocity
print(env.observation_space.low)  # print minimum position, velocity
print(env.action_space.n)

DISCRETE_OS_SIZE = [20] * len(
    env.observation_space.high)  # these determine the number of discrete values within a range
discrete_os_win_size = (env.observation_space.high - env.observation_space.low) / DISCRETE_OS_SIZE

print(discrete_os_win_size)  # these are the step sizes

epsilon = 0.5  # higher number --> more random
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES // 2 # double div = type 2 division to an integer.

epsilon_decay_value = epsilon/(END_EPSILON_DECAYING - START_EPSILON_DECAYING)

q_table = np.random.uniform(low=-2, high=0, size=(DISCRETE_OS_SIZE + [env.action_space.n]))  # 20 x 20 x 3

ep_rewards = []
aggr_ep_rewards = {'ep': [], 'avg': [], 'min': [], 'max': []}

print(q_table.shape)


def get_discrete_state(state):
    discrete_state = (state - env.observation_space.low) / discrete_os_win_size
    return tuple(discrete_state.astype(np.int))


discrete_state = get_discrete_state(env.reset())

print(discrete_state)

print(np.argmax(q_table[discrete_state]))  # get the action value, by selecting the index with the maximum q value

'''
done = False

while not done:
    action = 2  # Push it right
    new_state, reward, done, _ = env.step(action)  # state is position and velocity
    print(new_state)
    env.render()

env.close()
'''
for episode in range(EPISODES):
    if episode % SHOW_EVERY == 0:
        print(episode)
        render = True
    else:
        render = False
    discrete_state = get_discrete_state(env.reset())
    done = False

    while not done:
        if np.random.random() > epsilon:
            action = np.argmax(q_table[discrete_state])  #
        else:
            action = np.random.randint(0, env.action_space.n)
        new_state, reward, done, _ = env.step(action)  # state is position and velocity
        new_discrete_state = get_discrete_state(new_state)
        env.render()
        if render:  # rendering environment is really slow, so render every 2000
            env.render()
        if not done:
            max_future_q = np.max(q_table[new_discrete_state])
            current_q = q_table[discrete_state + (action,)]  # access the q-value entry from the 3D array
            new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
            q_table[discrete_state + (action,)] = new_q  # update the q_table with the new q value
        elif new_state[0] >= env.goal_position:
            print(f"We made it on episode {episode}")
            q_table[discrete_state + (action,)] = 0  # if it reaches goal, then the reward is 0

        discrete_state = new_discrete_state

    if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
        epsilon -= epsilon_decay_value

env.close()

# DQN load and play
# coded by St.Watermelon

import gym
import numpy as np
import tensorflow as tf
from dqn_learn import DQNagent

def main():

    #env_name = 'CartPole-v1'
    #env = gym.make(env_name)
    agent = DQNagent()

    agent.load_weights('./save_weights/')

    time = 0
    state = DQNagent.reset()

    while True:
        qs = agent.dqn(tf.convert_to_tensor([state], dtype=tf.float32))
        action = np.argmax(qs.numpy())

        state, reward, done, _ = env.step(action)
        time += 1

        print('Time: ', time, 'Reward: ', reward)

        if done:
            break

    

if __name__=="__main__":
    main()
import random
import config as cf
import gym
import scenario as sc
env_name = 'CartPole-v1'
env = gym.make(env_name)
print(env.env.__dict__)


print(len(sc.emBB))
print(sc.emBB[random.randrange(0,len(sc.emBB))].__dict__)

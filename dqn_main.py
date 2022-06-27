# DQN main
# coded by St.Watermelon

from dqn_learn import DQNagent
import config as cf
def main():

    max_episode_num = 50
    agent = DQNagent()
    agent.train(max_episode_num)
    agent.plot_result()
    agent.plot_cache_hit_result()
if __name__=="__main__":
    main()
    
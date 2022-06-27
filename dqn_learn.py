from distutils import core
from importlib.resources import path
from platform import node
from queue import Empty
from turtle import shape
from typing import List
from sympy import beta

from torch import dropout

import network as nt
import config as cf
import content as ct
import scenario as sc

from gym.spaces import Discrete, Box
from replaybuffer import ReplayBuffer
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt

import random

# Qnetwork
class DQN(Model):

    def __init__(self, action_n, state_dim):
        super(DQN, self).__init__()

        self.h1 = Dense(3 * state_dim, activation='relu')
        self.d1 = Dropout(rate = 0.2)
        self.h2 = Dense(9 * state_dim, activation='relu')
        self.d2 = Dropout(rate = 0.2)
        self.h3 = Dense(6 * state_dim, activation='relu')
        self.d3 = Dropout(rate = 0.2)
        self.h4 = Dense(2 * state_dim, activation='relu')
        self.d4 = Dropout(rate = 0.2)
        self.h5 = Dense(state_dim, activation='relu')
        self.q = Dense(action_n, activation='linear')

    def call(self, x):
        x = self.h1(x)
        x = self.d1(x)
        x = self.h2(x)
        x = self.d2(x)
        x = self.h3(x)
        x = self.d3(x)
        x = self.h4(x)
        x = self.d4(x)
        x = self.h5(x)
        q = self.q(x)
        return q


class DQNagent():

    def __init__(self):

        self.network = nt.Network()
        # state 정의
        # 1. DataCenter 가용 캐시 자원의 크기
        # 2. BS 가용 캐시 자원의 크기
        # 3. MicroBS 가용 캐시 자원의 크기

        # 4번부터는 나중에
        # 4. 서비스의 요청 빈도

# !       self.DataCenter_AR = self.get_AR("DataCenter")
# !       self.BS_AR = self.get_AR("BS")
# !       self.MicroBS_AR = self.get_AR("MicroBS")

        # BackBone 인 Data Center 에는 다 있다고 가정?
        # [path 중 Mirco Base Station에 저장, path 중 Base Station에 저장,DataCenter에 저장]
        self.action_space = Discrete(3)
        self.observation_space = Box(-1,1,shape=(3,))
        #self.actions = [1,2,3]
        self.action_n = 3
        # path는 [node, Micro BS, BS, Data center, Core Internet]
        self.path = []

        # state 서비스의 종류, 서비스의 요청 빈도, 캐시 가용 자원 크기
        # ! 각각의 BS의 캐쉬 가용 크기로 바꾸기
        # ! 입력되는 컨텐츠의 카테고리
        # ! 입력되는 요일(Round%7)
        # ! 독립 : 각  BS의 가용캐쉬 , 1. 컨테츠 카테고리 2. 입력되는 요일
        self.round_nb = 0
        self.round_day = 0
        self.state:np.array = self.set_state()
        #print("init 안에서의 self.state")
        #print(self.state)
        self.state_dim = self.state.shape[0]
        self.action_size = 3
    
        # DQN 하이퍼파라미터
        self.GAMMA = 0.95
        self.BATCH_SIZE = 4 #64
        self.BUFFER_SIZE = 20000
        self.DQN_LEARNING_RATE = 0.001
        self.TAU = 0.001
        self.EPSILON = 1.0
        self.EPSILON_DECAY = 0.995
        self.EPSILON_MIN = 0.01
        self.train_start = 100          # 학습을 시작하기 전 데이터를 얻을 횟수

        ## create Q networks
        self.dqn = DQN(self.action_n, self.state_dim)
        self.target_dqn = DQN(self.action_n, self.state_dim)

        self.dqn.build(input_shape=(None, self.state_dim))
        self.target_dqn.build(input_shape=(None, self.state_dim))

        self.dqn.summary()

        # optimizer
        self.dqn_opt = Adam(self.DQN_LEARNING_RATE)

        ## initialize replay buffer
        self.buffer = ReplayBuffer(self.BUFFER_SIZE)

        # save the results
        self.save_epi_reward = []
        self.save_epi_hit = []
        # ADAM
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=self.DQN_LEARNING_RATE)
        self.steps = 0
        self.memory = deque(maxlen = 10000)

        # reward parameter
        self.a = 0.01
        self.b = 0.01
        self.d_core = 0
        self.d_cache = 0
        self.R_cache = 0
        self.H_arg = 0
        self.c_node = 0
        self.stored_type = 0
        self.stored_nodeID = 0
        self.alpha_redundancy = 0
        self.beta_redundancy = 0

        # Done 조건 action이 7000번 일어나면 끝
        self.stop = 7000
        
        
        # cache hit count ==> network.py에 넣어야할지도 모름
        self.cache_hit_cnt = 0

        # epi 별 result.txt 에 출력
        self.result_file = open("result.txt",'a')

    def reset(self):
        self.network = nt.Network()

        # state 함수 안에 round_day를 가져오는 
        self.round_nb = 0
        self.state = self.set_state()
        self.cache_hit_cnt = 0
        return self.state

    def set_state(self):
        
        # TODO : 각 microBS, BS, DataCenter 에 해당하는 가용 캐시 크기 구함.  shape()
        state = []

        # network.py 에서 round_day 도 state에 추가할 예정
        # 그러면 step 함수 전에 빼와야함
        round_day =  self.network.days[self.round_nb] % 7
        state.append(round_day)

        # MicroBS
        for i in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):
            state.append(cf.microBS_SIZE - self.network.microBSList[i].storage.stored)

        # BS
        for i in range(cf.NUM_BS[0]*cf.NUM_BS[1]):
            state.append(cf.BS_SIZE - self.network.BSList[i].storage.stored)

        # DataCenter
        state.append(cf.CENTER_SIZE - self.network.dataCenter.storage.stored)

        state = np.array(state)
        return state
        
        
    def memorize(self, state, action, reward, next_state, done):

        self.memory.append(state,action,reward,next_state, done)

    def choose_action(self, state):
        
        #print("choose_action 들어옴")
        if np.random.random() <= self.EPSILON:
            action = self.action_space.sample()
            #print(action)
            return action
        else:
            qs = self.dqn(tf.convert_to_tensor([state],dtype=tf.float32))
            #print("qs : {}".format(qs))
            #Fprint("np.argmax(qs.numpy()) : {}".format(np.argmax(qs.numpy())))
            return np.argmax(qs.numpy())
        
    def update_target_network(self, TAU):
        phi = self.dqn.get_weights()
        #print("phi : {}".format(phi))
        target_phi = self.target_dqn.get_weights()

        for i in range(len(phi)):
            target_phi[i] = TAU * phi[i] + (1 - TAU) * target_phi[i]
        self.target_dqn.set_weights(target_phi)

    def dqn_learn(self, state, actions, td_targets):
        #print("dqn learn 들어옴")
        with tf.GradientTape() as tape:
            one_hot_actions = tf.one_hot(actions, self.action_n)
            #print(one_hot_actions)

            q = self.dqn(state, training=True)
            #print(q)
            q_values = tf.reduce_sum(one_hot_actions * q, axis=1, keepdims=True)
            loss = tf.reduce_mean(tf.square(q_values-td_targets))
        #print("dqn 계산 끝남")
        grads = tape.gradient(loss, self.dqn.trainable_variables)
        self.dqn_opt.apply_gradients(zip(grads, self.dqn.trainable_variables))

    def td_target(self, rewards, target_qs, dones):
        #print("td_target 진입")
        max_q = np.max(target_qs, axis=1, keepdims=True)
        y_k = np.zeros(max_q.shape)
        for i in range(max_q.shape[0]): # number of batch
            if dones[i]:
                y_k[i] = rewards[i]
            else:
                y_k[i] = rewards[i] + self.GAMMA * max_q[i]

        #print("td_target 나감")
        ##print(y_k)
        return y_k
    
    ## load actor weights
    def load_weights(self, path):
        self.dqn.load_weights(path + 'networkSIM_dqn.h5')

    def step(self, action):
        #print("step function 안에 들어옴")
        
        # 이제 여기서 요청 시작 {노드, 요청한 컨텐츠}
        # @ round_day 를 state 로 빼야함 
        # @ reset 할 때 고려
        round_day =  self.network.days[self.round_nb] % 7
        requested_content, path = self.network.request_and_get_path(round_day)
        
        if len(path) < 5:
            self.cache_hit_cnt += 1
            # 요청들어온 컨테츠가 이미 storage에 있을 때 뒤로 빼줌.
            ct.updatequeue(path,requested_content,self.network.microBSList,self.network.BSList,self.network.dataCenter)
            
        # ! act paratmeter : nodeID, requested_content, action
        #print("act 실행")

        if len(path) >= 4:
            self.stop = self.stop - 1
            self.act(path, requested_content, action)

        #! 종료 시점 언제 알려줄지도 수정
        # @ round_day 가 state에 포함되기 때문에 
        # @ next_state 를 구하기 전에 올려줌
        if self.stop != 0:
            self.round_nb += 1
            done = False
        else:
            print("7000번 action 실행")
            done = True
            self.stop = 7000
            self.round_nb = 0


        next_state = self.set_state()

        reward = self.get_reward(path, requested_content)

        return next_state, reward, done

    ## train the agent
    def train(self, max_episode_num):

        # initial transfer model weights to target model network
        self.update_target_network(1.0)

        for ep in range(int(max_episode_num)):

            # reset episode
            time, episode_reward, done = 0, 0, False
            # reset the environment and observe the first state
            #print("reset?")
            state = self.reset()

            #print("reset 직후 state : {}".format(state))
            while not done:
                # visualize the environment
                #self.env.render()
                # pick an action
                action = self.choose_action(state)
                #print("choose_action 끝")
                # observe reward, new_state
                #print("state : {}".format(state))
                next_state, reward, done = self.step(action)
                #print("next_state : {}".format(next_state))
                train_reward = reward + time*0.01

                # add transition to replay buffer
                self.buffer.add_buffer(state, action, train_reward, next_state, done)

                if self.buffer.buffer_count() > cf.MAX_ROUNDS * 0.1:  # start train after buffer has some amounts

                    # decaying EPSILON
                    if self.EPSILON > self.EPSILON_MIN:
                        self.EPSILON *= self.EPSILON_DECAY
                    
                    # sample transitions from replay buffer
                    states, actions, rewards, next_states, dones = self.buffer.sample_batch(self.BATCH_SIZE)
                    
                    # predict target Q-values
                    target_qs = self.target_dqn(tf.convert_to_tensor(next_states, dtype=tf.float32))

                    # compute TD targets
                    y_i = self.td_target(rewards, target_qs.numpy(), dones)

                    self.dqn_learn(tf.convert_to_tensor(states, dtype=tf.float32), actions, tf.convert_to_tensor(y_i, dtype=tf.float32))
                    
                    # update target network
                    self.update_target_network(self.TAU)


                # update current state
                state = next_state
                episode_reward += reward
                time += 1
                #print(time)

            ## display rewards every episode
            cache_hit = self.cache_hit_cnt/cf.MAX_ROUNDS
            print('Episode: ', ep+1, 'Time: ', time, 'cache_hit : ', cache_hit,'Reward: ', episode_reward)
            self.write_result_file(ep = ep, time = time, cache_hit = cache_hit, episode_reward = episode_reward)
            self.save_epi_reward.append(episode_reward)
            self.save_epi_hit.append(cache_hit)

            self.result_file
            ## save weights every episode
            self.dqn.save_weights("./save_weights/cacheSIM_dqn.h5")

        np.savetxt('./save_weights/cacheSIM_epi_reward.txt', self.save_epi_reward)
        np.savetxt('./save_weights/cacheSIM_epi_hit.txt', self.save_epi_hit)


    ## save them to file if done
    def plot_result(self):
        plt.plot(self.save_epi_reward)
        plt.savefig('rewards.png')
        plt.show()

    ## save them to file if done
    def plot_cache_hit_result(self):
        plt.plot(self.save_epi_hit)
        plt.savefig('cache_hit.png')
        plt.show()

    def write_result_file(self, ep, time, cache_hit, episode_reward):
        self.result_file.write('Episode: ')
        self.result_file.write(str(ep+1))
        self.result_file.write(' Time: ')
        self.result_file.write(str(time))
        self.result_file.write(' cache_hit : ')
        self.result_file.write(str(cache_hit))
        self.result_file.write(' Reward: ')
        self.result_file.write(str(episode_reward))
        self.result_file.write('\n')


    def act(self, path, requested_content, action):

        # TODO : Path 에서 requested_contents 를 MicroBS, BS, DataCenter 중 어디에 넣을지
        # requested_content, path

        # path [0,0]
        # path [0,0,0]
        # path [0,0,0,0]
        # path [0,0,0,0,0]
        # 이런식으로 나와도 그냥 전체 path를 구해서
        # Core Network 까지 늘린담에
        # path[1], path[2], path[3] 중 어디에 넣을건지
        #print("act 함수 들어옴")
        requested_content:ct.Content = requested_content
        path = path
        # !MicroBS 에 저장 ---> 꽉차있으면 앞에꺼(가장 업데이트가 안된 컨텐츠) 하나 지움
        # !삭제는 추후 Gain 에 의해서 delete
        if action == 0:
            
            # get_c_node 에 쓰일 변수
            self.stored_type = 0
            self.stored_nodeID = path[1]

            # 저장이 되어 있나? -> 저장할 공간이 있나? -> 1. 저장. / 2. 삭제 후 저장.
            if self.network.microBSList[path[1]].storage.isstored(requested_content) != 1:
                if self.network.microBSList[path[1]].storage.abletostore(requested_content):
                    self.network.microBSList[path[1]].storage.addContent(requested_content)
                else:
                    #! content.py -> delFirstStored 사용하자.
                    del_content = self.network.microBSList[path[1]].storage.storage[0]
                    self.network.microBSList[path[1]].storage.delContent(del_content)
                    self.network.microBSList[path[1]].storage.addContent(requested_content)

        # BS 에 저장 ---> 꽉차있으면 앞에꺼 하나 지움
        if action == 1:
            
            # get_c_node 에 쓰일 변수
            self.stored_type = 1
            self.stored_nodeID = path[2]

            if self.network.BSList[path[2]].storage.isstored(requested_content) != 1:
                if self.network.BSList[path[2]].storage.abletostore(requested_content):
                    self.network.BSList[path[2]].storage.addContent(requested_content)
                else:
                    del_content = self.network.BSList[path[2]].storage.storage[0]
                    self.network.BSList[path[2]].storage.delContent(del_content)
                    self.network.BSList[path[2]].storage.addContent(requested_content)

        # DataCenter 에 저장 ---> 꽉차있으면 앞에꺼 하나 지움
        if action == 2:

            # get_c_node 에 쓰일 변수
            self.stored_type = 2
            self.stored_nodeID = path[3]

            if self.network.dataCenter.storage.isstored(requested_content) != 1:
                if self.network.dataCenter.storage.abletostore(requested_content):
                    self.network.dataCenter.storage.addContent(requested_content)
                else:
                    del_content = self.network.dataCenter.storage.storage[0]
                    self.network.dataCenter.storage.delContent(del_content)
                    self.network.dataCenter.storage.addContent(requested_content)

        #update
        # ! self.get_AR("DataCenter")
        # ! self.get_AR("BS")
        # ! self.get_AR("MicroBS")
        # self.state = 
        #print("action : " + str(action))


    def get_reward(self, path, requested_content):
        """
        Return the reward.
        The reward is:
        
            Reward = a*(d_core - d_cache) - b*(#ofnode - coverage_node)

            a,b = 임의로 정해주자 실험적으로 구하자
            d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
            d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
            cf.NB_NODES : 노드의 갯수
            c_node : agent 저장할 때 contents가 있는 station이 포괄하는 device의 갯수
        """
        
        #reward = 0
        self.set_reward_parameter(path, requested_content=requested_content)
        reward = self.a*(self.d_core - self.d_cache) + self.b*self.c_node - 0.01*self.alpha_redundancy - 0.01*self.beta_redundancy
        """
        print("self.d_core : {}".format(self.d_core))
        print("self.d_cache : {}".format(self.d_cache))
        print("self.c_node : {}".format(self.c_node))
        print("self.alpha : {}".format(self.alpha_redundancy))
        print("self.beta : {}".format(self.beta_redundancy))
        """
        
        reward = float(reward)
        #print(reward)
        return reward

    def set_reward_parameter(self, path, requested_content):

        # d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
        #          

        # d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
                   
        # R_cache : 네트워크에 존재하는 동일한 캐시의 수
        #           for 문으로 돌려야겠다

        # c_node   : 캐싱된 파일이 커버하는 노드의 수 (coverage node)
        #           
        nodeID = path[0]
        self.d_core = self.get_d_core(nodeID, requested_content)
        self.d_cache = self.get_d_cache(nodeID, requested_content)
        self.c_node = self.get_c_node()
        self.alpha_redundancy, self.beta_redundancy = self.set_content_redundancy(requested_content)



    def get_d_core(self,nodeID, requested_content):
        # 코어 인터넷까지 가서 가져오는 경우를 봐야함
        # path 뒤에 추가해서 구하자
        path = []
        path = self.network.requested_content_and_get_path(nodeID, requested_content)

        # [4,68] 일 경우 ---> [4,68, search_next_path(microBS.x, microBS.y):BS, search_next_path(BS.x, BS.y):Datacenter, search_next_path(Datacenter.x, Datacenter.y):Core Internet]
        # path 다 채워질 떄까지 돌리자
        while len(path) != 5:

            # Micro에 캐싱되어 있는 경우, BS 추가
            if len(path) == 2:
                id = path[-1]
                closestID = self.network.search_next_path(self.network.microBSList[id].pos_x,self.network.microBSList[id].pos_y,1)
                path.append(closestID)

            # BS에 캐싱 되어 있는 경우, Data Center 추가
            elif len(path) ==  3:
                path.append(0)

            # 데이터 센터에 캐싱이 되어 있는 경우, Core Internet 추가
            elif len(path) == 4:
                path.append(0)
        #print(self.network.uplink_latency(path).shape)
        d_core = (self.network.uplink_latency(path) + self.network.downlink_latency(path)) * 1000
        
        return d_core

    def get_d_cache(self, nodeID, requested_content):
        # TODO : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
        path = []
        path = self.network.requested_content_and_get_path(nodeID, requested_content)

        d_cache = (self.network.uplink_latency(path) + self.network.downlink_latency(path)) * 1000

        return d_cache

    def get_c_node(self):
        # TODO : agent 저장할 때 contents가 있는 station이 포괄하는 device의 갯수
        c_node = 0
        tmpcnt = 0

        # MicroBS
        if self.stored_type == 0:
            c_node = len(self.network.MicroBSNodeList[self.stored_nodeID])
        
        # BS
        elif self.stored_type == 1:
            for i in self.network.BSNodeList[self.stored_nodeID]:
                tmpcnt += len(self.network.MicroBSNodeList[i])
            c_node = tmpcnt

        # DataCenter
        elif self.stored_type == 2:
            c_node = cf.NB_NODES

        return c_node

    def set_content_redundancy(self, content):
        
        #print(content.__dict__)
        full_redundancy = self.cal_full_redundancy(content)
        alpha_redundancy = self.cal_alpha_redundancy(content)
        beta_redundancy = full_redundancy - self.alpha_redundancy

        return alpha_redundancy, beta_redundancy

    # cal_alpha_redundacy
    # agent가 저장한 곳의 하위 노드의 content redundancy 를 구함
    def cal_alpha_redundancy(self, content):
        # 자기 자신 저장
        content_redundancy = 1

        """
        # @ agent가 저장한 곳이 Micro BS 이면 하위 노드가 없기 때문에 고려 X
        if self.stored_type == 0:
            content_redundancy = content_redundancy + 1
        """    

        # @ agent가 저장한 곳이 Base Station 이면 하위 Micro Node들 content redundancy 구함
        if self.stored_type == 1:
            leaf_node_list = self.network.BSNodeList[self.stored_nodeID]
            #print('microBS')
            #print(leaf_node_list)
            for i in leaf_node_list:
                if content in self.network.microBSList[i].storage.storage:
                    content_redundancy = content_redundancy + 1

        # @ agent가 저장한 곳이 Data Center이면 모든 MicroBS, BS의  content redundancy 구하면됌
        elif self.stored_type == 2:
            # Micro BS
            for i in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):
                if content in self.network.microBSList[i].storage.storage:
                    content_redundancy = content_redundancy + 1
            # BS
            for i in range(cf.NUM_BS[0]*cf.NUM_BS[1]):
                if content in self.network.BSList[i].storage.storage:
                    content_redundancy = content_redundancy + 1

        return content_redundancy

    def cal_full_redundancy(self, content):
        full_redundancy = 0
        # Micro BS
        for i in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):

            if content in self.network.microBSList[i].storage.storage:
                full_redundancy = full_redundancy + 1

            """
            print("{}번째 MicroBase Station Storage".format(i))
            for j in range(len(self.network.microBSList[i].storage.storage)):
                print(self.network.microBSList[i].storage.storage[j].__dict__)
            """
            
        # BS
        for i in range(cf.NUM_BS[0]*cf.NUM_BS[1]):

            if content in self.network.BSList[i].storage.storage:
                full_redundancy = full_redundancy + 1

            """
            print("{}번째 Base Station Storage".format(i)) 
            for j in range(len(self.network.BSList[i].storage.storage)):
                print(self.network.BSList[i].storage.storage[j].__dict__)
            """

        # Datacenter
        if content in self.network.dataCenter.storage.storage:
            full_redundancy = full_redundancy + 1

        """
        for j in range(len(self.network.dataCenter.storage.storage)):
            print("Datacenter Storage")
            print(self.network.dataCenter.storage.storage[j].__dict__)
        """

        return full_redundancy




    """
    #! H_arg 에 대한 수식 정의를 아직 내리지 못하여
    #! get_R_cache 와 get_H_arg 를 사용하는 수식은 연기한다. (2022/05/11)


    def set_reward(self):
    
    # Return the reward.
    # The reward is:
    
    #    Reward = a*(d_core - d_cache) - b*(R_cache/H_arg)

    #    a,b = 임의로 정해주자 실험적으로 구하자

    #    d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
    #    d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간

    #    ! 연기함  
    #    R_cache : 네트워크에 존재하는 동일한 캐시의 수
    #    H_arg   : 동일한 캐시 사이의 평균 홉 수 (캐시의 분산도를 나타냄)
    
    self.reward = 0


    self.reward = self.a*(self.d_core - self.d_cache) - self.b*(self.R_cache/self.H_arg)
    return self.reward

    def get_reward_parameter(self):

        # d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
        #           이해 못함

        # d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
                   
        # R_cache : 네트워크에 존재하는 동일한 캐시의 수
        #           for 문으로 돌려야겠다

        # H_arg   : 동일한 캐시 사이의 평균 홉 수 (캐시의 분산도를 나타냄)
        #           준영쓰

        return d_core, d_cache, R_cache, H_arg

    # R_cache 구하기
    def get_R_cache(self, content:ct.Content):

        # 요청이 들어온 컨텐츠에 대해서 R_cache 구하기
        self.R_cache = 0

        # INFO : network.storage : [capacity , stored_size, [contents:contentStorage]]
        #        network.storage.storage : [{'title' : '개콘', 'size' : 123}, ... ,{'title' : '9시뉴스', 'size' : 123}]

        # TODO : 1. Data Center 에 있는 지 확인
        
        if content in self.network.dataCenter.storage.storage:

            self.R_cache = self.R_cache + 1

        # TODO : 2. Base Station 에 있는 지 확인
        # 2.1 Base Station List 가져옴
        for i in self.network.BSList:

            # 2.2 해당 Base Station의 stored 된 contents List를 가져옴
            storedContentsList:List = i.storage.storage

            if content in storedContentsList:
                self.R_cache = self.R_cache + 1


        # TODO : 3. Micro Base Station 에 있는 지 확인
        for i in self.network.microBSList:

            # 2.2 해당 Base Station의 stored 된 contents List를 가져옴
            storedContentsList:List = i.storage.storage

            if content in storedContentsList:
                self.R_cache = self.R_cache + 1

        return self.R_cache

    def get_H_arg():


    """

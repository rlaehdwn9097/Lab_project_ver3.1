# dqn_learn.py
def get_AR(self, type):

    available_resource = 0
    storage = 0
    stored = 0
    if type == "DataCenter":
        available_resource = self.network.dataCenter.storage.capacity - self.network.dataCenter.storage.stored
        
    elif type == "BS":
        for i in range(cf.NUM_BS[0]*cf.NUM_BS[1]):

            stored = stored + self.network.BSList[i].storage.stored

        storage = cf.BS_SIZE * cf.NUM_BS[0]*cf.NUM_BS[1] 
        available_resource = storage - stored

    elif type == "MicroBS":
        for i in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):

            stored = stored + self.network.microBSList[i].storage.stored

        storage = cf.microBS_SIZE * cf.NUM_microBS[0]*cf.NUM_microBS[1] 
        available_resource = storage - stored

    return available_resource

def cal_content_redundancy(self):
        print("================== get_title ====================")
        print(content.get_title())
        content_redundancy = 0
        for i in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):
            for j in range(len(self.network.microBSList[i].storage.storage)):
                if self.network.microBSList[i].storage.storage[j].get_title() == content_title:
                    content_redundancy = content_redundancy + 1

        for i in range(cf.NUM_BS[0]*cf.NUM_BS[1]):
            for j in range(len(self.network.BSList[i].storage.storage)):
                if self.network.BSList[i].storage.storage[j].get_title() == content_title:
                    content_redundancy = content_redundancy + 1

        for i in range(len(self.network.dataCenter.storage.storage)):
            if self.network.dataCenter.storage.storage[i].get_title() == content_title:
                content_redundancy = content_redundancy + 1
        print(content_redundancy)
        print("=================================================")
import config as cf
import numpy as np

class Content(object):
    def __init__(self, _title, _size, _popularity, _peak_day,_category):
        self.title = _title
        self.size = _size
        self.popularity = _popularity
        self.peak_day =_peak_day
        self.category = _category

class contentStorage(object):
    def __init__(self, _size):
        self.capacity = _size
        self.stored = 0
        self.storage=[]

    def abletostore(self,c:Content):
        freeSpace = self.capacity-self.stored
        if(freeSpace>=c.size):
            return 1
        else:
            return 0 
    def addContent(self,c:Content):
        self.storage.append(c)
        self.stored = self.stored + c.size


    def isstored(self,c:Content):
        if len(self.storage)>0:
            for i in self.storage:
                if i.title == c.title:
                    return 1
        return 0
    def delContent(self,c:Content):
        newstorage=[]
        for i in self.storage:
            if i is c:
                self.stored = self.stored-c.size
            else:
                newstorage.append(i)
        self.storage=newstorage
    def delFirstStored(self):#사용한지 가장 오래된 매체 삭제
        self.stored = self.stored - self.storage[0].size 
        self.storage=self.storage[1:]

# data freshness 는 없나?

def updatequeue(path:list,c:Content,microBSList,BSList,dataCenter):
    if len(path) == 2:
        microBSList[path[1]].storage.delContent(c)
        microBSList[path[1]].storage.addContent(c)
    if len(path) == 3:
        BSList[path[2]].storage.delContent(c)
        BSList[path[2]].storage.addContent(c)
    if len(path) == 4:
        dataCenter.storage.delContent(c)
        dataCenter.storage.addContent(c)    


#def count_redundancy(contentList:list,self):

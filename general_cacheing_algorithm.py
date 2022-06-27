import string
import config as cf
import logging
import node as nd
import random
import scenario as sc
import math
import random
import content as ct
import numpy as np


def leave_copy_everywhere(path:list,c,microBSList,BSList,dataCenter):

    if(microBSList[path[2]].storage.abletostore(c)==1):
        microBSList[path[2]].storage.addContent(c)
        print(1)
    else:
        microBSList[path[2]].storage.delFirstStored()
        microBSList[path[2]].storage.addContent(c)
        print(2)

    if(BSList[path[3]].storage.abletostore(c)==1):
        BSList[path[3]].storage.addContent(c)
        print(1)
    else:
        BSList[path[3]].storage.delFirstStored()
        BSList[path[3]].storage.addContent(c)
        print(2)
    if(dataCenter.storage.abletostore(c)==1):
        dataCenter.storage.addContent(c)
        print(1)
    else:
        dataCenter.storage.delFirstStored()
        dataCenter.storage.addContent(c)
        print(2)

def leave_copy_down(path:list,c:ct.Content):
    if len(path)>2:
        if(path[-2].storage.abletostore(c)==1):
            path[-2].storage.addContent(c)
        else:
            path[-2].storage.delFirstStored()
            path[-2].storage.addContent(c)
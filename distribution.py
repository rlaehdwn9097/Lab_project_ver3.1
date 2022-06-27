import numpy as np
import random
def gaussian(x,mean,sigma):
    return(1/np.sqrt(2*np.pi*sigma**2))*np.exp(-(x-mean)**2/(2*sigma**2))
print(np.random.normal(0, 0.2, 1))
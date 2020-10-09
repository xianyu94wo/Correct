import time
from numba import jit
import numpy as np





def timer(function):
    def wrapper(*args, **kwargs):
        time_start = time.time()
        res = function(*args, **kwargs)
        cost_time = time.time() - time_start
        print("【%s】运行时间：【%.7f】秒" % (function.__name__, cost_time))
        return res
    return wrapper


@timer
def npcal(a):
    s = 0
    for i in range(a):
        s += i
    return s


@timer
@jit
def nbcal(aa):
    s = 0
    for i in range(aa):
        s += i
    return s

if __name__ == '__main__':
    #ar1 = np.random.randint(1, 200, size=(5, 7))
    ar1 = 100000000
    print(ar1)
    cc = npcal(ar1)
    print(cc)

    dd = nbcal(ar1)
    print(dd)
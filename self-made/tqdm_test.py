from tqdm import trange
from time import sleep
for i in trange(10, desc='1st loop'):
    for j in trange(5, desc='2nd loop'):
            sleep(0.01)
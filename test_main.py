# -*- coding: utf-8 -*-
"""
Created on Fri May 31 16:45:03 2019

@author: wenyz
"""
from multiprocessing import Process, Queue,cpu_count
import time
if __name__ == '__main__':
    sleep_time = [1,2,3,4,5,6,7]
    sleep_index = -1
    print(cpu_count())
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 15:44:43 2019

@author: wenyz
"""

from concurrent.futures import  ProcessPoolExecutor
import threading,time

raw_datas = []
bbb = ProcessPoolExecutor(4)

def test(val):
    time.sleep(3)
    print(val)
    
def add_data():
    
    
    
    for i in range(100):
        #time.sleep(1)
        #global raw_datas
        bbb.map(test,[i])
        #raw_datas.append(i*5)
    


def aaa():
    bbb()
    
    def bbb():
        print("bbbb")
    
if __name__ == '__main__':
    
    #raw_datas=[1,2,3,4,5,6,7]
    
    #t1 = threading.Thread(target=add_data,args=())
    #t1.start()
    
    #t1.join()
    
    #bbb.map(test,raw_datas)
    
    aaa()
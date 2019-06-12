# -*- coding: utf-8 -*-
"""
Created on Fri May 31 16:45:03 2019

@author: wenyz
"""
from multiprocessing import Process, Queue,cpu_count
import time
import threading

from queue import Queue

class test:
    
    def __init__(self,a,b,c):
        self.a =a
        self.b = b
        self.c = c
        ooos = []
        
        for i in range(10):
            ooos.append(Ooos(self))
        
        self.ooos = ooos
        
    def print_self(self):
        for sss in self.ooos:
            print('self print {}'.format(sss.status))

class Ooos:
    
    def __init__(self,test):
        self.status = 0
        self.test = test
        
def update(ooos):
    time.sleep(5)
    print('update ooos status')
    ooos.status = 1
    for eee in ooos.test.ooos:
        print(eee.status) 
    print('='*70)

class update_thread(threading.Thread):
    
    def __init__(self,quq):
        threading.Thread.__init__(self)
        self.quq = quq
        self.isDaemon = True

        
    def run(self):
        while True:
            if not self.quq.empty():
                ooos = self.quq.get()
                update(ooos)


class keep_print(threading.Thread):
    def __init__(self,test):
        threading.Thread.__init__(self)
        self.test = test
        self.isDaemon = True
        
    def run(self):
        while True:
            time.sleep(6)
            #self.test.print_self()
            for sss in self.test.ooos:
                print('keep print {}'.format(sss.status))

if __name__ == '__main__':
    
    current = test('aaa','bbb','ccc')
    
    qqq = Queue(10)
    
    for aa in current.ooos:
        qqq.put(aa)
    #qqq.put(None)
    threads = []
    gg = keep_print(current)
    gg.start()

    
    for i in range(3):
        tt = update_thread(qqq)
        tt.start()
        threads.append(tt)
        
    [ts.join() for ts in threads]
    #gg.join()
    
    qqq.join()
    
    print("finished")
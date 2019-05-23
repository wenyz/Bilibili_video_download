import time
from multiprocessing import Process, Queue

def producer(q):
    for i in range(1, 11):
        time.sleep(1)
        q.put(i)
        print("{}号产品已生产完毕".format(i))

def consumer(q):
    while 1:
        time.sleep(2)
        s = q.get()
        if s == None:
            break
        else:
            print("消费者已拿走{}个产品".format(s))

if __name__ == '__main__':
    # 通过队列来模拟缓冲区,大小设置为20
    q = Queue(20)
    # 生产者进程
    pro_p = Process(target=producer, args=(q,))
    pro_p.start()
    # 消费者进程
    con_p = Process(target=consumer, args=(q,))
    con_p.start()

    pro_p.join()    # 生产者进程执行完毕后才会执行主进程
    q.put(None)     # 主进程在生产者生产结束后发送结束信号None

# -*- coding: utf-8 -*-
import time
import urllib2
import threading
from Queue import Queue
from time import sleep

import FileUploadClient

# 配置：压力测试
#THREAD_NU = 19
#ONE_WORKER_NUM = 500
#LOOP_SLEEP = 0.01

# 配置：模拟运行状态
THREAD_NU = 100
ONE_WORKER_NUM = 10000
LOOP_SLEEP = 0.5

ERROR_NUM = 0

def doWork(index):
    t = threading.currentThread()
    
    try:
        ws = FileUploadClient('ws://192.168.2.103:9000/ws', protocols=[])#'http-only', 'chat'])
        #ws.daemon = False
        ws.connect()
    except KeyboardInterrupt:
        print "["+t.name+" "+str(index)+"] "  
        print e  
        global ERROR_NUM  
        ERROR_NUM += 1
        ws.close()

def working():
    t = threading.currentThread()
    
    i = 0
    while i < ONE_WORKER_NUM:
        i += 1
        doWork(i)
        sleep(LOOP_SLEEP)
        
    print "["+t.name+"] Sub Thread End"

def main():
    t1 = time.time()
    
    Threads = []
    
    # create threads
    for i in range(THREAD_NUM):
        t = threading.Thread(target=working, name="T"+str(i))
        t.setDaemon(True)
        Threads.append(t)
        
    for t in Threads:
        t.start()
        
    for t in Threads:
        t.join()
        
    print "main thread end"
    
    t2 = time.time()
    print "========================================"  
    print "任务数量:", THREAD_NUM, "*", ONE_WORKER_NUM, "=", THREAD_NUM*ONE_WORKER_NUM
    print "总耗时(秒):", t2-t1  
    print "每次请求耗时(秒):", (t2-t1) / (THREAD_NUM*ONE_WORKER_NUM)  
    print "每秒承载请求数:", 1 / ((t2-t1) / (THREAD_NUM*ONE_WORKER_NUM))
    print "错误数量:", ERROR_NUM 
     
if __name__ == "__main__": 
    main()
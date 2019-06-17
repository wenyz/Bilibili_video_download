# -*- coding: utf-8 -*-
"""
Created on Thu May 23 17:06:37 2019

@author: wenyz
"""
import requests,re,hashlib,urllib.request,json
import os, sys
import socket
socket.setdefaulttimeout(30)
import threading,time
from multiprocessing import Process,cpu_count
from queue import Queue
from concurrent.futures import  ProcessPoolExecutor

import configparser

import ffmpy3

_DOWNLOAD_THERAD_NUM = 5
_CONVERT_PROCESS_NUM = cpu_count()-1
_DOWNLOAD_HOME = "G:\\downloadtest"
_DIRECTORY_CREATE_LOCK = threading.Lock()
_CONVERT_PROCESS_EXECUTOR = ProcessPoolExecutor(_CONVERT_PROCESS_NUM)

config = configpaser.ConfigParser()

class AV:
    
    base_url = 'https://api.bilibili.com/x/web-interface/view?aid='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    
    def __init__(self,avid,quality):
        self.avid =  str(avid)
        self.quality = quality
        self.pages = []
        self._init_data()
    
    def _init_data(self):
        html = requests.get(self.base_url + self.avid,headers=self.headers).json()
        data = html['data']
        self.title = data["title"].replace(" ","_")
        cid_list = data['pages']
        clip_list = []
        for info in cid_list:
            self.pages.append(Page(str(info['cid']),info['page'],info['part'],self))
            
        for page in self.pages:
            clip_list = get_play_list(self.base_url +self.avid + '?p='+ str(page.num),page.cid,80)
            
            clips = []
            index = 0
            for clip in clip_list:
                index += 1
                clips.append(Clip(index,clip,page))
            page.clips = clips


class DownloadRawVideo(threading.Thread):
    def __init__(self,clips_queue):
        threading.Thread.__init__(self)
        self.clips_queue = clips_queue
        self.isDaemon = True
        
    def run(self):
        while True:
            if not self.clips_queue.empty():
                clip = self.clips_queue.get()
                self.down_raw_data(clip)
                self.clips_queue.task_done()

        
    def down_raw_data(self,clip):
        opener = urllib.request.build_opener()
        opener.addheaders = [
            ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #代理是必要的，不然很容易就被拒绝访问
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
            ('Accept', '*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Range', 'bytes=0-'),
            ('Referer',  AV.base_url),
            ('Origin', 'https://www.bilibili.com'),
            ('Connection', 'keep-alive'),
        ]
        urllib.request.install_opener(opener)
        
        currentVideoPath = os.path.join(_DOWNLOAD_HOME, clip.page.av.title,clip.page.title)
        if not os.path.exists(currentVideoPath):
            #防止多线程创建重复文件夹报错
            if _DIRECTORY_CREATE_LOCK.acquire():
                #double check lock
                if not os.path.exists(currentVideoPath):
                    os.makedirs(currentVideoPath)
                _DIRECTORY_CREATE_LOCK.release()
            
        download_file_name = os.path.join(currentVideoPath, r'{}-{}.flv'.format(clip.page.title, clip.num))
        if os.path.exists(download_file_name):
            print("{}已经下载完毕！",download_file_name) 
            return
            
        download_video(raw_url=clip.url, raw_file_name=download_file_name,raw_cmd=None)
        
def convert_video(page):
    print('convert_video executed')
    currentVideoPath = os.path.join(_DOWNLOAD_HOME, page.av.title,page.title)
    
    L = []
    root_dir = currentVideoPath
    
    for file in sorted(os.listdir(root_dir),key=lambda x:int(x[x.rindex("-") + 1:x.rindex(".")])):
        if os.path.splitext(file)[1] == '.flv':
            L.append("file '{}'".format(os.path.join(root_dir,file)))
            
    tmp_file_path = os.path.join(root_dir,'tmp.txt')
    tmp_file =  open(tmp_file_path,'w')
    
    for strs in L:
        tmp_file.write(strs+'\n')
    tmp_file.close()
    
    output = os.path.join(os.path.join(_DOWNLOAD_HOME, page.av.title),page.title + '.flv')
    
    ff = ffmpy3.FFmpeg(
            inputs={tmp_file_path:'-f concat -safe 0'},
            outputs = {output:'-c copy -y'},
            )
    
    ff.run()
    if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)
    print("complete")
        
# 访问API地址
def get_play_list(start_url, cid, quality):
    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    headers = {
        'Referer': AV.base_url,  # 注意加上referer
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }

    html = requests.get(url_api, headers=headers).json()

    video_list = []
    for i in html['durl']:
        video_list.append(i['url'])
    return video_list


def download_video(raw_url,raw_file_name,raw_cmd):
    sleep_time = [2,4,30,60,300,3600,20000]
    sleep_index = -1
    while True:
        sleep_index = (sleep_index+1)%7
        try:
            urllib.request.urlretrieve(url=raw_url, filename=raw_file_name,reporthook=raw_cmd)
            break
        except socket.timeout:
            print("socket timeout occured!")
            time.sleep(sleep_time[sleep_index])
        except urllib.error.URLError as e:
            print("urllib.error.URLError : ",e.reason)
            time.sleep(sleep_time[sleep_index])
        except Exception as e:
            print("unhandled Exception : ",e.reason)
            time.sleep(sleep_time[sleep_index])

class Page:
    def __init__(self,cid,num,title,av,url=None):
        self.av = av
        self.cid = cid
        self.url = url
        self.num = num
        self.title = title
        self.clips = []
        
class Clip:
    def __init__(self,num,url,page):
        self.num = num
        self.url = url
        self.page = page

def deal_av(avid,quality):
    current = AV(avid,quality)
    download_queue = Queue(maxsize=0)
    for page in current.pages:
        for clip in page.clips:
            download_queue.put(clip)
    
    threads = []
    for i in range(_DOWNLOAD_THERAD_NUM):
        thread = DownloadRawVideo(download_queue)
        thread.start()
        threads.append(thread)
        
    #[t.join() for t in threads]
    download_queue.join()
    print("av download finish")
    
    _CONVERT_PROCESS_EXECUTOR.map(convert_video,current.pages)
    
    

if __name__ == '__main__':
    deal_av('25755767',80)
    
    _CONVERT_PROCESS_EXECUTOR.shutdown()
    print("convert finished")
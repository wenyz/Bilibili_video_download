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

_DOWNLOAD_THERAD_NUM = 20
_CONVERT_PROCESS_NUM = cpu_count()-1
_DOWNLOAD_HOME = "G:\\downloadtest"
_DIRECTORY_CREATE_LOCK = threading.Lock()
_CONVERT_PROCESS_EXECUTOR = ProcessPoolExecutor(_CONVERT_PROCESS_NUM)
#_STATUS_LOCK = threading.Lock()

class AV:
    
    base_url = 'https://api.bilibili.com/x/web-interface/view?aid='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    
    def __init__(self,avid,quality):
        self.avid =  str(avid)
        self.quality = quality
        self.status = 0
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
        
    def run(self):
        while True:
            if not self.clips_queue.empty():
                clip = self.clips_queue.get()
                self.down_raw_data(clip)
                self.clips_queue.task_done()

        
    def down_raw_data(self,clip):
        opener = urllib.request.build_opener()
        opener.addheaders = [
            ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
            ('Accept', '*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            
            ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
            ('Referer',  AV.base_url),  # 注意修改referer,必须要加的!
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
            
        refresh_video(raw_url=clip.url, raw_file_name=download_file_name,raw_cmd=None)
#        if _STATUS_LOCK.acquire():
#            clip.status = 1        
#            tmp_status = 0
#            for cc in clip.page.clips:
#                #print('{}-{}'.format(cc.num,cc.status))
#                if cc.status == 0:
#                    tmp_status = 1
#            
#            #print('{}-{} is download'.format(clip.page.title,clip.num))
#            if tmp_status == 1:
#                _STATUS_LOCK.release()
#                return
#            
#            print('{} finished'.format(clip.page.title))
#            clip.page.status = 1
#            _STATUS_LOCK.release()
        
#        total = len(clip.page.clips)
#        tmp = 0
#        for file in currentVideoPath:
#            if not os.path.getsize(file)==0:
#                tmp = tmp+1
#                
#        
#        print('total = {},now is {}'.format(total,tmp))
        
            
        
        
def convert_video(page):
    currentVideoPath = os.path.join(_DOWNLOAD_HOME, page.av.title,page.title)
    
    L = []
    root_dir = currentVideoPath
    inputStr = "concat:"
    for file in sorted(os.listdir(root_dir),key=lambda x:int(x[x.rindex("-") + 1:x.rindex(".")])):
        print(file)
        if os.path.splitext(file)[1] == '.flv':
            filePath = os.path.join(root_dir,file)
            L.append(filePath)
    print(inputStr+"|".join(L)) 
        
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
    # print(url_api)
    html = requests.get(url_api, headers=headers).json()
    # print(json.dumps(html))
    #video_list = [html['durl'][0]['url']]
    video_list = []
    for i in html['durl']:
        video_list.append(i['url'])
    return video_list


def refresh_video(raw_url,raw_file_name,raw_cmd):
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
        self.status = 0
        self.title = title
        self.clips = []
        
class Clip:
    def __init__(self,num,url,page):
        self.num = num
        self.url = url
        self.status = 0
        self.page = page

def deal_av(avid,quality):
    current = AV(avid,quality)
    clips_queue = Queue(maxsize=0)
    convert_queue =Queue(maxsize=0)
    for page in current.pages:
        for clip in page.clips:
            clips_queue.put(clip)
    
    threads = []
    for i in range(_DOWNLOAD_THERAD_NUM):
        thread = DownloadRawVideo(clips_queue)
        thread.start()
        threads.append(thread)
        
    [t.join() for t in threads]
    clips_queue.join()
    print("av download finish")
    
    for page in current.pages:
        _CONVERT_PROCESS_EXECUTOR.map(target=convert_video,args=[page])
    
        


if __name__ == '__main__':
    deal_av('25755767',80)
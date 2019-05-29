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
            self.pages.append(Page(str(info['cid']),info['page'],info['part']))
            
        for page in self.pages:
            clip_list = get_play_list(self.base_url +self.avid + '?p='+ str(page.num),page.cid,80)
            
            clips = []
            index = 0
            for clip in clip_list:
                index += 1
                clips.append(Clip(index,clip))
            page.clips = clips
            
        
        qgc = 25
        ggc_threads = []
        
        for i in range(qgc):
            tt = threading.Thread(target=down_video2,args=(self.pages[1].clips[i].url,i))
            tt.start()
            ggc_threads.append(tt)
        
        for te in ggc_threads:
            te.join()
        
        print("="*90)
        
        #down_video2(self.pages[0].clips[0].url,0)
        #down_video2(self.pages[1].clips[1].url,1)
        #down_video2(self.pages[2].clips[2].url,2)
            
        
    def start_download(self):

        print("start download")
        
        
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


def down_video2(video_url,num):
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', "ttttttt")
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
    
    if not os.path.exists(currentVideoPath):
        os.makedirs(currentVideoPath)
    
    

    refresh_video(url1=video_url, filename1=os.path.join(currentVideoPath, r'{}-{}.flv'.format("qwer", num)),Schedule_cmd1=None)

#  下载视频
def down_video(video_list, title, start_url, page):
    num = 1
    print('[正在下载P{}段视频,请稍等...]:'.format(page) + title)
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title)  # 当前目录作为下载目录
    for i in video_list:
        opener = urllib.request.build_opener()
        # 请求头
        opener.addheaders = [
             ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
            ('Accept', '*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
            ('Referer', start_url),  # 注意修改referer,必须要加的!
            ('Origin', 'https://www.bilibili.com'),
            ('Connection', 'keep-alive'),
        ]
        urllib.request.install_opener(opener)
        # 创建文件夹存放下载的视频
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)
        # 开始下载
#        if len(video_list) > 1:
#            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}-{}.flv'.format(title, num)),reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
#        else:
#            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}.flv'.format(title)),reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
#        num += 1

        if len(video_list) > 1:
            refresh_video(url1=i, filename1=os.path.join(currentVideoPath, r'{}-{}.flv'.format(title, num)),Schedule_cmd1=None)  # 写成mp4也行  title + '-' + num + '.flv'
        else:
            refresh_video(url1=i, filename1=os.path.join(currentVideoPath, r'{}.flv'.format(title)),Schedule_cmd1=None)  # 写成mp4也行  title + '-' + num + '.flv'
        num += 1

def refresh_video(url1,filename1,Schedule_cmd1):
    try:

        if os.path.exists(filename1):
            print("{}已经下载完毕！",filename1)
            return
        urllib.request.urlretrieve(url=url1, filename=filename1,reporthook=Schedule_cmd1)
        #urllib.request.urlretrieve(url1,filename1)
    except socket.timeout:
        count = 1
        while count <= 5:
            try:
                urllib.request.urlretrieve(url=url1, filename=filename1,reporthook=Schedule_cmd1)
                #urllib.request.urlretrieve(url1,filename1)
                break
            except socket.timeout:
                err_info = 'Reloading for %d time'%count if count == 1 else 'Reloading for %d times'%count
                print(err_info)
                count += 1
            except urllib.error.URLError as e:
                err_info = 'URLError for %d time'%count if count == 1 else 'Reloading for %d times'%count
                print(err_info)
                count += 1
        if count > 5:
            print("downloading picture fialed!")
    except urllib.error.URLError as e:
        count = 1
        while count <= 5:
            try:
                urllib.request.urlretrieve(url=url1, filename=filename1,reporthook=Schedule_cmd1)
                #urllib.request.urlretrieve(url1,filename1)
                break
            except socket.timeout:
                err_info = 'Reloading for %d time'%count if count == 1 else 'Reloading for %d times'%count
                print(err_info)
                count += 1
            except urllib.error.URLError as e:
                err_info = 'URLError for %d time'%count if count == 1 else 'Reloading for %d times'%count
                print(err_info)
                count += 1
        if count > 5:
            print("downloading picture fialed!")

class Page:
    def __init__(self,cid,num,title,url=None):
        self.cid = cid
        self.url = url
        self.num = num
        self.status = 0
        self.title = title
        self.clips = []
        
class Clip:
    def __init__(self,num,url):
        self.num = num
        self.url = url
        self.status = 0

if __name__ == '__main__':
    av1 = AV('25755767',80)
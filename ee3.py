# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 17:19:40 2019

@author: wenyz
"""

import os,sys
from moviepy.editor import *


def combine_video(video_list, title):
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title)  # 当前目录作为下载目录
    
    print(currentVideoPath)
    if 1 == 1:
        # 视频大于一段才要合并
        print('[下载完成,正在合并视频...]:' + title)
        # 定义一个数组
        L = []
        # 访问 video 文件夹 (假设视频都放在这里面)
        root_dir = currentVideoPath
        # 遍历所有文件
        for file in sorted(os.listdir(root_dir), key=lambda x: int(x[x.rindex("-") + 1:x.rindex(".")])):
            # 如果后缀名为 .mp4/.flv
            if os.path.splitext(file)[1] == '.flv':
                # 拼接成完整路径
                filePath = os.path.join(root_dir, file)
                print(filePath)
                # 载入视频
                video = VideoFileClip(filePath)
                print("load video")
                # 添加到数组
                L.append(video)
        # 拼接视频
        final_clip = concatenate_videoclips(L, method='compose')
        # 生成目标视频文件
        
        print("q"*30)
        fifi = os.path.join(root_dir, r'{}.mp4'.format(title))
        #final_clip.write_videofile(os.path.join(root_dir, r'{}.mp4'.format(title)), fps=24, remove_temp=False)
        final_clip.write_videofile("D:\111.mp4", fps=24, remove_temp=False,codec='flv')
        print('[视频合并完成]' + title)

    else:
        # 视频只有一段则直接打印下载完成
        print('[视频合并完成]:' + title)
        
        


if __name__ == '__main__':
    print("="*10)
    #combine_video("", "01_课题介绍Introduction")
    combine_video("", "01_学习的要义")
    print("="*10)
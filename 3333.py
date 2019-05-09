# -*- coding: utf-8 -*-
"""
Created on Wed May  8 10:21:12 2019

@author: wenyz
"""
import os,sys
from moviepy.editor import *
import ffmpy3

if __name__ == '__main__':
    #currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', "01_学习的要义","01_课题介绍Introduction-5.flv")
    #currentVideoPath = "G:\\opensource_appreciation\\py\\Bilibili_video_download\\bilibili_video\\01_学习的要义\\01_课题介绍Introduction-5.flv"
    #clip = VideoFileClip(currentVideoPath).rotate(180)
    #clip.ipython_display(width=180,maxduration=8024000000)
    
    #ff = ffmpy3.FFmpeg(
    #        inputs={"concat:G:\\opensource_appreciation\\py\\ffmpeg-20190507-e25bddf-win64-static\\bin\\input1.ts|G:\\opensource_appreciation\\py\\ffmpeg-20190507-e25bddf-win64-static\\bin\\input2.ts|G:\\opensource_appreciation\\py\\ffmpeg-20190507-e25bddf-win64-static\\bin\\input3.ts":None},
    #        outputs = {"G:\\opensource_appreciation\\py\\ffmpeg-20190507-e25bddf-win64-static\\bin\\bbbb.mp4":None},
    #        global_options = {"-c copy":None,"-bsf:a aac_adtstoasc":None,"-movflags +faststart":None}
    #        )
    #
    #ff.run()
    #print("complete")
    
    
    currentVideoPath = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'bilibili_video', "inputss")  # 当前目录作为下载目录
    
    L = []
    root_dir = currentVideoPath
    inputStr = "concat:"
    for file in sorted(os.listdir(root_dir),key=lambda x:int(x[x.rindex("-") + 1:x.rindex(".")])):
        print(file)
        if os.path.splitext(file)[1] == '.flv':
            filePath = os.path.join(root_dir,file)
            L.append(filePath)
    print(inputStr+"|".join(L))
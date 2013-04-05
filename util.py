# -*- coding: utf-8 -*-
import os
import os.path
import glob
import wave
import numpy as np


#读取声音文件
def wavread(file):
    '''
    读取指定的ffile,返回声音数据，采样率，数据点数
    '''
    f = wave.open(file, u'rb')
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    str_data = f.readframes(nframes)
    f.close()
    wave_data = np.fromstring(str_data, dtype=np.short)
    return wave_data, framerate, sampwidth * 8, nframes


def FilenameFilter(path):
    '''
       遍历指定文件夹下的wav日志
    '''
    filenames = []
    for filename in glob.glob(os.path.join(path, "*.wav")):
        filenames.append(filename)
    return filenames


def path_match_platform(path):
    path = unicode(path)
    if os.name == 'nt':
        if '/' in path:
            path.replace('/', '\\')
    elif os.name == 'posix':
        if '\\' in path:
            path.replace('\\', '/')
    return os.path.normpath(path)

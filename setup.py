# -*- coding: utf-8 -*-
#
# Copyright © 2013 dragondjf
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see guidata/__init__.py for details)

"""
guidata.disthelper

How to create an executable with py2exe or cx_Freeze with less efforts than
writing a complete setup script.
"""

'''
***********************************问题1***************************************************
cx_Freeze库中的dist.py文件中的改动
        def __init __():
            .....
            .....
    135     self.bin_path_includes = []
    136     self.bin_path_excludes = []


        def run(self):
            .....
            .....
    168     binPathIncludes = self.bin_path_includes,
    169     binPathExcludes = self.bin_path_excludes)

用于解决下面这个问题：
    error: error in setup script: command 'build_exe' has no such option 'bin_path_includes'

***********************************问题2*****************************************************
重新定义add_image_path()函数, 主要增加如下代码
    if 'library.zip' in path:
        path = path.replace('/library.zip', '')
用于解决利用guidata.disthelpers中打包guidata库时产生的报错
    在library.zip中无法找到guidata库中的images文件夹


'''
import os
import shutil
from guidata.disthelpers import Distribution
import matplotlib

if os.name != "nt":
    def add_image_path(path, subfolders=True):
        """Append image path (opt. with its subfolders) to global list IMG_PATH"""
        if not isinstance(path, unicode):
            path = fs_to_unicode(path)
        global IMG_PATH
        if 'library.zip' in path:
            path = path.replace('/library.zip', '')
        IMG_PATH.append(path)
        if subfolders:
            for fileobj in os.listdir(path):
                pth = osp.join(path, fileobj)
                if osp.isdir(pth):
                    IMG_PATH.append(pth)
else:
    target_dir = "dist"

if __name__ == '__main__':

    if os.name == "nt":
        matplotlibdata_files = matplotlib.get_py2exe_datafiles()

        dist = Distribution()
        dist.vs2008 = None
        dist.setup(name=u"Application demo", version='1.0.0',
                   description=u"Application  based on MetroMathPlot.py",
                   script="MetroMathPlot.py", target_name="MetroMathPlot",
                   icon="images/DMathPlot.ico")

        dist.add_modules('PyQt4', 'guidata', 'guiqwt')
        dist.bin_excludes += ["libzmq.dll"]
        dist.includes += ['PyQt4.Qwt5','matplotlib']
        dist.data_files += matplotlibdata_files
        dist.data_files += [('phonon_backend', [
                'C:\Python27\Lib\site-packages\PyQt4\plugins\phonon_backend\phonon_ds94.dll'
                ]),
            ('imageplugins', [
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qgif4.dll',
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll',
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll',
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qico4.dll',
            ])]

        dist.excludes += [
                  '_gtkagg',
                  '_tkagg',
                  '_agg2',
                  '_cairo',
                  '_cocoaagg',
                  '_fltkagg',
                  '_gtk',
                  '_gtkcairo', ]

        dist.build('py2exe')

        '''
            拷贝响应的图片皮肤和与项目有关的资源文件到打包目录
        '''
        for item in ['icons', 'images', 'skin', 'wavs']:
            shutil.copytree(os.getcwd() + os.sep + item, os.getcwd() + os.sep + os.sep.join(['dist', item]))
    else:
        dist = Distribution()
        dist.vs2008 = None
        dist.setup(name=u"Application demo", version='1.0.0',
                   description=u"Application  based on MetroMathPlot.py",
                   script="MetroMathPlot.py", target_name="MetroMathPlot",
                   icon="images/DMathPlot.ico")

        dist.add_modules('PyQt4', 'matplotlib', 'guidata', 'guiqwt')
        dist.includes += ['PyQt4.Qwt5']
        dist.build('cx_Freeze')

        '''
            拷贝响应的图片皮肤和与项目有关的资源文件到打包目录
        '''
        for item in ['icons', 'images', 'skin', 'wavs']:
            shutil.copytree(os.getcwd() + os.sep + item, os.getcwd() + os.sep + os.sep.join([target_dir, item]))

        '''
            拷贝影响编译可执行文件运行的 第三方库 到编译目录下
        '''
        for item in ['encodings', 'scipy']:
            package = __import__(item)
            package_path = os.path.dirname(package.__file__)
            shutil.copytree(package_path, os.getcwd() + os.sep + os.sep.join([target_dir, item]))

        '''
            将guidata库 拷贝 到编译目录下
        '''
        for item in ['guidata', 'guiqwt']:
            gui_path = os.getcwd() + os.sep + os.sep.join([target_dir, item])
            if os.path.isdir(gui_path):
                shutil.rmtree(gui_path)
                package = __import__(item)
                package_path = os.path.dirname(package.__file__)
                shutil.copytree(package_path, gui_path, symlinks=True)

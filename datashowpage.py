#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from figurewidget import FigureWidget
import configdialog
from guiutil import set_skin
import algorithm
import util
import random


class DataShowPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DataShowPage, self).__init__(parent)
        self.parent = parent
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)  # 设置分割窗口水平排列
        self.splitter.setOpaqueResize(True)  # 设定分割窗的分割条在拖动时是否为实时更新显示，默认True表示实时更新

        self.createToolBar()

        self.splitter_figure = QtGui.QSplitter()
        self.splitter_figure.setOrientation(QtCore.Qt.Vertical)
        self.f1 = FigureWidget('Figure 1', point_num=100)
        self.splitter_figure.addWidget(self.f1)

        self.splitter.addWidget(self.navigation)
        self.splitter.addWidget(self.splitter_figure)
        self.splitter.setSizes([self.width() / 4, self.width() * 3 / 4])  # 设置初始化时各个分割窗口的大小
        self.splitter.setStretchFactor(1, 1)  # 设置编号为1的控件为可伸缩控件，第二个参数为表示自适应调整，大于0表示只有为编号为1的控件会自适应调整

        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(self.splitter)
        self.setLayout(self.mainLayout)

        self.navigation_flag = True   # 导航标志，初始化时显示导航
        self.settingdialog = configdialog.ConfigDialog()
        self.wavhandler = WavHandler(figurewidget=self.f1)
        QtCore.QObject.connect(self.settingdialog, QtCore.SIGNAL('send(PyQt_PyObject)'), self.wavhandler, QtCore.SLOT('settings(PyQt_PyObject)'))

    def createToolBar(self):
        navbutton = ['Start', 'Pause', 'Custom']
        self.buttontext = {
            'Start': u'开始',
            'Pause': u'暂停',
            'Custom': u'自定义'
        }
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QVBoxLayout()

        for item in navbutton:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(self.buttontext[item]))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        set_skin(self.navigation, os.sep.join(['skin', 'qss', 'MetroDataShow.qss']))

        getattr(self, 'StartButton').clicked.connect(self.settings)

    def settings(self):
        self.settingdialog.show()


class WavHandler(QtCore.QObject):

    started = QtCore.SIGNAL('send(PyQt_PyObject)')

    def __init__(self, parent=None, figurewidget=None):
        super(WavHandler, self).__init__(parent)
        self.figurewidget = figurewidget
        self.data = algorithm.creat_data(algorithm.Names)
        QtCore.QObject.connect(self, self.started, self.figurewidget, QtCore.SLOT('startwork(PyQt_PyObject)'))

    @QtCore.pyqtSlot(dict)
    def settings(self, kargs):
        self.wav_parameter = kargs
        self.setup()

    def setup(self):
        self.wavfiles = util.FilenameFilter(util.path_match_platform(self.wav_parameter['wavpath']))
        # self.timer = self.startTimer(100)
        # self.handle()
        self.timer = self.startTimer(100)

    def handle(self):
        # for wavfile in self.wavfiles:
        #     x, fs, bits, N = util.wavread(unicode(wavfile))
        #     self.x = (x + 32768) / 16
        #     for i in range(1, len(x) / 1024):
        #         for key in algorithm.Names:
        #             self.data[key][:-1] = self.data[key][1:]
        #         raw_data = self.x[1024 * (i - 1):1024 * i]
        #         self.data['max'][-1] = max(raw_data)
        #         self.data['min'][-1] = min(raw_data)
        #         # self.emit(self.started, self.data)
        #         # # self.timer = self.startTimer(100)
        #         # time.sleep(1)
        for key in algorithm.Names:
            self.data[key][:-1] = self.data[key][1:]
        a = [3000 * random.random(), 3000 * random.random()]
        self.data['max'][-1] = max(a)
        self.data['min'][-1] = min(a)

    def finish(self):
        pass

    def timerEvent(self, evt):
        self.handle()
        self.emit(self.started, self.data)
        # self.killTimer(self.timer)

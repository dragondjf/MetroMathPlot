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
import threading
import time


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
        self.figurewidget = FigureWidget('Figure 1', point_num=100)
        self.splitter_figure.addWidget(self.figurewidget)

        self.splitter.addWidget(self.navigation)
        self.splitter.addWidget(self.splitter_figure)
        self.splitter.setSizes([self.width() / 4, self.width() * 3 / 4])  # 设置初始化时各个分割窗口的大小
        self.splitter.setStretchFactor(1, 1)  # 设置编号为1的控件为可伸缩控件，第二个参数为表示自适应调整，大于0表示只有为编号为1的控件会自适应调整

        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(self.splitter)
        self.setLayout(self.mainLayout)

        self.navigation_flag = True   # 导航标志，初始化时显示导航

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

        getattr(self, 'StartButton').clicked.connect(self.startploting)
        getattr(self, 'PauseButton').clicked.connect(self.stopploting)

    def startploting(self):
        self.figurewidget.plotflag = True

    def stopploting(self):
        self.figurewidget.plotflag = False


class InteractiveManage(QtCore.QObject):

    started = QtCore.SIGNAL('send(PyQt_PyObject)')

    def __init__(self, parent=None, **pages):
        super(InteractiveManage, self).__init__(parent)
        self.parent = parent
        for key, value in pages.items():
            setattr(self, key, value)

        self.settingdialog = configdialog.ConfigDialog()
        self.data = algorithm.creat_data(algorithm.Names)

        QtCore.QObject.connect(self, self.started, getattr(self, 'DataShowPage').figurewidget, QtCore.SLOT('startwork(PyQt_PyObject)'))
        QtCore.QObject.connect(self.settingdialog, QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('settings(PyQt_PyObject)'))

        getattr(getattr(self, 'DataShowPage'), 'CustomButton').clicked.connect(self.setdialogshow)

        self.importwavspreed = 0.2

    def tcpServerstart(self):
        t = threading.Thread(name="Listen Thread 1", target=self.handle)
        t.setDaemon(True)
        t.start()

    def setdialogshow(self):
        self.settingdialog.show()

    @QtCore.pyqtSlot(dict)
    def settings(self, kargs):
        self.wav_parameter = kargs
        self.wavfiles = util.FilenameFilter(util.path_match_platform(self.wav_parameter['wavpath']))

    def handle(self):
        while True:
            if hasattr(self, 'wavfiles'):
                for wavfile in self.wavfiles:
                    x, fs, bits, N = util.wavread(unicode(wavfile))
                    self.x = (x + 32768) / 16
                    for i in range(1, len(x) / 1024):
                        for key in algorithm.Names:
                            self.data[key][:-1] = self.data[key][1:]
                        raw_data = self.x[1024 * (i - 1):1024 * i]
                        self.data['max'][-1] = max(raw_data)
                        self.data['min'][-1] = min(raw_data)
                        self.emit(self.started, self.data)
                        time.sleep(self.importwavspreed / self.wav_parameter['importwavspreed'])
            else:
                pass

    def timerEvent(self, evt):
        pass

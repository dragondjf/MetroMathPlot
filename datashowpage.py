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

    @QtCore.pyqtSlot()
    def stopploting(self):
        self.figurewidget.plotflag = False

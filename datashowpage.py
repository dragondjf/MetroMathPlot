#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from PyQt4 import QtGui
from PyQt4 import QtCore

import threading
import multiprocessing
import Queue
import time
import websocket
import json

from configdialog import QInputDialog, QMessageBox
from figurewidget import FigureWidget
import configdialog
from guiutil import set_skin, movecenter
# from cache import padata
import util


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
        i = 0
        setattr(self, 'wavefigure%d' % i, WaveFigure('Figure%d' % i, point_num=300))
        getattr(self, 'wavefigure%d' % i).setObjectName('WaveFigure%d' % i)
        self.splitter_figure.addWidget(getattr(self, 'wavefigure%d' % i))

        self.splitter.addWidget(self.navigation)
        self.splitter.addWidget(self.splitter_figure)
        self.splitter.setSizes([self.width() / 4, self.width() * 3 / 4])  # 设置初始化时各个分割窗口的大小
        self.splitter.setStretchFactor(1, 1)  # 设置编号为1的控件为可伸缩控件，第二个参数为表示自适应调整，大于0表示只有为编号为1的控件会自适应调整

        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(self.splitter)
        self.setLayout(self.mainLayout)

        self.navigation_flag = True   # 导航标志，初始化时显示导航

    def createToolBar(self):
        navbutton = ['Start', 'Pause', 'Custom', 'Add']
        self.buttontext = {
            'Start': u'开始',
            'Pause': u'暂停',
            'Custom': u'自定义',
            'Add': u'增加'
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
        getattr(self, 'AddButton').clicked.connect(self.addFigure)

    def startploting(self):
        for i in xrange(self.splitter_figure.count()):
            setattr(getattr(self, 'wavefigure%d' % i), 'plotflag', True)

    @QtCore.pyqtSlot()
    def stopploting(self):
        for i in xrange(self.splitter_figure.count()):
            setattr(getattr(self, 'wavefigure%d' % i), 'plotflag', False)

    def addFigure(self):
        i = self.splitter_figure.count()
        setattr(self, 'wavefigure%d' % i, WaveFigure('Figure%d' % i, point_num=300))
        getattr(self, 'wavefigure%d' % i).setObjectName('wavefigure%d' % i)
        self.splitter_figure.addWidget(getattr(self, 'wavefigure%d' % i))
        self.emit(QtCore.SIGNAL('send(int)'), i)


class WaveFigure(FigureWidget):
    def __init__(self, title, point_num=300):
        super(WaveFigure, self).__init__(title, [], [])
        # self.title = title
        self.plotflag = True
        # 与右键有关的初始化设置
        self.point_num = point_num   # 默认显示点数
        self.pauseflag = False  # 默认不暂停

        configdlg = configdialog.ConfigDialog()
        self.settingdialog = configdialog.ChildDialog(None, configdlg)
        QtCore.QObject.connect(getattr(self.settingdialog, 'Ok' + 'Button'), QtCore.SIGNAL('clicked()'), configdlg, QtCore.SLOT('save_settings()'))  # 点击弹出窗口OkButton，执行保存参数函数
        QtCore.QObject.connect(self.settingdialog.child, QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('settings(PyQt_PyObject)'))  # 交互管理窗口获取保存的配置

    @QtCore.pyqtSlot(list)
    def startwork(self, padata, showf):
        try:
            if self.plotflag:
                self.ax.clear()
                if 'gno' in self.settintparameter:
                    self.ax.set_title(self.settintparameter['gno'])
                for item in showf:
                    if len(showf) == 1:
                        color = ['r']
                    elif len(showf) == 2:
                        color = ['r', 'b']
                    elif len(showf) == 3:
                        color = ['r', 'g', 'b']
                    self.ax.plot(padata[item][-self.point_num:], color=color[showf.index(item)])
                self.fig.canvas.draw()
        except Exception, e:
            pass

    def createContextMenu(self):
        '''
        创建右键菜单
        '''
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # 创建QMenu
        self.contextMenu = QtGui.QMenu(self)
        style_QMenu1 = "QMenu {background-color: #ABABAB; border: 1px solid black;}"
        style_QMenu2 = "QMenu::item {background-color: transparent;}"
        style_QMenu3 = "QMenu::item:selected { /* when user selects item using mouse or keyboard */background-color: #654321;}"
        style_QMenu = QtCore.QString(style_QMenu1 + style_QMenu2 + style_QMenu3)
        self.contextMenu.setStyleSheet(style_QMenu)

        self.action_datafrom = self.contextMenu.addAction(u'选择数据来源')
        self.action_pointnum = self.contextMenu.addAction(u'设置数据显示点数')
        self.action_pause = self.contextMenu.addAction(u'暂停')
        self.action_NavigationToolbar = self.contextMenu.addAction(u'显示绘图导航')
        self.action_delete = self.contextMenu.addAction(u'删除此图')
        # 将动作与处理函数相关联
        # 这里为了简单，将所有action与同一个处理函数相关联
        # 当然也可以将他们分别与不同函数关联，实现不同的功能
        self.action_datafrom.triggered.connect(self.datafromHandler)
        self.action_pointnum.triggered.connect(self.pointnumHandler)
        self.action_pause.triggered.connect(self.pauseHandler)
        self.action_NavigationToolbar.triggered.connect(self.NavigationToolbarHandler)
        self.action_delete.triggered.connect(self.deleteHandler)

    def showContextMenu(self, pos):
        '''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        coursePoint = QtGui.QCursor.pos()  # 获取当前光标的位置
        self.contextMenu.move(coursePoint)
        self.contextMenu.show()

    def datafromHandler(self):
        self.setdialogshow(self.objectName())

    def setdialogshow(self, objectname):
        self.settingdialog.child.boundfig(str(objectname))
        mainwindow = self.parent().parent().parent().parent.parent()
        self.settingdialog.setGeometry(mainwindow.geometry())
        movecenter(self.settingdialog)
        self.settingdialog.show()
        self.settingdialog.fadeInWidget()

    @QtCore.pyqtSlot(dict)
    def settings(self, kargs):
        self.settintparameter = kargs
        if 'wavpath' in kargs:
            self.wavfiles = util.FilenameFilter(util.path_match_platform(self.settintparameter['wavpath']))
            if not hasattr(self, 'datahandler'):
                self.datahandler = WaveReplayHandler(self, self.wavfiles)
            else:
                self.datahandler.cmd_queue.put_nowait(self.settintparameter)

        else:
            if not hasattr(self, 'datahandler'):
                self.datahandler = WaveThreadHandler(self)
            else:
                self.datahandler.cmd_queue.put_nowait(self.settintparameter)

    def pointnumHandler(self):
        '''
        设置数据显示点数
        '''
        self.input_dialog = QInputDialog()
        i, ok = self.input_dialog.getInteger(u"设置数据点数", "number:", self.point_num, 1, 4096, 300)
        if ok:
            self.point_num = i
        # print self.point_num

    def pauseHandler(self):
        '''
        暂停和启动波形
        '''
        if not self.pauseflag:
            self.action_pause.setText(u'启动')
            self.emit(QtCore.SIGNAL('datag(bool)'), self.pauseflag)
            self.pauseflag = True
        else:
            self.action_pause.setText(u'暂停')
            self.emit(QtCore.SIGNAL('datag(bool)'), self.pauseflag)
            self.pauseflag = False

    def NavigationToolbarHandler(self):
        '''
        导航工具条显示与隐藏
        '''
        if self.mpl_toolbar.isVisible():
            self.action_NavigationToolbar.setText(u'显示绘图导航')
            self.mpl_toolbar.setVisible(False)
        else:
            self.action_NavigationToolbar.setText(u'隐藏绘图导航')
            self.mpl_toolbar.setVisible(True)

    def deleteHandler(self):
        '''
        删除此绘图控件
        '''
        if hasattr(self, 'timer'):
            self.killTimer(self.timer)
        try:
            self.deleteLater()
        except Exception, e:
            # print e
            pass

class WaveThreadHandler(threading.Thread):
    def __init__(self, figure):
        threading.Thread.__init__(self)
        self.cmd_queue = Queue.Queue()
        self.figure = figure
        self.paid = self.figure.settintparameter['_id']
        self.featurevalueflags = self.figure.settintparameter['featurevalue']
        self.setDaemon(True)
        self.start()

    def run(self):
        try:
            ws = websocket.create_connection("ws://localhost:9000/waves/%s" % self.paid)
            ws.send(json.dumps(self.featurevalueflags))
        except Exception, e:
            return
        import algorithm
        padata = algorithm.creat_data(algorithm.Names)
        while True:
            try:
                self.figure.settintparameter = self.cmd_queue.get_nowait()
                if self.paid == self.figure.settintparameter['_id']:
                    pass
                else:
                    self.paid = self.figure.settintparameter['_id']
                    ws.close()
                    ws = websocket.create_connection("ws://localhost:9000/waves/%s" % self.paid)
                self.featurevalueflags = self.figure.settintparameter['featurevalue']
                ws.send(json.dumps(self.featurevalueflags))
            except Queue.Empty:
                pass

            showf = []
            for key in self.featurevalueflags:
                if type(self.featurevalueflags[key]) is bool and self.featurevalueflags[key]:
                    showf.append(key)

            result = json.loads(ws.recv())
            for item in result:
                for key in padata.keys():
                    padata[key][:-1] = padata[key][1:]
                for key in item:
                    padata[key][-1] = item[key]
            self.figure.startwork(padata, showf)


class WaveProcessHandler(multiprocessing.Process):
    def __init__(self, figure):
        multiprocessing.Process.__init__(self)
        self.figure = figure
        self.paid = self.figure.settintparameter['_id']
        self.featurevalueflags = self.figure.settintparameter['featurevalue']
        # self.setDaemon(True)
        self.start()

    def run(self):
        try:
            ws = websocket.create_connection("ws://localhost:9000/waves/%s" % self.paid)
            ws.send(json.dumps(self.featurevalueflags))
        except Exception, e:
            return
        import algorithm
        padata = algorithm.creat_data(algorithm.Names)
        while True:
            showf = []
            for key in self.featurevalueflags:
                if type(self.featurevalueflags[key]) is bool and self.featurevalueflags[key]:
                    showf.append(key)
            result = json.loads(ws.recv())
            for item in result:
                for key in padata.keys():
                    padata[key][:-1] = padata[key][1:]
                for key in item:
                    padata[key][-1] = item[key]
            self.figure.startwork(padata, showf)


class WaveReplayHandler(threading.Thread):
    def __init__(self, figure, wavfiles):
        threading.Thread.__init__(self)
        self.cmd_queue = Queue.Queue()
        self.figure = figure
        self.wavfiles = wavfiles
        self.importwavspreed = 0.1
        self.setDaemon(True)
        self.start()

    def run(self):
        import algorithm
        padata = algorithm.creat_data(algorithm.Names)
        while True:
            try:
                self.figure.settintparameter = self.cmd_queue.get_nowait()
            except Queue.Empty:
                pass
            if hasattr(self, 'wavfiles'):
                for wavfile in self.wavfiles:
                    x, fs, bits, N = util.wavread(unicode(wavfile))
                    self.x = (x + 32768) / 16
                    for i in range(1, len(x) / 1024):
                        for key in padata:
                            padata[key][:-1] = padata[key][1:]
                        raw_data = self.x[1024 * (i - 1):1024 * i]
                        padata['max'][-1] = max(raw_data)
                        padata['min'][-1] = min(raw_data)
                        self.figure.startwork(padata, ['max', 'min'])
                        time.sleep(self.importwavspreed / self.figure.settintparameter['importwavspreed'])

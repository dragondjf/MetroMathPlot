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

from guiutil import *
from figurewidget import FigureWidget
import configdialog
import util
from cache import padict


timeinteral = 100


class DataShowPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DataShowPage, self).__init__(parent)
        self.parent = parent
        self.createLeftToolBar()
        self.createTopToolBar()

        # self.manager = PlotManager(self)

        self.fvbox = QtGui.QVBoxLayout()
        self.fvbox.addWidget(self.toptoolbar)

        i = 0
        self.createPlotFig(i, self.fvbox)

        if self.fvbox.count() <= 2:
            index = self.fvbox.count() - 2
            plotfig = getattr(self, 'plotfig%d' % index)
            getattr(plotfig, 'HideButton').setEnabled(False)

        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(self.navigation)
        self.mainLayout.addLayout(self.fvbox)
        self.setLayout(self.mainLayout)
        self.layout().setContentsMargins(0, 0, 10, 10)

        self.navigation_flag = True   # 导航标志，初始化时显示导航
        set_skin(self, os.sep.join(['skin', 'qss', 'Metroform.qss']))

    def createLeftToolBar(self):
        navbutton = ['Start', 'Pause', 'Add', 'Show']
        self.buttontext = {
            'Start': u'开始',
            'Pause': u'暂停',
            'Add': u'增加',
            'Show': u"显示"
        }
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QVBoxLayout()

        for item in navbutton:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(self.buttontext[item]))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)

        getattr(self, 'StartButton').clicked.connect(self.startHandler)
        getattr(self, 'PauseButton').clicked.connect(self.pauseHandler)
        getattr(self, 'AddButton').clicked.connect(self.addHandler)
        getattr(self, 'ShowButton').clicked.connect(self.ShowHandler)

    def createTopToolBar(self):
        toolbar = QtGui.QToolBar()
        toolbar.setObjectName("PlotToolBar")
        self.point_numLabel = QtGui.QLabel(u"显示波形点数")
        self.xrange_box = QtGui.QSpinBox()
        self.xrange_box.setMinimum(1)
        self.xrange_box.setMaximum(4096)
        self.xrange_box.setSingleStep(300)
        self.xrange_box.setValue(300)
        toolbar.addWidget(self.point_numLabel)
        toolbar.addWidget(self.xrange_box)

        self.xrange_box.valueChanged.connect(self.pointchange)

        self.toptoolbar = toolbar

    def startHandler(self):
        for index in range(self.fvbox.count() - 1):
            plotfig = getattr(self, 'plotfig%d' % index)
            plotfig.startHandler()

        getattr(self, 'StartButton').setEnabled(False)
        getattr(self, 'PauseButton').setEnabled(True)

    def pauseHandler(self):
        for index in range(self.fvbox.count() - 1):
            plotfig = getattr(self, 'plotfig%d' % index)
            plotfig.pauseHandler()

        getattr(self, 'StartButton').setEnabled(True)
        getattr(self, 'PauseButton').setEnabled(False)

    def addHandler(self):
        i = self.fvbox.count() - 1
        self.createPlotFig(i, self.fvbox)

        for index in range(self.fvbox.count() - 1):
            plotfig = getattr(self, 'plotfig%d' % index)
            getattr(plotfig, 'HideButton').setEnabled(True)
        if i == 3:
            getattr(self, 'AddButton').setEnabled(False)

    def ShowHandler(self):
        for index in range(self.fvbox.count() - 1):
            plotfig = getattr(self, 'plotfig%d' % index)
            if not plotfig.isVisible():
                plotfig.setVisible(True)
                plotfig.timer = plotfig.startTimer(timeinteral)

    def createPlotFig(self, index, fvbox):
        setattr(self, 'plotfig%d' % index, WaveFigure(point_num=self.xrange_box.value()))
        plot = getattr(self, 'plotfig%d' % index)
        plot.setObjectName('WaveMatPlotLibFigure%d' % index)
        fvbox.addWidget(plot)

    def pointchange(self, i):
        for index in range(self.fvbox.count() - 1):
            plotfig = getattr(self, 'plotfig%d' % index)
            plotfig.point_num = i


class PlotWidget(QtGui.QWidget):
    """
    Filter testing widget
    parent: parent widget (QWidget)
    x, y: NumPy arrays
    func: function object (the signal filter to be tested)
    """
    def __init__(self, parent=None, x=[], y=[], func=None, point_num=300):
        super(PlotWidget, self).__init__(parent)
        self.x = x
        self.y = y
        self.func = func
        #---guiqwt curve item attribute:
        self.curve_item = None

        self.point_num = point_num
        self.setup_widget()

    def setup_widget(self):
        #---Create the plot widget:
        self.createPlotCurve()
        self.createCtrlWidget()

        vlayout = QtGui.QHBoxLayout()
        vlayout.addWidget(self.curvewidget)
        vlayout.addWidget(self.ctrlwidget)
        self.setLayout(vlayout)

    def createPlotCurve(self):
        curvewidget = FigureWidget(self)
        self.curvewidget = curvewidget

    def createCtrlWidget(self):
        self.ctrlbuttons = [['DataSource', 'Hide'], ['Start', 'Pause']]
        self.buttontext = {
            'DataSource': u"数据\n来源",
            'Start': u'开始',
            'Pause': u'暂停',
            'Hide': u'隐藏',
        }
        self.ctrlwidget = QtGui.QWidget()
        navigationLayout = QtGui.QGridLayout()

        for buttons in self.ctrlbuttons:
            for item in buttons:
                button = item + 'Button'
                setattr(self, button, QtGui.QPushButton(self.buttontext[item]))
                getattr(self, button).setObjectName('Plot%s' % button)
                navigationLayout.addWidget(getattr(self, button), self.ctrlbuttons.index(buttons), buttons.index(item))

        self.ctrlwidget.setLayout(navigationLayout)
        getattr(self, 'StartButton').setEnabled(False)
        getattr(self, 'PauseButton').setEnabled(False)
        set_skin(self.ctrlwidget, os.sep.join(['skin', 'qss', 'MetroGuiQwtPlot.qss']))


class WaveFigure(PlotWidget):
    def __init__(self, point_num=300):
        super(WaveFigure, self).__init__(point_num=point_num)

        configdlg = configdialog.ConfigDialog()
        self.settingdialog = configdialog.ChildDialog(None, configdlg)
        QtCore.QObject.connect(getattr(self.settingdialog, 'Ok' + 'Button'), QtCore.SIGNAL('clicked()'), configdlg, QtCore.SLOT('save_settings()'))  # 点击弹出窗口OkButton，执行保存参数函数
        QtCore.QObject.connect(self.settingdialog.child, QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('settings(PyQt_PyObject)'))  # 交互管理窗口获取保存的配置

        getattr(self, 'DataSourceButton').clicked.connect(self.datafromHandler)
        getattr(self, 'HideButton').clicked.connect(self.hideHandler)
        getattr(self, 'StartButton').clicked.connect(self.startHandler)
        getattr(self, 'PauseButton').clicked.connect(self.pauseHandler)

    def startwork(self, padata, showf):
        self.curvewidget.ax.clear()
        for key in showf:
            if len(showf) == 1:
                color = ['r']
            elif len(showf) == 2:
                color = ['r', 'b']
            elif len(showf) == 3:
                color = ['r', 'g', 'b']
            self.curvewidget.ax.plot(padata[key][-self.point_num:], color=color[showf.index(key)])
        self.curvewidget.fig.canvas.draw()

    def datafromHandler(self):
        self.setdialogshow(self.objectName())

    def setdialogshow(self, objectname):
        self.settingdialog.child.boundfig(str(objectname))
        mainwindow = self.parent().parent
        self.settingdialog.setGeometry(mainwindow.geometry())
        movecenter(self.settingdialog)
        self.settingdialog.show()
        self.settingdialog.fadeInWidget()

    def hideHandler(self):
        self.setVisible(False)
        if hasattr(self, 'timer'):
            self.killTimer(self.timer)

    def startHandler(self):
        getattr(self, 'StartButton').setEnabled(False)
        getattr(self, 'PauseButton').setEnabled(True)
        self.timer = self.startTimer(timeinteral)

    def pauseHandler(self):
        if hasattr(self, 'timer'):
            self.killTimer(self.timer)
        getattr(self, 'PauseButton').setEnabled(False)
        getattr(self, 'StartButton').setEnabled(True)

    @QtCore.pyqtSlot(dict)
    def settings(self, kargs):
        self.settintparameter = kargs
        if 'wavpath' in kargs:
            self.wavfiles = util.FilenameFilter(util.path_match_platform(self.settintparameter['wavpath']))
            if not hasattr(self, 'datahandler'):
                self.datahandler = WaveReplayHandler(self.objectName(), self.wavfiles, self.settintparameter['importwavspreed'])
        else:
            if not hasattr(self, 'datahandler'):
                self.datahandler = WaveThreadHandler(self)

        if 'featurevalue' in self.settintparameter:
            showf = []
            flags = self.settintparameter['featurevalue']
            for key in flags:
                    if type(flags[key]) is bool and flags[key]:
                        showf.append(key)
            self.showf = showf
        else:
            self.showf = ['max', 'min']
        getattr(self, 'StartButton').setEnabled(True)

    def timerEvent(self, event):
        if self.objectName() in padict:
            self.startwork(padict[self.objectName()], self.showf)
        else:
            self.killTimer(self.timer)


class WaveThreadHandler(threading.Thread):
    def __init__(self, figure):
        threading.Thread.__init__(self)
        self.cmd_queue = Queue.Queue()
        self.figure = figure
        self.addr = self.figure.settintparameter['addr']
        self.paid = self.figure.settintparameter['_id']
        self.featurevalueflags = self.figure.settintparameter['featurevalue']
        self.setDaemon(True)
        self.start()

    def run(self):
        try:
            ws = websocket.create_connection("ws://%s/waves/%s" % (self.addr, self.paid))
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
                    ws = websocket.create_connection("ws://%s/waves/%s" % (self.addr, self.paid))
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
            ws = websocket.create_connection("ws://192.168.10.226:9000/waves/%s" % self.paid)
            print ws
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
    def __init__(self, figurename, wavfiles, importspreed):
        threading.Thread.__init__(self)
        self.figurename = figurename
        self.wavfiles = wavfiles
        self.importspreed = importspreed
        self.importwavspreed = 0.2
        self.setDaemon(True)
        self.start()

    def run(self):
        import algorithm
        padata = algorithm.creat_data(algorithm.Names)
        while True:
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
                        padict.update({self.figurename: padata})
                        time.sleep(self.importwavspreed / self.importspreed)

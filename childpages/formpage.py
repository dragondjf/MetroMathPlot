#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore

from guiqwt.plot import CurveWidget
from guiqwt.builder import make
import guiqwt

from guiutil import *
import util
import configdialog
from appserver.wavehandler import WaveReplayHandler, WaveThreadHandler
from cache import padict

timeinteral = 100


class FormPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FormPage, self).__init__(parent)
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
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroPlotItemRightControl.qss']))

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
        plot.setObjectName('WaveGuiQwtFigure%d' % index)
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
        curvewidget = CurveWidget(self)
        curvewidget.register_all_curve_tools()
        curvewidget.plot.set_antialiasing(True)

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
        set_skin(self.ctrlwidget, os.sep.join(['skin', 'qss', 'MetroPlotLeftControl.qss']))


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

    def startwork(self, padata, showf, color):
        for key in showf:
            if not hasattr(self, key + 'item'):
                setattr(self, key + 'item', make.curve(range(self.point_num), padata[key][-self.point_num:], color=color[showf.index(key)]))
                self.curvewidget.plot.add_item(getattr(self, key + 'item'))
            else:
                for key in showf:
                    getattr(self, key + 'item').set_data(range(self.point_num), padata[key][-self.point_num:])

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
                self.datahandler = WaveThreadHandler(self.objectName(), self.settintparameter)

        if 'featurevalue' in self.settintparameter:
            showf = []
            flags = self.settintparameter['featurevalue']
            for key in flags:
                    if type(flags[key]) is bool and flags[key]:
                        showf.append(key)
            self.showf = showf
        else:
            self.showf = ['max', 'min']

        if len(self.showf) == 1:
            color = ['r']
        elif len(self.showf) == 2:
            color = ['r', 'b']
        elif len(self.showf) == 3:
            color = ['r', 'b', 'g']

        self.color = color

        getattr(self, 'StartButton').setEnabled(True)

    def timerEvent(self, event):
        if self.objectName() in padict:
            self.startwork(padict[self.objectName()], self.showf, self.color)
            for item in self.curvewidget.plot.get_items():
                if isinstance(item, guiqwt.curve.CurveItem):
                    item.plot().do_autoscale()
        else:
            self.killTimer(self.timer)

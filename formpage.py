#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore

from array import array
from math import sin, cos
import numpy as np
from guiqwt.plot import PlotManager, CurvePlot
from guiqwt.plot import CurveWidget
from guiqwt.builder import make
import guiqwt
from guiutil import set_skin, movecenter
import util
import configdialog
from datashowpage import WaveReplayHandler, WaveThreadHandler

PLOT_DEFINE = [[u"sin1f", u"cos1f"], [u"sin3f", u"cos3f"], [u"sin合成", u"cos合成"]]
COLORS = ["blue", "red"]
DT = 0.001


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

        configdlg = configdialog.ConfigDialog()
        self.settingdialog = configdialog.ChildDialog(None, configdlg)
        QtCore.QObject.connect(getattr(self.settingdialog, 'Ok' + 'Button'), QtCore.SIGNAL('clicked()'), configdlg, QtCore.SLOT('save_settings()'))  # 点击弹出窗口OkButton，执行保存参数函数
        # QtCore.QObject.connect(self.settingdialog.child, QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('settings(PyQt_PyObject)'))  # 交互管理窗口获取保存的配置

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
        set_skin(self.navigation, os.sep.join(['skin', 'qss', 'Metroform.qss']))

        getattr(self, 'AddButton').clicked.connect(self.addPlotFig)
        getattr(self, 'ShowButton').clicked.connect(self.ShowPlotFig)

    def createTopToolBar(self):
        toolbar = QtGui.QToolBar()
        self.auto_yrange_checkbox = QtGui.QCheckBox(u"Y轴自动调节")
        self.auto_xrange_checkbox = QtGui.QCheckBox(u"X轴自动调节")
        self.xrange_box = QtGui.QSpinBox()
        self.xrange_box.setMinimum(5)
        self.xrange_box.setMaximum(50)
        self.xrange_box.setValue(10)
        self.auto_xrange_checkbox.setChecked(True)
        self.auto_yrange_checkbox.setChecked(True)
        toolbar.addWidget(self.auto_yrange_checkbox)
        toolbar.addWidget(self.auto_xrange_checkbox)
        toolbar.addWidget(self.xrange_box)
        self.toptoolbar = toolbar

    def addPlotFig(self):
        i = self.fvbox.count() - 1
        self.createPlotFig(i, self.fvbox)

        for index in range(self.fvbox.count() - 1):
            plotfig = getattr(self, 'plotfig%d' % index)
            getattr(plotfig, 'HideButton').setEnabled(True)

    def ShowPlotFig(self):
        for index in range(self.fvbox.count() - 1):
            plotfig = getattr(self, 'plotfig%d' % index)
            if not plotfig.isVisible():
                plotfig.setVisible(True)
                plotfig.timer = plotfig.startTimer(200)

    def createPlotFig(self, index, fvbox):
        setattr(self, 'plotfig%d' % index, WaveFigure())
        plot = getattr(self, 'plotfig%d' % index)
        plot.setObjectName('WaveFigure%d' % index)
        fvbox.addWidget(plot)
        # manager.register_standard_tools()
        # manager.get_default_tool().activate()

        # style = ""
        # for i in range(self.fvbox.count() - 1):
        #     style += "QPushButton#PlotButton%d{height:%dpx}" % (i, 1000)

        # set_skin(self, os.sep.join(['skin', 'qss', 'Metroform.qss']), style)


class PlotWidget(QtGui.QWidget):
    """
    Filter testing widget
    parent: parent widget (QWidget)
    x, y: NumPy arrays
    func: function object (the signal filter to be tested)
    """
    def __init__(self, parent=None, x=[], y=[], func=None):
        super(PlotWidget, self).__init__(parent)
        self.x = x
        self.y = y
        self.func = func
        #---guiqwt curve item attribute:
        self.curve_item = None
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
        set_skin(self.ctrlwidget, os.sep.join(['skin', 'qss', 'MetroGuiQwtPlot.qss']))


class WaveFigure(PlotWidget):
    def __init__(self):
        super(WaveFigure, self).__init__()

        configdlg = configdialog.ConfigDialog()
        self.settingdialog = configdialog.ChildDialog(None, configdlg)
        QtCore.QObject.connect(getattr(self.settingdialog, 'Ok' + 'Button'), QtCore.SIGNAL('clicked()'), configdlg, QtCore.SLOT('save_settings()'))  # 点击弹出窗口OkButton，执行保存参数函数
        QtCore.QObject.connect(self.settingdialog.child, QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('settings(PyQt_PyObject)'))  # 交互管理窗口获取保存的配置

        getattr(self, 'DataSourceButton').clicked.connect(self.datafromHandler)
        getattr(self, 'HideButton').clicked.connect(self.hideHandler)
        getattr(self, 'StartButton').clicked.connect(self.startHandler)
        getattr(self, 'PauseButton').clicked.connect(self.pauseHandler)

    def startwork(self, padata, showf):
        for key in showf:
            if not hasattr(self, key + 'item'):
                setattr(self, key + 'item', make.curve(range(300), padata[key][-300:]))
                self.curvewidget.plot.add_item(getattr(self, key + 'item'))
            else:
                for key in showf:
                    getattr(self, key + 'item').set_data(range(300), padata[key][-300:])

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
        self.killTimer(self.timer)

    def startHandler(self):
        self.timer = self.startTimer(200)
        getattr(self, 'StartButton').setEnabled(False)
        getattr(self, 'PauseButton').setEnabled(True)

    def pauseHandler(self):
        self.killTimer(self.timer)
        getattr(self, 'PauseButton').setEnabled(False)
        getattr(self, 'StartButton').setEnabled(True)

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

    def timerEvent(self, event):
        for item in self.curvewidget.plot.get_items():
            if isinstance(item, guiqwt.curve.CurveItem):
                item.plot().do_autoscale()

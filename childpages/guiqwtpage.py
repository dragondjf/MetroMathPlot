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
import plotpage
from cache import padict


class GuiQwtPage(plotpage.PlotPage):
    def __init__(self, parent=None):
        super(GuiQwtPage, self).__init__(parent)
        pass

    def createPlotFig(self, index, fvbox):
        setattr(self, 'plotfig%d' % index, WaveFigure(point_num=self.xrange_box.value()))
        plot = getattr(self, 'plotfig%d' % index)
        plot.setObjectName('WaveGuiQwtFigure%d' % index)
        fvbox.addWidget(plot)


class WaveFigure(plotpage.PlotFigure):
    def __init__(self, point_num=300):
        super(WaveFigure, self).__init__(point_num=point_num)
        self.plotmode = "by timer"

    def timerEvent(self, event):
        if self.objectName() in padict:
            self.startwork(padict[self.objectName()], self.showf, self.color)
        else:
            self.killTimer(self.timer)

    def startwork(self, padata, showf, color):
        for key in showf:
            if not hasattr(self, key + 'item'):
                setattr(self, key + 'item', make.curve(range(self.point_num), padata[key][-self.point_num:], color=color[showf.index(key)]))
                self.curvewidget.plot.add_item(getattr(self, key + 'item'))
            else:
                for key in showf:
                    getattr(self, key + 'item').set_data(range(self.point_num), padata[key][-self.point_num:])

        for item in self.curvewidget.plot.get_items():
            if isinstance(item, guiqwt.curve.CurveItem):
                item.plot().do_autoscale()

    @QtCore.pyqtSlot()
    def refresh(self):
        if hasattr(self, "datahandler"):
            if self.datahandler.event.isSet():
                padata = padict[self.objectName()]
                showf = self.showf
                color = self.color
                for key in showf:
                    if not hasattr(self, key + 'item'):
                        setattr(self, key + 'item', make.curve(range(self.point_num), padata[key][-self.point_num:], color=color[showf.index(key)]))
                        self.curvewidget.plot.add_item(getattr(self, key + 'item'))
                    else:
                        for key in showf:
                            getattr(self, key + 'item').set_data(range(self.point_num), padata[key][-self.point_num:])

    def createPlotCurve(self):
        curvewidget = CurveWidget(self)
        curvewidget.register_all_curve_tools()
        curvewidget.plot.set_antialiasing(True)
        self.curvewidget = curvewidget

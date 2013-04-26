#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from PyQt4 import QtGui
from PyQt4 import QtCore


from guiutil import *
from figurewidget import FigureWidget
import configdialog

import plotpage
from cache import padict
import util


class MatPlotLibPage(plotpage.PlotPage):
    def __init__(self, parent=None):
        super(MatPlotLibPage, self).__init__(parent)
        pass

    def createPlotFig(self, index, fvbox):
        setattr(self, 'plotfig%d' % index, WaveFigure(point_num=self.xrange_box.value()))
        plot = getattr(self, 'plotfig%d' % index)
        plot.setObjectName('WaveMatPlotLibFigure%d' % index)
        fvbox.addWidget(plot, stretch=1)


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
        self.curvewidget.ax.clear()
        for key in showf:
            self.curvewidget.ax.plot(padata[key][-self.point_num:], color=color[showf.index(key)])
        self.curvewidget.fig.canvas.draw()

    @QtCore.pyqtSlot()
    def refresh(self):
        if hasattr(self, "datahandler"):
            if self.datahandler.event.isSet():
                padata = padict[self.objectName()]
                showf = self.showf
                color = self.color
                self.curvewidget.ax.clear()
                for key in showf:
                    self.curvewidget.ax.plot(padata[key][-self.point_num:], color=color[showf.index(key)])
                self.curvewidget.fig.canvas.draw()

    def createPlotCurve(self):
        curvewidget = FigureWidget(self)
        self.curvewidget = curvewidget

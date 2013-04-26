#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from guiutil import *
import configdialog

import plotpage
import pyqtgraph as pg
from cache import padict
import util


class PyQtGraphPage(plotpage.PlotPage):
    def __init__(self, parent=None):
        super(PyQtGraphPage, self).__init__(parent)
        pass

    def createPlotFig(self, index, fvbox):
        setattr(self, 'plotfig%d' % index, WaveFigure(point_num=self.xrange_box.value()))
        plot = getattr(self, 'plotfig%d' % index)
        plot.setObjectName('WaveQtGrapheFigure%d' % index)
        fvbox.addWidget(plot)


class WaveFigure(plotpage.PlotFigure):
    def __init__(self, point_num=300):
        super(WaveFigure, self).__init__(point_num=point_num)
        self.plotmode = "by timer"

    @QtCore.pyqtSlot()
    def refresh(self):
        if hasattr(self, "datahandler"):
            if self.datahandler.event.isSet():
                padata = padict[self.objectName()]
                showf = self.showf
                color = self.color
                for key in showf:
                    if not hasattr(self, key + 'item'):
                        setattr(self, key + 'item', pg.PlotCurveItem(padata[key][-self.point_num:], pen=color[showf.index(key)]))
                        self.curvewidget.addItem(getattr(self, key + 'item'))
                        getattr(self, key + 'item').setData(padata[key][-self.point_num:])
                    else:
                        for key in showf:
                            getattr(self, key + 'item').setData(padata[key][-self.point_num:])

    def timerEvent(self, event):
        if self.objectName() in padict:
            self.startwork(padict[self.objectName()], self.showf, self.color)
        else:
            self.killTimer(self.timer)

    def startwork(self, padata, showf, color):
        for key in showf:
            if not hasattr(self, key + 'item'):
                setattr(self, key + 'item', pg.PlotCurveItem(padata[key][-self.point_num:], pen=color[showf.index(key)]))
                self.curvewidget.addItem(getattr(self, key + 'item'))
                getattr(self, key + 'item').setData(padata[key][-self.point_num:])
            else:
                for key in showf:
                    getattr(self, key + 'item').setData(padata[key][-self.point_num:])

    def mouseMoved(self, evt):
        pos = evt  ## using signal proxy turns original arguments into a tuple
        plotItem = self.curvewidget.plotItem
        if plotItem.sceneBoundingRect().contains(pos):
            mousePoint = plotItem.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            title = []
            if hasattr(self, 'showf'):
                for key in self.showf:
                    if hasattr(self, key + 'item'):
                        plotcurveItem = getattr(self, key + 'item')
                        xData, yData = plotcurveItem.getData()
                        if index > 0 and index < len(xData):
                            if self.color[self.showf.index(key)] is 'r':
                                color = 'red'
                            elif self.color[self.showf.index(key)] is 'g':
                                color = 'green'
                            elif self.color[self.showf.index(key)] is 'b':
                                color = 'blue'
                            title.append("<span style='color: %s'>%s=%d</span>" % (color, key, yData[index]))
                plotItem.setTitle("<span style='font-size: 12pt'>%s=%d, " % ('i', index) + ' ,'.join(title))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def createPlotCurve(self):
        self.curvewidget = pg.PlotWidget(self)

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)

        self.curvewidget.plotItem.addItem(self.vLine, ignoreBounds=True)
        self.curvewidget.plotItem.addItem(self.hLine, ignoreBounds=True)

        self.curvewidget.plotItem.setAutoVisible(y=True)
        self.curvewidget.plotItem.setLabels(left="<span style='font-size: 12pt'> left", bottom="<span style='font-size: 12pt'> bottom", right='right', top='top')
        self.curvewidget.plotItem.scene().sigMouseMoved.connect(self.mouseMoved) #鼠标移动响应

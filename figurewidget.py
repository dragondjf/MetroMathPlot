#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure


class FigureWidget(QtGui.QWidget):
    """Matplotlib Figure widget to display CPU utilization"""

    def __init__(self, parent=None, title="Figrue", point_num=300, x=[], y=[]):
        # save the current CPU info (used by updating algorithm)R
        super(FigureWidget, self).__init__(parent)

        # 数据初始化
        self.x = x
        self.y = y
        # 绘图控件初始化
        self.fig = Figure()
        self.fig.set_figwidth(1000)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.mpl_toolbar.setVisible(False)

        # 控件摆放设置
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        # vbox.addLayout(hbox)
        self.setLayout(vbox)

        # 创建右键菜单
        # self.createContextMenu()

        # 设置子图属性
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(title)
        # self.ax.patch.set_facecolor('#888888')
        self.ax.autoscale_view()
        self.data, = self.ax.plot(self.x, self.y, label='analysis')
        self.ax.legend()
        # # force a redraw of the Figure

        self.fig.canvas.draw()

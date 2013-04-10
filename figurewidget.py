#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from configdialog import QInputDialog, QMessageBox


class FigureWidget(QtGui.QWidget):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, title="Figrue", point_num=300, x=[], y=[]):
        # save the current CPU info (used by updating algorithm)R
        super(FigureWidget, self).__init__()

        # 数据初始化
        self.x = x
        self.y = y
        # 绘图控件初始化
        self.fig = Figure()
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
        self.createContextMenu()

        # 设置子图属性
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(title)
        # self.ax.patch.set_facecolor('#888888')
        self.ax.autoscale_view()
        self.data, = self.ax.plot(self.x, self.y, label='analysis')
        self.ax.legend()
        # # force a redraw of the Figure

        self.fig.canvas.draw()

        self.plotflag = False
        # 与右键有关的初始化设置
        self.point_num = point_num   # 默认显示点数
        self.pauseflag = False  # 默认不暂停
        # initialize the iteration counter
        self.cnt = 0

        # 开启定时器，timer_interval间隔触发一次事件
        self.timerEvent(None)
        self.timer_interval = 100
        # self.startwork()

    @QtCore.pyqtSlot(dict)
    def startwork(self, data):
        if self.plotflag:
            self.ax.clear()
            self.ax.plot(data['max'][-self.point_num:], color='r')
            self.ax.plot(data['min'][-self.point_num:], color='b')
            self.fig.canvas.draw()

    def set_Xdata(self, x):
        self.x = x

    def set_Ydata(self, y):
        self.y = y

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

        self.action_pointnum = self.contextMenu.addAction(u'设置数据显示点数')
        self.action_pause = self.contextMenu.addAction(u'暂停')
        self.action_NavigationToolbar = self.contextMenu.addAction(u'显示绘图导航')
        # self.action_addaxes = self.contextMenu.addAction(u'增加子图')
        self.action_delete = self.contextMenu.addAction(u'删除此图')
        # 将动作与处理函数相关联
        # 这里为了简单，将所有action与同一个处理函数相关联
        # 当然也可以将他们分别与不同函数关联，实现不同的功能
        self.action_pointnum.triggered.connect(self.pointnumHandler)
        self.action_pause.triggered.connect(self.pauseHandler)
        self.action_NavigationToolbar.triggered.connect(self.NavigationToolbarHandler)
        # self.action_addaxes.triggered.connect(self.addaxesHandler)
        self.action_delete.triggered.connect(self.deleteHandler)

    def showContextMenu(self, pos):
        '''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        coursePoint = QtGui.QCursor.pos()  # 获取当前光标的位置
        self.contextMenu.move(coursePoint)
        self.contextMenu.show()

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
        self.deleteLater()

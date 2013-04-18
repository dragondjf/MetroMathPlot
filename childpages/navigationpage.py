#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from guiutil import *


class NavigationPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(NavigationPage, self).__init__(parent)
        self.parent = parent
        self.createContextMenu()

    def createContextMenu(self):
        '''
        创建右键菜单
        '''
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # 创建QMenu
        self.contextMenu = QtGui.QMenu()
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
        # self.action_pointnum.triggered.connect(self.pointnumHandler)
        # self.action_pause.triggered.connect(self.pauseHandler)
        # self.action_NavigationToolbar.triggered.connect(self.NavigationToolbarHandler)
        # # self.action_addaxes.triggered.connect(self.addaxesHandler)
        # self.action_delete.triggered.connect(self.deleteHandler)

    def showContextMenu(self, pos):
        '''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        coursePoint = QtGui.QCursor.pos()  # 获取当前光标的位置
        self.contextMenu.move(coursePoint)
        self.contextMenu.show()

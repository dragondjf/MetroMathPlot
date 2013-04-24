#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from guiutil import set_skin


class ContextMenu(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ContextMenu, self).__init__(parent)
        self.parent = parent
        # self.createContextMenu()

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

        self.action_NavigationToolbar = self.contextMenu.addAction(u'隐藏导航条')
        self.action_Navigation = self.contextMenu.addAction(u'Navigation')
        self.action_Back = self.contextMenu.addAction(u'Back')
        self.action_Forward = self.contextMenu.addAction(u'Forward')

        self.action_NavigationToolbar.triggered.connect(self.NavigationToolbarHandler)
        self.action_Navigation.triggered.connect(self.parent.backnavigationPage)
        self.action_Back.triggered.connect(self.parent.backPage)
        self.action_Forward.triggered.connect(self.parent.forwardnextPage)

    def showContextMenu(self, pos):
        '''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        coursePoint = QtGui.QCursor.pos()  # 获取当前光标的位置
        self.contextMenu.move(coursePoint)
        self.contextMenu.show()

    def NavigationToolbarHandler(self):
        '''
        导航工具条显示与隐藏
        '''
        if self.navigation.isVisible():
            self.action_NavigationToolbar.setText(u'显示导航')
            self.navigation.setVisible(False)
        else:
            self.action_NavigationToolbar.setText(u'隐藏导航')
            self.navigation.setVisible(True)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.navigation.rect().contains(event.pos()):
                self.navigation.setVisible(True)
            else:
                self.navigation.setVisible(False)

            # if self.navigation.isVisible():
            #     self.action_NavigationToolbar.setText(u'隐藏导航')
            # else:
            #     self.action_NavigationToolbar.setText(u'显示导航')


class ChildPage(ContextMenu):
    """docstring for childPage"""
    def __init__(self, parent=None, child=None):
        super(ChildPage, self).__init__(parent)
        self.parent = parent
        self.child = child
        self.createNavigation()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.navigation)
        mainLayout.addWidget(self.child)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(5, 5, 0, 0)

    def createNavigation(self):
        navbutton = ['Navigation', 'Back', 'Forward', 'Min', 'Max', 'Close']
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QHBoxLayout()

        for item in navbutton:
            button = item + 'Button'
            if item not in ['Min', 'Max', 'Close']:
                setattr(self, button, QtGui.QPushButton(item))
            else:
                setattr(self, button, QtGui.QPushButton())

            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        self.navigation.setMaximumHeight(60)
        self.navigation.setContentsMargins(0, 0, 0, 0)

        QtCore.QObject.connect(getattr(self, 'Navigation' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent, QtCore.SLOT('backnavigationPage()'))
        QtCore.QObject.connect(getattr(self, 'Back' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent, QtCore.SLOT('backPage()'))
        QtCore.QObject.connect(getattr(self, 'Forward' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent, QtCore.SLOT('forwardnextPage()'))

        QtCore.QObject.connect(getattr(self, 'Min' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent.parent(), QtCore.SLOT('showMinimized()'))
        QtCore.QObject.connect(getattr(self, 'Max' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent.parent(), QtCore.SLOT('windowMaxNormal()'))
        QtCore.QObject.connect(getattr(self, 'Close' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent.parent(), QtCore.SLOT('close()'))

        # set_skin(self, os.sep.join(['skin', 'qss', 'MetroToolBar.qss']))

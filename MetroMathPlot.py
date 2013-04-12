#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from intermanager import InteractiveManager
from effects import FaderWidget
from childpage import ChildPage
from navigationpage import NavigationPage
from homepage import HomePage
from systempage import SystemPage
from datashowpage import DataShowPage
from formpage import FormPage
from viewpage import ViewPage
from toolpage import ToolPage
from productpage import ProductPage
from helppage import HelpPage
from aboutpage import AboutPage
from guiutil import set_skin, set_bg


class MetroWindow(QtGui.QWidget):

    funcpages = {}

    def __init__(self, parent=None):
        super(MetroWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.MetroButtons = [['Home', 'System', 'DataShow'], ['Form', 'View', 'Tool'], ['Product', 'Help', 'About']]
        self.createMetroButton()

        self.pages = QtGui.QStackedWidget()

        self.pages.addWidget(self.navigationPage)

        self.createChildPages()

        self.createConnections()
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.pages)
        self.setLayout(mainLayout)

        self.faderWidget = None
        self.connect(self.pages, QtCore.SIGNAL("currentChanged(int)"), self.fadeInWidget)  # 页面切换时淡入淡出效果
        self.layout().setContentsMargins(0, 0, 0, 0)

    def createMetroButton(self):
        self.navigationPage = NavigationPage()
        buttonLayout = QtGui.QGridLayout()
        buttonLayout.setHorizontalSpacing(10)   # 设置和横向间隔像素
        buttonLayout.setVerticalSpacing(10)    # 设置纵向间隔像素
        for buttons in self.MetroButtons:
            for item in buttons:
                button = item + 'Button'
                setattr(self, button, QtGui.QPushButton(item))
                getattr(self, button).setObjectName(button)
                buttonLayout.addWidget(getattr(self, button), self.MetroButtons.index(buttons), buttons.index(item))

        self.buttonLayout = buttonLayout
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroNavigation.qss']))

        self.navigationPage.setLayout(buttonLayout)

    def createChildPages(self):
        for buttons in self.MetroButtons:
            for item in buttons:
                page = item + 'Page'
                childpage = 'child' + page
                setattr(self, page, getattr(sys.modules[__name__], page)(self))
                setattr(self, childpage, ChildPage(self, getattr(self, page)))
                self.funcpages[page] = getattr(self, page)
                self.pages.addWidget(getattr(self, childpage))

    def createConnections(self):
        for buttons in self.MetroButtons:
            for item in buttons:
                button = item + 'Button'
                getattr(self, button).clicked.connect(self.childpageChange)

    def childpageChange(self):
        currentpage = getattr(self, unicode('child' + self.sender().text()) + 'Page')
        self.pages.setCurrentWidget(currentpage)

    @QtCore.pyqtSlot()
    def backnavigationPage(self):
        self.pages.setCurrentWidget(self.navigationPage)

    @QtCore.pyqtSlot()
    def backPage(self):
        index = self.pages.currentIndex()
        if index == 0:
            self.pages.setCurrentWidget(self.navigationPage)
        else:
            self.pages.setCurrentIndex(index - 1)

    @QtCore.pyqtSlot()
    def forwardnextPage(self):
        index = self.pages.currentIndex()
        if index < 9:
            self.pages.setCurrentIndex(index + 1)
        else:
            self.pages.setCurrentWidget(self.navigationPage)

    def fadeInWidget(self, index):
        '''
            页面切换时槽函数实现淡入淡出效果
        '''
        self.faderWidget = FaderWidget(self.pages.widget(index))
        self.faderWidget.start()


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.centeralwindow = MetroWindow(self)
        self.setCentralWidget(self.centeralwindow)

        self.setWindowIcon(QtGui.QIcon('images' + os.sep + 'DMathPlot.ico'))  # 设置程序图标
        self.setGeometry(300, 300, 1200, 800)  # 初始化窗口位置和大小
        self.center()  # 将窗口固定在屏幕中间
        self.setMinimumSize(800, 600)
        self.setWindowTitle('Math Plot')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        set_skin(self, os.sep.join(['skin', 'qss', 'dragondjf.qss']))  # 设置背景图

        self.fullscreenflag = False  # 初始化时非窗口最大话标志
        self.navigation_flag = True   # 导航标志，初始化时显示导航
        self.layout().setContentsMargins(0, 0, 0, 0)

        # self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)  # 隐藏标题栏， 可以拖动边框改变大小
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 隐藏标题栏， 无法改变大小
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化
        # self.setMouseTracking(True)

    def set_background(self, bg=None):
        set_bg(self, bg)
        self.setAutoFillBackground = True

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # self.setGeometry(QtGui.QDesktopWidget().availableGeometry())

    @QtCore.pyqtSlot()
    def windowMaxNormal(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Escape:
            reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.close()
            else:
                return
        elif evt.key() == QtCore.Qt.Key_F11:
            if not self.fullscreenflag:
                self.showFullScreen()
                self.fullscreenflag = True
            else:
                self.showNormal()
                self.fullscreenflag = False
        elif evt.key() == QtCore.Qt.Key_F10:
            currentpage = self.centralWidget().pages.currentWidget()
            if hasattr(currentpage, 'navigation'):
                if self.navigation_flag:
                    currentpage.navigation.setVisible(False)
                    currentpage.action_NavigationToolbar.setText(u'显示导航')
                    self.navigation_flag = False
                else:
                    currentpage.navigation.setVisible(True)
                    currentpage.action_NavigationToolbar.setText(u'隐藏导航')
                    self.navigation_flag = True
        elif evt.key() == QtCore.Qt.Key_F9:
            currentpage = self.centralWidget().pages.currentWidget().child
            if hasattr(currentpage, 'navigation'):
                if currentpage.navigation_flag:
                    currentpage.navigation.setVisible(False)
                    currentpage.navigation_flag = False
                else:
                    currentpage.navigation.setVisible(True)
                    currentpage.navigation_flag = True
        elif evt.key() == QtCore.Qt.Key_Return:
            if isinstance(self.focusWidget(), QtGui.QPushButton):
                self.focusWidget().click()


def main():
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    interactivemanager = InteractiveManager(main, **main.centeralwindow.funcpages)
    # interactivemanager.tcpServerstart()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

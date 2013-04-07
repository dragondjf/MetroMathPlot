#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import util
from PyQt4 import QtGui
from PyQt4 import QtCore
from figurewidget import FigureWidget
from effects import FaderWidget

'''
1：不要在顶层窗口（无父类的窗口）中使用setStyleSheet() ，否则其一父窗口的背景不会改变，
    其次其子窗口的背景设置方法变得局限唯一，不能再使用其它方法！
2：如果一个一般窗口（非顶层窗口）还有子窗口，那最好不要使用setStyleSheet()来设置其背景颜色，
    因为虽然此时该窗口的背景设置是生效的，但是其子窗口的背景设置也变得局限唯一，只能使用setStyleSheet，而不能使用其它方法！
    当然：你如果就是只想使用这种方法，那也完全可以！！


说白了就是：不要再MainWindow中使用setStyleSheet()！
    而上边之所以强调拓宽子窗口设置背景的方法范围，这是
    因为：如果只能用setStyleSheet样式表来设置背景图片的话，
    该图片是无法缩放的，如果其大小与widget窗口大小不相符，则我们无法用程序来实现图片的缩放，
    除非我们直接处理图片使其大小与widget窗口相符； 而如果不局限于用setStyleSheet样式表来设置的话，
    我们可以选择用QPalette调色版，其内部setBrush()之前，我们完全可以先对图片进行scale缩放再刷到窗口上，
    这样就避免直接去处理图片，灵活性强一点！
==========================================================================
'''


def set_bg(widget, bg=None):
    '''
        设置背景颜色或者图片
    '''
    if bg is None:
        bg = QtGui.QColor('#ABABAB')
    palette = QtGui.QPalette(widget)
    palette.setBrush(widget.backgroundRole(), QtGui.QBrush(bg))
    widget.setPalette(palette)
    setattr(widget, 'bg', bg)


def set_skin(QApplication, qssfile, style=''):
    qss = QtCore.QFile(qssfile)
    qss.open(QtCore.QIODevice.ReadOnly)
    if qss.isOpen():
        QApplication.setStyleSheet(QtCore.QVariant(qss.readAll()).toString() + style)
    qss.close()


class ContextMenu(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ContextMenu, self).__init__(parent)
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

            if self.navigation.isVisible():
                self.action_NavigationToolbar.setText(u'隐藏导航')
            else:
                self.action_NavigationToolbar.setText(u'显示导航')


class childPage(ContextMenu):
    """docstring for childPage"""
    def __init__(self, parent=None, child=None):
        super(childPage, self).__init__(parent)
        self.parent = parent
        self.child = child
        self.createNavigation()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.navigation)
        mainLayout.addWidget(self.child)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def createNavigation(self):
        navbutton = ['Navigation', 'Back', 'Forward']
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QHBoxLayout()

        for item in navbutton:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(item))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        self.navigation.setMaximumHeight(60)
        self.navigation.setContentsMargins(0, 0, 0, 0)

        QtCore.QObject.connect(getattr(self, 'Navigation' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent, QtCore.SLOT('backnavigationPage()'))
        QtCore.QObject.connect(getattr(self, 'Back' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent, QtCore.SLOT('backPage()'))
        QtCore.QObject.connect(getattr(self, 'Forward' + 'Button'), QtCore.SIGNAL('clicked()'), self.parent, QtCore.SLOT('forwardnextPage()'))
        set_skin(self, os.sep.join(['skin', 'qss', 'ToolBarMetro.qss']))


class HomePage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(HomePage, self).__init__(parent)
        set_skin(self, os.sep.join(['skin', 'qss', 'dragondjf.qss']))
        set_bg(parent)
        self.initpythonGrounp()
        # self.initClientGrounp()
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.pythonGroup)
        # mainLayout.addLayout(self.clientLayout)
        mainLayout.addSpacing(12)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

    def initpythonGrounp(self):
        pythonGroup = QtGui.QGroupBox(u"自定义python环境")

        pythonpathLabel = QtGui.QLabel(u'python可执行路径：')
        self.pythonpathEdit = QtGui.QLineEdit(sys.executable)
        pythonpathButton = QtGui.QPushButton('...')
        pythonpathButton.clicked.connect(self.setpythonpath)

        pythonscriptLabel = QtGui.QLabel(u'需要编译的Python Script：')
        self.pythonscriptEdit = QtGui.QLineEdit()
        pythonscriptButton = QtGui.QPushButton('...')
        pythonscriptButton.clicked.connect(self.setpythonscript)

        pythonrunButton = QtGui.QPushButton(u'执行')
        pythonrunButton.clicked.connect(self.runscript)

        pythonLayout = QtGui.QGridLayout()
        pythonLayout.addWidget(pythonpathLabel, 0, 0)
        pythonLayout.addWidget(self.pythonpathEdit, 0, 1)
        pythonLayout.addWidget(pythonpathButton, 0, 2)

        pythonLayout.addWidget(pythonscriptLabel, 1, 0)
        pythonLayout.addWidget(self.pythonscriptEdit, 1, 1)
        pythonLayout.addWidget(pythonscriptButton, 1, 2)

        pythonLayout.addWidget(pythonrunButton, 2, 2)

        pythonGroup.setLayout(pythonLayout)

        self.pythonGroup = pythonGroup

    def initClientGrounp(self):
        self.index = 1
        clientGrounp = QtGui.QGroupBox(u'Tcp Client')

        clientIpLabel = QtGui.QLabel(u'客户端Ip地址：')
        clientPortLabel = QtGui.QLabel(u'客户端端口号：')
        self.clientIpEdit_1 = QtGui.QLineEdit()
        self.clientPortEdit_1 = QtGui.QLineEdit()

        grounpLayout = QtGui.QGridLayout()
        grounpLayout.addWidget(clientIpLabel, 0, 0, QtCore.Qt.AlignCenter)
        grounpLayout.addWidget(clientPortLabel, 0, 1, QtCore.Qt.AlignCenter)
        grounpLayout.addWidget(self.clientIpEdit_1, 1, 0)
        grounpLayout.addWidget(self.clientPortEdit_1, 1, 1)

        clientGrounp.setLayout(grounpLayout)

        buttonGrounp = QtGui.QHBoxLayout()
        addButton = QtGui.QPushButton(u'增加')
        addButton.clicked.connect(self.addclient)
        deleteButton = QtGui.QPushButton(u'删除')
        deleteButton.clicked.connect(self.deleteclient)

        buttonGrounp.addWidget(addButton)
        buttonGrounp.addWidget(deleteButton)

        clientLayout = QtGui.QVBoxLayout()
        clientLayout.addWidget(clientGrounp)
        clientLayout.addLayout(buttonGrounp)

        self.clientGrounp = clientGrounp
        self.grounpLayout = grounpLayout
        self.clientLayout = clientLayout

    def setpythonpath(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u"设置python.exe的完整路径", u'', "Python (*.exe);;All Files (*)")
        self.pythonexe = util.path_match_platform(fileName)
        self.pythonpathEdit.setText(self.pythonexe)

    def setpythonscript(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u"选择需要执行的python Script", u'', "Python Script(*.py *pyw);;All Files (*)")
        self.pythonscript = util.path_match_platform(fileName)
        self.pythonscriptEdit.setText(self.pythonscript)

    def addclient(self):
        self.index = self.index + 1
        setattr(self, 'clientIpEdit_%s' % self.index, QtGui.QLineEdit())
        setattr(self, 'clientPortEdit_%s' % self.index, QtGui.QLineEdit())
        self.grounpLayout.addWidget(getattr(self, 'clientIpEdit_%s' % self.index), self.index, 0)
        self.grounpLayout.addWidget(getattr(self, 'clientPortEdit_%s' % self.index), self.index, 1)
        self.grounpLayout.setRowStretch(self.index, 1)

    def deleteclient(self):
        if self.index == 0:
            return
        print self.grounpLayout.rowCount()
        self.grounpLayout.removeWidget(getattr(self, 'clientIpEdit_%s' % self.index))
        self.grounpLayout.removeWidget(getattr(self, 'clientPortEdit_%s' % self.index))
        self.index = self.index - 1

    def runscript(self):
        if not hasattr(self, 'pythonscript'):
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                u'请注意', u'没有可执行的python script, 请载入需要执行的脚本',
                QtGui.QMessageBox.NoButton, self)
            msgBox.addButton("&Ok", QtGui.QMessageBox.AcceptRole)
            msgBox.addButton("&Cancel", QtGui.QMessageBox.RejectRole)
            if msgBox.exec_() == QtGui.QMessageBox.AcceptRole:
                self.setpythonscript()
            else:
                return
        else:
            scriptprocee = subprocess.Popen([sys.executable, self.pythonscript], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


class SystemPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SystemPage, self).__init__(parent)
        self.parent = parent


class DataShowPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DataShowPage, self).__init__(parent)
        self.parent = parent
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)  # 设置分割窗口水平排列
        self.splitter.setOpaqueResize(True)  # 设定分割窗的分割条在拖动时是否为实时更新显示，默认True表示实时更新

        self.createToolBar()

        self.splitter_figure = QtGui.QSplitter()
        self.splitter_figure.setOrientation(QtCore.Qt.Vertical)
        self.f1 = FigureWidget('Figure 1')
        self.splitter_figure.addWidget(self.f1)

        self.splitter.addWidget(self.navigation)
        self.splitter.addWidget(self.splitter_figure)
        self.splitter.setSizes([self.width() / 4, self.width() * 3 / 4])  # 设置初始化时各个分割窗口的大小
        self.splitter.setStretchFactor(1, 1)  # 设置编号为1的控件为可伸缩控件，第二个参数为表示自适应调整，大于0表示只有为编号为1的控件会自适应调整

        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(self.splitter)
        self.setLayout(self.mainLayout)

    def createToolBar(self):
        navbutton = ['Start', 'Pause', 'Choose']
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QVBoxLayout()

        for item in navbutton:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(item))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        set_skin(self.navigation, os.sep.join(['skin', 'qss', 'MetroDataShow.qss']))


class FormPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FormPage, self).__init__(parent)
        self.parent = parent


class ViewPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ViewPage, self).__init__(parent)
        self.parent = parent


class ToolPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ToolPage, self).__init__(parent)
        self.parent = parent
        self.createButtons()

    def createButtons(self):
        self.ToolButtons = [
            [u'BackGroundColor', u'BackGroundImage'],
            ['ButtonColor', 'ButtonImage'],
            ['ToolButtonColor', 'ToolButtonImage']
        ]
        self.buttontext = {
            'BackGroundColor': u'窗口背景颜色',
            'BackGroundImage': u'窗口背景图片',
            'ButtonColor': u'磁贴背景颜色',
            'ButtonImage': u'磁贴背景图片',
            'ToolButtonColor': u'工具条背景颜色',
            'ToolButtonImage': u'工具条背景图片'
        }
        buttonLayout = QtGui.QGridLayout()
        for buttons in self.ToolButtons:
            for item in buttons:
                button = item + 'Button'
                setattr(self, button, QtGui.QPushButton(self.buttontext[item]))
                getattr(self, button).setObjectName(button)
                getattr(self, button).clicked.connect(getattr(self, 'set_' + item))
                buttonLayout.addWidget(getattr(self, button), self.ToolButtons.index(buttons), buttons.index(item))

        self.setLayout(buttonLayout)

    def set_BackGroundColor(self):
        self.colordialog = QtGui.QColorDialog()
        bgcolor = self.colordialog.getColor()
        style = 'QMainWindow {background : rgb(%s,%s,%s);}' % (bgcolor.red(), bgcolor.green(), bgcolor.blue())
        set_skin(self.parent.parent(), os.sep.join(['skin', 'qss', 'dragondjf.qss']), style)

    def set_BackGroundImage(self):
        self.openFilesPath = QtCore.QString(os.getcwd() + os.sep + 'images')
        filename = QtGui.QFileDialog.getOpenFileName(self,
            "Choose a picture", self.openFilesPath,
            "All Files (*);; Images (*.png *.bmp *.jpg)")
        style = 'QMainWindow {border-image : url(%s);}' % str(QtCore.QDir(QtCore.QDir.currentPath()).relativeFilePath(filename))
        set_skin(self.parent.parent(), os.sep.join(['skin', 'qss', 'dragondjf.qss']), style)

    def set_ButtonColor(self):
        self.colordialog = QtGui.QColorDialog()
        bgcolor = self.colordialog.getColor()
        style = 'QPushButton {background : rgb(%s,%s,%s);}' % (bgcolor.red(), bgcolor.green(), bgcolor.blue())
        set_skin(self.parent, os.sep.join(['skin', 'qss', 'NavigationMetro.qss']), style)

    def set_ButtonImage(self):
        self.openFilesPath = QtCore.QString(os.getcwd() + os.sep + 'images')
        filename = QtGui.QFileDialog.getOpenFileName(self,
            "Choose a picture", self.openFilesPath,
            "All Files (*);; Images (*.png *.bmp *.jpg)")
        style = 'QPushButton {border-image : url(%s);}' % str(QtCore.QDir(QtCore.QDir.currentPath()).relativeFilePath(filename))
        set_skin(self.parent, os.sep.join(['skin', 'qss', 'NavigationMetro.qss']), style)

    def set_ToolButtonColor(self):
        self.colordialog = QtGui.QColorDialog()
        bgcolor = self.colordialog.getColor()
        style = 'QPushButton {background : rgb(%s,%s,%s);}' % (bgcolor.red(), bgcolor.green(), bgcolor.blue())
        for item in self.parent.pages.children():
            if isinstance(item, childPage):
                set_skin(item, os.sep.join(['skin', 'qss', 'ToolBarMetro.qss']), style)

    def set_ToolButtonImage(self):
        self.openFilesPath = QtCore.QString(os.getcwd() + os.sep + 'images')
        filename = QtGui.QFileDialog.getOpenFileName(self,
            "Choose a picture", self.openFilesPath,
            "All Files (*);; Images (*.png *.bmp *.jpg)")
        style = 'QPushButton {border-image : url(%s);}' % str(QtCore.QDir(QtCore.QDir.currentPath()).relativeFilePath(filename))
        for item in self.parent.pages.children():
            if isinstance(item, childPage):
                set_skin(item, os.sep.join(['skin', 'qss', 'ToolBarMetro.qss']), style)


class ProductPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ProductPage, self).__init__(parent)
        self.parent = parent


class HelpPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(HelpPage, self).__init__(parent)
        self.parent = parent


class AboutPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(AboutPage, self).__init__(parent)
        self.parent = parent


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


class MetroWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MetroWindow, self).__init__(parent)
        self.parent = parent
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
        for buttons in self.MetroButtons:
            for item in buttons:
                button = item + 'Button'
                setattr(self, button, QtGui.QPushButton(item))
                getattr(self, button).setObjectName(button)
                buttonLayout.addWidget(getattr(self, button), self.MetroButtons.index(buttons), buttons.index(item))
        set_skin(self, os.sep.join(['skin', 'qss', 'NavigationMetro.qss']))

        self.navigationPage.setLayout(buttonLayout)

    def createChildPages(self):
        for buttons in self.MetroButtons:
            for item in buttons:
                page = item + 'Page'
                childpage = 'child' + page
                setattr(self, page, getattr(sys.modules[__name__], page)(self))
                setattr(self, childpage, childPage(self, getattr(self, page)))
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
        self.setWindowTitle("Config Dialog")
        self.setWindowIcon(QtGui.QIcon('images' + os.sep + 'DMathPlot.ico'))  # 设置程序图标
        self.setGeometry(300, 300, 800, 600)  # 初始化窗口位置和大小
        self.center()  # 将窗口固定在屏幕中间
        self.setMinimumSize(800, 600)
        self.setWindowTitle('Math Plot')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        set_skin(self, os.sep.join(['skin', 'qss', 'dragondjf.qss']))  # 设置背景图

        self.fullscreenflag = False  # 初始化时非窗口最大话标志
        self.navigation_flag = True   # 导航标志，初始化时显示导航
        self.layout().setContentsMargins(0, 0, 0, 0)

    def set_background(self, bg=None):
        set_bg(self, bg)
        self.setAutoFillBackground = True

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # self.setGeometry(QtGui.QDesktopWidget().availableGeometry())

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
            if hasattr(self.centralWidget().pages.currentWidget(), 'navigation'):
                if self.navigation_flag:
                    self.centralWidget().pages.currentWidget().navigation.setVisible(False)
                    self.centralWidget().pages.currentWidget().action_NavigationToolbar.setText(u'显示导航')
                    self.navigation_flag = False
                else:
                    self.centralWidget().pages.currentWidget().navigation.setVisible(True)
                    self.centralWidget().pages.currentWidget().action_NavigationToolbar.setText(u'隐藏导航')
                    self.navigation_flag = True
        elif evt.key() == QtCore.Qt.Key_Return:
            if isinstance(self.focusWidget(), QtGui.QPushButton):
                self.focusWidget().click()


def main():
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

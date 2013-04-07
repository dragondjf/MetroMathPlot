#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from guiutil import set_skin, set_bg


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
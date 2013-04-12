#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

import os
import sys
from PyQt4 import QtCore, QtGui
from effects import FaderWidget
from guiutil import set_skin
from algorithm import Names


class ConfigurationPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ConfigurationPage, self).__init__(parent)

        self.configGroup = QtGui.QGroupBox(u"设置回演参数")

        self.ipLabel = QtGui.QLabel(u"IP地址：")
        self.ipEdit = QtGui.QLineEdit(u"192.168.100.100")

        self.channelLabel = QtGui.QLabel(u"通道号：")
        self.channelCombo = QtGui.QComboBox()
        self.channelCombo.addItem('1')
        self.channelCombo.addItem('2')
        self.channelCombo.addItem('3')
        self.channelCombo.addItem('4')

        self.wavpathLabel = QtGui.QLabel(u"选择日志路径：")
        self.wavpathButton = QtGui.QPushButton(u'...')
        self.wavpathButton.clicked.connect(self.setExistingDirectory)
        self.wavpathEdit = QtGui.QLineEdit(os.getcwd() + os.sep + 'wavs')
        self.wavpathHLayout = QtGui.QGridLayout()
        self.wavpathHLayout.addWidget(self.wavpathEdit, 0, 0)
        self.wavpathHLayout.addWidget(self.wavpathButton, 0, 1)

        self.startTimeLabel = QtGui.QLabel(u"样本开始时间：")
        self.startTimeEdit = QtGui.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.startTimeEdit.setDisplayFormat("yyyy-MM-dd: hh-mm-ss")
        self.endTimeLabel = QtGui.QLabel(u"样本截止时间：")
        self.endTimeEdit = QtGui.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.endTimeEdit.setDisplayFormat("yyyy-MM-dd: hh-mm-ss")

        self.importWavSpreedLabel = QtGui.QLabel(u"导入速度：")
        self.importWavSpreedCombo = QtGui.QComboBox()
        self.importWavSpreedCombo.addItem('1')
        self.importWavSpreedCombo.addItem('2')
        self.importWavSpreedCombo.addItem('3')
        self.importWavSpreedCombo.addItem('4')

        self.SetPALayout = QtGui.QGridLayout()
        self.SetPALayout.addWidget(self.ipLabel, 0, 0)
        self.SetPALayout.addWidget(self.ipEdit, 0, 1)
        self.SetPALayout.addWidget(self.channelLabel, 1, 0)
        self.SetPALayout.addWidget(self.channelCombo, 1, 1)
        self.SetPALayout.addWidget(self.wavpathLabel, 2, 0)
        self.SetPALayout.addLayout(self.wavpathHLayout, 2, 1)
        self.SetPALayout.addWidget(self.startTimeLabel, 3, 0)
        self.SetPALayout.addWidget(self.startTimeEdit, 3, 1)
        self.SetPALayout.addWidget(self.endTimeLabel, 4, 0)
        self.SetPALayout.addWidget(self.endTimeEdit, 4, 1)
        self.SetPALayout.addWidget(self.importWavSpreedLabel, 5, 0)
        self.SetPALayout.addWidget(self.importWavSpreedCombo, 5, 1)

        self.configGroup.setLayout(self.SetPALayout)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.configGroup)
        self.mainLayout.addStretch(1)

        self.setLayout(self.mainLayout)

    def setExistingDirectory(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self, u"选择日志路径", os.getcwd(), options)
        self.wavpathEdit.setText(directory)


class FsWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FsWidget, self).__init__(parent)
        fsGroup = QtGui.QGroupBox(u"实时波形设置")
        PALabel = QtGui.QLabel(u"选择防区：")
        self.PACombo = QtGui.QComboBox()
        self.initfromMongoDB()

        featurevalueLabel = QtGui.QLabel(u'选择特征值：')
        self.featurevalueWidget = self.creatFeatureValueWidget()

        pointnumberLabel = QtGui.QLabel(u'显示波形点数：')
        pointnumberEdit =  QtGui.QSpinBox()
        pointnumberEdit.setMaximum(4096)
        pointnumberEdit.setValue(300)
        pointnumberEdit.setMinimum(1)
        self.pointnumberEdit = pointnumberEdit

        fsLayout = QtGui.QGridLayout()
        fsLayout.addWidget(PALabel, 0, 0)
        fsLayout.addWidget(self.PACombo, 0, 1)
        fsLayout.addWidget(featurevalueLabel, 1, 0)
        fsLayout.addWidget(self.featurevalueWidget, 1, 1)
        fsLayout.addWidget(pointnumberLabel, 2, 0)
        fsLayout.addWidget(self.pointnumberEdit, 2, 1)
        fsGroup.setLayout(fsLayout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(fsGroup)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

    def creatFeatureValueWidget(self):
        featurevalueWidget = QtGui.QWidget()
        fsGridLoyout = QtGui.QGridLayout()
        Names = [
            ['max', 'min', 'davg'] + ['f%d' % n for n in range(0, 8)] + ['time'], 
            ['alarmflag', 'alarmrate'] + ['data%d' % n for n in range(0, 10)]
        ]
        for keys in Names:
            for key in keys:
                setattr(self, key + 'CheckBox', QtGui.QCheckBox(key))
                getattr(self, key + 'CheckBox').setObjectName(key + 'CheckBox')
                fsGridLoyout.addWidget(getattr(self, key + 'CheckBox'), Names.index(keys), keys.index(key))
        featurevalueWidget.setLayout(fsGridLoyout)
        return featurevalueWidget

    def initfromMongoDB(self):
        self.PAlist = {}
        from mongokit import Connection
        connection = Connection()
        for docment in connection['gsd']['PA_Col'].find():
            self.PACombo.addItem(docment['gno'])
            self.PAlist[docment['gno']] = str(docment['_id'])


class FsPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FsPage, self).__init__(parent)

        self.fswidget0 = FsWidget()

        self.createNavigation()
        getattr(self, 'AddButton').clicked.connect(self.addfswidget)
        getattr(self, 'DeleteButton').clicked.connect(self.deletefswidget)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.fswidget0)
        mainLayout.addWidget(self.navigation)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def addfswidget(self):
        index = self.layout().indexOf(self.navigation)
        if index < 4:
            setattr(self, 'fswidget' + str(index), FsWidget())
            self.layout().insertWidget(index, getattr(self, 'fswidget' + str(index)))
        else:
            QMessageBox().information(u'实时波形最多容许4个!')

    def deletefswidget(self):
        index = self.layout().indexOf(self.navigation)
        if index > 0:
            getattr(self, 'fswidget' + str(index-1)).deleteLater()
        else:
            QMessageBox().information(u'实时波形设置必须至少有一个!')

    def createNavigation(self):
        buttons = ['Add', 'Delete']
        self.buttontext = {'Add': u"增加", 'Delete': u"删除"}
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QHBoxLayout()
        for item in buttons:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(self.buttontext[item]))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        self.navigation.setMaximumHeight(60)
        self.navigation.setContentsMargins(0, 0, 0, 0)


class QueryPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QueryPage, self).__init__(parent)

        packagesGroup = QtGui.QGroupBox("Look for packages")

        nameLabel = QtGui.QLabel("Name:")
        nameEdit = QtGui.QLineEdit()

        dateLabel = QtGui.QLabel("Released after:")
        dateEdit = QtGui.QDateTimeEdit(QtCore.QDate.currentDate())

        releasesCheckBox = QtGui.QCheckBox("Releases")
        upgradesCheckBox = QtGui.QCheckBox("Upgrades")

        hitsSpinBox = QtGui.QSpinBox()
        hitsSpinBox.setPrefix("Return up to ")
        hitsSpinBox.setSuffix(" results")
        hitsSpinBox.setSpecialValueText("Return only the first result")
        hitsSpinBox.setMinimum(1)
        hitsSpinBox.setMaximum(100)
        hitsSpinBox.setSingleStep(10)

        startQueryButton = QtGui.QPushButton("Start query")

        packagesLayout = QtGui.QGridLayout()
        packagesLayout.addWidget(nameLabel, 0, 0)
        packagesLayout.addWidget(nameEdit, 0, 1)
        packagesLayout.addWidget(dateLabel, 1, 0)
        packagesLayout.addWidget(dateEdit, 1, 1)
        packagesLayout.addWidget(releasesCheckBox, 2, 0)
        packagesLayout.addWidget(upgradesCheckBox, 3, 0)
        packagesLayout.addWidget(hitsSpinBox, 4, 0, 1, 2)
        packagesGroup.setLayout(packagesLayout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(packagesGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(startQueryButton)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


class QMessageBox(QtGui.QDialog):

    def __init__(self, parent=None):
        super(QMessageBox, self).__init__(parent)
        self.setObjectName('QMessageBox')
        self.setGeometry(300, 300, 400, 200)
        self.center()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroDialog.qss']))  # 设置弹出框样式
        self.setWindowIcon(QtGui.QIcon('icons/Write.png'))
        self.setModal(True)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def information(self, info):
        infoButton = QtGui.QPushButton('info')
        infoButton.setObjectName('Info' + 'Button')
        info = QtGui.QTextEdit(info)
        info.setReadOnly(True)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(infoButton)
        mainLayout.addWidget(info)
        # mainLayout.addStretch(4)
        infoButton.clicked.connect(self.clickReturn)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.exec_()

    def clickReturn(self):
        self.close()


class QInputDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(QInputDialog, self).__init__(parent)
        self.setObjectName('QInputDialog')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroDialog.qss']))  # 设置弹出框样式
        self.setWindowIcon(QtGui.QIcon('icons/Write.png'))
        self.setModal(True)
        self.createNavigation()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def createNavigation(self):
        buttons = ['Ok', 'Cancel']
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QHBoxLayout()
        for item in buttons:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(item))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        self.navigation.setMaximumHeight(60)
        self.navigation.setContentsMargins(0, 0, 0, 0)

        getattr(self, 'Cancel' + 'Button').clicked.connect(self.clickReturn)
        getattr(self, 'Ok' + 'Button').clicked.connect(self.clickReturn)

    def getInteger(self, title, intLabel, value, minvalue=-2147483647, maxvalue=2147483647, step=1):
        titleLabel = QtGui.QLabel(title)
        intLabel = QtGui.QLabel(intLabel)
        intValue = QtGui.QSpinBox()
        intValue.setMaximum(maxvalue)
        intValue.setValue(value)
        intValue.setMinimum(minvalue)
        intValue.setSingleStep(step)
        intValue.lineEdit().setReadOnly(False)

        intwidget = QtGui.QWidget()
        Layout = QtGui.QGridLayout()
        Layout.addWidget(titleLabel, 0, 0)
        Layout.addWidget(intLabel, 1, 0)
        Layout.addWidget(intValue, 1, 1)
        intwidget.setLayout(Layout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(intwidget)
        mainLayout.addWidget(self.navigation)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        mainLayout.addStretch(1)

        self.intValue = intValue
        self.value = self.intValue.value()
        self.flag = False

        self.center()
        self.exec_()
        return self.intValue.value(), self.flag

    def getDouble(self, title, doubleLabel, value, minvalue=-2147483647, maxvalue=2147483647, step=1.0, decimals=5):
        titleLabel = QtGui.QLabel(title)
        doubleLabel = QtGui.QLabel(doubleLabel)
        doubleValue = QtGui.QDoubleSpinBox()
        doubleValue.setMaximum(maxvalue)
        doubleValue.setValue(value)
        doubleValue.setMinimum(minvalue)
        doubleValue.setSingleStep(step)
        doubleValue.setDecimals(decimals)
        doubleValue.lineEdit().setReadOnly(False)

        doublewidget = QtGui.QWidget()
        Layout = QtGui.QGridLayout()
        Layout.addWidget(titleLabel, 0, 0)
        Layout.addWidget(doubleLabel, 1, 0)
        Layout.addWidget(doubleValue, 1, 1)
        doublewidget.setLayout(Layout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(doublewidget)
        mainLayout.addWidget(self.navigation)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        mainLayout.addStretch(1)

        self.doubleValue = doubleValue
        self.exec_()
        return self.doubleValue.value(), self.flag

    def getText(self, title, textLabel, text, mode=QtGui.QLineEdit.Normal):
        titleLabel = QtGui.QLabel(title)
        textLabel = QtGui.QLabel(textLabel)
        textValue = QtGui.QLineEdit(text)
        textValue.setEchoMode(mode)

        textwidget = QtGui.QWidget()
        Layout = QtGui.QGridLayout()
        Layout.addWidget(titleLabel, 0, 0)
        Layout.addWidget(textLabel, 1, 0)
        Layout.addWidget(textValue, 1, 1)
        textwidget.setLayout(Layout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(textwidget)
        mainLayout.addWidget(self.navigation)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        mainLayout.addStretch(1)

        self.textValue = textValue
        self.exec_()
        return unicode(self.textValue.text()), self.flag

    def getItem(self, title, itemLabel, items, index, editable=True):
        titleLabel = QtGui.QLabel(title)
        itemLabel = QtGui.QLabel(itemLabel)
        itemValue = QtGui.QComboBox()
        for item in items:
            itemValue.addItem(item)
        itemValue.setCurrentIndex(0)
        itemValue.setEditable(editable)

        itemwidget = QtGui.QWidget()
        Layout = QtGui.QGridLayout()
        Layout.addWidget(titleLabel, 0, 0)
        Layout.addWidget(itemLabel, 1, 0)
        Layout.addWidget(itemValue, 1, 1)
        itemwidget.setLayout(Layout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(itemwidget)
        mainLayout.addWidget(self.navigation)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        mainLayout.addStretch(1)

        self.itemValue = itemValue
        self.exec_()
        return unicode(self.itemValue.currentText()), self.flag

    def clickReturn(self):
        self.close()
        if self.sender() is getattr(self, 'Ok' + 'Button'):
            self.flag = True
        elif self.sender() is getattr(self, 'Cancel' + 'Button'):
            self.flag = False


class ChildDialog(QtGui.QDialog):
    def __init__(self, parent=None, child=None):
        super(ChildDialog, self).__init__(parent)
        self.parent = parent
        self.child = child
        self.createNavigation()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.child)
        mainLayout.addWidget(self.navigation)
        self.setLayout(mainLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化
        self.setModal(True)
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroDialog.qss']))  # 设置弹出框样式
        self.setWindowIcon(QtGui.QIcon('skin/icons/light/appbar.cog.png'))

    def createNavigation(self):
        buttons = ['Ok', 'Cancel']
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QHBoxLayout()
        for item in buttons:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(item))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        self.navigation.setMaximumHeight(60)
        self.navigation.setContentsMargins(0, 0, 0, 0)

        getattr(self, 'Cancel' + 'Button').clicked.connect(self.close)

    def fadeInWidget(self):
        '''
            页面切换时槽函数实现淡入淡出效果
        '''
        self.faderWidget = FaderWidget(self)
        self.faderWidget.start()


class ConfigDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)

        self.contentsWidget = QtGui.QListWidget()
        self.contentsWidget.setViewMode(QtGui.QListView.IconMode)
        self.contentsWidget.setIconSize(QtCore.QSize(96, 84))
        self.contentsWidget.setMovement(QtGui.QListView.Static)
        self.contentsWidget.setMaximumWidth(128)
        self.contentsWidget.setSpacing(12)

        self.pagesWidget = QtGui.QStackedWidget()
        self.configpage = ConfigurationPage()
        self.fspage = FsPage()
        self.querypage = QueryPage()

        self.pagesWidget.addWidget(self.fspage)
        self.pagesWidget.addWidget(self.configpage)
        self.pagesWidget.addWidget(self.querypage)

        self.createIcons()
        self.contentsWidget.setCurrentRow(0)

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        self.setLayout(mainLayout)

        self.fig = ''

    @QtCore.pyqtSlot()
    def save_settings(self):
        currentwidget =  self.pagesWidget.currentWidget()
        kargs = {}
        if currentwidget is self.fspage:
            i = 0
            for widget in self.fspage.children():
                if isinstance(widget, FsWidget):
                    cupa = {}
                    cupa['_id'] = widget.PAlist[unicode(widget.PACombo.currentText())]
                    cupa['featurevalue'] = {}
                    for checkbox in widget.featurevalueWidget.children():
                        if isinstance(checkbox, QtGui.QCheckBox):
                            cupa['featurevalue'][unicode(checkbox.text())] =  checkbox.isChecked()
                    cupa['featurevalue']['st'] =  widget.pointnumberEdit.value()
                    cupa['featurevalue']['ed'] =  1
                    cupa['gno'] = unicode(widget.PACombo.currentText())
                    kargs[i] = cupa
                    i += 1

        elif currentwidget is self.configpage:
            kargs['ip'] = unicode(self.configpage.ipEdit.text())
            kargs['channel'] = unicode(self.configpage.channelCombo.currentText())
            kargs['wavpath'] = unicode(self.configpage.wavpathEdit.text())
            kargs['starttime'] = self.configpage.startTimeEdit.dateTime().toTime_t()
            kargs['endtime'] = self.configpage.startTimeEdit.dateTime().toTime_t()
            kargs['importwavspreed'] = int(unicode(self.configpage.importWavSpreedCombo.currentText()))
            kargs['fig'] = getattr(self, 'fig')
        else:
            pass
        self.emit(QtCore.SIGNAL('send(PyQt_PyObject)'), kargs)
        self.parent().close()

    def boundfig(self, fig):
        setattr(self, 'fig', fig)

    def changePage(self, current, previous):
        if not current:
            current = previous
        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def createIcons(self):
        updateButton = QtGui.QListWidgetItem(self.contentsWidget)
        updateButton.setIcon(QtGui.QIcon('icons/update.png'))
        updateButton.setText(u"实时波形")
        updateButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        updateButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        configButton = QtGui.QListWidgetItem(self.contentsWidget)
        configButton.setIcon(QtGui.QIcon('icons/config.png'))
        configButton.setText(u"日志回演")
        configButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        configButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        queryButton = QtGui.QListWidgetItem(self.contentsWidget)
        queryButton.setIcon(QtGui.QIcon('icons/query.png'))
        queryButton.setText(u"Query")
        queryButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        queryButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.contentsWidget.currentItemChanged.connect(self.changePage)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    a = QInputDialog()
    # print a.getItem(u'请输入', u'显示点数：', ['5000', '6000'], True)
    # print a.getText(u'请输入', u'显示点数：', '5000')
    print a.getInteger(u'请输入', u'显示点数：', 5000)
    # print a.getDouble(u'请输入', u'显示点数：', 10)
    # QMessageBox().information(u'这是一个很好的button，\n\r支持文本换行\n' * 5)
    sys.exit(app.exec_())

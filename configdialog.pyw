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
from PyQt4 import QtCore, QtGui


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
        self.wavpathEdit = QtGui.QLineEdit(os.getcwd())
        self.wavpathHLayout = QtGui.QGridLayout()
        self.wavpathHLayout.addWidget(self.wavpathEdit, 0, 0)
        self.wavpathHLayout.addWidget(self.wavpathButton, 0, 1)

        self.startTimeLabel = QtGui.QLabel(u"样本开始时间：")
        self.startTimeEdit = QtGui.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.startTimeEdit.setDisplayFormat("yyyy-MM-dd: hh-mm-ss")
        self.endTimeLabel = QtGui.QLabel(u"样本截止时间：")
        self.endTimeEdit = QtGui.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.endTimeEdit.setDisplayFormat("yyyy-MM-dd: hh-mm-ss")

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

        self.configGroup.setLayout(self.SetPALayout)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.configGroup)
        self.mainLayout.addStretch(1)

        self.setLayout(self.mainLayout)

    def setExistingDirectory(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self, u"选择日志路径", os.getcwd(), options)
        self.wavpathEdit.setText(directory)


class UpdatePage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(UpdatePage, self).__init__(parent)

        updateGroup = QtGui.QGroupBox("Package selection")
        systemCheckBox = QtGui.QCheckBox("Update system")
        appsCheckBox = QtGui.QCheckBox("Update applications")
        docsCheckBox = QtGui.QCheckBox("Update documentation")

        packageGroup = QtGui.QGroupBox("Existing packages")

        packageList = QtGui.QListWidget()
        qtItem = QtGui.QListWidgetItem(packageList)
        qtItem.setText("Qt")
        qsaItem = QtGui.QListWidgetItem(packageList)
        qsaItem.setText("QSA")
        teamBuilderItem = QtGui.QListWidgetItem(packageList)
        teamBuilderItem.setText("Teambuilder")

        startUpdateButton = QtGui.QPushButton("Start update")

        updateLayout = QtGui.QVBoxLayout()
        updateLayout.addWidget(systemCheckBox)
        updateLayout.addWidget(appsCheckBox)
        updateLayout.addWidget(docsCheckBox)
        updateGroup.setLayout(updateLayout)

        packageLayout = QtGui.QVBoxLayout()
        packageLayout.addWidget(packageList)
        packageGroup.setLayout(packageLayout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(updateGroup)
        mainLayout.addWidget(packageGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(startUpdateButton)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


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
        self.updatepage = UpdatePage()
        self.querypage = QueryPage()

        self.pagesWidget.addWidget(self.configpage)
        self.pagesWidget.addWidget(self.updatepage)
        self.pagesWidget.addWidget(self.querypage)

        self.createIcons()
        self.contentsWidget.setCurrentRow(0)

        okButton = QtGui.QPushButton("Ok")
        cancelButton = QtGui.QPushButton("Close")

        cancelButton.clicked.connect(self.close)
        okButton.clicked.connect(self.save_settings)

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        buttonsLayout = QtGui.QHBoxLayout()

        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(okButton)
        buttonsLayout.addWidget(cancelButton)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)

        self.setWindowTitle("Config Dialog")

    def save_settings(self):
        kargs = {}
        kargs['ip'] = unicode(self.configpage.ipEdit.text())
        kargs['channel'] = unicode(self.configpage.channelCombo.currentText())
        kargs['wavpath'] = unicode(self.configpage.wavpathEdit.text())
        kargs['starttime'] = self.configpage.startTimeEdit.dateTime().toTime_t()
        kargs['endtime'] = self.configpage.startTimeEdit.dateTime().toTime_t()
        self.emit(QtCore.SIGNAL('send(PyQt_PyObject)'), kargs)
        self.close()

    def changePage(self, current, previous):
        if not current:
            current = previous
        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def createIcons(self):
        configButton = QtGui.QListWidgetItem(self.contentsWidget)
        configButton.setIcon(QtGui.QIcon('icons/config.png'))
        configButton.setText("Configuration")
        configButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        configButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        updateButton = QtGui.QListWidgetItem(self.contentsWidget)
        updateButton.setIcon(QtGui.QIcon('icons/update.png'))
        updateButton.setText("Update")
        updateButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        updateButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        queryButton = QtGui.QListWidgetItem(self.contentsWidget)
        queryButton.setIcon(QtGui.QIcon('icons/query.png'))
        queryButton.setText("Query")
        queryButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        queryButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.contentsWidget.currentItemChanged.connect(self.changePage)

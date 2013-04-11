#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import threading
from guiutil import set_skin


class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def childNumber(self):
        if self.parentItem != None:
            return self.parentItem.childItems.index(self)
        return 0

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return self.itemData[column]

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.childItems):
            return False

        for row in range(count):
            data = [None for v in range(columns)]
            item = TreeItem(data, self)
            self.childItems.insert(position, item)

        return True

    def insertColumns(self, position, columns):
        if position < 0 or position > len(self.itemData):
            return False

        for column in range(columns):
            self.itemData.insert(position, None)

        for child in self.childItems:
            child.insertColumns(position, columns)

        return True

    def parent(self):
        return self.parentItem

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.childItems):
            return False

        for row in range(count):
            self.childItems.pop(position)

        return True

    def removeColumns(self, position, columns):
        if position < 0 or position + columns > len(self.itemData):
            return False

        for column in range(columns):
            self.itemData.pop(position)

        for child in self.childItems:
            child.removeColumns(position, columns)

        return True

    def setData(self, column, value):
        if column < 0 or column >= len(self.itemData):
            return False

        self.itemData[column] = value

        return True


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, headers, data, parent=None):
        super(TreeModel, self).__init__(parent)

        rootData = [header for header in headers]
        self.rootItem = TreeItem(rootData)
        self.setupModelData(data, self.rootItem)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return None

        item = self.getItem(index)
        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return 0

        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def insertColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        success = self.rootItem.insertColumns(position, columns)
        self.endInsertColumns()

        return success

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = parentItem.insertChildren(position, rows,
                self.rootItem.columnCount())
        self.endInsertRows()

        return success

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = self.getItem(index)
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    def removeColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success = self.rootItem.removeColumns(position, columns)
        self.endRemoveColumns()

        if self.rootItem.columnCount() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent=QtCore.QModelIndex()):
        parentItem = self.getItem(parent)

        return parentItem.childCount()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole:
            return False

        item = self.getItem(index)
        result = item.setData(index.column(), value)

        if result:
            self.dataChanged.emit(index, index)

        return result

    def setupModelData(self, connection, parent):

        parents = [parent]
        dbs = []
        for db in connection.database_names():
            dbdata = [db, '', 'db']
            parents[0].insertChildren(parents[-1].childCount(), 1, self.rootItem.columnCount())
            for column in range(len(dbdata)):
                parents[-1].child(parents[-1].childCount() -1).setData(column, dbdata[column])
            dbs.append(parents[-1].child(parents[-1].childCount() - 1))

            cols = []
            for collection in connection[db].collection_names():
                coldata = [collection, '', 'collection']
                dbs[-1].insertChildren(dbs[-1].childCount(), 1 , self.rootItem.columnCount())
                for column in range(len(coldata)):
                    dbs[-1].child(dbs[-1].childCount() -1).setData(column, coldata[column])

                cols.append(dbs[-1].child(dbs[-1].childCount() - 1))
                docs = []
                for docment in connection[db][collection].find():
                    if '_id' in docment:
                        docdata = [repr(docment[u'_id']), str(docment), 'docment']
                        cols[-1].insertChildren(cols[-1].childCount(), 1 , self.rootItem.columnCount())
                    else:
                        docdata = [str(docment[u'ns']), str(docment), 'docment']
                        cols[-1].insertChildren(cols[-1].childCount(), 1 , self.rootItem.columnCount())
                    for column in range(len(coldata)):
                        cols[-1].child(cols[-1].childCount() -1).setData(column, docdata[column])
                    docs.append(cols[-1].child(cols[-1].childCount() - 1))
                    for key, value in docment.items():
                        itemdata = [key, repr(value), str(type(value))]
                        docs[-1].insertChildren(docs[-1].childCount(), 1 , self.rootItem.columnCount())
                        for column in range(len(coldata)):
                            docs[-1].child(docs[-1].childCount() -1).setData(column, itemdata[column])


class ViewPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ViewPage, self).__init__(parent)
        self.parent = parent
        self.createToolBar()
        self.creatSearchEdit()

        self.view = QtGui.QTreeView(self)

        self.treeWidget = QtGui.QWidget()
        self.treeLayout = QtGui.QVBoxLayout()
        self.treeLayout.addWidget(self.searchEdit)
        self.treeLayout.addWidget(self.view)
        self.treeWidget.setLayout(self.treeLayout)

        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(self.navigation)
        self.mainLayout.addWidget(self.treeWidget)
        self.setLayout(self.mainLayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroViewPage.qss']))

    def creatSearchEdit(self):
        self.searchEdit = QtGui.QLineEdit()
        self.searchEdit.setObjectName('SearchEdit')
        completer = QtGui.QCompleter()
        self.searchEdit.setCompleter(completer)
        model = QtGui.QStringListModel()
        completer.setModel(model)
        self.get_data(model)

    def get_data(self, model):
        model.setStringList(["completion", "data", "goes", "here"])

    def createToolBar(self):
        navbutton = ['Start', 'Pause', 'Custom']
        self.buttontext = {
            'Start': u'开始查询\n数据库',
            'Pause': u'暂停',
            'Custom': u'自定义'
        }
        self.navigation = QtGui.QWidget()
        navigationLayout = QtGui.QVBoxLayout()

        for item in navbutton:
            button = item + 'Button'
            setattr(self, button, QtGui.QPushButton(self.buttontext[item]))
            getattr(self, button).setObjectName(button)
            navigationLayout.addWidget(getattr(self, button))
        self.navigation.setLayout(navigationLayout)
        set_skin(self.navigation, os.sep.join(['skin', 'qss', 'MetroDataShow.qss']))

        getattr(self, 'StartButton').clicked.connect(self.startQueryMongoDB)
        # getattr(self, 'PauseButton').clicked.connect(self.stopploting)

    def startQueryMongoDB(self):
        from mongokit import Connection
        connection = Connection()
        headers =  ("Index", "Value", "Type")
        self.model = TreeModel(headers, connection)
        self.view.setModel(self.model)
        for column in range(self.model.columnCount()):
            self.view.resizeColumnToContents(column)

        self.view.setColumnWidth(0, self.parent.geometry().width() / 4)
        self.view.setColumnWidth(1, self.parent.geometry().width() * 3 / 5)

        getattr(self, 'StartButton').setEnabled(False)

    def resizeEvent(self, event):
        self.view.setColumnWidth(0, self.parent.geometry().width() / 4)
        self.view.setColumnWidth(1, self.parent.geometry().width() * 3 / 5)

#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from figurewidget import FigureWidget
import configdialog
import algorithm
import util
import threading
import time
import websocket
import json


class InteractiveManager(QtCore.QObject):

    started = {'figurewidget0': QtCore.SIGNAL('send0(PyQt_PyObject, PyQt_PyObject)')}

    senddata = QtCore.pyqtSignal(dict, list)

    def __init__(self, parent=None, **pages):
        super(InteractiveManager, self).__init__(parent)
        self.parent = parent
        for key, value in pages.items():
            setattr(self, key, value)

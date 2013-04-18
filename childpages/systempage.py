#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from guiutil import *


class SystemPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SystemPage, self).__init__(parent)
        self.parent = parent

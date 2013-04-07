#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore


class ProductPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ProductPage, self).__init__(parent)
        self.parent = parent

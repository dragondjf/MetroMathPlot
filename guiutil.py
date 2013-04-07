#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore


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

#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from figurewidget import FigureWidget
import configdialog
import algorithm
import util
import threading
import thread
import time
import websocket
import json


class InteractiveManager(QtCore.QObject):

    started = QtCore.SIGNAL('send(PyQt_PyObject, PyQt_PyObject)')

    def __init__(self, parent=None, **pages):
        super(InteractiveManager, self).__init__(parent)
        self.parent = parent
        for key, value in pages.items():
            setattr(self, key, value)

        configdlg = configdialog.ConfigDialog()
        self.settingdialog = configdialog.ChildDialog(None, configdlg)

        QtCore.QObject.connect(getattr(self.settingdialog, 'Ok' + 'Button'), QtCore.SIGNAL('clicked()'), configdlg, QtCore.SLOT('save_settings()'))  # 点击弹出窗口OkButton，执行保存参数函数
        QtCore.QObject.connect(self.settingdialog.child, QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('settings(PyQt_PyObject)'))  # 交互管理窗口获取保存的配置

        # QtCore.QObject.connect(self.parent.centeralwindow.pages, QtCore.SIGNAL("currentChanged(int)"), getattr(self, 'DataShowPage'), QtCore.SLOT('stopploting()'))  # 页面切换时暂停波形绘制功能

        # QtCore.QObject.connect(self, self.started, getattr(self, 'DataShowPage').figurewidget, QtCore.SLOT('startwork(PyQt_PyObject, PyQt_PyObject)'))  # 向绘图控件传递需要绘制的数据
        
        QtCore.QObject.connect(getattr(self, 'DataShowPage'), QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('interfigure(PyQt_PyObject)'))
        # QtCore.QObject.connect(getattr(self, 'DataShowPage'), QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('interfigure(PyQt_PyObject)'))

        getattr(getattr(self, 'DataShowPage'), 'Custom' + 'Button').clicked.connect(self.setdialogshow)  # 打开设置对话框

        self.importwavspreed = 0.2
        self.data = algorithm.creat_data(algorithm.Names)

    # def tcpServerstart(self):
    #     # t = threading.Thread(name="Listen Thread 1", target=self.handle)
    #     t = threading.Thread(name="Listen Thread 1", target=self.websocketHandle)
    #     t.setDaemon(True)
    #     t.start()
    @QtCore.pyqtSlot(int)
    def interfigure(self, i):
        print i
        f = getattr(getattr(self, 'DataShowPage'), 'figurewidget%d' % i)
        QtCore.QObject.connect(f, QtCore.SIGNAL('send()'), self, QtCore.SLOT('setdialogshow()'))

    @QtCore.pyqtSlot()
    def setdialogshow(self):
        self.settingdialog.show()
        self.settingdialog.setGeometry(self.parent.geometry())
        self.settingdialog.fadeInWidget()

    @QtCore.pyqtSlot(dict)
    def settings(self, kargs):
        self.settintparameter = kargs
        if 'wavpath' in kargs:
            self.wavfiles = util.FilenameFilter(util.path_match_platform(self.settintparameter['wavpath']))

        self.websocketHandle()

    def handle(self):
        while True:
            if hasattr(self, 'wavfiles'):
                for wavfile in self.wavfiles:
                    x, fs, bits, N = util.wavread(unicode(wavfile))
                    self.x = (x + 32768) / 16
                    for i in range(1, len(x) / 1024):
                        for key in algorithm.Names:
                            self.data[key][:-1] = self.data[key][1:]
                        raw_data = self.x[1024 * (i - 1):1024 * i]
                        self.data['max'][-1] = max(raw_data)
                        self.data['min'][-1] = min(raw_data)
                        self.emit(self.started, self.data)
                        time.sleep(self.importwavspreed / self.wav_parameter['importwavspreed'])
            else:
                pass

    def websocketHandle(self):
        for i in self.settintparameter:
            t = threading.Thread(name="Wave Thread %d" % i, target=self.wavhandle, args=(self.settintparameter[i]['_id'],self.settintparameter[i]['featurevalue'] , ))
            t.setDaemon(True)
            t.start()

    def wavhandle(self, _id, featurevalue):
        ws = websocket.create_connection("ws://localhost:9000/waves/%s" % _id)
        ws.send(json.dumps(featurevalue))
        while True:
            showf = []
            for key in featurevalue:
                if type(featurevalue[key]) is bool and featurevalue[key]:
                    showf.append(key)

            result = json.loads(ws.recv())
            for item in result:
                for key in algorithm.Names:
                    self.data[key][:-1] = self.data[key][1:]
                for key in item:
                    self.data[key][-1] = item[key]
            self.emit(self.started, self.data, showf)

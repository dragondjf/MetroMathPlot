#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import configdialog
import algorithm
import util
import threading
import time
import websocket


class InteractiveManager(QtCore.QObject):

    started = QtCore.SIGNAL('send(PyQt_PyObject)')

    def __init__(self, parent=None, **pages):
        super(InteractiveManager, self).__init__(parent)
        self.parent = parent
        for key, value in pages.items():
            setattr(self, key, value)

        configdlg = configdialog.ConfigDialog()
        self.settingdialog = configdialog.ChildDialog(None, configdlg)

        QtCore.QObject.connect(getattr(self.settingdialog, 'Ok' + 'Button'), QtCore.SIGNAL('clicked()'), configdlg, QtCore.SLOT('save_settings()'))  # 点击弹出窗口OkButton，执行保存参数函数
        QtCore.QObject.connect(self.settingdialog.child, QtCore.SIGNAL('send(PyQt_PyObject)'), self, QtCore.SLOT('settings(PyQt_PyObject)'))  # 交互管理窗口获取保存的配置

        QtCore.QObject.connect(self.parent.centeralwindow.pages, QtCore.SIGNAL("currentChanged(int)"), getattr(self, 'DataShowPage'), QtCore.SLOT('stopploting()'))  # 页面切换时暂停波形绘制功能

        QtCore.QObject.connect(self, self.started, getattr(self, 'DataShowPage').figurewidget, QtCore.SLOT('startwork(PyQt_PyObject)'))  # 向绘图控件传递需要绘制的数据
        getattr(getattr(self, 'DataShowPage'), 'Custom' + 'Button').clicked.connect(self.setdialogshow)  # 打开设置对话框

        self.importwavspreed = 0.2
        self.data = algorithm.creat_data(algorithm.Names)

    def tcpServerstart(self):
        # t = threading.Thread(name="Listen Thread 1", target=self.handle)
        t = threading.Thread(name="Listen Thread 1", target=self.websocketHandle)
        t.setDaemon(True)
        t.start()

    def setdialogshow(self):
        self.settingdialog.show()
        self.settingdialog.setGeometry(self.parent.geometry())
        self.settingdialog.fadeInWidget()

    @QtCore.pyqtSlot(dict)
    def settings(self, kargs):
        self.wav_parameter = kargs
        self.wavfiles = util.FilenameFilter(util.path_match_platform(self.wav_parameter['wavpath']))

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
        # enableTrace(True)
        ws = websocket.create_connection("ws://localhost:9000/waves/5164dd0a5ce2c809f75773cb")
        import json
        true = True
        false = False
        ws.send(json.dumps({"max":true,"min":true,"davg":true,"alarmflag":false,"alarmrate":false,"data0":false,"f0":false,"data1":false,"f1":false,"data2":false,"f2":false,"data3":false,"f3":false,"data4":false,"f4":false,"data5":false,"f5":false,"data6":false,"f6":false,"data7":false,"f7":false,"data8":false,"data9":false,"st":300,"ed":1}))
        while True:
            result = json.loads(ws.recv())
            for item in result:
                for key in algorithm.Names:
                    self.data[key][:-1] = self.data[key][1:]
                for key in item:
                    self.data[key][-1] = item[key]
            self.emit(self.started, self.data)

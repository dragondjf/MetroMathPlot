#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import websocket
from PyQt4 import QtCore
import multiprocessing
import Queue
import time
import websocket
import json

from cache import padict
import util


class WaveThreadHandler(threading.Thread, QtCore.QObject):

    plotsignal = QtCore.pyqtSignal()

    def __init__(self, figurename, settintparameter):
        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)
        self.figurename = figurename
        self.settintparameter = settintparameter
        self.DBaddr = self.settintparameter['Appaddr']
        self.paid = self.settintparameter['_id']
        self.featurevalueflags = self.settintparameter['featurevalue']
        self.setDaemon(True)
        self.start()

    def run(self):
        try:
            ws = websocket.create_connection("ws://%s/waves/%s" % (self.DBaddr, self.paid))
            ws.send(json.dumps(self.featurevalueflags))
        except Exception, e:
            return
        import algorithm
        padata = algorithm.creat_data(algorithm.Names)
        while True:
            if self.paid == self.settintparameter['_id']:
                pass
            else:
                self.paid = self.settintparameter['_id']
                ws.close()
                ws = websocket.create_connection("ws://%s/waves/%s" % (self.DBaddr, self.paid))

            self.featurevalueflags = self.settintparameter['featurevalue']
            ws.send(json.dumps(self.featurevalueflags))
            showf = []
            for key in self.featurevalueflags:
                if type(self.featurevalueflags[key]) is bool and self.featurevalueflags[key]:
                    showf.append(key)

            result = json.loads(ws.recv())
            for item in result:
                for key in padata.keys():
                    padata[key][:-1] = padata[key][1:]
                for key in item:
                    padata[key][-1] = item[key]
            padict.update({self.figurename: padata})
            self.plotsignal.emit()


class WaveReplayHandler(threading.Thread, QtCore.QObject):

    plotsignal = QtCore.pyqtSignal()

    def __init__(self, figurename, wavfiles, importspreed, plotmode):
        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)

        self.event = threading.Event()
        self.event.set()

        self.figurename = figurename
        self.wavfiles = wavfiles
        self.importspreed = importspreed
        self.plotmode = plotmode
        self.importwavspreed = 0.2
        self.setDaemon(True)

    def run(self):
        import algorithm
        padata = algorithm.creat_data(algorithm.Names)
        while self.event.isSet():
            if hasattr(self, 'wavfiles'):
                for wavfile in self.wavfiles:
                    x, fs, bits, N = util.wavread(unicode(wavfile))
                    self.x = (x + 32768) / 16
                    for i in range(1, len(x) / 1024):
                        for key in padata:
                            padata[key][:-1] = padata[key][1:]
                        raw_data = self.x[1024 * (i - 1):1024 * i]
                        padata['max'][-1] = max(raw_data)
                        padata['min'][-1] = min(raw_data)
                        padict.update({self.figurename: padata})
                        if self.plotmode == "by data":
                            self.plotsignal.emit()
                        time.sleep(self.importwavspreed / self.importspreed)

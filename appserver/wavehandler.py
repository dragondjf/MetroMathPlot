#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import websocket

import threading
import multiprocessing
import Queue
import time
import websocket
import json

from cache import padict
import util


class WaveThreadHandler(threading.Thread):
    def __init__(self, figurename, settintparameter):
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


class WaveReplayHandler(threading.Thread):
    def __init__(self, figurename, wavfiles, importspreed):
        threading.Thread.__init__(self)
        self.figurename = figurename
        self.wavfiles = wavfiles
        self.importspreed = importspreed
        self.importwavspreed = 0.2
        self.setDaemon(True)
        self.start()

    def run(self):
        import algorithm
        padata = algorithm.creat_data(algorithm.Names)
        while True:
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
                        time.sleep(self.importwavspreed / self.importspreed)

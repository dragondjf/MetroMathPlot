#!/usr/bin/python
# -*- coding: utf-8 -*-

# from mongokit import Connection

# connection = Connection()
# print dir(connection)
# db = connection['gsd']
# print connection.HOST, connection.port, connection.server_info()
# print connection.database_names()
# print db.name
# print db.collection_names()
# print dir(db['PA_Col'])
# for col in db.collection_names():
#     print col,'\n\n'
#     for doc in  db[col].find():
#         print doc
#coding=utf-8 
import sys
from PyQt4.QtGui import (QApplication, QWidget, QFont, QListWidget,
    QHBoxLayout, QVBoxLayout, QShortcut, QKeySequence)
import numpy as np
from spyderlib.widgets.sourcecode.codeeditor import CodeEditor
from spyderlib.widgets.internalshell import InternalShell
from spyderlib.widgets.dicteditor import DictEditorWidget

class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.code_editor = CodeEditor(self)
        self.code_editor.setup_editor(
            language = "python",
            font = QFont("Courier New")
        )
        run_sc = QShortcut(QKeySequence("F5"), self, self.run)

        self.shell = InternalShell(self, {"demo":self},
            multithreaded = False,
            max_line_count = 3000,
            font = QFont("Courier new", 10)
        )

        self.dict_editor = DictEditorWidget(self, {})
        self.dict_editor.editor.set_filter(self.filter_namespace)
        self.dict_editor.set_data(self.shell.interpreter.namespace)
        vbox = QVBoxLayout()
        vbox.addWidget(self.code_editor)
        vbox.addWidget(self.shell)

        hbox = QHBoxLayout()
        hbox.addWidget(self.dict_editor)
        hbox.addLayout(vbox)

        self.setLayout(hbox)
        self.resize(800, 600)

    def filter_namespace(self, data):
        result = {}
        support_types = [np.ndarray, int, long, float, str, tuple, dict, list]
        for key, value in data.iteritems():
            if not key.startswith("__") and type(value) in support_types:
                result[key] = value
        return result

    def run(self):
        code = str(self.code_editor.toPlainText())
        namespace = self.shell.interpreter.namespace
        exec code in namespace
        self.dict_editor.set_data(namespace)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    try:
        demo = Demo()
        demo.show()
    except Exception as ex:
        import traceback
        sys.__stdout__.write(traceback.format_exc())
    sys.exit(app.exec_())

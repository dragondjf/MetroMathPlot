#!/usr/bin/python
# -*- coding: utf-8 -*-

from mongokit import Connection

connection = Connection()
print dir(connection)
db = connection['gsd']
print connection.HOST, connection.port, connection.server_info()
print connection.database_names()
print db.name
print db.collection_names()
print dir(db['PA_Col'])
for col in db.collection_names():
    print col,'\n\n'
    for doc in  db[col].find():
        print doc

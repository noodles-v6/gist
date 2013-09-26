#!/usr/bin/env python
# -*- coding: utf-8 -*-

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from hbase import Hbase
from hbase.ttypes import *

transport = TSocket.TSocket('192.168.1.46', 9090)
transport = TTransport.TBufferedTransport(transport)

protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = Hbase.Client(protocol)

transport.open()

tableName = 'meta'

#rowKey = 'row-key1'
#
#result = client.getRow(tableName, rowKey)
#print result
#for r in result:
#    print 'the row is ' , r.row
#    print 'the values is ' , r.columns.get('cf:a').value

#scan = TScan()
#id = client.scannerOpenWithScan(tableName, scan)
#
#result2 = client.scannerGetList(id, 10)
#
#print result2

scanner = client.scannerOpen(tableName, '', ['list'])
print scanner
f = open( 'datamodel.txt', 'w' )
for ts in client.scannerGetList(scanner, 90):
    #print dir(ts.columns)
    for t in ts.columns.values():
        print t.value
        #f.write(t.value)

f.close()

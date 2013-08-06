# -*- coding: utf-8 -*-
import argparse
import random
import os
import time
import json
import uuid

import cherrypy
import pickle
import threadpool

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage
from ws4py.messaging import BinaryMessage

filenum = 0

def save_file(*args):
    handler, filename, data, sleeptime = args[0]
    f = open(filename, 'wb')
    f.write(data)
    f.close()
    handler.send('success : ' + filename)

def save_file_callback():
    print "save_file_callback"

class FileWebSocketHandler(WebSocket):
    def received_message(self, m):
        if isinstance(m, BinaryMessage):
            global filenum
            filenum += 1
            filename = str(filenum) + '.tmp'
            #filename = str(uuid.uuid4()) + '.tmp'
            requests = threadpool.makeRequests(save_file, [[self, filename, m.data, 1.5]], save_file_callback)
            [pool.putRequest(req) for req in requests]

        elif isinstance(m, TextMessage):
            cherrypy.log("got: " + m.data)
            if  m.data == 'getsessionid':
                ret = {'code':0, 'sessionid':'sessionid_134234242'}
                self.send(json.dumps(ret))
            else:
                self.send('Invalid command: ' + m.data)

    def closed(self, code, reason=":-\)"):
        print self, " closed"

class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        return "hello :-)"

    @cherrypy.expose
    def getserviceid(self):
        ret = {'code':0, 'serviceid':'serviceid_23243729472'}
        return json.dumps(ret)

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

if __name__ == '__main__':
    import logging
    from ws4py import configure_logger
    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='File CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl', action='store_true')
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    if args.ssl:
        cherrypy.config.update({'server.ssl_certificate': './server.crt',
                                'server.ssl_private_key': './server.key'})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    pool = threadpool.ThreadPool(5)

    cherrypy.quickstart(Root(args.host, args.port, args.ssl), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': FileWebSocketHandler
            },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
            }
        }
    )

    pool.wait()

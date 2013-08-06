# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient

class FileUploadClient(WebSocketClient):
    def opened(self):
        def data_provider(filename):
            ifile = open(filename, 'rb')
            while True:
                d = ifile.read(128)
                if not d:
                    break
                yield d
            ifile.close()

        self.send(data_provider("FileTraveller.java"), True)
        self.send(data_provider("bigfile.bin"), True)
        #for i in range(0, 200, 25):
        #    print(i)
        #    self.send("*" * i)

    def closed(self, code, reason):
        print(("Closed down", code, reason))

    def received_message(self, m):
        print("=> %d %s" % (len(m), str(m)))
        if len(m) == 175:
            self.close(reason='Bye bye')

if __name__ == '__main__':
    try:
        ws = FileUploadClient('ws://192.168.2.103:9000/ws', protocols=[])#'http-only', 'chat'])
        ws.daemon = False
        ws.connect()
    except KeyboardInterrupt:
        ws.close()

# -*- coding: utf-8 -*-
# Устанавливаем стандартную внешнюю кодировку = utf8
import sys, os
import asyncore
import socket
import json
import logging
import time
from websocket import create_connection

class ListenerHandler(asyncore.dispatcher):
    def __init__(self, sock, listener):
        asyncore.dispatcher.__init__(self, sock)
        self.listener = listener

    def handle_read(self):        
        data = self.recv(8192).decode('cp866')        
        if data:
            print data
            self.listener.send_message(data, 1)

    def handle_write(self):
        if (time.time() - self.listener.start_time)>0.2 and self.listener.shell_addr:
            self.listener.send_message("Shell connected to %s" % self.listener.shell_addr, 1)
            self.listener.shell_addr = None    
        command = self.listener.get_message().encode('cp866')
        if not command:
            return
        self.send(command)

    def handle_close(self):
        if ((time.time() - self.listener.start_time)>0.2):
            self.listener.send_message("\nShell was disconnected", 2)
            self.listener.connection.close()
            sys.exit(1)
        self.listener.send_message("", 0)
        self.close()


class Listener(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger()
        self.pid = os.getpid()
        self.host = '0.0.0.0'
        self.port = 5555
        self.wsport = 49999
        self.connection = create_connection("ws://%s:%s" % ("127.0.0.1", self.wsport))
        self.run()

    def run(self):
        options = {}
        options = self.get_options()
        self.port = options.get('PORT', self.port)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        try:
            self.bind((self.host, self.port))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        self.listen(5)
        self.send_message("Listening on %s:%s" % (self.host, str(self.port)))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            self.send_message('', 1)
            self.start_time = time.time()
            self.shell_addr = repr(addr)
            handler = ListenerHandler(sock, self)

    def send_message(self, message, state=0):
        ''' Listener message to gui
        :param message: Message from shell
        :param state: 0 - shell is not connected
                      1 - shell connected
                      2 - shell disconnected
        '''
        self.logger.info(message)
        req = dict(command="listener_message", args=dict(action="add", message=message, pid=self.pid, state=state))
        self.connection.send(json.dumps(req))

    def get_message(self):
        req = dict(command="listener_message", args=dict(action="get", message="", pid=self.pid, state=None))
        self.connection.send(json.dumps(req))
        resp = dict(message='')
        try:
            resp = json.loads(self.connection.recv())
        except Exception:
            self.logger.exception(str(Exception))
        finally:
            self.logger.debug(resp["message"])
            return resp["message"]

    def get_options(self):
        connection = create_connection("ws://%s:%s" % ("127.0.0.1", 49999))
        req = dict(command="listener_get_options", args=dict(pid=self.pid))
        connection.send(json.dumps(req))
        try:
            resp = json.loads(connection.recv())
        except Exception:
            self.logger.exception(str(Exception))
        connection.close()
        self.logger.debug(resp)
        return resp

if __name__=="__main__":
    server = Listener()
    asyncore.loop()
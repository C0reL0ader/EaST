# -*- coding: utf-8 -*-
import Queue
import sys, os
import asyncore
import socket
import json
import logging
import time
from websocket import create_connection
import select


class ListenerHandler(asyncore.dispatcher):
    def __init__(self, sock, listener):
        asyncore.dispatcher.__init__(self, sock)
        self.listener = listener

    def handle_read(self):        
        data = self.recv(8192)
        if data:
            self.listener.send_message(data, 1)

    def handle_write(self):
        res = select.select([self.listener.connection.sock], [], [], 0.2)
        if not res[0]:
            return
        resp = json.loads(self.listener.connection.recv())
        self.listener.logger.info("Recieved: " + str(resp))
        command = resp["message"]
        if not command:
            return
        self.send(command+"\n")

    def handle_close(self):
        self.listener.send_message("\nShell was disconnected", 2)
        self.listener.logger.info("Shell was disconnected")
        self.listener.connection.close()
        self.close()
        self.listener.close()
        sys.exit(1)


class Listener(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler('Logs/listener.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.pid = os.getpid()
        self.host = '0.0.0.0'
        self.port = 5555
        self.wsport = 49999
        self.handler = None
        self.connection = create_connection("ws://%s:%s" % ("127.0.0.1", self.wsport))
        self.hello()
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
            self.logger.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        self.listen(1)
        self.send_message("Listening on %s:%s" % (self.host, str(self.port)))

    def handle_accept(self):
        if self.handler:
            return 
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            self.shell_addr = repr(addr)
            self.send_message("Shell connected to %s" % self.shell_addr, 1)
            self.handler = ListenerHandler(sock, self)


    def send_message(self, message, state=0):
        ''' Listener message to gui
        :param message: Message from shell
        :param state: 0 - shell is not connected
                      1 - shell connected
                      2 - shell disconnected
        '''
        self.logger.info(("Listener PID = %s" % self.pid) +  message)
        req = dict(command="listener_message", args=dict(message=message, pid=self.pid, state=state))
        self.connection.send(json.dumps(req))

    def get_options(self):
        req = dict(command="listener_get_options", args=dict(pid=self.pid))
        self.connection.send(json.dumps(req))
        resp = {}
        try:
            resp = json.loads(self.connection.recv())
        except Exception as e:
            self.logger.exception(e)
        self.logger.debug(resp)
        return resp

    def hello(self):
        data = dict(hello=dict(name=self.pid.__str__(), type="listener"))
        self.connection.send(json.dumps(data))
        # wait for hello
        self.connection.recv()

if __name__=="__main__":
    server = Listener()
    asyncore.loop()

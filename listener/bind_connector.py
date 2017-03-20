import socket
import asyncore
import os, sys
import select
import errno
from websocket import create_connection
from Commands import APIClient
import json

class TCPBindConnector(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.__module_name = sys.argv[-1]
        self.wsport = 49999
        self.connection = create_connection("ws://%s:%s" % ("127.0.0.1", self.wsport))
        self.api = APIClient(self.connection)
        self.pid = os.getpid()
        self.hello()
        self.run()

    def handle_connect(self):
        self.send_message("Connection to %s:%s succeeded" % (self.host, self.port), 1)

    def handle_close(self):
        self.send_message("\nShell was disconnected", 2)
        self.connection.close()
        self.close()
        sys.exit(1)

    def handle_read(self):
        data = self.recv_all()
        if data:
            self.send_message(data, 1)

    def recv_all(self, chunk=4096):
        buffer = []
        while 1:
            try:
                data = self.recv(chunk)
                if not data:
                    break
                buffer.append(data)
            except socket.error, e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    #  There is no data
                    break
        return "".join(buffer)

    def handle_write(self):
        res = select.select([self.connection.sock], [], [], 0.2)
        if not res[0]:
            return
        resp = json.loads(self.connection.recv())
        command = resp.get('message')
        if not command:
            return
        self.send(command+"\n")

    def hello(self):
        self.api.hello(self.__module_name, 'listener')

    def run(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        options = self.get_options()
        self.host = options.get('HOST')
        self.port = options.get('PORT')
        self.send_message('Trying to connect to %s:%s' % (self.host, self.port))
        self.connect((self.host, self.port))

    def get_options(self):
        resp = self.api.send_command('get_listener_options', module_name=self.__module_name)
        return resp

    def send_message(self, message, state=0):
        ''' Listener message to gui
        :param message: Message from shell
        :param state: 0 - shell is not connected
                      1 - shell connected
                      2 - shell disconnected
        '''
        self.api.send_command('on_listener_message', message=message, module_name=self.__module_name, state=state)

    def recv_command(self):
        data = self.connection.recv()
        data = json.loads(data)
        return data.get('message')

if __name__=="__main__":
    server = TCPBindConnector()
    asyncore.loop()

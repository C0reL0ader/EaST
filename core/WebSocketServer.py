import struct
import SocketServer
import logging
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
from StringIO import StringIO
import sys
import errno
import socket


from Commands import Commands

HOST = "0.0.0.0"
PORT = 8080

FIN    = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

OPCODE_TEXT = 0x01
CLOSE_CONN  = 0x8


class WebSocketsHandler(SocketServer.StreamRequestHandler):
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def __init__(self, request, client_address, server):
        SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)
        self.server = server

    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        #self.server.logger.info("connection established"+ self.client_address.__str__())
        self.handshake_done = False
        self.keep_alive = True

    def handle(self):
        while self.keep_alive:
            if not self.handshake_done:
                self.handshake()
            elif self.valid_client:
                self.read_next_message()

    def read_bytes(self, num):
        try:
            bytes = self.rfile.read(num)
        except socket.error as error:
            if error.errno == errno.WSAECONNRESET:
                return (None, None)
        return map(ord, bytes)

    def read_next_message(self):
        b1, b2 = self.read_bytes(2)

        if not b1:
            self.keep_alive = 0
            return

        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        
        if opcode == CLOSE_CONN:
            self.keep_alive = 0
            return
        if not masked:
            self.keep_alive = 0
            return

        if payload_length == 126:
            payload_length = struct.unpack(">H", self.rfile.read(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack(">Q", self.rfile.read(8))[0]

        masks = self.read_bytes(4)
        decoded = ""
        for char in self.read_bytes(payload_length):
            char ^= masks[len(decoded) % 4]
            decoded += chr(char)
        self.on_message(decoded)

    def send_message(self, message, req=None):
        if message == "":
            return
        if req:
            self.request = req
        self.request.send(chr(129))
        length = len(message)
        if length <= 125:
            self.request.send(chr(length))
        elif 126 <= length <= 65535:
            self.request.send(chr(126))
            self.request.send(struct.pack(">H", length))
        else:
            self.request.send(chr(127))
            self.request.send(struct.pack(">Q", length))
        self.request.send(message)

    def handshake(self):
        data = self.request.recv(1024).strip()
        new_data = data.split('\r\n', 1)
        if not new_data:
            return
        headers = Message(StringIO(data.split('\r\n', 1)[1]))
        if headers.get("Upgrade", None) == "Websocket" or headers.get("Upgrade", None) == "websocket":
            key = headers['Sec-WebSocket-Key']
            digest = b64encode(sha1(key + self.magic).hexdigest().decode('hex'))
            response = 'HTTP/1.1 101 Switching Protocols\r\n'
            response += 'Upgrade: websocket\r\n'
            response += 'Connection: Upgrade\r\n'
            response += 'Sec-WebSocket-Accept: %s\r\n\r\n' % digest
            self.handshake_done = self.request.send(response)
            self.valid_client = True

    def on_message(self, message):
        if not message:
            return
        self.server.command_handler.execute(message, self)


class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, request_handler_class, bind_and_activate=True):
        SocketServer.TCPServer.__init__(self, server_address, request_handler_class)
        self.command_handler = Commands(self)
        self.logger = logging.getLogger()
        self.all_processes = []
        self.allow_reuse_address = True;

    def add_process(self, process):
        self.all_processes.append(process)

    def remove_process(self, process):
        self.all_processes.remove(process)

    def kill_all_processes(self):
        for proc in self.all_processes:
            proc.kill()

if __name__ == "__main__":
    server = ThreadedServer((HOST, PORT), WebSocketsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        # ctrl+c will kill a server
        print "Killing server"
        server.shutdown()

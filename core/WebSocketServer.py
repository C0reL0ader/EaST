import Queue
import asyncore
import errno
import json
import logging
import struct
from StringIO import StringIO
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
import socket
from threading import Thread

import sys

from Commands import Commands

FIN = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f
OPCODE_TEXT = 0x01
CLOSE_CONN = 0x8


class ClientTypes:
    ui = "ui"
    module = "module"
    listener = "listener"


class WebSocketServer(asyncore.dispatcher):
    """Receives connections and establishes handlers for each client.
    """

    def __init__(self, host, port, connections):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.address = self.socket.getsockname()
        self.listen(connections)
        self.clients = {}
        self.all_processes = []
        self.command_handler = Commands(self)

    def handle_accept(self):
        # Called when a client connects to our socket
        socket, details = self.accept()
        self.clients[socket] = WebsocketHandler(sock=socket, server=self)

    def handle_close(self):
        self.close()

    def add_process(self, process):
        self.all_processes.append(process)

    def remove_process(self, process):
        if process in self.all_processes:
            self.all_processes.remove(process)

    def kill_all_processes(self):
        for client in self.clients.values():
            client.close()
        for proc in self.all_processes:
            proc.kill()
        self.close()
        sys.exit(1)

    def get_client_by_name(self, name):
        for client in self.clients.values():
            if client.name == name:
                return client
        return None

    def send_message_to_client(self, name, message):
        client = self.get_client_by_name(name)
        if client:
            client.send_message(message)

    def send_message_to_all_uis(self, message):
        ui_clients = [client for client in self.clients.values() if client.type == ClientTypes.ui]
        for client in ui_clients:
            client.send_message(message)


class WebsocketHandler(asyncore.dispatcher):
    """Handles echoing messages from a single client.
    """
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    def __init__(self, sock, server=None):
        self.name = ""
        self.type = ""
        self.server = server
        self.handshake_done = False
        self.keep_alive = True
        self.valid_client = False
        self.data_to_write = Queue.Queue()
        self.logger = logging.getLogger(__name__)
        asyncore.dispatcher.__init__(self, sock=sock)
        return

    def writable(self):
        """Call handle_write only if data_to_write is not empty"""
        return not self.data_to_write.empty()

    def readable(self):
        """Call handle_read only if connection is keep_alive"""
        return self.keep_alive

    def handle_write(self):
        """Write as much as possible of the most recent message we have received."""
        data = self.data_to_write.get()
        self.send(data)

    def send_message(self, message):
        self.data_to_write.put(chr(129))
        length = len(message)
        if length <= 125:
            self.data_to_write.put(chr(length))
        elif 126 <= length <= 65535:
            self.data_to_write.put(chr(126))
            self.data_to_write.put(struct.pack(">H", length))
        else:
            self.data_to_write.put(chr(127))
            self.data_to_write.put(struct.pack(">Q", length))
        self.data_to_write.put(message)

    def handle_read(self):
        """Read an incoming message from the client"""
        if not self.handshake_done:
            self.handshake()
        elif self.valid_client:
            self.read_next_message()

    def handshake(self):
        data = self.recv(1024).strip()
        new_data = data.split('\r\n', 1)
        if not new_data:
            return
        headers = Message(StringIO(data.split('\r\n', 1)[1]))
        if headers.get("Upgrade", None).lower() == "websocket":
            key = headers['Sec-WebSocket-Key']
            digest = b64encode(sha1(key + self.magic).hexdigest().decode('hex'))
            response = 'HTTP/1.1 101 Switching Protocols\r\n'
            response += 'Upgrade: websocket\r\n'
            response += 'Connection: Upgrade\r\n'
            response += 'Sec-WebSocket-Accept: %s\r\n\r\n' % digest
            self.send(response)
            self.handshake_done = True
            self.valid_client = True

    def read_bytes_splitted(self, num):
        try:
            bytes = self.read_bytes(num)
        except socket.error as error:
            if error.errno == errno.WSAECONNRESET:
                return (None, None)
        return map(ord, bytes)

    def read_bytes(self, num):
        data = self.buffer[:num]
        self.buffer = self.buffer[num:]
        return data

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

    def read_next_message(self):
        try:
            self.buffer = self.recv_all()
        except socket.error as error:
            if error.errno == errno.WSAECONNRESET:
                pass
        try:
            b1, b2 = self.read_bytes_splitted(2)
        except:
            self.keep_alive = False
            return

        if not b1:
            self.keep_alive = False
            return

        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if opcode == CLOSE_CONN:
            self.keep_alive = False
            return
        if not masked:
            self.keep_alive = False
            return

        if payload_length == 126:
            payload_length = struct.unpack(">H", self.read_bytes(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack(">Q", self.read_bytes(8))[0]

        masks = self.read_bytes_splitted(4)
        decoded = ""
        for char in self.read_bytes_splitted(payload_length):
            char ^= masks[len(decoded) % 4]
            decoded += chr(char)
        self.on_message(decoded)

    def on_message(self, message):
        message = parse_json(message)
        if not message:
            return
        # Check for hello
        if "hello" in message:
            self.hello(message["hello"])
            return
        self.server.command_handler.execute(message, self)

    def hello(self, args):
        """After connection to server client must do handshake sending its name and type
        Params:
                args: (dict)
                args["name"]: (String)
                args["type"]: (String) 'module', 'listener' or 'ui'
        """
        name = self.check_and_make_unique_name(args["name"])
        type = args["type"]
        self.type = type
        self.name = name
        self.logger.info("Hello," + self.name)
        self.send_message(json.dumps(dict(command="hello")))

    def check_and_make_unique_name(self, name, suffix=1):
        names = [client.name for client in self.server.clients.values()]
        if name not in names:
            return name
        new_name = "%s(%s)" % (name, suffix)
        if new_name in names:
            suffix += 1
            return self.check_and_make_unique_name(name, suffix)
        else:
            return name

    def handle_close(self):
        self.close()
        if self.socket in self.server.clients:
            del self.server.clients[self.socket]


def parse_json(message):
    if not message:
        return None
    try:
        data = json.loads(message)
    except Exception, e:
        logging.getLogger(__name__).exception(e)
        return None
    return data


if __name__ == '__main__':
    import socket
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )

    host, port = ('', 49999) # let the kernel give us a port
    server = WebSocketServer(host, port, 1000)
    asyncore.loop()
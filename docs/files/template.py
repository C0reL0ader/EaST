#!/usr/bin/env python

#IMPORTS SECTION
from collections import OrderedDict  # for rigth options order
from Sploit import Sploit  # base class for module
#INFO SECTION
INFO = {}
INFO['NAME'] = ''  # Module name
INFO['DESCRIPTION'] = ''  # Short description of vulnerability
INFO['VENDOR'] = ''  # Vulnerable soft vendor's homepage
INFO['CVE Name'] = ''  # CVE if exists(like 2017-9999)
INFO['NOTES'] = """ """  # Full description of vulnerability
INFO['DOWNLOAD_LINK'] = ''  # Link to vulnerable soft
INFO['LINKS'] = []  # Some helpful links(like exploit's page on exploit-db or link to some article)
INFO['CHANGELOG'] = ''  # Usually it's exploit writing date
INFO['PATH'] = 'General/'  # Virtual path of module. It used by module tree in GUI

# OPTIONS SECTION
OPTIONS = OrderedDict()
OPTIONS['HOST'] = '127.0.0.1'
OPTIONS['PORT'] = 9999


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)

    def run(self):
        #Get options from gui
        self.args()
        #YOUR CODE

        ##########
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()

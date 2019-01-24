from Sploit import Sploit
from collections import OrderedDict

INFO = OrderedDict()
INFO['NAME'] = ""
INFO['DESCRIPTION'] = ""
INFO['VENDOR'] = ""
INFO['CVE Name'] = ""
INFO['NOTES'] = """
"""
INFO['DOWNLOAD_LINK'] = ""
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "/"
INFO['AUTHOR'] = ""

OPTIONS = OrderedDict()
{MODULE_OPTIONS}

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

{MODULE_FIELDS}

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
{MODULE_GETARGS}
        

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting') # send message to gui
        ####################
        # Your main code here
        ####################
        self.finish(True) # If True - module succeeded, if False - module failed


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
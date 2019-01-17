from Sploit import Sploit
from collections import OrderedDict

INFO = {}
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
OPTIONS["OPTION1"] = "VALUE1", dict(description="Option description") # Will create text field in GUI and returns "str" value type
OPTIONS["OPTION2"] = 10, dict(description="Option description") # Will create text field and returns "int" value type
OPTIONS["OPTION3"] = False, dict(description="Option description") # Will create checkbox and returns "bool" value type
OPTIONS["OPTION4"] = dict(options=["value1", "value2"], selected="value1"), dict(description="Option description") # Will create combobox and you'll can choose value(in this case "value1" or "value2"). Field "selected" makes value default

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.option1 = self.args.get("OPTION1")
        self.option2 = self.args.get("OPTION2")
        self.option3 = self.args.get("OPTION3")
        self.option4 = self.args.get("OPTION4")

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
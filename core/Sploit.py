#!/usr/bin/env python
import time
import os
import sys
import json
import logging
import socket

sys.path.append("./../core")


from websocket import create_connection

PORT = 49999
HOST = "localhost"

#simple common exception handler for method run
def _deco(self, func):
    def wrapper():
        try:
            res = func()
        except Exception as e:
            res = None
            self.logger.exception(e)
            self.log(e)
            self.finish(False)
        return res
    return wrapper

class Sploit:
    """
        This is the base class for all exploits in the tool.
    """
    def __init__(self, logfile="", debugfile="", logger=None):
        # Logger will need in the future to log to file
        """
            Initialization routines.
        """
        # Module name
        self.name = ""
        # PID of running module
        self.pid = os.getpid()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler('Logs/exploits.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.connection = create_connection("ws://%s:%s" % (HOST, PORT),
                                            sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
        self.hello()
        self.run = _deco(self, self.run)
        return

    def args(self, options={}):
        """
            This function get required options from server.
        """
        req = dict(command="get_args_for_module", args=dict(pid=self.pid))
        self.logger.info(req.__str__())
        self.connection.send(json.dumps(req))
        resp = self.connection.recv()
        return json.loads(resp)

    def get_listener_options(self):
        """
        :return: Listener options from server
        """
        return

    def check(self):
        """
            This function is checking the response banner to verify that
            target is vulnerable or not.
        """
        return

    def run(self):
        """
            The main function that does all of the magic.
            It returns 0 on failed and 1 on success.
        """
        return

    def log(self, message='', inline=False, replace=False):
        """
            This function provides necessary routines
            for logging any results of the exploit.
            :param message: Message to log
            :param inline: Prints log inline
            :param replace: Replace last log message
        """
        try:
            self.send_message(message, inline=inline, replace=replace)
        except Exception as e:
            self.logger.exception(e)
        return

    def finish(self, is_successful):
        """
            This function finishes module execution
            if <is_successful>=True - module done succefully
            if <is_successful>=False - module failed
        """
        if is_successful:
            msg = "Module %s was succeeded" % self.name
        else:
            msg = "Module %s was failed" % self.name
        self.send_message(msg, is_successful)
        sys.exit()


    def writefile(self, filedata, filename=""):
        """
        This function is for saving the result of the
        exploit if the results are too large to print or if the aim
        of the exploit is to steal some info or download the file.
        """
        dirname = "./OUTPUTS/" + self.name
        if not filename:
            filename = "response_" + time.strftime("%b_%d_ %Y_%H-%M-%S", time.gmtime()) + ".html"
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except Exception, exception:
                """
                ! The kind of error sould be
                managed with respect to 
                os version or type...
                """
                self.logger.error(
                    "An error has occured during creating the directory '%s' : <%s>"
                    % (dirname, str(sys.exc_info()[1]))
                )
                return 0
        filepath = dirname + "/" + filename
        fd = file(filepath, "wb+")
        try:
            fd.write(filedata)
        except Exception:
            self.logger.error("An error has occured during writing output : <%s>" % (str(sys.exc_info()[1])))
            return 0
        fd.close()
        self.log("wrote to %s" % filepath)
        return 1

    def send_message(self, message, is_successful=None, inline=False, replace=False):
        self.logger.debug(message)
        args = dict(pid=self.pid, module_name=self.name, message=str(message).decode("cp1251").encode("utf-8"),
                    state=is_successful, inline=inline, replace=replace)
        req = dict(command="message", args=args)
        self.connection.send(json.dumps(req))
        # waiting for response
        self.connection.recv()
        if is_successful is not None:
            self.connection.close()

    def hello(self):
        args = dict(hello=dict(name=self.pid.__str__(), type="module"))
        self.connection.send(json.dumps(args))
        # wait for hello
        self.connection.recv()

if __name__ == "__main__":
    s = Sploit()
    s.log("123")

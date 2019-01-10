#!/usr/bin/env python
import sys
import traceback
import time
import os
import json
import logging
import socket
import base64
from random import choice
from string import ascii_letters
from string import digits
from websocket import create_connection
sys.path.append("./../core")
from Commands import APIClient


PORT = 49999
HOST = "127.0.0.1"


# simple common exception handler for method run
def _deco(self, func):
    def wrapper():
        try:
            res = func()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            self.finish(False)
            # res = None
            # self.logger.exception(e)
            # self.log(e)
            # self.finish(False)
        return res
    return wrapper


class Sploit:
    """
        This is the base class for all exploits in the tool.
    """
    def __init__(self, logfile="", debugfile="", logger=None, options={}):
        # Logger will need in the future to log to file
        """
            Initialization routines.
        """
        # Module name
        self.name = ""
        self.__module_name = sys.argv[-1]
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
        self.API_COMMANDS_HANDLER = APIClient(self.connection)
        self.hello()
        self.run = _deco(self, self.run)
        if bool(options):
            self.create_args(options)

    def create_args(self, options={}):
        self.args = self.args(options)
        for o in options:
            var = o.lower().replace(" ", "_")
            var_val = self.args.get(o, options[o])
            setattr(self, var, var_val)
        return

    def args(self, options={}):
        """
            This function get required options from server.
        """
        resp = self.API_COMMANDS_HANDLER.send_command('get_module_args', module_name=self.__module_name)
        return resp

    def get_listener_options(self):
        """
        :return: Listener options from server
        """
        resp = self.API_COMMANDS_HANDLER.send_command('get_listener_options', module_name=self.__module_name)
        return resp

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

    def logImage(self, image):
        """Sends image to GUI's log window
        :param image: (Stream)
        :return:
        Usage:
        1)    with open('example.jpg', 'rb') as f:
                  image = f.read()
                  self.log(image)
        2)    image = urllib2.urlopen('http://blablabla/image.jpg').read()
              self.log(image)
        """
        image = base64.b64encode(image)
        try:
            self.send_message(image, msg_type="image")
        except Exception as e:
            self.logger.exception(e)
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
            print e
        return

    def finish(self, is_successful):
        """
        Finishes module execution
        Args:
            is_successful: (bool) If True - module succeeded, False - module failed
        """
        if is_successful:
            msg = "Module %s was succeeded" % self.name
        else:
            msg = "Module %s was failed" % self.name
        self.send_message(msg, is_successful)
        sys.exit()

    def writefile(self, filedata, filename=""):
        """
        Save the result of the
        exploit if the results are too large to print or if the aim
        of the exploit is to steal some info or download the file.
        Args:
            filedata: (string) Contents of file
            filename: (string) Filename
        """
        dirname = "./OUTPUTS/" + self.name
        if not filename:
            filename = "response_" + time.strftime("%b_%d_ %Y_%H-%M-%S", time.gmtime()) + ".html"
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except Exception as e:
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

    def connect_to_remote_shell(self, target_ip, target_port):
        """
        Use this method to connect to bind paylod
        Args:
            target_ip: IP address of target
            target_port: PORT of bind payload
        """
        import subprocess
        from Commands import FW_ROOT_PATH
        bind_shell_path = os.path.join(FW_ROOT_PATH, 'listener', 'bind_connector.py')
        self.API_COMMANDS_HANDLER.send_command('add_listener_options', module_name=self.__module_name,
                                               options=dict(HOST=target_ip, PORT=target_port))
        listener_process = subprocess.Popen([sys.executable, bind_shell_path, self.__module_name], shell=False, env=os.environ.copy())
        self.API_COMMANDS_HANDLER.send_command('add_listener_pid', module_name=self.__module_name, pid=listener_process.pid)


    def send_message(self, message, is_successful=None, inline=False, replace=False, msg_type="text"):
        self.logger.debug(message)
        self.API_COMMANDS_HANDLER.send_command('register_module_message', module_name=self.__module_name,
                                               message=str(message), state=is_successful,
                                               inline=inline, replace=replace, type=msg_type)
        if is_successful is not None:
            self.connection.close()

    def is_listener_connected(self):
        """
        Check listener state
        :return: True - if shell is connected to listener
                 False - if shell is not connected to listener
                 None - if listener is not available
        """
        time.sleep(1)  # for limiting requests
        resp = self.API_COMMANDS_HANDLER.send_command('is_listener_connected', module_name=self.__module_name)
        return resp.get('state')

    def hello(self):
        self.API_COMMANDS_HANDLER.hello(self.__module_name, 'module')

    def random_string(self, size=6, chars=ascii_letters + digits):
        # you can change chars to digits or specify your string value
        return ''.join(choice(chars) for _ in range(size))

if __name__ == "__main__":
    s = Sploit()
    s.log("123")

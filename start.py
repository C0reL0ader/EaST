import os, sys
import threading
import logging
import BaseHTTPServer
from ui.httpd import HTTPRequestHandler
import subprocess
import zipfile
from shutil import rmtree
import argparse
import importlib
from core.WebSocketServer import ThreadedServer, WebSocketsHandler

sys.path.append("./core")
sys.path.append("./shellcodes")

VERSION = "0.9.4"

class FrameworkStarter:
    def __init__(self, host="localhost", ws_port=49999, port=80):
        self.host = host
        self.port = port
        self.ws_port = ws_port
        self.platform = "win" if os.name == "nt" else "other"
        self.logger = None
        self.prepare_logging(False)
        self.prepare_environment()
        self.dependencies = ["six", "websocket"]
        self.install_missing_deps()
        self.parse_args()

    def prepare_logging(self, verbose):
        if not os.path.exists("Logs"):
            os.makedirs("Logs")
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler('Logs/commonLog.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        if verbose:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def prepare_environment(self):
        root_dir = os.getcwd()
        core = os.path.join(root_dir, "core")
        shellcodes = os.path.join(root_dir, "shellcodes")
        paths = [root_dir, core, shellcodes]
        os.environ.data["PYTHONPATH"] = ";".join(paths) if self.platform == "win" else ":".join(paths)

    def install_missing_deps(self):
        """
        Check and install missing dependencies
        """
        is_there_deps = False
        for module in self.dependencies:
            try:
                imported = importlib.import_module(module)
            except ImportError:
                is_there_deps = True
                print("Module %s will be installed" % module)
                self.install_python_lib(module)
        if is_there_deps:
            print("All dependencies installed")
            os.execv(sys.executable, [sys.executable] + sys.argv)


    def install_python_lib(self, relative_path):
        modules_path = os.path.join(os.getcwd(), "3rdPartyTools", "")
        zipOb = zipfile.ZipFile(modules_path + relative_path+'.zip')
        zipOb.extractall(modules_path + relative_path)
        module_path = ''.join(["", str(os.getcwd()), "/3rdPartyTools/"+relative_path+"/"])
        args = [sys.executable, '%ssetup.py' % module_path, 'install']
        proc = subprocess.Popen(args, cwd=module_path, shell=False)
        proc.communicate()
        message = "%s installed successfully" % relative_path
        print(message)
        rmtree(modules_path + relative_path)

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', dest='port', default=80, type=int,
                            help='Webserver port')
        parser.add_argument('--default-route', dest='use_default_route',
                            help='Use 0.0.0.0 as webserver IP', action='store_const',
                            const=True,
                            default=False)
        args = parser.parse_args()
        if args.port:
            self.port = args.port
        if args.use_default_route:
            self.host = "0.0.0.0"
        return args

    def start_servers(self):
        print("Starting servers...")
        ws_server = ThreadedServer((self.host, self.ws_port), WebSocketsHandler)
        http_server = BaseHTTPServer.HTTPServer((self.host, self.port), HTTPRequestHandler)
        th1 = threading.Thread(target=ws_server.serve_forever)
        th2 = threading.Thread(target=http_server.serve_forever)
        threads = [th1, th2]
        for t in threads:
            t.daemon = True
            t.start()
        print("GUI available @ %s:%s" % (self.host, self.port))
        while len(threads) > 0:
            try:
                # Join all threads using a timeout so it doesn't block
                # Filter out threads which have been joined or are None
                threads = [t.join(1000) for t in threads if t is not None and t.isAlive()]
            except KeyboardInterrupt:
                ws_server.shutdown()
                ws_server.kill_all_processes()
                http_server.shutdown()
                os._exit(1)


if __name__ == "__main__":
    runner = FrameworkStarter()
    runner.start_servers()

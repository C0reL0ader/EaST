import os, sys
import threading
import logging
import BaseHTTPServer
from ui.httpd import HTTPRequestHandler
import subprocess
import zipfile
from shutil import rmtree

sys.path.append("/core")


def prepare_logging(log_to_console):
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('Logs/commonLog.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if log_to_console:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)


def install_missing_modules():
    """
    Install unpacked python modules from 3rdPartyTools
    """
    modules_paths = ["six","websocket_client"]
    answer = ""
    while not answer:
        answer = raw_input("Do you want to install dependencies?[Y/n]")
        if answer == '':
            break
        if answer.lower() != 'y' and answer.lower() != 'n':
            print "Answer must be 'y' or 'n'"
            continue
    if answer.lower() == 'n':
        sys.exit(1)
    else:
        for module in modules_paths:
            install_python_lib(module)


def install_python_lib(relative_path):
    modules_path = os.getcwd() + "\\3rdPartyTools\\"
    zipOb = zipfile.ZipFile(modules_path + relative_path+'.zip')
    zipOb.extractall(modules_path + relative_path)
    module_path = ''.join(["", str(os.getcwd()), "/3rdPartyTools/"+relative_path+"/"])
    args = [sys.executable, '%ssetup.py' % module_path, 'install']
    proc = subprocess.Popen(args, cwd=module_path, shell=False)
    proc.communicate()
    message = "%s installed successfully" % relative_path
    print(message)
    rmtree(modules_path + relative_path)
    logger.info(message)


VERSION = "0.9.2"
WS_HOST = "localhost"
WS_PORT = 49999
CLI_PORT = 80

from core.WebSocketServer import ThreadedServer, WebSocketsHandler

if __name__ == "__main__":
    LOG_TO_CONSOLE = False
    prepare_logging(LOG_TO_CONSOLE)
    logger = logging.getLogger()
    if len(sys.argv) > 1:
        CLI_PORT = int(sys.argv[1])
    try:
        import websocket
    except ImportError:
        print "Module 'websocket-client' not found."
        logger.error("Module %s not found." % "websocket")
        install_missing_modules()
    print("Starting servers...")
    ws_server = ThreadedServer((WS_HOST, WS_PORT), WebSocketsHandler)
    http_server = BaseHTTPServer.HTTPServer((WS_HOST, CLI_PORT), HTTPRequestHandler)
    th1 = threading.Thread(target=ws_server.serve_forever)
    th2 = threading.Thread(target=http_server.serve_forever)
    threads = [th1, th2]
    for t in threads:
        t.daemon = True
        t.start()
    print("GUI available @ %s:%s" % (WS_HOST, CLI_PORT))
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

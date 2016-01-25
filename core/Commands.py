import os
import subprocess
import sys
import json
import logging

import Modules
import PortScannerMT
from Modules import ModulesHandler
from ListenerHandler import ListenerHandler
from OptionsParser import OptionsParser
from ReportGenerator import ReportGenerator

EXPLOITS_PATH = "./exploits/"
LISTENER = "./listener/listener.py"
PACKS_PATH = "3rdParty/"


class Commands:
    def __init__(self, server):
        self.commands = {"exploit": self.start_module,
                         "message": self.register_module_message,
                         "modules_log": self.get_modules_log,
                         "kill_process": self.kill_process,
                         "options": self.get_module_options,
                         "get_args_for_module": self.get_module_args,
                         "restore_tabs": self.restore_tabs,
                         "get_all_server_data": self.get_all_server_data,
                         "listener_message": self.on_listener_message,
                         "listener_get_options": self.get_listener_options,
                         "gui_command_to_listener": self.gui_command_to_listener,
                         "get_source": self.get_source,
                         "save_source": self.save_source,
                         "generate_report": self.generate_report
                         }
        self.server = server
        self.using_module = ""
        self.available_modules = self.get_all_modules_paths()
        self.modules_handler = ModulesHandler(server)
        self.listener_handler = ListenerHandler(server)
        self.logger = logging.getLogger()
        self.options_parser = OptionsParser()
        self.port_scanner = PortScannerMT.Scanner(4000, 5000)
        self.report_generator = ReportGenerator()

    def get_all_modules_paths(self):
        """Get common modules and modules from packs if available"""
        exploits = Modules.get_modules_names_dict(EXPLOITS_PATH)
        if not os.path.exists(PACKS_PATH):
            os.makedirs(PACKS_PATH)
        files = os.listdir(PACKS_PATH)
        packs = []
        for f in files:
            path_to_pack = os.path.join(PACKS_PATH, f)
            if os.path.isdir(path_to_pack):
                pack_dirs = [fname.lower() for fname in os.listdir(path_to_pack)]
                if "exploits" in pack_dirs:
                    full_path_to_pack_exploits = os.path.join(path_to_pack, "exploits")
                    exploits.update(Modules.get_modules_names_dict(full_path_to_pack_exploits))
        return exploits

    def execute(self, message, request):
        """
        Execution of command from websocket-client
        @param (JSON)message:  Object, containing keys "command" and "args"
        @param request: Websocket client request. Used to send response from server to this client
        """
        if message == "":
            return
        data = parse_json(message)
        if not data or type(data) is not dict or "command" not in data.keys() or "args" not in data.keys():
            resp = dict(command="message", args="This is not command")
            request.send_message(json.dumps(resp))
            return
        command = data["command"]
        args = data["args"]
        if command in self.commands.keys():
            self.commands[command](args, request)

    def start_module(self, args, request):
        """Run a module
        @param (dict)args: key 'module_name' => (string) Name of module
                           key 'listener' => (bool) Use listener
                           key 'listener_options' => (dict) Listener options
        """
        if args["module_name"] not in self.available_modules.keys():
            return
        module_name = self.available_modules[args["module_name"]]
        use_listener = args["use_listener"]
        options = args["options"]
        new_module_name = self.modules_handler.make_unique_name(args["module_name"])
        if use_listener:
            free_socket_data = self.port_scanner.scan(search_for='closed', first_match=True, nthreads=10)
            if free_socket_data:
                listener_options = dict(PORT=free_socket_data[0][1])
                print listener_options

            listener_process = subprocess.Popen([sys.executable, LISTENER], shell=False, env=os.environ.copy())
            self.listener_handler.addListener(new_module_name, listener_process, listener_options)
            self.server.add_process(listener_process)
        process = subprocess.Popen([sys.executable, module_name], shell=False, env=os.environ.copy())
        options = self.options_parser.parse_data(options)
        self.modules_handler.register_process(new_module_name, args["module_name"], process, options)
        self.server.add_process(process)

        # We need to register first log message of module
        log_args = {"pid": process.pid,
                    "module_name": new_module_name,
                    "message": "Module %s has been started" % new_module_name,
                    "listener": use_listener,
                    "state": None
                    }
        self.register_module_message(log_args, request)

        # Send command to GUI to start logging
        self.send_all(log_args, request, "start_module")

    def get_all_server_data(self, args, request):
        """
        Send server data to gui(version, available modules)
        """
        data = []
        for name in self.available_modules.keys():
            data.append([self.available_modules[name], name])
        available_modules = self.modules_handler.get_modules_info(data)
        
        # Get framework version
        module = self.modules_handler.import_from_uri("start.py")
        version = "?"
        if module and hasattr(module, "VERSION"):
            version = module.VERSION
        args = dict(modules=available_modules, version=version)
        resp = dict(command="set_all_data", args=args)
        request.send_message(json.dumps(resp))        

    def restore_tabs(self, args, request):
        """ Send data of working modules to restore tabs in gui
        """
        log = self.modules_handler.get_full_log()
        listeners_messages = self.listener_handler.getListenersMessages()
        for module_name in log.keys():
            if module_name in listeners_messages.keys():
                log[module_name]["listener"]=listeners_messages[module_name]
            else:
                log[module_name]["listener"] = None
        resp = dict(command="restore_tabs", args=log)
        request.send_message(json.dumps(resp))

    def get_modules_log(self, args, request):
        """Get last log message of module
        :param args: (dict):
                    key "module_name":(string) Name of module;
                    key "pid": (int) PID of this module
        """
        modules = self.modules_handler.get_full_log()
        listeners_messages = self.listener_handler.getListenersMessages()
        for module_name in modules.keys():
            if module_name in listeners_messages.keys():
                modules[module_name]["listener"] = listeners_messages[module_name]
        resp = dict(command="modules_log", args=modules)
        request.send_message(json.dumps(resp))
        return

    def kill_process(self, args, request):
        """Kills running process
                :param args: (dict):
                key "module_name":(string) Name of module;
                key "pid": (int) PID of this module
        """
        module_name = args["module_name"]
        if module_name not in self.modules_handler.processes.keys():
            return
        remove = "remove" in args
        self.modules_handler.kill_process(module_name, remove)
        self.listener_handler.killListener(module_name)

    def register_module_message(self, args, request):
        """Add log message from module
        @param (dict)args: (string)'message'=>Message from module;
                           (bool)'state'=>State of module(success, fail or nothing);
                           (int)'pid'=>Process ID of module
                           (bool)'inline'=>Write on last line if True
                           (bool)'replace'=>Replace last line if True
        """
        inline = args.get("inline", False)
        replace = args.get("replace", False)
        if "message" in args.keys() and "state" in args.keys() and "pid" in args.keys():
            self.modules_handler.add(args["pid"], args["message"], args["state"], inline, replace)
            if args["state"] is not None:
                self.generate_report(args["pid"])

    def get_module_options(self, args, request):
        """Send options of module to gui
        @param (dict)args: (string)'module_name'=>Name of module
        """
        if args["module_name"] in self.available_modules.keys():
            opts = self.modules_handler.get_available_options_for_module(self.available_modules[args["module_name"]])
        opts = self.options_parser.prepare_options(opts)
        json_resp = []
        for key in opts.keys():
            json_resp.append(dict(option=key, value=opts[key]))
        self.send_all(json_resp, request, "options")



    def get_module_args(self, args, request):
        """
        Send modules options to running module
        """
        resp = self.modules_handler.get_module_options(args["pid"])
        module_name = self.modules_handler.get_module_name_by_pid(args["pid"])
        listener_options = self.listener_handler.getListenerOptionsByName(module_name)
        resp["listener"] = listener_options
        request.send_message(json.dumps(resp))

    def on_listener_message(self, args, request):
        """
        Add message from listener to gui or get last command from gui to listener
        """
        pid = args['pid']
        message = args['message']
        action = args['action']
        state = args['state']
        if action == 'get':
            message = self.listener_handler.getMessageFromGui(pid)
            request.send_message(json.dumps(dict(message=message)))
            return
        if action == 'add':
            self.listener_handler.addMessageToGui(pid, message)
        if state is not None:
            self.listener_handler.setShellConnected(pid, state)

    def get_listener_options(self, args, request):
        """
        Send options sets by gui to listener
        """
        pid = args['pid']
        options = self.listener_handler.getListenerOptions(pid)
        request.send_message(json.dumps(options))

    def gui_command_to_listener(self, args, request):
        """
        Add gui command to listener to queue
        """
        module_name = args['module_name']
        message = args['message']
        self.listener_handler.addMessageFromGui(module_name, message)

    def get_source(self, args, request):
        """
        Get source code of module
        """
        module_name = args['module_name']
        with open(self.available_modules[args['module_name']]) as file:
            lines = file.read().splitlines()
            source = "\n".join(lines)
        resp = dict(command="get_source", args=dict(message=source, module_name=module_name))
        request.send_message(json.dumps(resp))

    def save_source(self, args, request):
        """
        Save edited source code of module
        """
        code = args['message'].encode('utf-8')
        f = open(self.available_modules[args['module_name']],'w')
        f.write(code)
        f.close()

    def generate_report(self, pid):
        module_name = self.modules_handler.get_module_name_by_pid(pid)
        if not module_name:
            return
        module_inst = self.modules_handler.get_module_inst_by_name(module_name)
        listener_inst = self.listener_handler.get_listener_inst_by_name(module_name)
        info = self.modules_handler.get_module_info((self.available_modules[module_inst.original_name], module_name))
        module_temp = {
            "LOG": module_inst.log,
            "RESULT": module_inst.state,
            "IS_SHELL_CONNECTED": listener_inst.isShellConnected if listener_inst else "False",
            "OPTIONS": module_inst.options,
            "LISTENER": listener_inst.options if listener_inst else None
        }
        module_temp.update(info)
        module_temp["CVE"] = module_temp["CVE Name"]
        self.report_generator.append_module(module_temp)


    def send_all(self, message, request=None, command=""):		
        self.logger.debug(message)
        if request:
            resp = {}
            if command:
                resp["command"] = command
            else:
                resp["command"] = "message"
            resp["args"] = message
            request.send_message(json.dumps(resp))


def parse_json(message):
    try:
        data = json.loads(message)
    except Exception:
        logging.getLogger().warn(str(Exception))
        return None
    return data

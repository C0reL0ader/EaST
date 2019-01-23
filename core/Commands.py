# coding=utf-8
import os
import subprocess
import sys
import json
import logging
import inspect
import Modules
import PortScannerMT
from Modules import ModulesHandler
from OptionsParser import OptionsParser
from ReportGenerator import ReportGenerator
from ServiceMessagesHandler import ServiceMessagesHandler
from uuid import uuid4

FW_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
EXPLOITS_PATH = os.path.join(FW_ROOT_PATH, 'exploits')
LISTENER_PATH = os.path.join(FW_ROOT_PATH, 'listener', 'listener.py')
PACKS_PATH = os.path.join(FW_ROOT_PATH, '3rdParty')


class APIClient:
    def __init__(self, wsclient):
        self.wsclient = wsclient

    def check_coding(self, kwargs):
        for key, value in kwargs.items():
            if type(value) is unicode:
                value = value.encode('utf-8')
            if type(value) is str:
                try:
                    value.decode('utf-8')
                except UnicodeDecodeError:
                    value = value.decode('utf-8', 'replace')
            kwargs[key] = value

    def hello(self, module_name, type):
        args = json.dumps(dict(hello=dict(name=module_name, type=type), uuid=str(uuid4())))
        self.wsclient.send(args)
        self.wsclient.recv()

    def send_command(self, command, **kwargs):
        cmd = dict(command=command, args=kwargs, uuid=str(uuid4()))
        try:
            req = json.dumps(cmd)
        except UnicodeDecodeError:
            self.check_coding(kwargs)
            req = json.dumps(cmd)
        self.wsclient.send(req)
        res = self.wsclient.recv()
        res = json.loads(res)
        return res['args']


class API:
    def callable(foo):
        def api_wrapped(self, *args, **kwargs):
            return foo(self, *args, **kwargs)

        setattr(api_wrapped, '__wrapped__', foo)
        return api_wrapped

    callable = staticmethod(callable)

    def __init__(self):
        pass


class Commands(API):
    def __init__(self, server):
        API.__init__(self)
        self.commands = self.get_api_functions()
        self.server = server
        self.available_modules = self.get_all_modules_paths()
        self.modules_handler = ModulesHandler(self)
        self.logger = logging.getLogger()
        self.options_parser = OptionsParser()
        self.port_scanner = PortScannerMT.Scanner(4000, 5000)
        self.report_generator = ReportGenerator()
        self.service_messages_handler = ServiceMessagesHandler()

    def get_api_functions(self):
        """
        Find all api_wrapped methods in class Commands
        Returns (dict): method name => method
        """
        api_methods = {k: v for k, v in vars(self.__class__).items() if
                       inspect.isfunction(v) and v.__name__ == 'api_wrapped'}
        return api_methods

    def get_all_modules_paths(self):
        """Get common modules and modules from packs if available"""
        exploits = Modules.get_modules_names_dict(EXPLOITS_PATH)
        if not os.path.exists(PACKS_PATH):
            os.makedirs(PACKS_PATH)
        files = os.listdir(PACKS_PATH)
        for f in files:
            path_to_pack = os.path.join(PACKS_PATH, f)
            if os.path.isdir(path_to_pack):
                pack_dirs = [fname.lower() for fname in os.listdir(path_to_pack)]
                if "exploits" in pack_dirs:
                    full_path_to_pack_exploits = os.path.join(path_to_pack, 'exploits')
                    exploits.update(Modules.get_modules_names_dict(full_path_to_pack_exploits))
        return exploits

    def _get_wrapped_function_required_args(self, func):
        if not hasattr(func, '__wrapped__'):
            return None
        args_spec = inspect.getargspec(func.__wrapped__)
        # Now slice 2 first arguments(self, client) and kw_args
        required_args = args_spec.args[2: - len(args_spec.defaults or [])]
        return args_spec.args, required_args

    def execute(self, message, client):
        """
        Execution of command from websocket-client
        @param message:(Dict)  Object, containing keys "command" and "args"
        @param client:(WebSocketHandler) Websocket client handler. Used to send response from server to this client
        """
        if not message or type(message) is not dict or "command" not in message or "args" not in message:
            self.send_error(client, 'Error while handling request')
            return
        command = message["command"]
        args = message["args"]
        uuid = message.get('uuid')
        args = args if args else {}
        if command not in self.commands:
            self.send_error(client, 'Wrong command')
            return
        func = self.commands[command]
        func_args, func_req_args = self._get_wrapped_function_required_args(func)

        # find missing or excess args
        func_args_set = set(func_args)
        func_req_args_set = set(func_req_args)
        input_args_set = set(args)
        intersection = func_req_args_set.intersection(input_args_set)
        # missing
        if len(intersection) != len(func_req_args_set):
            diff = func_req_args_set.difference(input_args_set)
            msg = 'Following required parameters are missing: %s' % ', '.join(diff)
            print(command, 'Error: %s' % msg)
            self.send_error(client, msg)
            return
        diff = input_args_set.difference(func_args_set)
        if diff:
            msg = 'Following parameters are excess: %s' % ', '.join(diff)
            print(command, 'Error: %s' % msg)
            self.send_error(client, msg)
            return
        # if no errors call func
        resp = func(self, client, **args)
        if uuid:
            client.send_message(dict(command='on_callback', args=resp, uuid=uuid))

    @API.callable
    def start_module(self, client, module_name, use_listener, use_custom_port=False, custom_port=0, listener_type=1, options={}):
        """
        Runs a module
        Args:
            module_name: (string) Name of module
            use_listener: (bool) If True - enable listener for module
            use_custom_port: (bool) Use custom listener port
            custom_port: (int) Custom listener port
            listener_type: (int) 1 - reverse, 2 - bind
            options: (dict) Option of module set up in GUI
        Returns:
            (dict):
                'module_name': (string) Unique name of running module
                'listener': (bool) Is listener enabled
        """
        if module_name not in self.available_modules:
            print('There is no module with name %s' % module_name)
            return
        module_path = self.available_modules[module_name]
        new_module_name = self.modules_handler.make_unique_name(module_name)
        options = self.options_parser.parse_data(options)
        running_module = self.modules_handler.register_process(new_module_name, module_name, options)
        if use_listener and listener_type == 1:
            exclude_ports = self.modules_handler.get_busy_ports_list()
            if use_custom_port and custom_port:
                if custom_port in exclude_ports or self.port_scanner.check_port_state(custom_port):
                    message = 'Lister port %d is busy. Try another port for listener' % custom_port
                    return self.make_error(message)
                listener_options = dict(PORT=custom_port)
            else:
                free_socket_data = self.port_scanner.scan(search_for='closed', first_match=True, nthreads=10,
                                                          exclude=exclude_ports)
                listener_options = dict(PORT=free_socket_data[0][1])
            running_module.listener_options = listener_options
            listener_process = subprocess.Popen([sys.executable, LISTENER_PATH, new_module_name], shell=False, env=os.environ.copy())
            self.modules_handler.add_listener_pid(new_module_name, listener_process.pid)
        process = subprocess.Popen([sys.executable, module_path, new_module_name], shell=False, env=os.environ.copy())
        self.modules_handler.add_module_pid(new_module_name, process.pid)
        return dict(module_name=new_module_name, listener=use_listener)

    @API.callable
    def install_via_pip(self, client, library_name):
        """
        Install python module via pip
        Args:
            library_name: Name of module to install
        """
        import subprocess
        try:
            proc = subprocess.Popen(['pip', 'install', library_name])
        except Exception as e:
            print e
            return self.make_error('Can\'t install module %s' % library_name)
        else:
            proc.communicate()
            if proc.returncode == 0:
                self.service_messages_handler.remove_import_error(library_name)
                return dict(module_to_import=library_name)
            return self.make_error('Can\'t install module %s' % library_name)

    @API.callable
    def get_all_server_data(self, client):
        """
        Returns dict of modules, version, service messages
        """
        data = []
        self.service_messages_handler.reset()
        for name in self.available_modules:
            data.append([self.available_modules[name], name])
        available_modules = self.modules_handler.get_modules_info(data)
        service_messages = self.service_messages_handler.get_grouped()
        # Get framework version
        module = self.modules_handler.import_from_uri("start.py", False)
        version = "?"
        if module and hasattr(module, "VERSION"):
            version = module.VERSION
        return dict(modules=available_modules, version=version, serviceMessages=service_messages)

    @API.callable
    def get_modules_log(self, client):
        """
        Get all modules and listeners log
        """
        modules = self.modules_handler.get_full_log()
        return modules

    @API.callable
    def kill_process(self, client, module_name):
        """
        Kills running processes of module and listener if exists
        Args:
            module_name: (string) Name of module
        """
        if module_name not in self.modules_handler.running_modules:
            return
        self.modules_handler.kill_process(module_name)

    @API.callable
    def register_module_message(self, client, message, state, module_name, type='text', inline=False, replace=False):
        """
        Add log message from module
        Args:
            message: (string) Message from module
            state: (bool or None) State of module(success, fail or nothing)
            module_name: (string) Name og running module
            type: (string) text or image
            inline: (bool) Write on last line if True
            replace: (bool) Replace last line if True
        """
        module = self.modules_handler.add_message(module_name, message, state, inline, replace, type)
        message = {"command": "on_module_message",
                   "args": {
                       "module_name": module.module_name,
                       "message": module.log[-1].formatted(),
                       "state": state
                   }}
        # TODO REPORTS
        # if state is not None:
        #     self.generate_report(pid)
        self.send_message_to_ui(message)
        return dict(message="ok")

    @API.callable
    def get_module_options(self, client, module_name):
        """
        Send options of module to gui
        Args:
            module_name: real module name without '.py' extension
        Returns:
            (list) List of options from module's dict OPTIONS
        """
        if module_name in self.available_modules:
            opts = self.modules_handler.get_available_options_for_module(self.available_modules[module_name])
        opts = self.options_parser.prepare_options(opts)
        json_resp = []
        for key in opts:
            json_resp.append(dict(option=key, value=opts[key]))
        return json_resp

    @API.callable
    def get_module_args(self, client, module_name):
        """
        Get module options changed by GUI
        Args:
            module_name: (string) Name of running module
        Returns:
            (dict) Dict of options
        """
        resp = self.modules_handler.get_changed_options(module_name)
        return resp

    @API.callable
    def gui_command_to_listener(self, client, module_name, message):
        """
        Sends command from GUI to listener
        Args:
            module_name: (string) Name of running module
            message: (string) Message for listener from gui(os command)
        """
        self.modules_handler.add_listener_message(module_name, ">> " + message)
        args = dict(module_name=module_name, message=message)
        self.send_message_to_listener(module_name, args)

    @API.callable
    def on_listener_message(self, client, module_name, message, state):
        """
        Add message from listener to gui or get last command from gui to listener
        Args:
            module_name: (string) Name of running module
            message: (string) Message from listener
            state: (int)  0 - shell is not connected
                          1 - shell connected
                          2 - shell disconnected
        """
        self.modules_handler.add_listener_message(module_name, message, state)
        data = dict(command="on_listener_message", args=dict(module_name=module_name, state=state, message=message))
        self.send_message_to_ui(data)

    @API.callable
    def get_listener_options(self, client, module_name):
        """
        Get listener options by listener PID or module PID
        Args:
            module_name: (string) Name of running module
        """
        if not module_name:
            return self.make_error('PIDs are not specified')
        options = self.modules_handler.get_module_inst_by_name(module_name).listener_options
        return options

    @API.callable
    def add_listener_options(self, client, module_name, options):
        """
        Adds/Changes options of listener
        Args:
            module_name: (string) Name of running module
            options: (dict) listener options
        """
        module = self.modules_handler.get_module_inst_by_name(module_name)
        module.listener_options = options
        return {"re"}

    @API.callable
    def add_listener_pid(self, client, module_name, pid):
        """
        Adds listener PID to running module instance
        Args:
            module_name: (string) Name of running module
            pid: (int) Listener PID
        """
        self.modules_handler.add_listener_pid(module_name, pid)

    @API.callable
    def get_source(self, client, module_name):
        """
        Get source code of module
        Args:
            module_name: (string) real module name, without '.py' extension
        """
        with open(self.available_modules[module_name]) as f:
            lines = f.read().splitlines()
            source = "\n".join(lines)
        return dict(message=source, module_name=module_name)

    @API.callable
    def save_source(self, client, module_name, message):
        """
        Save edited source code of module
        Args:
            module_name: (string) real module name, without '.py' extension
            message: (string) Edited source code of module
        """
        host, port = client.socket.getsockname()
        if "localhost" not in host and "127.0.0.1" not in host:
            message = "Only localhost user can save sources"
            self.send_error(client, message)
            return
        code = message.encode('utf-8')
        with open(self.available_modules[module_name], 'wb') as f:
            f.write(code)
        self.send_info(client, 'Module %s successfully changed' % module_name)

    @API.callable
    def is_listener_connected(self, client, module_name):
        """
        Get info about state of listener
        Args:
            module_name: (string) Name of running module
        """
        state = None
        module = self.modules_handler.get_module_inst_by_name(module_name)
        if module:
            state = module.is_shell_connected
            if state == 0:
                state = False
            elif state == 1:
                state = True
        resp = dict(state=state)
        return resp

    @API.callable
    def create_module(self, client, module_name, module_options):
        """
        Create new module with a given name
        Args:
            module_name: (string) Name of the new module
        """
        if not module_name.lower().endswith('.py'):
            module_name = module_name + '.py'

        dotdotslash_payloads = ['../', '..\\', '..\\/']
        while True:
            replace_occured = False
            for payload in dotdotslash_payloads:
                if payload in module_name:
                    module_name = module_name.replace(payload, '')
                    replace_occured = True
            if not replace_occured:
                break

        if os.path.isfile('./exploits/'+ module_name):
            # if that name is already taken - abort, in order to not to replace the existing module
            self.send_error(client, 'That name is already taken')
            return

        print('{} {}'.format(module_name, module_options))

        try:
            with open('./exploits/'+ module_name, 'w') as create_f, open('./templates/clean.py', 'r') as read_f:
                create_f.write(read_f.read())
            self.send_info(client, 'Module created')
            self.available_modules = self.get_all_modules_paths()
        except Exception as ex:
            self.send_error(client, 'Failed to create new module\r\n{}'.format(ex))

    def make_error(self, error_msg):
        return dict(error=True, message=error_msg)

    def send_error(self, client, error_msg):
        client.send_message(dict(command='on_error', args=dict(message=error_msg)))

    def send_info(self, client, info_msg):
        client.send_message(dict(command='on_info', args=dict(message=info_msg)))

    def generate_report(self, module_name):
        module_inst = self.modules_handler.get_module_inst_by_name(module_name)
        info = self.modules_handler.get_module_info((self.available_modules[module_inst.original_name], module_name))
        module_vars = {
            "LOG": module_inst.log,
            "RESULT": module_inst.state,
            "OPTIONS": module_inst.options
        }
        listener_vars = {
            "IS_SHELL_CONNECTED": module_inst.is_shell_connected,
            "LISTENER_OPTIONS": module_inst.listener_options,
            "LISTENER_LOG": '\n'.join(module_inst.listener_messages)
        }
        module_vars.update(info)
        module_vars.update(listener_vars)
        module_vars["CVE"] = module_vars["CVE Name"]
        self.report_generator.append_module(module_vars)

    def send_message_to_ui(self, message):
        self.server.send_message_to_all_uis(message)

    def send_message_to_listener(self, module_name, message):
        self.server.send_message_to_listener(module_name, message)

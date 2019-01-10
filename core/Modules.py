import datetime
import sys
import os
import imp
import logging
import traceback
from modulefinder import ModuleFinder


class ModuleMessageElement:
    def __init__(self, message, type="text"):
        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message = message
        self.type = type

    def formatted(self):
        return {
            "time": self.time,
            "message": self.message,
            "type": self.type
        }


class RunningModule:
    def __init__(self, module_name, options, pid=None, listener_pid=None, listener_options=None):
        self.module_name = module_name
        self.original_name = ""
        self.pid = pid  # pid of running module
        self.options = options
        self.log = []  # Log messages
        self.state = None  # None - module is run, True - succeeded, False - failed
        self.listener_options = listener_options if listener_options else {}
        self.listener_pid = listener_pid
        self.is_shell_connected = 0
        self.listener_messages = []


class ModulesHandler:
    def __init__(self, commands_handler):
        self.commands_handler = commands_handler
        self.server = commands_handler.server
        self.running_modules = {}
        # Options of every module
        self.modules_options = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing modules handler")

    def add_module_pid(self, module_name, pid):
        module = self.running_modules.get(module_name)
        if module:
            self.server.add_process(pid)
            module.pid = pid

    def add_listener_pid(self, module_name, pid):
        module = self.running_modules.get(module_name)
        if module:
            self.server.add_process(pid)
            module.listener_pid = pid

    def add_message(self, module_name, new_message, state=None, inline=False, replace=False, type='text'):
        if module_name in self.running_modules:
            if inline:
                current_message = self.running_modules[module_name].log[-1].message
                self.running_modules[module_name].log[-1].message = current_message + new_message
            else:
                self.running_modules[module_name].log.append(ModuleMessageElement(new_message, type))
            if replace:
                self.running_modules[module_name].log[-1].message = new_message
            if state is not None:
                self.running_modules[module_name].state = state
            return self.running_modules[module_name]

    def add_listener_message(self, module_name, message, state=None):
        if module_name in self.running_modules:
            module = self.running_modules[module_name]
            module.listener_messages.append(message)
            if state:
                module.is_shell_connected = state
                if state == 2:
                    self.server.remove_process(module.listener_pid)

    def register_process(self, module_name, original_name, options):
        """	Register new running module as process
        @param module_name: Module name
        @param process: subprocess.Popen() instance
        """
        new_process = RunningModule(module_name, options)
        new_process.original_name = original_name
        self.running_modules[module_name] = new_process
        return new_process

    def kill_process(self, module_name):
        """	Kill process and remove it from list of running modules
        :param pid: PID of running process
        """
        if module_name not in self.running_modules:
            return
        module = self.running_modules[module_name]
        self.server.remove_process(module.pid)
        self.server.remove_process(module.listener_pid)
        del self.running_modules[module_name]

    def get_full_log(self):
        log = {}
        for module_name in self.running_modules:
            message_elements = self.running_modules[module_name].log
            temp_messages = []
            for element in message_elements:
                temp_messages.append(element.formatted())
            log[module_name] = dict(
                state=self.running_modules[module_name].state,
                message=temp_messages,
                listener=self.running_modules[module_name].listener_messages
            )
        return log

    def get_module_log(self, module_name):
        if module_name not in self.running_modules:
            return None
        module = self.running_modules[module_name]
        message_elements = module.log
        temp_messages = []
        for element in message_elements:
            temp_messages.append(element.formatted())
        log = dict(
                state=self.running_modules[module_name].state,
                message="\n".join(temp_messages),
                new_messages=self.running_modules[module_name].new_messages
        )
        self.running_modules[module_name].new_messages = False
        return log

    def import_from_uri(self, uri, absl=True):
        """Import module by given path
        :param uri: (string) Path to module
        :param absl: (bool) Is path absolute
        :return: python module instance
        """
        if not absl:
            uri = os.path.normpath(os.path.join(os.path.dirname(__file__), "../" + uri))
        path, fname = os.path.split(uri)
        mname, ext = os.path.splitext(fname)
        no_ext = os.path.join(path, mname)
        if os.path.exists(no_ext + '.py'):
            try:
                return imp.load_source(mname, no_ext + '.py')
            except ImportError as e:
                finder = ModuleFinder()
                finder.run_script(no_ext + '.py')
                bad_imports = map(lambda mod_tup: mod_tup[0],
                                  filter(lambda x: x[1].get('__main__'), finder.badmodules.items()))
                for mn in bad_imports:
                    self.commands_handler.service_messages_handler.add_message(e.message,
                                                                               module_with_unknown_import=mname,
                                                                               module_to_import=mn)
                print 'Error: module %s requires %s' % (mname, ', '.join(bad_imports))
            except:
                res = []
                exc_type, exc_value, exc_traceback = sys.exc_info()
                formatted_lines = traceback.format_exc().split('\n')
                res.append(formatted_lines[0])
                res.extend(formatted_lines[3:])
                msg = '\r\n'.join(res)
                print(msg)

    def get_modules_info(self, names):
        """Gets info about given modules
        :param names: (List of strings) Paths to modules
        :return: (Dict)Key=>Path to module, Value=>'INFO' dict of imported module
        """
        res = []
        for name in names:
            info = self.get_module_info(name)
            if info:
                res.append(info)
        res = make_tree(res)
        return res

    def get_module_info(self, name):
        module = self.import_from_uri(name[0])
        if hasattr(module, 'INFO'):
            if type(module.INFO.get('LINKS')) is not list:
                module.INFO['LINKS'] = [module.INFO.get('LINKS', '')]
            module.INFO["NAME"] = name[1]
            return module.INFO
        return None

    def get_changed_options(self, module_name):
        options = self.running_modules[module_name].options
        options['listener'] = self.running_modules[module_name].listener_options
        return options

    def get_available_options_for_module(self, module_name):
        module = self.import_from_uri(module_name)
        if hasattr(module, 'OPTIONS'):
            return module.OPTIONS
        else:
            return {}

    def get_module_inst_by_name(self, module_name):
        return self.running_modules.get(module_name)

    def make_unique_name(self, module_name, suffix=1):
        if module_name not in self.running_modules:
            return module_name
        name = "%s(%s)" % (module_name, suffix)
        if name in self.running_modules:
            suffix += 1
            return self.make_unique_name(module_name, suffix)
        else:
            return name

    def get_busy_ports_list(self):
        """Gets ports with status 2"""
        res = [int(module.listener_options.get("PORT"))
               for module_name, module
               in self.running_modules.iteritems()
               if module.is_shell_connected != 2 and module.listener_options.get("PORT")]
        return res


def get_modules_names_dict(path_to_files):
    """Get list of .py files names in directory"""
    files = os.listdir(path_to_files)
    res = {}
    for filename in files:
        if filename.endswith(".py"):
            res[filename[:-3]] = os.path.join(path_to_files, filename)
    return res


def _attach(branch, module, trunk):
    """
    Insert a branch of directories on its trunk.
    """
    parts = branch.split('/', 1)
    if len(parts) == 1:  # branch is a file
        module["isFile"] = True
        trunk.append(module)
    else:
        node, others = parts
        node = node.capitalize()
        node_obj = dict(NAME=node, DESCRIPTION=node, isFile=False)
        res, index = is_module_in_trunk(trunk, node)
        if res:
            _attach(others, module, trunk[index]["children"])
        else:
            node_obj["children"] = []
            trunk.append(node_obj)
            _attach(others, module, node_obj["children"])


def make_tree(modules):
    main_dict = []
    for module in modules:
        if "PATH" in module:
            _attach(module["PATH"]+module["NAME"], module, main_dict)
        else:
            _attach(module["NAME"], module, main_dict)
    return main_dict


def is_module_in_trunk(trunk, name):
    index = 0
    for index, module in enumerate(trunk):
        if module["NAME"] == name:
            return True, index
    return False, index

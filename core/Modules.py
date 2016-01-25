import datetime
import sys
import os
import imp
import logging
import traceback


class ModuleMessageElement:
    def __init__(self, message):
        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message = message


class RunningProcess:
    def __init__(self, module_name, process, options):
        """
        :param module_name:(string) Module name
        :param process:(subprocess.Popen) Running process
        """
        self.module_name = module_name
        self.original_name = ""
        self.process = process
        self.pid = process.pid
        self.options = options
        self.log = []
        self.state = None
        self.new_messages = False


class ModulesHandler:
    def __init__(self, server):
        self.server = server
        # For manage running processes
        self.processes = {}
        # Options of every module
        self.modules_options = {}
        self.logger = logging.getLogger()
        self.logger.info("Initializing modules handler")

    def add(self, pid, new_message, state=None, inline=False, replace=False):
        module_name = self.get_module_name_by_pid(pid)
        if module_name in self.processes:
            if inline:
                current_message = self.processes[module_name].log[-1].message
                self.processes[module_name].log[-1].message = current_message + new_message
            else:
                self.processes[module_name].log.append(ModuleMessageElement(new_message))
            if replace:
                self.processes[module_name].log[-1].message = new_message
            self.processes[module_name].new_messages = True
            if state is not None:
                self.processes[module_name].state = state

    def register_process(self, module_name, original_name, process, options):
        """	Register new running module as process
        @param module_name: Module name
        @param process: subprocess.Popen() instance
        """
        new_process = RunningProcess(module_name, process, options)
        new_process.original_name = original_name
        self.processes[module_name] = new_process
        self.logger.debug("Process with PID =%s and name '%s' was added" % (new_process.pid, new_process.module_name))

    def get_full_log(self):
        log = {}
        for module_name in self.processes.keys():
            message_elements = self.processes[module_name].log
            temp_messages = []
            for element in message_elements:
                temp_messages.append("%s: %s" % (element.time, element.message))
            log[module_name] = dict(
                state=self.processes[module_name].state,
                message="\n".join(temp_messages),
                new_messages=self.processes[module_name].new_messages
            )
            self.processes[module_name].new_messages = False
        return log

    def get_module_log(self, module_name):
        if module_name not in self.processes:
            return None
        module = self.processes[module_name]
        message_elements = module.log
        temp_messages = []
        for element in message_elements:
            temp_messages.append("%s: %s" % (element.time, element.message))
        log = dict(
                state=self.processes[module_name].state,
                message="\n".join(temp_messages),
                new_messages=self.processes[module_name].new_messages
        )
        self.processes[module_name].new_messages = False
        return log

    def kill_process(self, module_name, remove=False):
        """	Kill process and remove it from list of running modules
        :param pid: PID of running process
        """
        if module_name not in self.processes.keys():
            return
        self.server.remove_process(self.processes[module_name].process)
        self.processes[module_name].process.terminate()
        del self.processes[module_name]

    @staticmethod
    def import_from_uri(uri, absl=False):
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
            except:
                res = []
                exc_type, exc_value, exc_traceback = sys.exc_info()
                formatted_lines = traceback.format_exc().split('\n')
                res.append(formatted_lines[0])
                res.extend(formatted_lines[3:])
                msg = '\r\n'.join(res)
                print("\r\n")
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
            module.INFO["NAME"] = name[1]
            return module.INFO
        return None

    def get_module_options(self, pid):
        module_name = self.get_module_name_by_pid(pid)
        return self.processes[module_name].options

    def get_available_options_for_module(self, module_name):
        """Get options of given module
            :param module_name: (string) Relative path to module
            :return: (Dict)Key=> Option name, Value=>Option value
        """
        if module_name not in self.modules_options.keys():
            module = self.import_from_uri(module_name)
            if hasattr(module, 'OPTIONS'):
                return module.OPTIONS
            else:
                return {}

    def get_module_inst_by_name(self, module_name):
        if module_name in self.processes:
            return self.processes[module_name]

    def make_unique_name(self, module_name, suffix=1):
        if module_name not in self.processes.keys():
            return module_name
        name = "%s(%s)" % (module_name, suffix)
        if name in self.processes.keys():
            suffix += 1
            return self.make_unique_name(module_name, suffix)
        else:
            return name

    def get_module_name_by_pid(self, pid):
        for module_name in self.processes.keys():
            if self.processes[module_name].pid == pid:
                return module_name
        return None

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

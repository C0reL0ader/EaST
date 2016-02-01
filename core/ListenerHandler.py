import Queue
import json
import subprocess
import sys, os

class Listener:
    def __init__(self, module_name, process):
        self.module_name = module_name
        self.process = process
        self.options = {}
        self.isShellConnected = 0
        self.messages = []

    def addMessage(self, message):
        self.messages.append(message)

    def addOption(self, option, value):
        self.options[option] = value

    def getOptions(self):
        return self.options

    def setShellConnected(self, state=0):
        self.isShellConnected = state

    def getMessages(self):
        return self.messages

    def getMessagesFormatted(self):
        return "\n".join(self.messages)

class ListenerHandler:
    def __init__(self, server):
        self.listeners = {}
        self.server = server

    def addListener(self, module_name, process, options):
        if module_name not in self.listeners.keys():
            self.listeners[module_name] = Listener(module_name, process)
            self.setListenerOptions(module_name, options)

    def getListener(self, module_name):
        if module_name in self.listeners.keys():
            return self.listeners[module_name]
        return None

    def killListener(self, module_name):
        if module_name in self.listeners.keys():
            self.listeners[module_name].process.kill()
            del self.listeners[module_name]

    def addMessage(self, module_name, message):
        if module_name not in self.listeners.keys():
            return
        self.listeners[module_name].addMessage(message)

    def getModuleMessages(self, module_name):
        if module_name not in self.listeners.keys():
            return
        return self.listeners[module_name].getMessages()

    def getModuleMessagesFormatted(self, module_name):
        if module_name not in self.listeners.keys():
            return
        return self.listeners[module_name].getMessagesFormatted()

    def getModuleNameByPid(self, pid):
        for listener_name in self.listeners.keys():
            if self.listeners[listener_name].process.pid == pid:
                return listener_name
        return None

    def getPidByModuleName(self, module_name):
        if module_name in self.listeners:
            return self.listeners[module_name].process.pid
        return None

    def getListenersMessages(self):
        res = {}
        for listener_name, listener in self.listeners.iteritems():
            res[listener_name] = dict(
                message=listener.getMessagesFormatted(),
                connected=listener.isShellConnected
            )
        return res

    def setListenerOptions(self, module_name, options):
        for option in options:
            self.listeners[module_name].addOption(option, options[option])

    def getListenerOptions(self, pid):
        module_name = self.getModuleNameByPid(pid)
        if not module_name:
            return {}
        return self.listeners[module_name].getOptions()

    def getListenerOptionsByName(self, module_name):
        if module_name in self.listeners.keys():
            return self.listeners[module_name].getOptions()
        return {}

    def setShellConnected(self, pid, state):
        module_name = self.getModuleNameByPid(pid)
        if module_name:
            self.listeners[module_name].setShellConnected(state)

    def get_listener_inst_by_name(self, module_name):
        if module_name in self.listeners.keys():
            return self.listeners[module_name]

    def get_busy_ports_list(self):
        """Gets ports with status 2"""
        res = [int(listener.options["PORT"])
               for listener_name, listener
               in self.listeners.iteritems()
               if listener.isShellConnected != 2]
        return res


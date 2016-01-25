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
        self.messagesFromGui = Queue.Queue()
        self.messagesToGui = []
        self.new_message_from_listener = False

    def addMessageFromGui(self, message):
        self.messagesFromGui.put(message)

    def getMessageFromGui(self):
        if self.messagesFromGui.qsize() > 0:
            command = self.messagesFromGui.get()
            if command == "":
                return ""
            else:
                return command + '\n'
        return ""

    def addMessageToGui(self, message):
        self.new_message_from_listener = True
        self.messagesToGui.append(message)

    def getMessagesForGui(self):
        if len(self.messagesToGui)>0:
            return '\n'.join(self.messagesToGui)
        else:
            return ""

    def addOption(self, option, value):
        self.options[option] = value

    def getOptions(self):
        return self.options

    def setShellConnected(self, state=0):
        self.isShellConnected = state

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

    def addMessageFromGui(self, module_name, message):
        if module_name not in self.listeners.keys():
            return
        self.listeners[module_name].addMessageFromGui(message)

    def getMessageFromGui(self, pid):
        module_name = self.getModuleNameByPid(pid)
        if module_name:
            return self.listeners[module_name].getMessageFromGui()
        return ""

    def addMessageToGui(self, pid, message):
        if not message:
            return
        module_name = self.getModuleNameByPid(pid)
        if module_name:
            self.listeners[module_name].addMessageToGui(message)

    def getMessagesForGui(self, module_name):
        if module_name not in self.listeners.keys():
            return
        return self.listeners[module_name].getMessagesForGui()

    def getModuleNameByPid(self, pid):
        for listener_name in self.listeners.keys():
            if self.listeners[listener_name].process.pid == pid:
                return listener_name
        return None

    def getListenersMessages(self):
        res = {}
        for listener_name in self.listeners.keys():
            res[listener_name] = dict(
                message=self.listeners[listener_name].getMessagesForGui(),
                connected=self.listeners[listener_name].isShellConnected,
                new_messages=self.listeners[listener_name].new_message_from_listener
            )
            self.listeners[listener_name].new_message_from_listener = False
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


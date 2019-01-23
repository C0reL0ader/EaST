# coding=utf-8

class CreateModuleHandler:
    def __init__(self):

        self.template = self.load_template()
        self.options = {}

    def load_template(self):
        with open('./templates/clean.py', 'r') as f:
            return f.read()

    def create_module(self, module_name, module_options):
        options = ''
        for k,v in module_options:
            options += 'OPTIONS["{}"]={}'

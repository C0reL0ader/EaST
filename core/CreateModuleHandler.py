# coding=utf-8

DEFAULT_OPTIONS = """OPTIONS["OPTION1"] = "VALUE1", dict(description="Option description") # Will create text field in GUI and returns "str" value type
OPTIONS["OPTION2"] = 10, dict(description="Option description") # Will create text field and returns "int" value type
OPTIONS["OPTION3"] = False, dict(description="Option description") # Will create checkbox and returns "bool" value type
OPTIONS["OPTION4"] = dict(options=["value1", "value2"], selected="value1"), dict(description="Option description") # Will create combobox and you'll can choose value(in this case "value1" or "value2"). Field "selected" makes value default
"""
DEFAULT_GETARGS = """        self.option1 = self.args.get("OPTION1")
        self.option2 = self.args.get("OPTION2")
        self.option3 = self.args.get("OPTION3")
        self.option4 = self.args.get("OPTION4")"""

class CreateModuleHandler:
    def __init__(self):

        self.template = self.load_template()

    def load_template(self):
        with open('./templates/clean.py', 'r') as f:
            return f.read()

    def create_module(self, module_name, module_options):
        module_name = self.sanitize(module_name)
        options = ''
        fields = ''
        getargs = ''
        padding = ' ' * 8
        print(repr(module_options))
        for option in module_options:
            if option['type'] == 'string':
                options += 'OPTIONS["{}"] = "{}", dict(description=\'{}\')\n'.format(option['name'], option['value'], option['desc'])
                fields += '{}self.{} = \'{}\'\n'.format(padding, option['name'].lower(), option['value'])
                getargs += '{0}self.{1} = self.args.get("{2}", self.{1})\n'.format(padding, option['name'].lower(), option['name'])

            elif option['type'] == 'int' or option['type'] == 'boolean':
                options += 'OPTIONS["{}"] = {}, dict(description=\'{}\')\n'.format(option['name'], option['value'], option['desc'])
                fields += '{}self.{} = {}\n'.format(padding, option['name'].lower(), option['value'])
                getargs += '{0}self.{1} = self.args.get("{2}", self.{1})\n'.format(padding, option['name'].lower(), option['name'])

            elif option['type'] == 'select':
                pass
            else:
                continue
        print('done generating')
        try:
            if len(module_options) > 0:
                module = self.template.format(MODULE_OPTIONS=options, MODULE_FIELDS=fields, MODULE_GETARGS=getargs)
            else:
                module = self.template.format(MODULE_OPTIONS=DEFAULT_OPTIONS, MODULE_FIELDS='', MODULE_GETARGS=DEFAULT_GETARGS)
            print('beginning write')
            with open('./exploits/{}'.format(module_name), 'w') as f:
                f.write(module)
                print('write ok')
            return True
        except:
            import traceback
            traceback.print_exc()
            return False

    def sanitize(self, module_name):
        dotdotslash_payloads = ['../', '..\\', '..\\/']
        while True:
            replace_occured = False
            for payload in dotdotslash_payloads:
                if payload in module_name:
                    module_name = module_name.replace(payload, '')
                    replace_occured = True
            if not replace_occured:
                break
        return module_name
            




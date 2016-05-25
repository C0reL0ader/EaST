from collections import OrderedDict

class OptionsParser:
    def __init__(self):
        pass

    def parse_data(self, data):
        res = {}
        for entry in data:
            if entry['value']['type'] == 'int':
                if 'value' in entry['value'] and entry['value']['value']:
                    res[entry['option']] = int(entry['value']['value'])
            elif entry['value']['type'] == 'list':
                res[entry['option']] = entry['value']['selected']
            elif entry['value']['type'] == 'bool':
                res[entry['option']] = entry['value']['value']
            else:
                if 'value' in entry['value'] and entry['value']['value']:
                    res[entry['option']] = entry['value']['value']
        return res

    def prepare_options(self, options):
        res = OrderedDict()
        for option in options.keys():
            value = options[option]
            ext_options = {}
            # check for extended options
            if type(value) is tuple:
                if len(value) > 1 and type(value[1] is dict):
                    ext_options = value[1]
                value = value[0]
            if type(value) is int:
                res[option] = dict(type="int", value=value)
            elif type(value) is bool:
                res[option] = dict(type="bool", value=value)
            elif type(value) is dict:
                res[option] = value
                res[option]["type"] = "list"
            else:
                res[option] = dict(type="string", value=value)
            res[option].update(ext_options)
        return res

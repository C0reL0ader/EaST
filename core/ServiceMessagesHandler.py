from itertools import groupby

class ServiceMessageLevel:
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class ServiceMessageType:
    IMPORT = 1
    UPDATES = 2


class ServiceMessage:
    def __init__(self, message, message_type, level, **kwargs):
        self.message = message
        self.message_type = message_type
        self.level = level
        self.module_to_import = kwargs.get('module_to_import')
        self.module_with_unknown_import = kwargs.get('module_with_unknown_import')

    def serialize(self):
        return self.__dict__


class ServiceMessagesHandler:
    def __init__(self):
        self.messages = []

    def reset(self):
        self.messages = []

    def remove_import_error(self, library_name):
        self.messages = filter(lambda x: x.module_to_import != library_name, self.messages)

    def get_grouped(self):
        from collections import defaultdict
        messages = []
        messages_by_import = defaultdict(list)
        for message in self.messages:
            if message.message_type == ServiceMessageType.IMPORT:
                messages_by_import[message.module_to_import].append((message.module_with_unknown_import))
            else:
                messages.append(message.serialize())
        map_fn = lambda x: dict(message='Modules %s require python module %s' % (', '.join(x[1]), x[0]),
                                message_type=ServiceMessageType.IMPORT,
                                module_to_import=x[0],
                                level=ServiceMessageLevel.ERROR,
                                installed=False
                                )
        messages_by_import = map(map_fn, messages_by_import.items())
        return messages + messages_by_import

    def serialize(self):
        return [message.serialize() for message in self.messages]

    def add_message(self, message, message_type=ServiceMessageType.IMPORT, level=ServiceMessageLevel.ERROR, **kwargs):
        msg = ServiceMessage(message, message_type, level, **kwargs)
        if msg.serialize() in self.serialize():
            return
        self.messages.append(ServiceMessage(message, message_type, level, **kwargs))

    def get_messages(self, message_type=None, level=None):
        msgs = filter(lambda item: (item.message_type == message_type if message_type else True)
                                   and (item.level == level if level else True), self.messages)
        return [msg.serialize() for msg in msgs]

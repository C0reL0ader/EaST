class Shellcode:
    def __init__(self, os_target='', os_target_arch='', connectback_ip='localhost', connectback_port=5555, badchars=['\x00']):
        self.OS_TARGET = os_target
        self.OS_TARGET_ARCH = os_target_arch
        self.CONNECTBACK_IP = connectback_ip
        self.CONNECTBACK_PORT = connectback_port
        self.BADCHARS = badchars
        return

    def get_shellcode(self):
        return ''

    def make_inline(self, payload):
        payload = payload.replace('\t',' ')
        payload = payload.replace('\r',' ')
        payload = payload.replace('\n',' ')
        return payload

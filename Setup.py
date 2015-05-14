#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''Install script for hip-tools programm suite'''

import os
import sys
import subprocess
import zipfile

import write_utf

Writer = write_utf.write_gen()

   
# get user login
log = os.getlogin()
    
def fix_path(f_path):
    '''fix path in executables. Currentrly not used'''

    data = []
    
    fb = open(f_path)
    lines = fb.readlines()
    fb.close()

    for line in lines:
        line = line.decode('utf8')
        if 'listbooks(\'hiplib\')' in line:
            line = line.replace("\'hiplib\'", "\"/usr/local/lib/hip-tools/hiplib\"")

        elif 'hiplib' in line:
            line = line.replace("os.getcwd(), \"hiplib\"", "\"/usr/local/lib/hip-tools/hiplib\"")

        data.append(line)
    Writer.write_file(f_path + '.tmp', data)

def write_main(main_path):
    path = main_path
    
    files_list = ['booklst.py', 'get_par.py', 'hipcomment.py', 'hip_config.py', 'hipconv.py', 'hipindex', 'hipsearch', 'numb_conv.py', 'russ_simp.py', 'slovenize.py', 'textview.py', 'ucs8conv.py', 'write_utf.py']

    # write main programm files
    for f_name in files_list:
        subprocess.call(['cp', '-p', f_name, os.path.join(path, f_name)])

    subprocess.call(['chmod', '744', os.path.join(path, 'hipindex')])
    subprocess.call(['chmod', '744', os.path.join(path, 'hipsearch')])
#    subprocess.call(['chmod', '744', os.path.join(path, 'textview.py')])

def write_lib(lib_inst_path, local_path):
    # write hip library

    lib_inst_path = os.path.join(lib_inst_path, "hip_tools")

    if os.path.exists(lib_inst_path):
        b = raw_input('Do you wish to rewrite your old %s library? (yes/no) ' % local_path[0])
        if b == 'yes':
#            subprocess.call(['cp', '-r', '-v', '-p', local_path[1], lib_inst_path])
            print local_path[0]


#    else:
#        subprocess.call(['mkdir', lib_inst_path])
#            subprocess.call(['cp', '-r', '-v', '-p', local_path[1], lib_inst_path])

#
## write config files
#
#files_dic = {'hipsearch.config': '.hipsearch.config', 'hipindex.config': '.hipindex.config'}
#
#path = os.path.join('/home', log)
#
#[subprocess.call(['cp', '-R', '-p', f_name, os.path.join(path, files_dic[f_name])]) for f_name in files_dic]

if __name__ == '__main__':

    from optparse import OptionParser
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-m", "--mainpath", dest="mainpath", action="store", help="Path to write main files to")
    parser.add_option("-l", "--libpath", dest="libpath", action="store", help="Path to write libraries to")
    
    (options, args) = parser.parse_args()
    
    # by default use '/usr/local/bin' and '/usr/local/lib' as install paths
    if options.mainpath:
        main_path = options.mainpath
    else:
        main_path = '/usr/local/bin'
        
    if options.libpath:
        lib_inst_path = options.libpath
    else:
        lib_inst_path = '/usr/local/lib'

    print main_path, lib_inst_path
#    sys.exit(0)

    # path to hiplib and greeklib cloned directories
    # They are supposed to be next to current dir, not in it:
    hippath = ['hiplib', os.path.abspath('../hiplib')]
    grpath = ['greeklib', os.path.abspath('../greeklib')]
    

    write_main(main_path)

    for i in [hippath, grpath]:
        if os.path.exists(i[1]):
            write_lib(lib_inst_path, i)
        else:
            print "Didn\'t find", i[0], "library. If you wish to install it, download from git@github.com:hiptools"
 

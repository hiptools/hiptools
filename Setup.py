#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''Install script for hip-tools programm suite'''

import os
import sys
import subprocess
#import zipfile
import ConfigParser


import write_utf

Writer = write_utf.write_gen()
config = ConfigParser.ConfigParser()
   
# get user login
usr = os.getlogin()
log = os.path.expanduser(''.join(['~', usr]))
print 'log', log
    
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
    
    files_list = ['booklst.py', 'get_par.py', 'hipcomment.py', 'hipconv.py', 'hipindex', 'hipsearch', 'numb_conv.py', 'russ_simp.py', 'slovenize.py', 'textview.py', 'write_utf.py']

    # write main programm files
    for f_name in files_list:
        subprocess.call(['cp', '-p', '-v', f_name, os.path.join(path, f_name)])

    subprocess.call(['chmod', '744', os.path.join(path, 'hipindex')])
    subprocess.call(['chmod', '744', os.path.join(path, 'hipsearch')])
#    subprocess.call(['chmod', '744', os.path.join(path, 'textview.py')])

def write_lib(lib_inst_path, grpath, hippath):
    # write hip libraries

    # check common hiplib directory
    if not os.path.exists(lib_inst_path):
        subprocess.call(['mkdir', lib_inst_path])

    for i in [grpath, hippath]:
        # check local paths for libs
        if not os.path.exists(i[1]):
            print "Didn\'t find", i[0], "library. If you wish to install it, download from git@github.com:hiptools"
            return None
        # check install paths for libs, ask to rewrite if exists
        if os.path.exists(os.path.join(lib_inst_path, i[0])):
            b = raw_input('Do you wish to rewrite your old %s library? (yes/no) ' % i[0])
            if b == 'yes':
                subprocess.call(['cp', '-r', '-v', '-p', local_path[1], lib_inst_path])

        else:
            subprocess.call(['cp', '-r', '-v', '-p', i[1], lib_inst_path])


def create_conf(path, lib_inst_path):
    # write config files

    if not os.path.exists(path):
        subprocess.call(['mkdir', path])

    full_path = os.path.join(path, 'hiptools')
    if not os.path.exists(full_path):
        subprocess.call(['mkdir', full_path])

    config.add_section('LibraryPaths')
    config.add_section('SearchOptions')
    config.add_section('Fonts')
    config.add_section('Style')

    config.set('LibraryPaths', 'gr_path', os.path.join(lib_inst_path, "greeklib"))
    config.set('LibraryPaths', 'sl_path', os.path.join(lib_inst_path, "hiplib"))
    config.set('SearchOptions', 'default_search_group', 'Богослужебные')
    config.set('SearchOptions', 'default_search_group_gr', 'Minologion_base')
    config.set('SearchOptions', 'diacritics_off', 'True')
    config.set('SearchOptions', 'betacode', 'True')
    config.set('Fonts', 'gr_font', 'Old Standard TT 18')
    config.set('Fonts', 'sl_font', 'Orthodox.tt Ucs8 22')
    config.set('Style', 'default_style', 'slavonic')
    config.set('Style', 'brackets_off', 'True')

    with open(os.path.join(full_path, 'hiptoolsrc'), 'wb') as configfile:
        config.write(configfile)

    subprocess.call(['cp', '-v', 'parallel', full_path])
    subprocess.call(['cp', '-v', 'titlo_filter', full_path])

    owner = ''.join([usr, ":", usr])

    subprocess.call(['chown', '-R',  owner, full_path])

#files_dic = {'hipsearch.config': '.hipsearch.config', 'hipindex.config': '.hipindex.config'}
#    files_ls = ['.hiptools.config', 'parallel']
#
#    path = os.path.join(os.path.expanduser('~'), '.config', 'hiptools')
#
#    if not os.path.exists(path):
#        subprocess.call(['mkdir', path])
#
#    for f_name in files_ls:
#        subprocess.call(['cp', '-R', 'v', '-p', f_name, os.path.join(path, f_name)])

if __name__ == '__main__':

    from optparse import OptionParser
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-m", "--mainpath", dest="mainpath", action="store", help="Path to write main files to")
    parser.add_option("-l", "--libpath", dest="libpath", action="store", help="Path to write libraries to")
    
    (options, args) = parser.parse_args()
    
    # by default use '/usr/local/bin' and '/usr/local/lib' as install paths
    # TODO: fix path in programm files
    if options.mainpath:
        main_path = options.mainpath
    else:
        main_path = '/usr/local/bin'
        
    if options.libpath:
        lib_inst_path = options.libpath
    else:
        lib_inst_path = '/usr/local/lib/hiptools'

    print main_path, lib_inst_path
#    sys.exit(0)

    # path to hiplib and greeklib cloned directories
    # They are supposed to be next to current dir, not in it:
    grpath = ['greeklib', os.path.abspath('../greeklib')]
    hippath = ['hiplib', os.path.abspath('../hiplib')]
    

    write_main(main_path)

    write_lib(lib_inst_path, grpath, hippath)

    path = os.path.join(log, '.config')
    create_conf(path, lib_inst_path) 
    os.getuid()

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
    [subprocess.call(['cp', '-p', f_name, os.path.join(path, f_name) for f_name in files_list]

    subprocess.call(['chmod', '744', os.path.join(path, 'hipindex')])
    subprocess.call(['chmod', '744', os.path.join(path, 'hipsearch')])

# write hip library

#path = '/usr/local/lib/hip_tools'
#
#if not os.path.exists('/usr/local/lib/hip_tools'):
#    print 'no lib dir'
#    subprocess.call(['mkdir', '/usr/local/lib/hip-tools'])
#
#subprocess.call(['cp', '-R', '-p', 'hiplib', path])
#
## write config files
#
#files_dic = {'hipsearch.config': '.hipsearch.config', 'hipindex.config': '.hipindex.config'}
#
#path = os.path.join('/home', log)
#
#[subprocess.call(['cp', '-R', '-p', f_name, os.path.join(path, files_dic[f_name])]) for f_name in files_dic]

if __name__ == '__main__':

#    from optparse import OptionParser
#    usage = "usage: %prog [options] dir"
#    parser = OptionParser(usage=usage)
#
#    parser.add_option("-g", "--greek", dest="greek", action="store_true", help="Switch to greek")
#    parser.add_option("-s", "--slav", dest="slav", action="store_true", help="Switch to slavonic")
#    
#    (options, args) = parser.parse_args()

    # path to hiplib and greeklib cloned directories
    hippath = ['hiplib', os.path.abspath('../hiplib')]
    grpath = ['greeklib', os.path.abspath('../greeklib')]

    write_main('/usr/local/bin')

#    for i in [hippath, grpath]:
#        if os.path.exists(i[1]):
#            write_lib(hippath)
#        else:
#            print "Didn\'t find", i[0], "library. If you wish to install it, download from git@github.com:hiptools"
 

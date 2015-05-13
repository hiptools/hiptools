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
    
#def fix_path(f_path):
#    '''fix path in executables'''
#
#    data = []
#    
#    fb = open(f_path)
#    lines = fb.readlines()
#    fb.close()
#
#    for line in lines:
#        line = line.decode('utf8')
#        if 'listbooks(\'hiplib\')' in line:
#            line = line.replace("\'hiplib\'", "\"/usr/local/lib/hip-tools/hiplib\"")
#
#        elif 'hiplib' in line:
#            line = line.replace("os.getcwd(), \"hiplib\"", "\"/usr/local/lib/hip-tools/hiplib\"")
#
#        data.append(line)
#    Writer.write_file(f_path + '.tmp', data)
#
###Main###
#
## fix pathes inside main programms
#[fix_path(f_path) for f_path in ['hipindex', 'hipsearch']]

# write main programm files

files_dic = {'booklst.py': 'booklst.py', 'get_par.py': 'get_par.py', 'hipcomment.py': 'hipcomment.py', 'hip_config.py': 'hip_config.py', 'hipconv.py': 'hipconv.py', 'hipindex': 'hipindex', 'hipsearch': 'hipsearch', 'numb_conv.py': 'numb_conv.py', 'parallel': 'parallel', 'readme.txt': 'readme.txt', 'russ_simp.py': 'russ_simp.py', 'slovenize.py': 'slovenize.py', 'textview.py': 'textview.py', 'ucs8conv.py': 'ucs8conv.py', 'write_utf.py': 'write_utf.py'}


files_dic = {'booklst.py': 'booklst.py', 'hipcomment.py': 'hipcomment.py', 'hip_config.py': 'hip_config.py', 'hipconv.py': 'hipconv.py', 'hipindex': 'hipindex', 'hipsearch': 'hipsearch', 'numb_conv.py': 'numb_conv.py', 'parallel': 'parallel', 'hipview.py': 'hipview.py', 'write_utf.py': 'write_utf.py', 'get_par.py': 'get_par.py'}
path = '/usr/local/bin'

[subprocess.call(['cp', '-p', f_name, os.path.join(path, files_dic[f_name])]) for f_name in files_dic]

subprocess.call(['chmod', '744', os.path.join(path, 'hipindex')])
subprocess.call(['chmod', '744', os.path.join(path, 'hipsearch')])

# write hip library

path = '/usr/local/lib/hip-tools'

if not os.path.exists('/usr/local/lib/hip-tools'):
    print 'no lib dir'
    subprocess.call(['mkdir', '/usr/local/lib/hip-tools'])

subprocess.call(['cp', '-R', '-p', 'hiplib', path])

# write config files

files_dic = {'hipsearch.config': '.hipsearch.config', 'hipindex.config': '.hipindex.config'}

path = os.path.join('/home', log)

[subprocess.call(['cp', '-R', '-p', f_name, os.path.join(path, files_dic[f_name])]) for f_name in files_dic]

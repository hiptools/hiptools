#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import codecs 
import re
import sys
import os
import xml.etree.ElementTree as ET
import subprocess

import ConfigParser

class Findaname():
    def __init__(self):
        pass

    def searcher(self, find_n):
        s_path = os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'saints.xml')
        tree = ET.parse(s_path)
        root = tree.getroot()
        res = []

        for mn in root.iter('month'):
            for d in mn.iter('day'):
                for fs in d.iter('feast'):
                    if find_n in fs.get('name'):
                        res_path = os.path.join(lib_path, 'min',  d.get('filename').encode('utf8'))
                        res.append([res_path, d.get('date').encode('utf8'), fs.get('name').encode('utf8')])
                         
        # [filename, date, text]
        return res

if __name__ == '__main__':

    al = Findaname()

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc'))

    lib_path = config.get('LibraryPaths', 'sl_path')

    from optparse import OptionParser
    usage = "usage: %prog [options] dir"
    parser = OptionParser(usage=usage)

#    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Create new base")

    (options, args) = parser.parse_args()

    chuck = re.compile(u'\d\d?', re.U)

    def output(res):
        # recursive func, outputs results, checks input, starts a popup
        for i in range(len(res)):
            print i, res[i][1], res[i][2]
        nm = raw_input('pick number or [q]uit! ')
        if nm == 'q':
            sys.exit(1)
        elif not chuck.match(nm):
            print 'Use q to quit, numbers to open file'
            # here's the recursion
            output(res)
        else:
            f_name = ''.join(res[int(nm)])
            print 'opening file: ', res[int(nm)][0]
            subprocess.Popen(['textview.py', res[int(nm)][0]])

    if args:
        res = al.searcher(args[0].decode('utf8'))
        output(res)

    else:
        print 'No args. What\'s to search? Exiting'
        sys.exit(1)


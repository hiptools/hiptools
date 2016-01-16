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
        tree = ET.parse('saints.xml')
        root = tree.getroot()
        res = []

        for mn in root.iter('month'):
            for d in mn.iter('day'):
                for fs in d.iter('feast'):
                    if find_n in fs.get('name'):
                        res_path = os.path.join(lib_path, 'min',  d.get('filename').encode('utf8'))
                        res.append([res_path, d.get('date').encode('utf8'), fs.get('name').encode('utf8')])
                         
#                        print d.get('date').encode('utf8'), fs.get('name').encode('utf8')

#            print bk.tag, bk.attrib
#            print fs.get('name')
#                pr = xml.findall('.//child[@id="123"]...')


#                for p in bk.iter('start'):
#                    if p.get('num') == zach:
#                        chap = p.get('chap')
#                        ver = p.get('ver')
#                        res.append((chap, ver))

        # [date, text]
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

    if args:
        res = al.searcher(args[0].decode('utf8'))
        if res:
            for i in range(len(res)):
                print i, res[i][1], res[i][2]
        else:
            print 'no such thing, sorry'
            sys.exit(1)
    else:
        print 'No args. What\'s to search? Exiting'
        sys.exit(1)

    nm = raw_input('pick number or [q]uit! ')
    # if 'q' choosen programm quits
    if nm == 'q':
        sys.exit(1)
    
    f_name = ''.join(res[int(nm)])
    print 'opening file: ', res[int(nm)][0]
    subprocess.Popen(['textview.py', res[int(nm)][0]])

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''Translate old 'zachalo' rubrication into
chapter-verse system'''
# so far we only get zachalo's beginning coordinates

#import codecs 
import sys
import os
import xml.etree.ElementTree as ET

class Zachalo():
    def __init__(self):
        pass


    def f_search(self, book, zach):
        z_path = os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'zach.xml')
        tree = ET.parse(z_path)
        root = tree.getroot()
        res = []

        for bk in root.iter('book'):
#            print bk.tag, bk.attrib
            if bk.get('name') == book:
                for p in bk.iter('start'):
                    if p.get('num') == zach:
                        chap = p.get('chap')
                        ver = p.get('ver')
                        res.append((chap, ver))

        return res

if __name__ == '__main__':

    za = Zachalo()
#    za.opener()

    from optparse import OptionParser
    usage = "usage: %prog Mf 35"
    parser = OptionParser(usage=usage)

#    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Create new base")

    (options, args) = parser.parse_args()
    if args:
        if args[0].startswith('Мф') or args[0].startswith('Mf'):
            book = "Matthew"
        if args[0].startswith('Мк') or args[0].startswith('Mk'):
            book = "Mark"
        if args[0].startswith('Лк') or args[0].startswith('Lk'):
            book = "Luke"
        if args[0].startswith('Ин') or args[0].startswith('Jn'):
            book = "John"
    if len(args) < 2:
        print 'not enough args, exiting'
        sys.exit(1)
    else:
        res = za.f_search(book, args[1])
        if res:
#            print args[1], "зачало =", book, "(", res[0], ":", res[1], ")"

            for tr in res:
                print args[1], "зачало =", book, "(", tr[0], ":", tr[1], ")"
#                print args[1], "зачало =", book, "(", tr[0], ":", tr[1], ")"
        else:
            print 'Увы, такого зачала не нашлось'

 

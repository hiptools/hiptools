#! /usr/bin/python2
# -*- coding: utf-8 -*-
'''Convert ucs8 text into plain text (with or without diacritics)'''

import sys
import codecs

import hipconv
import russ_simp

conv = hipconv.Repl()
russ = russ_simp.Mn(True, True, True)

def convert_ucs(f_name):

    # Внимательно с кодировкой !!!
    fp = codecs.open(f_name, "rb", "utf8")
#    line = fp.readline()
    lines = fp.readlines()
    fp.close()

    res = []
    for line in lines:
        line = line.strip()
        line = conv(line, 'b_csl')   #.encode('utf8')
        res.append(line)
    return res

if __name__ == '__main__':

    argv = sys.argv
    if len(argv) > 1:
        f_name = argv[1]

    res = convert_ucs(f_name)
    for i in res:
        i = russ.conv_str(i)
#        i = i.encode('utf8')
        print i

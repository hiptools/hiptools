#! /usr/bin/python2
# -*- coding: utf-8 -*-

import codecs
import re
import os
import sys
import chardet

import numb_conv

n_conv = numb_conv.NumParser()

class Mn:
    def __init__(self, stress=None, color=None, junk=None):

        self.stress_sw = stress

        self.color_sw = color

        self.junk_sw = junk

#        if self.color_sw:
#            print 'color'

        self.rg_er = re.compile(r"(.*)ъ(|\.|,|;|:|\?|!)?$", re.U)

        self.diacr = [["`", "\'"],
                    ["^", "\'"]]

        self.color = ["%<", "%>"]

        self.junk = ["{", "}", "@", "!"]

        self.lett = [["jа", "я"],
                    ["JА", "Я"],
                    ["_я", "я"],
                    ["_Я", "Я"],
                    ["jь", "е"],
                    ["Jь", "Е"],
                    ["_е", "е"],
                    ["_Е", "Е"],
                    ["_о", "о"],
                    ["_О", "О"],
                    ["_w", "о"],
                    ["_W", "О"],
                    ["w", "о"],
                    ["W", "О"],
                    ["о_у", "у"],
                    ["О_у", "У"],
                    ["о<у>", "у"],
                    ["О<у>", "У"],
                    ["s", "з"],
                    ["S", "З"],
                    ["i", "и"],
                    ["I", "И"],
                    ["v\"", "и"],
                    ["V\"", "И"],
                    ["v\'", "и\'"],
                    ["V\'", "И\'"],
                    ["v=", "и"],
                    ["V=", "И"],
                    ["v", "в"],
                    ["V", "В"],
                    ["f", "ф"],
                    ["F", "Ф"],
                    ["_кс", "кс"],
                    ["_Кс", "Кс"],
                    ["_пс", "пс"],
                    ["_Пс", "Пс"],
                    ["\\", ""],
                    ["=", ""]]


        # fill up the titlo-filter list from file
        fil_name = '/usr/local/bin/titlo_filter'
#        fil_name = 'titlo_filter_sm'

        try:
            fp = codecs.open(fil_name, "rb", "utf8")
            text_l = fp.readlines()
            fp.close()

            self.filter = []
            
            for line in text_l:
                line = line.encode('utf8').strip()

                a, b = line.split(' ')
#                print a, b

                a = re.compile(a, re.U)

                self.filter.append((a, b))
#                print self.filter

        except IOError:
            print 'no such file found:', fil_name

#        sys.exit(1)

    def opener(self, f_name):
        try:
            fp = open(f_name)
            text_l = fp.readlines()
            fp.close()

            slice = ''.join(text_l[:3])
            enc = chardet.detect(slice)['encoding']

            if not enc:
                enc = 'utf8'

            for line in text_l:
                line = line.decode(enc)
                out = self.conv_str(line)

                print out
     
        except IOError:
            print 'no such file found:', f_name


           
    def conv_str(self, line):
        # that's more useful for debugging

        line = line.strip().split(' ')
        line_l = []

#        print line

        for wrd in line:
            wrd = wrd.strip()
            wrd = wrd.encode('utf8')
            wrd = self.conv_ru(wrd)
            line_l.append(wrd)

        res = ' '.join(line_l)

        return res


    def conv_ru(self, wrd):
        '''russify the word'''

        # open up titlo
        if '~' in wrd or '\\' in wrd:
            for key, val in self.filter:
#                if key in wrd:
                if key.search(wrd):
#                    wrd = wrd.replace(key, val)
                    wrd = key.sub(val, wrd)
                    break
        # numbers
        if '~' in wrd:
            wrd = wrd.decode('utf8')
            res = n_conv.slav2rus(wrd)

            if res[0]:
                wrd = str(res[0]) + res[1]

            wrd = wrd.encode('utf8')

#            print 'word:', wrd

# DEBUG titlo_filter and numb_conv!!! ^^^

        # convert slavic letters
        for a, b in self.lett:
            wrd = wrd.replace(a, b)

        for a, b in self.diacr:
            wrd = wrd.replace(a, b)

        if self.stress_sw:
#            print 'stress'
            wrd = wrd.replace("\'", "")
#                print i
#                print wrd

        if self.color_sw:
            for y in self.color:
                wrd = wrd.replace(y, "")
#                print y
#                print wrd

        if self.junk_sw:
            for j in self.junk:
                wrd = wrd.replace(j, "")

        if "ъ" in wrd:
            wrd = self.rg_er.sub("\\1\\2", wrd)


        return wrd

###################main###########################

if __name__ == '__main__':

    from optparse import OptionParser
    usage = "usage: russ_simp.py [options] file"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", dest="debug", action='store_true', default=False, help="Work in the debuging mode")
    parser.add_option("-s", "--stress", dest="stress", action='store_true', default=False, help="Remove stress from text")
    parser.add_option("-c", "--color", dest="color", action='store_true', default=False, help="Remove color tags from text")
    parser.add_option("-j", "--junk", dest="junk", action='store_true', default=False, help="Remove service symbols from text")
    (options, args) = parser.parse_args()

    rep = Mn(options.stress, options.color, options.junk)

    if args:
        f_path = args[0]
        rep.opener(f_path)

    elif options.debug:
#        rep.conv_str(u'пр\сн')
        rep.conv_str(u'<%п>%е\'снь')

    else:
        print "No file name given, exiting"
        sys.exit(1)

#TODO: titlo_filter_sm use it when small filter needed.
# fix titilo_filter so, that it would output captial letters in words like Христос
# make option for including|excluding comments in hip
# fix parser from russify to work with tags like %< @{ etc. Otherwise "%<Гласъ а~%> doesn't work

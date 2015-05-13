#! /usr/bin/python
# -*- coding: utf-8 -*-

#import pygtk
#pygtk.require('2.0')
#import gtk
import codecs
import re
import os
import sys

# formerly - ucs8conv, renamed
#import hipconv
#import hip_config
#from hipview import Text

#conv = hipconv.Repl()

class Mn:
    def __init__(self):
        self.rg_stress = re.compile("\'(\.|,|;|:|\?|!)?$", re.U)
        self.rg_i = re.compile(r'(.*?)(и\'?)(а|е|и|о|у|ю|я|й)(.*?)', re.U)

        # don't change r"", or unicode attributes
        self.rg_er = re.compile(r"(.*)(б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ)(|\.|,|;|:|\?|!)?$", re.U)

#        self.rg_noer = re.compile(u'.*[^\\\](б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ)(\.|,|;|:|\?|!)?$', re.U)
        
#        self.rg_prid = re.compile(r'^(А|_Е|И|I|_О|О|_W|W|У|Jь|Ю|_Я|Я|i|jь|jа|_е|_о|_w|v\'|v\"|w|а|е|и|о|у|ы|ю|я)(.*)', re.U)
        # don't change r"", or unicode attributes
        self.rg_prid = re.compile(r"^(А|Е|И|О|У|Ы|Ю|Я|а|е|и|о|у|ы|ю|я)(.*)", re.U)
        
        self.yat = [re.compile("[Бб]е\'г", re.U), 
                    re.compile("[Бб]есо\'в", re.U), 
                    re.compile("[Бб]е\'с", re.U), 
                    re.compile("[Вв]е\'к", re.U), 
                    re.compile("[Вв]е\'р", re.U), 
                    re.compile("[Вв]е\'чн", re.U), 
                    re.compile("[Вв]се\'м", re.U), 
                    re.compile("[Гг]ре\'х", re.U), 
                    re.compile("[Гг]ре\'ш", re.U), 
                    re.compile("[Дд]е\'л", re.U), 
                    re.compile("[Лл]е\'т", re.U),
                    re.compile("[Нн]аве\'т", re.U), 
                    re.compile("[Нн]ы\'не", re.U), 
                    re.compile("[Пп]е\'сн", re.U), 
                    re.compile("[Пп]е\'ти ", re.U), 
                    re.compile("[Тт]е\'м", re.U), 
                    re.compile("[Тт]е\'х", re.U), 
                    re.compile("[Хх]ле\'б", re.U), 
                    re.compile("[Цц]е\'л", re.U)] 

        self.selo = [re.compile("[Зз]ве\'зд", re.U),
                    re.compile("[Зз]е\'ли", re.U),
                    re.compile("[Зз]ла\'к", re.U),
                    re.compile("[Зз]ло", re.U),
                    re.compile("[Зз]ве\'р", re.U),
                    re.compile("[Зз]ми", re.U),
                    re.compile("[Зз]ело", re.U),
                    re.compile("[Зз]е\'ль", re.U),
                    re.compile("[Зз]о\'л", re.U),
                    re.compile("[Зз]е\'ниц", re.U)]

        self.yako = [["я=\'коже", "jа=\'коже"],
                    ["Я=\'коже", "Jа=\'коже"],
                    ["я=\'ко", "jа=\'кw"],
                    ["Я=\'ко", "Jа=\'кw"]]

        self.wmega = [["о=т", "w\\\т"],
                    ["О=т", "W\\\т"],
                    ["о=", "w="],
                    ["О=", "_W="],
                    ["о=ста", "w=ста"],
                    ["О=ста", "W=ста"]]

        # fill up the titlo-filter list from file
        try:
            fp = codecs.open("/usr/local/bin/titlo_filter", "rb", "utf8")
            text_l = fp.readlines()
            fp.close()

            self.filter = []
            
            for line in text_l:
                line = line.encode('utf8').strip()

                a, b = line.split(' ')
                a = a.replace("R", "")

                self.filter.append((b, a))

        except IOError:
            print 'no such file found: titlo_filter'



    def opener(self, f_name):
        try:
            fp = codecs.open(f_name, "rb", "utf8")
            text_l = fp.readlines()
            fp.close()

        except IOError:
            print 'no such file found:', f_name


        for line in text_l:
            out = self.conv_str(line)
            print out
            
    def conv_str(self, line):
        # that's more useful for debugging

        line = line.strip().split(' ')
        line_l = []

        for wrd in line:
            wrd = wrd.strip()
            wrd = wrd.encode('utf8')
            wrd = self.conv_sl(wrd)
            line_l.append(wrd)

        line = ' '.join(line_l)

        return line


    def conv_sl(self, wrd):
        '''slavenize'em good'''

        wrd = self.rg_stress.sub("`", wrd, re.U)

        # replace yat 
        for reg in self.yat:
            if reg.search(wrd):
                wrd = wrd.replace("е", "jь")

        # replace selo 
        for s in self.selo:
            if s.search(wrd):
                if wrd.startswith("з"):
                    wrd = re.sub(r"^з", r"s", wrd, flags=re.U)
                else:
                    wrd = re.sub(r"^З", r"S", wrd, flags=re.U)
        # replace и with i                    
        if "и\'" in wrd:
            wrd = self.rg_i.sub('\\1i\'\\3\\4', wrd, re.U)
        else:
            wrd = self.rg_i.sub('\\1i\\3\\4', wrd, re.U)

##################don't touch this, while it works!!!!#########
        # pridyhanie
        if self.rg_prid.search(wrd):
            wrd = self.rg_prid.sub('\\1=\\2', wrd)

        # put er at the end
        wrd = self.rg_er.sub('\\1\\2ъ\\3', wrd, re.U) 
####################################################################
        # yako
        for a, b in self.yako:
            if a in wrd:
                wrd = wrd.replace(a, b)
        # wmega
        for a, b in self.wmega:
            if a == wrd:
                wrd = b

        # replace у with о_у
        if wrd.startswith("у"):
            # why it doesnt get unicode? stupid python
            # have to cut off 2 symbols for 1 letter, esle it fails
            wrd = wrd[2:]
            wrd = "о_у" + wrd
        elif wrd.startswith("У"):
            wrd = wrd[2:]
            wrd = "О_у" + wrd
        # jа 
        elif wrd.startswith("я"):
            wrd = wrd[2:]
            wrd = "jа" + wrd
        elif wrd.startswith("Я"):
            wrd = wrd[2:]
            wrd = "Jа" + wrd
        # _е
        elif wrd.startswith("е"):
            tmp = wrd[2:]
            wrd = '_е' + tmp
        elif wrd.startswith("Е"):
            wrd = wrd[2:]
            wrd = "_Е" + wrd

        # put the titlo in
        for key, val in self.filter:
            if key in wrd:
                wrd = wrd.replace(key, val)

        return wrd

    def sub_let(self, m):
        # check for starting letter, replace it

        pairs = [["я", "jа"],
                ["Я", "Jа"],
                ["у", "о_у"],
                ["У", "О_у"]]
#                [u"", u""],
#                [u"", u""],
#                [u"", u""],
        found = m.group(1)
        if found:
            for a, b in pairs:
                if found.startswith(a):
                    return b

###################main###########################

if __name__ == '__main__':
    rep = Mn()
    #rep.opener('tmp3.hip')
    #rep.conv_str(u'пе\'снь')
    from optparse import OptionParser
    usage = "usage: russ_simp.py [options] file"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", dest="debug", action='store_true', default=False, help="Work in the debuging mode")
    (options, args) = parser.parse_args()
    
    if args:

        rep.opener(args[0])
        
    elif options.debug:
#        rep.conv_str(u'пр\сн')
        rep.conv_str(u'<%п>%е\'снь')

    else:
        print "No file name given, exiting"
        sys.exit(1)


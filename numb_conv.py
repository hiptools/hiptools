#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

global debug
debug = 1

class NumParser:

    def __init__(self):

        #    $str = preg_replace("/(.*)\{(\w+~\w?)\}(.*)/", '$1$2$3', $str); // вырезаем фигур скобки в середине числа (Пролог)
        self.patt_fig = re.compile(u'(.*)\{(\w+~\w?)\}(.*)', re.U) 
#	$cut_off = preg_split("/(#?\w{1,}~_?\w?)(-?)(#?\w{1,}~_?\w?)?/", $str, -1, PREG_SPLIT_NO_EMPTY | PREG_SPLIT_DELIM_CAPTURE);
#        self.patt_pairs = re.compile(u'(#?\w{1,}~_?\w?) ?-? ?(#?\w{1,}~_?\w?)?', re.U)
        
#############TODO: 4 brackets is probably not enough. Also look for \*@ ???
#        self.patt_pairs = re.compile(u'(#?\w{1,}~_?\w?)-(#?\w{1,}~_?\w?[.,:;!\(\)\[\]%<>\*@]{0,14})?', re.U)

#TODO: нужна проверка на -ый...
#        self.patt_pairs = re.compile(u'(#?\w{1,}~_?\w?)-(#?\w{1,}~_?\w?.*)?', re.U)
#        self.patt_pairs = re.compile(u'(#?\w{1,}~_?\w?)-(#?\w{1,}~_?\w?.{0,14})?', re.U)
#        self.patt_pairs = re.compile(u'(#?\w{1,}~_?\w?)-(#?\w{1,}~_?\w?.*|.*)?', re.U)
        self.patt_pairs = re.compile(u'(#?\w{1,}~_?\w?)-(#?\w{1,}~_?\w?)', re.U)

#        self.patt_diff = re.compile(u'^(#\w)?(\w)?(\w)?(\w)(\s|[.,:;!\(\)\[\]%<>\*@]{0,14})?$', re.U)
#        self.patt_diff = re.compile(u'^(#\w)?(\w)?(\w)?(\w)(.*)$', re.U)
#        self.patt_diff = re.compile(u'^(#\w)?(\w)?(\w)?(\w)$', re.U)
        self.patt_diff = re.compile(u'^(#\w)?(\w)?(\w)?(\w)(-\w\w?)?(|\.|,|;|:|\?|!)?$', re.U)

        # change positions in number (units after tens)
#        self.patt_sub = re.compile(u'(.*)(а|в|г|д|e|s|з|и|f)(i)(|\s|[.,:;!\(\)\[\]%<>\*@]{0,14})?$', re.U)
        self.patt_sub = re.compile(u'(.*)(а|в|г|д|e|s|з|и|f)(i)(.*)$', re.U)


        self.num_ls = [(u"#а", 1000), 
                        (u"#в", 2000), 
                        (u"#г", 3000), 
                        (u"#д", 4000), 
                        (u"#e", 5000), 
                        (u"#s", 6000), 
                        (u"#з", 7000), 
                        (u"#и", 8000), 
                        (u"#f", 9000), 
                        (u"#i", 10000), 
                        (u"а", 1), 
                        (u"в", 2), 
                        (u"г", 3), 
                        (u"д", 4), 
                        (u"e", 5), 
                        (u"s", 6), 
                        (u"з", 7), 
                        (u"и", 8), 
                        (u"f", 9), 
                        (u"i", 10), 
                        (u"к", 20), 
                        (u"л", 30), 
                        (u"м", 40), 
                        (u"н", 50), 
                        (u"x", 60), 
                        (u"o", 70), 
                        (u"п", 80), 
                        (u"ч", 90), 
                        (u"р", 100), 
                        (u"с", 200), 
                        (u"т", 300), 
                        (u"u", 400), 
                        (u"ф", 500), 
                        (u"х", 600), 
                        (u"p", 700), 
                        (u"w", 800), 
                        (u"ц", 900)]

        self.cmp_let = [(u"w\т", "w"), 
                        (u"_пс", "p"), 
                        (u"_кс", "x"), 
                        (u"_о", "o"), 
                        (u"_е", "e"), 
                        (u"_у", "u"),
                        (u"_i", "i"),
                        (u"_", ""), # tempor: remove underscore!
                        (u"~", "")] # tempor: remove tilda!
        
        self.num_categ = [[
                        (u"а", 1), 
                        (u"в", 2), 
                        (u"г", 3), 
                        (u"д", 4), 
                        (u"e", 5), 
                        (u"s", 6), 
                        (u"з", 7), 
                        (u"и", 8), 
                        (u"f", 9)],

                       [(u"i", 10), 
                        (u"к", 20), 
                        (u"л", 30), 
                        (u"м", 40), 
                        (u"н", 50), 
                        (u"x", 60), 
                        (u"o", 70), 
                        (u"п", 80), 
                        (u"ч", 90)],

                       
                       [(u"р", 100), 
                        (u"с", 200), 
                        (u"т", 300), 
                        (u"u", 400), 
                        (u"ф", 500), 
                        (u"х", 600), 
                        (u"p", 700), 
                        (u"w", 800), 
                        (u"ц", 900)],

                        [(u"#а", 1000), 
                        (u"#в", 2000), 
                        (u"#г", 3000), 
                        (u"#д", 4000), 
                        (u"#e", 5000), 
                        (u"#s", 6000), 
                        (u"#з", 7000), 
                        (u"#и", 8000), 
                        (u"#f", 9000), 
                        (u"#i", 10000)]] 

    def slav2rus(self, word):
        '''General preparation of given word for process()
        '''

        res = []

        # replace braces (in Prolog)
        word = self.patt_fig.sub(u'\1\2\3', word)
#        print 'word', word

        ### word may contain two parts, for ex: и~-к~а
        word_ls = self.patt_pairs.match(word)
        if word_ls:
#            print 'word_ls', word_ls.groups()
            for t_word in word_ls.groups():
                out = self.process(t_word)
                if out:
#                    print out[0]
                    glued = ''.join([str(out[0]), out[1]])
#                    res.append(str(out[0]))
                    res.append(glued)
                else:
                    print 'error! breaking'
                    return [0, '']
            res_list = ['-'.join(res), '']
        else:
            res_list = self.process(word)

        return res_list

    def process(self, t_word):
        # clear garbage and complex letters

        tail1 = ""
        tail2 = ""

        for pair in self.cmp_let:
            t_word = t_word.replace(pair[0], pair[1])
        
        # change positions in number (units after tens)
        t_word = self.patt_sub.sub(r'\1\3\2\4', t_word)


        # Check if this is a slavic number.
        # try match?
        if self.patt_diff.search(t_word):

            t_lst = list(self.patt_diff.findall(t_word)[0])

            # get the trailing chars (.,!...)
            if t_lst[5]:
                tail1 = t_lst.pop(5)
            if t_lst[4]:
                tail2 = t_lst.pop(4)

            tail = ''.join([tail1, tail2])

            # remove empty entries
            # is it still nesessary?
            while '' in t_lst:
                t_lst.remove('')

            res = [self.sl_num_cnv(t_lst), tail]
        else:
            res = [0, '']

        # summ (number) and tail (string), to check outside, if we got real number (res[0] != 0)
        return res


    def sl_num_cnv(self, m):
        '''as argument gets list (not tuple) of slavic letters, 
        presenting numbers. Returns arithmetical summ'''

        found_ls = m
#        print 'found_ls', ''.join(found_ls)
        summa = 0
        self.tmp_ls = self.num_categ[:]


        def loopy(i):
            for num in self.tmp_ls:
#                print 'num', num
                for pair in num:
                    if pair[0] == i:
#                        print pair[0]
                        self.tmp_ls = self.tmp_ls[1:]
                        return pair[1]
            return 0

        for i in reversed(found_ls):
            res = loopy(i)
            if res:
                summa += res
            else:
                if debug:
                    print 'wrong number sintax'
                return 0
#        print 'summa', summa
        return summa

    def rus2slav(self, string):
        '''Конвертер из арабских цифр в славянские. 
        Принимает отдельные числа (надо конвертировать в строку!'''

#        print 'str: ', string
        num_dict = {}
        found_ls = []
        out = []
        # why turn it over?
        str_ls = list(string)[::-1]

#        all_ls = [self.units_ls, self.tens_ls, self.hunds_ls, self.thous_ls]

        # copy of replacement list, so it may be changed?
        all_ls = self.num_categ[:]

        for lst_num in range(len(str_ls)): 
            for slav, arab in all_ls[lst_num]:
                if str_ls[lst_num] in str(arab) and str_ls[lst_num] != '0':
                    found_ls.append(slav)
                    break

        found_ls = found_ls[::-1]

        if len(found_ls) == 1:
            found_ls.append('~')
        elif len(found_ls) > 1:
            if 10 < int(string[-2:]) < 20:
                found_ls[-1:], found_ls[-2:-1] = found_ls[-2:-1], found_ls[-1:]
            found_ls.insert(len(found_ls) - 1, '~')
        for lett in found_ls:
            for repl, sear in self.cmp_let:
                if lett == sear:
                    lett = lett.replace(sear, repl)
            out.append(lett)

        return ''.join(out)

if __name__ == '__main__':

    Parser = NumParser()
    print Parser.slav2rus(u'#афл~в-й,')

# вывести список пар русская цифра - славянская
#    for x in range(1, 50):
#       print x, Parser.rus2slav(str(x)).encode('utf8')

#    print Parser.slav2rus(u'пишем #аск~з, и это к~ .', 'context')
#    print  Parser.rus2slav('15')

#    for i in range(1000):
#        print Parser.slav2rus(Parser.rus2slav(str(i)))
#        print Parser.slav2rus(Parser.rus2slav(str(i)))

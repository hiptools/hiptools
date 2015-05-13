#! /usr/bin/python
# -*- coding: utf-8 -*-
"""Module to handle comments in HIP texts"""

import re

class Brackets:
    def __init__(self):
        self.kill_brac = None
        # regexps for different bracket types
#        self.parent = re.compile(u'\(.+?\)|\[.+?\]|\{.+?\}| с\\х\s', re.DOTALL | re.U)
        self.parent = re.compile(u'\(.+?\)|\[.+?\]|\{.+?\}', re.DOTALL | re.U)

    def collect(self, found):
        '''callback for substitution in repl_brac()'''

        word = found.group(0)
        self.data.append(word)
        if not self.kill_brac:
            # leave brackets as is.
            if '{' in word:
                # ucs8 draws junk instead of curly brackets, replace
                word = word.replace('{', '(')
                word = word.replace('}', ')')
                word = word.replace('@', '')
            return word
        else:
            if '[' in word:
                word = word.replace('[', '')
                word = word.replace(']', '')
                return word
            else:
                return ''
            
    def repl_brac(self, in_str, kill_brac=None):
        self.kill_brac = kill_brac
        self.data = []
        out = self.parent.sub(self.collect, in_str)
        
        return (out, self.data)

# TODO: tooltips showing self.data comments in TextView()

if __name__ == "__main__":
    br = Brackets()
#    res = br.repl_brac('караоке(однако)кыш;(lij)пиф\nпаф[ыв]нужтыж@{ао}усе', False)
    res = br.repl_brac('караоке(однако)кыш;(lij)пиф\nпаф[ыв]нужтыж@{ао}усе', True)
#    res = br.repl_brac('караоке', True)
    print res[0]
    print res[1]

    

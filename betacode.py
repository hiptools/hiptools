#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class Beta():
    '''Module to convert betacode into greek unicode'''
    def __init__(self):

        self.gr_filter = [['a|', u'\u1fb3'],
                        ['h|', u'\u1fc3'],
                        ['w|', u'\u1ff3'],
#                        ['a|', u'\u'],
                        ['a', u'\u03b1'],
                        ['b', u'\u03b2'],
                        ['g', u'\u03b3'],
                        ['d', u'\u03b4'],
                        ['e', u'\u03b5'],
                        ['z', u'\u03b6'],
                        ['h', u'\u03b7'],
                        ['q', u'\u03b8'],
                        ['i', u'\u03b9'],
                        ['k', u'\u03ba'],
                        ['l', u'\u03bb'],
                        ['m', u'\u03bc'],
                        ['n', u'\u03bd'],
                        ['x', u'\u03be'],
                        ['o', u'\u03bf'],
                        ['p', u'\u03c0'],
                        ['r', u'\u03c1'],
                        ['j', u'\u03c2'],
                        ['s', u'\u03c3'],
                        ['t', u'\u03c4'],
                        ['u', u'\u03c5'],
                        ['f', u'\u03c6'],
                        ['c', u'\u03c7'],
                        ['y', u'\u03c8'],
#                        ['|', u'\u037a'], # ypogegrammeni
                        ['w', u'\u03c9'],

                          ['A', u'\u0391'],
                          ['B', u'\u0392'],
                          ['G', u'\u0393'],
                          ['D', u'\u0394'],
                          ['E', u'\u0395'],
                          ['Z', u'\u0396'],
                          ['H', u'\u0397'],
                          ['Q', u'\u0398'],
                          ['I', u'\u0399'],
                          ['K', u'\u039a'],
                          ['L', u'\u039b'],
                          ['M', u'\u039c'],
                          ['N', u'\u039d'],
                          ['X', u'\u039e'],
                          ['O', u'\u039f'],
                          ['P', u'\u03a0'],
                          ['R', u'\u03a1'],
                          ['S', u'\u03a3'],
                          ['T', u'\u03a4'],
                          ['U', u'\u03a5'],
                          ['F', u'\u03a6'],
                          ['C', u'\u03a7'],
                          ['Y', u'\u03a8'],
                          ['W', u'\u03a9']]

        #print self.gr_filter.extend(self.gr_filt_c)
        
#    def convert_s(self, b_word):
#        # small letters
#        for a, b in self.gr_filter:
#            b_word = b_word.replace(a, b)
#        return b_word
#
#    def convert_b(self, b_word):
#        # capital letters
#        for a, b in self.gr_filt_c:
#            b_word = b_word.replace(a, b)
#        return b_word

    def convert_all(self, b_word):
        # all letters
        for a, b in self.gr_filter:
            b_word = b_word.replace(a, b)
        return b_word


#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Process config files from hip-tools'''

import os
import codecs

class Service:

    def __init__(self, conf_name):
#        print conf_name

        # defaults
        conf_ls = {
            'sl_font': 'Orthodox.tt Ucs8 22',
            'gr_font': 'Old Standard TT 18',
            'default_style': 'slavonic',
            'diacritics_off': 'True',
            'default_search_group': 'Богослужебные',
            'default_search_group_gr': 'Minologion_base',
            'brackets_off': 'True',
            'gr_path': '/usr/local/lib/',
            'sl_path': '/usr/local/lib/hip_tools/'
        }

        home = os.path.expanduser('~')
        conf = os.path.join(home, conf_name)
        try:
            config = codecs.open(conf, "rb", "utf8")
            stuff = config.readlines()
            config.close()

            for line in stuff:
                if not line.startswith('#') and not line == '\n':
                    key = line.split('=')[0].strip().lower()
                    val = line.split('=')[1].strip()
                    if conf_ls.has_key(key): # use only supported options
                        conf_ls[key] = val

        except IOError:
            print 'No configuration file available at', conf
        self.__dict__.update(conf_ls) # save these values as class fields

if __name__ == '__main__':
    sv = Service('.hipindex.config')

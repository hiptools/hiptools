#! /usr/bin/python
# -*- coding: utf-8 -*-
'''Get parallel for greek or slavic service.'''

import pygtk
pygtk.require('2.0')
import gtk

import codecs
import re
import sys
import os
import logging

#import hip_config
import ConfigParser
import write_utf
Writer = write_utf.write_gen()


class Par:
    def __init__(self, greek=True):

#        self.config = hip_config.Service('.hiptools.config')
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc'))

#        self.gr_path = self.config.gr_path
        self.gr_path = self.config.get('LibraryPaths', 'gr_path')
#        print 'gr_path', self.gr_path
#        self.sl_path = self.config.sl_path
        self.sl_path = self.config.get('LibraryPaths', 'sl_path')

        # if True, module called from grindex or gr_search
        # else - from hipindex of hipsearch
        self.greek = greek
        self.hip = re.compile(r'(hiplib/|greeklib/)', re.U)
        
        self.par_path = os.path.join(os.path.expanduser('~'), ".config", "hiptools", "parallel")
        print self.par_path

    def choose_path(self):
        '''dialog to choose parallel path'''

        f_name = ""

        dialog = gtk.FileChooserDialog("Open..", None, 
                gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, 
#                gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL, 
                    gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        dialog.set_default_response(gtk.RESPONSE_OK)

        fil = gtk.FileFilter()
        fil.set_name("Hip files")
        fil.add_pattern("*.hip")
        dialog.add_filter(fil)

        fil = gtk.FileFilter()
        fil.set_name("Txt files")
        fil.add_pattern("*.txt")
        dialog.add_filter(fil)

        fil = gtk.FileFilter()
        fil.set_name("All files")
        fil.add_pattern("*")
        dialog.add_filter(fil)

        fold = dialog.set_current_folder(os.path.join(self.sl_path, "trunk/hiplib"))
#        print 'folder', fold

        response = dialog.run()
#        fold = dialog.get_current_folder()

        if response == gtk.RESPONSE_OK:
#            dialog.add_shortcut_folder("/home/frpaul/svnhip/trunk")
            f_name = dialog.get_filename()
#            print "f_name", f_name

        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected' 
            f_name = None
        dialog.destroy()
        return f_name

    def get_par(self, path1=None):
        '''write down parallel path'''

        path2 = self.choose_path()
        if path2:
            fir_list = self.hip.split(path1)
            sec_list = self.hip.split(path2)
            path1 = os.path.join(fir_list[1], fir_list[2])
            path2 = os.path.join(sec_list[1], sec_list[2])
            line = path1 + '==' + path2 + '\n'
#            print line

#            temp_path = os.path.join(self.gr_path, "parallel")
            temp_path = os.path.join(os.path.expanduser('~'), ".config", "hiptools", "parallel")

            #temp_path = os.path.join(os.path.expanduser("~"), "parallel")
            Writer.write_file(temp_path, [line,], "a")
        else:
            print 'have not found second path'

    def open_par(self, path1=None):
        '''Returns path parallel to given one'''

        if path1:
            fp = codecs.open(self.par_path, "rb", "utf-8")
            f_lines = fp.readlines()
            fp.close()
            
            # remove first part from path, like "/usr/local/lib
            fir_list = self.hip.split(path1)
            path1 = os.path.join(fir_list[1], fir_list[2])
            print 'path1', path1

#            print f_lines
            for line in f_lines:
                if path1 in line:
                    print 'found parallel path ', line
                    parts = line.split("==")
                    if self.greek:
                        op_path = os.path.join(os.path.split(self.sl_path)[0], parts[1])

#                        op_path = op_path.rstrip()
                        print "parts[1]", parts[1]

                    else:
#                        op_path = os.path.join(self.gr_path, parts[0])
                        op_path = os.path.join(os.path.split(self.gr_path)[0], parts[0])
#                        print "slav op_path", op_path
                        print "parts[0]", parts[0]

#                    print "op_path", op_path

                    return op_path

#                else:
#                    print 'did not find parallel to file', path1
                    
        else:
            print 'no path given to open'

        return None

if __name__ == '__main__':
    fine = Par(True)
    fine.get_par("greeklib/oct/ihos_1/Tone1Fri.xml")
#    fine.open_par("greeklib/oct/ihos_1/Tone1Fri.xml")

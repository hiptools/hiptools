#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

import codecs 
import re
import sys
import os
import xml.etree.ElementTree as ET
import subprocess

import ConfigParser

class Findaname():
    '''Finds names of the saints and other feasts and corresponding service texts in hip library.
     All names searched should be in Genetive case'''
    def __init__(self):
        pass

    def searcher(self, find_n):
        s_path = os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'saints.xml')
        tree = ET.parse(s_path)
        root = tree.getroot()
        res = []

        for mn in root.iter('month'):
            for d in mn.iter('day'):
                for fs in d.iter('feast'):
                    if find_n in fs.get('name'):
                        res_path = os.path.join(lib_path, 'min',  d.get('filename').encode('utf8'))
                        res.append([res_path, d.get('date').encode('utf8'), fs.get('name').encode('utf8')])
                         
        # [filename, date, text]
        return res

    def entry_cb(self, ent):
        search_w = ent.get_text()

def destroy_cb(widget):
    gtk.main_quit()
    return False


class Main_face():
    '''GUI'''
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_resizable(True)
        window.set_border_width(10)
        window.set_size_request(600, 500)

        window.set_title("Найденные имена")
        window.set_border_width(0)
        window.connect("destroy", destroy_cb) 

        box1 = gtk.VBox(False, 0)
        window.add(box1)
        box1.show()
        box2 = gtk.VBox(False, 3)
        box2.set_border_width(3)
        box1.pack_start(box2, True, True, 0)
        box2.show()

        hbox = gtk.HBox(False, 0)
        hbox.show()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.model = gtk.TreeStore(str, str)
        self.tv = gtk.TreeView(self.model)
        self.selection = self.tv.get_selection()
#        self.tv.connect('row-activated', self.key_press)

        sw.add(self.tv)

        label = gtk.Label() 
        entry = gtk.Entry()
        button = gtk.Button('Поиск')
        
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn("Дата", cell1, text=0)
        self.column2 = gtk.TreeViewColumn("Память святого", cell2, text=1)

        self.tv.append_column(self.column)
        self.tv.append_column(self.column2)

        # hide second column 
#        self.column2.set_visible(False)
        
        sw.show_all()
        self.tv.show()
        box2.pack_start(hbox, False, False, 0)
        hbox.pack_start(entry, True, False, 10)
        hbox.pack_end(button, False, False, 0)
        box2.pack_start(label, False, False, 0)
        box2.pack_start(sw)

        label.show()
        entry.show()

        window.show()


        entry.connect('activate', sr.entry_cb)

def main():
    gtk.main()
    return 0

if __name__ == '__main__':

    sr = Findaname()

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc'))

    lib_path = config.get('LibraryPaths', 'sl_path')

    from optparse import OptionParser
    usage = "usage: %prog name"
    parser = OptionParser(usage=usage)

    parser.add_option("-c", "--cli", dest="cli", action="store_true", help="use CLI indtead of GUI")

    (options, args) = parser.parse_args()

    if not options.cli:
        face = Main_face()
        main()

    else:
        chuck = re.compile(u'\d\d?', re.U)

        def output(res):
            # recursive func, outputs results, checks input, starts a popup
            for i in range(len(res)):
                print i, res[i][1], res[i][2]
            nm = raw_input('pick number or [q]uit! ')
            if nm == 'q':
                sys.exit(1)
            elif not chuck.match(nm):
                print 'Use q to quit, numbers to open file'
                # here's the recursion
                output(res)
            else:
                f_name = ''.join(res[int(nm)])
                print 'opening file: ', res[int(nm)][0]
                subprocess.Popen(['textview.py', res[int(nm)][0]])

        if args:
            res = sr.searcher(args[0].decode('utf8'))
            if res:
                output(res)
            else:
                print 'Nothing is found, sorry'
                sys.exit(1)

        else:
            print 'No args. What\'s to search? Exiting'
            sys.exit(1)


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
from textview import Show_text

class Findaname():
    '''Finds names of the saints and other feasts and corresponding service texts in hip library.
     All names searched should be in Genetive case'''
    def __init__(self):
        self.split_parag = re.compile(u'(?:\r?\n){2,}', re.U)
        self.kill_rn = re.compile(u'(?:\r?\n)', re.U)
        self.html_del = re.compile(r'<.*?>', re.S)


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
        print search_w

        res = self.searcher(search_w)
        for name in res:
            print name[1], name[2]
        self.ins(res)

    def ins(self, res):
        
        for i in res:
            iter = face.model.append()
            face.model.set(iter, 0, i[0])
            face.model.set(iter, 1, i[1])
            face.model.set(iter, 2, i[2])
#            path_s_u = face.path2name(i[0]).decode('utf8')[:40]
#            face.model.set(iter, 3, path_s_u)
#            self.model.set(iter, 3, '')
#            self.model.set(iter, 3, path2name(i[0]))


    def on_click(self, widget, iter, path):
        ''' callback, row in TreeView clicked '''

        selection = widget.get_selection()
        model, path = selection.get_selected_rows()
        # get iter in Viewer (found entries)
        iter_v = model.get_iter(path[0])
        file_path = model.get_value(iter_v, 0) 
        title = model.get_value(iter_v, 1) 
#        print file_path

        try:
#            if face.mode:
#                fp = codecs.open(file_path, "rb", "utf8")
#            else:
            fp = codecs.open(file_path, "rb", "cp1251")
            f_lines = fp.readlines()
            fp.close()
        except IOError:
            print 'no such file found'


        # create window to output selected text
        txt_win = Show_text(False)
        txt_win.path1 = file_path
        txt_win.window3.set_title(title)

        text_ls = []
        txt = ''.join(f_lines)

        parts_ls = self.split_parag.split(txt)
        for part in parts_ls:
            part = self.kill_rn.sub(' ', part)
            text_ls.append(part)
        txt1 = '\n\n'.join(text_ls)

        txt_win.ins_txt_hip(txt1)


#        txt_win.mode = face.mode
#
#        txt_win.window3.set_title(face.path2name(file_path))
#
#        if face.mode:
#            txt_win.ins_txt_gr(txt_ins)
#        else:
#            txt_win.ins_txt_hip(txt_ins)



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
        self.model = gtk.ListStore(str, str, str, str)
        self.tv = gtk.TreeView(self.model)
        self.selection = self.tv.get_selection()
        self.tv.connect('row-activated', sr.on_click)

        self.modelfilter = self.model.filter_new()
        self.tv.set_model(self.modelfilter)

        sw.add(self.tv)

        label = gtk.Label() 
        entry = gtk.Entry()
        button = gtk.Button('Поиск')
        
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        cell1.set_property('font', 'FreeSans 12')
        cell2.set_property('font', 'FreeSans 12')
        self.column = gtk.TreeViewColumn("Дата", cell1, text=1)
        self.column2 = gtk.TreeViewColumn("Память святого", cell2, text=2)
        self.tv.append_column(self.column)
        self.tv.append_column(self.column2)
#        self.tv.set_search_column(2)

        # hide second column 
#        self.column2.set_visible(False)
        
        sw.show_all()
        self.tv.show()
        box2.pack_start(hbox, False, False, 0)
        hbox.pack_start(entry, True, True, 1)
        hbox.pack_end(button, False, False, 1)
        box2.pack_start(label, False, False, 0)
        box2.pack_start(sw)

        label.show()
        entry.show()
        button.show()

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


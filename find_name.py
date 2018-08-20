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
#import subprocess
import unicodedata
import datetime

import ConfigParser
from textview import Show_text
from betacode import Beta
from old_date import Old

bcode = Beta()

class Findaname():
    '''Finds names of the saints and other feasts and corresponding service texts in hip library.
     All names searched should be in Genetive case. No need to start with capital letter! '''
    def __init__(self, mode=False):
        self.split_parag = re.compile(u'(?:\r?\n){2,}', re.U)
        self.kill_rn = re.compile(u'(?:\r?\n)', re.U)
        self.html_del = re.compile(r'<.*?>', re.S)
        if mode:
            self.mode = True
            self.xml_file = 'saints_gr.xml'
            self.lib_path = os.path.join(config.get('LibraryPaths', 'gr_path'), 'Minologion')
            self.enc = 'utf-8'
        else:
            self.mode = False
            self.xml_file = 'saints_hip.xml'
            self.lib_path = os.path.join(config.get('LibraryPaths', 'sl_path'), 'min')
            self.enc = 'cp1251'
        print self.lib_path

#        min_ls = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
        self.min_ls = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]

    def txt_output(self, res):
        # recursive func, outputs results in text version of the prog, checks input, starts a popup

        for i in range(len(res)):
            print i, res[i][1], res[i][2]

        nm = raw_input('pick number or [q]uit! ')

        if nm == 'q':
            sys.exit(1)
            
        elif not chuck.match(nm):
            print 'Use q to quit, numbers to open file'
            # here's the recursion
            self.txt_output(res)

        else:
#            f_name = ''.join(res[int(nm)])
            print 'opening file: ', res[int(nm)][0]
            self.opener(res[int(nm)][0], res[int(nm)][2], cli = True)
#            self.opener(res[int(nm)][0], 'just text')

    def searcher(self, find_n):

        find_n = bcode.convert_all(find_n)
#        find_n = bcode.convert_s(find_n)
#       find_n = bcode.convert_b(find_n)
        print "this is beta code", find_n

        find_n = find_n.decode('utf-8')
        find_n = find_n.title() # first letter to uppercase
        find_n = unicodedata.normalize('NFD', find_n)

        s_path = os.path.join(os.path.expanduser('~'), '.config', 'hiptools', self.xml_file)
        tree = ET.parse(s_path)
        root = tree.getroot()
        res = []

        for mn in root.iter('month'):
            for d in mn.iter('day'):
                for fs in d.iter('feast'):
                    s_line = fs.get('name')
                    # clean all apostrophs (stresses) from searched text
                    if self.mode:
                        for a in [u'\u0300', u'\u0342', u'\u0301', u'\u0314', u'\u0313']:
                            s_line = s_line.replace(a, '')

                    if find_n in s_line:
                        res_path = os.path.join(self.lib_path, fs.get('filename').encode('utf8'))
                        res.append([res_path, d.get('date').encode('utf8'), fs.get('name').encode('utf8')])
# TODO: 
# 
        yr = datetime.date.today().year
# определить старый юлианский год в модуле old_date
        (dy, mnc) = res[0][1].split()

#        print 'day', dtt[0], 'mon', dtt[1][:-1], 'year', yr
        mth = 'zz'
        for z in range(len(self.min_ls)):
            if self.min_ls[z] == mnc[:-1]:
                mth = z + 1
#                print dy, mth, yr

        olddate = Old().to_new((int(dy), int(mth), int(yr)))
        print olddate
        res[0].append(olddate)
        # [filename, date, text]
        return res

    def entry_cb(self, ent):
        search_w = ent.get_text()
        print search_w

        res = self.searcher(search_w)
        if res:
            for name in res:
                print name[1], name[2]
            face.model.clear()
            self.ins(res)
        else:
            print 'nothing\'s found. Sorry'
#TODO: make a popup or smth

    def ins(self, res):
#        face.model.cleanup() 
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

        self.opener(file_path, title)

    def opener(self, file_path, title, cli=False):
#        print 'path', file_path
        try:
            fp = codecs.open(file_path, "rb", self.enc)
            f_lines = fp.readlines()
            fp.close()
        except IOError:
            print 'no such file found', file_path

            # create window to output selected text
        txt_win = Show_text(self.mode)
        txt_win.path1 = file_path
        txt_win.window3.set_title(title)

        text_ls = []
        txt = ''.join(f_lines)

        parts_ls = self.split_parag.split(txt)
        for part in parts_ls:
            part = self.kill_rn.sub(' ', part)
            text_ls.append(part)
        txt1 = '\n\n'.join(text_ls)

        if self.mode:
            txt_win.ins_txt_gr(txt1)
        else:
            txt_win.ins_txt_hip(txt1)

        if cli:
            txt_win.window3.connect("destroy", self.destroy_cb) 
            main()


    def destroy_cb(self, widget):
        gtk.main_quit()
        return False


class Main_face():
    '''GUI'''
    def __init__(self, mode=False):

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_resizable(True)
        window.set_border_width(10)
        window.set_size_request(600, 500)

        window.set_title("Найденные имена")
        window.set_border_width(0)
        window.connect("destroy", sr.destroy_cb) 

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


    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc'))


    from optparse import OptionParser
    usage = "usage: %prog name"
    parser = OptionParser(usage=usage)

    parser.add_option("-c", "--cli", dest="cli", action="store_true", help="use CLI indtead of GUI")
    parser.add_option("-m", "--menu", dest="menu", action="store_true", help="CLI menu to view corresponding services.")
    parser.add_option("-g", "--greek", dest="greek", action="store_true", help="Search in greek base instead of slavic")

    (options, args) = parser.parse_args()

    if not options.cli:
        if options.greek:
            sr = Findaname(True)
            face = Main_face()
        else:
            sr = Findaname(False)
            face = Main_face()

        main()

    else:
        chuck = re.compile(u'\d\d?', re.U)

        if args:
            if options.greek:
                sr = Findaname(True)
            else:
                sr = Findaname(False)

            res = sr.searcher(args[0].decode('utf8'))
            if res:
                if options.menu:
                    sr.txt_output(res)
                else:
                    for i in range(len(res)):
                        print i, res[i][1], res[i][3], "н.ст.,", res[i][2]

            else:
                print 'Nothing is found, sorry'
                sys.exit(1)

        else:
            print 'No args. What\'s to search? Exiting'
            sys.exit(1)


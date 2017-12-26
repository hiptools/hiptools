#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import codecs
import re
import os
import sys
import chardet

import xml.etree.ElementTree as ET

# formerly - ucs8conv, renamed
import hipconv
import ConfigParser
# comment parser
import hipcomment
import write_utf
import slovenize
import get_par

conv = hipconv.Repl()
brac = hipcomment.Brackets()
Writer = write_utf.write_gen()
slov = slovenize.Mn()

def destroy_cb(widget):
    gtk.main_quit()
    return False


class Show_text:
    """ text viewer 

    """
    def __init__(self, Mode=True):
        # mode=true means greek mode 
        self.r_vs = re.compile(r'g (.*?) (\d{1,2})[:, ](\d{1,2})')

        self.book_names = [[['Мф','Mf','Mt', 'мф', 'mf', 'mt'], 'Matthew'],
                            [['Мк', 'Mk', 'мк', 'mk'], 'Mark'],
                            [['Лк', 'Lk', 'лк', 'lk'], 'Luke'],
                            [['Ин', 'Jh', 'Jhn', 'Jn', 'ин', 'jh', 'jhn', 'jn'], 'John']]

#        self.res_num = 0
#        self.text = 'Searching...'
        window2 = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window2.set_resizable(True)
        window2.set_border_width(10)
        window2.set_size_request(950, 450)

        window2.set_title("Просмотр результатов")
        window2.set_border_width(0)
#        window2.connect('key_press_event', on_key_press_event)

        box1 = gtk.VBox(False, 0)
        window2.add(box1)
        box1.show()
        box2 = gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.model = gtk.ListStore(str, str, str)
        self.tv = gtk.TreeView(self.model)
        self.selection = self.tv.get_selection()

#        self.tv.connect('key_press_event', self.on_key_press_event)
#        self.tv.connect('row-activated', self.on_click)

        self.modelfilter = self.model.filter_new()
#        self.modelfilter.set_visible_func(vis, self.small)
        self.tv.set_model(self.modelfilter)

        sw.add(self.tv)

        self.label = gtk.Label() 
        self.entry = gtk.Entry()
        
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        cell3 = gtk.CellRendererText()
        cell1.set_property('font', 'FreeSans 12')
        cell2.set_property('font', 'FreeSans 12')
        cell3.set_property('font', 'FreeSans 12')
        self.column1 = gtk.TreeViewColumn("Num", cell1, text=0)
        self.column2 = gtk.TreeViewColumn("Verse", cell2, text=1)
        self.column3 = gtk.TreeViewColumn("Text", cell3, text=2)
        self.tv.append_column(self.column1)
        self.tv.append_column(self.column2)
        self.tv.append_column(self.column3)
        self.tv.set_search_column(1)
        self.tv.set_search_column(2)
#        self.tv.set_search_column(3)
        
        sw.show_all()
        self.tv.show()
        box2.pack_start(self.label, False, False, 0)
        box2.pack_start(sw)
        box2.pack_start(self.entry, False, False, 0)

        self.entry.connect('activate', self.entry_cb)
#        self.entry.connect('key_press_event', self.on_key_press_event)
#        self.label.set_text("Найдено " + str(count) + " совпадений")
        self.entry.show()
        self.label.show()

        if __name__ == '__main__':
            window2.connect('destroy', destroy_cb)

        window2.show()

#    def on_key_press_event(self, widget, event):
#        """Callback for find-Entry in results window"""
#        keyname = gtk.gdk.keyval_name(event.keyval)
#
#        if event.state & gtk.gdk.CONTROL_MASK:
#            if keyname == ":" or keyname == "Cyrillic_zhe_capital":
#                print 'zhezhe'
# 
##        model, path = self.selection.get_selected_rows()
##        iter_v = model.get_iter(path[0])
##        file_path = model.get_value(iter_v, 0) 

    def entry_cb(self, ent):
        """Callback for entry widg
           Look for word in results of primary search

        """
 
        addr = ent.get_text()
#        fnc, arg = addr.split()
#        if fnc == 'g': # go to verse
            
#            args = r_vs.split(arg)
        if self.r_vs.search(addr):
            args = self.r_vs.split(addr)
            if args:
                bk = args[1]
                ch = args[2]
                vs = args[3]
#                print bk, ch, vs
                # get full book name
                for sh, lg in self.book_names:
                    if bk in sh:
                        bk = lg
                        print bk

            else:
                print 'Some error occured. Perhaps, a typo?'
            bk_path = os.path.join('hipxml_eua', bk + '.xml')
            print bk_path
            # this doesnt work. Have to rewright TreeView
            self.ins_txt(self.xml_open(bk_path))
            self.show_verse(ch, vs)

    def xml_open(self, *args):
        print 'args xml_open', args

        t_name = ""
        tree = ET.parse(args[0])
        root = tree.getroot()
#        res = []

        f_lines = [] # list of the book chapters

        head = root.find('header')
        # can't check 'head' the usual way - parser swears
        if ET.iselement(head):
            f_lines.append(head.text)

#        for att in root.attrib:
#            if att == 'title':
#                t_name = root.attrib['title']
        vss = []
        #  make a list of verses, chapters, prepends (num = None)
        ch_num = ''

        for bk in root.iter('span'):
            if bk.get('type') == 'chapter':
                ch_num = bk.get('num')
                if vss:
                    f_lines.append(vss)
                    vss = []
                # begin new chapter - chapter text is included into verses list
                vss.append([ch_num, '0', bk.text])
            elif bk.get('type') == 'verse':
                # chapter, verse, text 
                vss.append([ch_num, bk.get('num'), bk.text])

            else:
                # prepend case
                vss.append(['0', '0', bk.text])

        return f_lines

    def ins_txt(self, f_lines):
        # every ch is a chapter, first ch = [header, prepend]
        for ch  in f_lines:
            for tp, nm, txt in ch:
#                print tp, nm, txt
                iter = self.model.append()
                self.model.set(iter, 0, tp)
                self.model.set(iter, 1, nm)
                self.model.set(iter, 2, txt)

    def show_verse(self, c, v):

        data = [c, v]

        def find_match(model, path, iter, data):
            # if there is a verse number:
            if model.get_value(iter, 1):
                ch = model.get_value(iter, 0)
                vs = model.get_value(iter, 1)
                
                if data == [ch, vs]:
                    data.append(path)
        self.modelfilter.foreach(find_match, data)
        search_res = data[-1:]

        if search_res:
            self.selection.select_path(search_res[0])
            self.tv.scroll_to_cell(search_res[0])
        else:
            print 'no match found'


if __name__ == '__main__':

#    argv = sys.argv

    from optparse import OptionParser
    usage = "usage: %prog [options] file"
    parser = OptionParser(usage=usage)

#    parser.add_option("-x", "--xml", dest="xml", action="store_true", help="Open as xml")
#    parser.add_option("-g", "--greek", dest="greek", action="store_true", help="Switch to greek")
    
    (options, args) = parser.parse_args()

#    config = hip_config.Service('.hipeditor.config')
#    config = hip_config.Service('.hiptools.config')
#    config = ConfigParser.ConfigParser()

    if args:

        f_path = args[0]
#        print f_path

        txt_win = Show_text(True)
#        txt_win.path1 = args[0]
#        f_lines = txt_win.xml_open(args[0])
        f_lines = txt_win.xml_open(args[0])
#        print f_lines
        txt_win.ins_txt(f_lines)
        txt_win.show_verse('14','2')


    else:
        print 'no arguments, exiting'
        sys.exit(0)

    def main():
        gtk.main()
        return 0

    main()

#TODO: сделай нормальную замену шрифта в греческом окне (C+u). Пока вылазят xml-тэги.

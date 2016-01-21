#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import codecs
import re
import os
import sys

#import hipconv
import booklst
import ConfigParser

#from ht_callb import Connect_ind
#from ht_callb import Connect_sear
#from ht_callb import Process
#from ht_callb import Process_s

config = ConfigParser.ConfigParser()

class Txt(gtk.TextView):
    """ Subclass of TextView
    
    """
    def __init__(self, conf_path=None):

        gtk.TextView.__init__(self)

#        config = hip_config.Service('.hipsearch.config')
        if conf_path:
            config.read(conf_path)
        else:
            config.read(os.path.join(os.getcwd(), '.config', 'hiptools', 'hiptoolsrc'))

        self.base_txt = ""
#        self.mode = config.default_style

        self.style_s = config.get('Style', 'default_style')
        self.sl_font = config.get('Fonts', 'sl_font')
        self.sl_font_prev = ''
        self.plain_font = 'Tahoma 16'


        # if style_s == True, have to use Process_s().style_txt()
#        self.style_s = False

#        print 'font!!!', config.default_font
#        print 'def mode!!!', self.mode

#class Mug(Connect_ind, Connect_sear, Process, Process_s):
class Mug():
    """ Mug of the main programm

    """
    def __init__(self, conf_path):

        self.conf_path = conf_path

        self.config = config        
        self.config.read(self.conf_path)
        # slav-greek switches for viewer and search tools
        # if mode == True - switched to greek, else - to slavonic
        # mode for search tool
        if self.config.get('Switches', 'library_greek_s') == 'True':
            self.mode_s = True
        elif self.config.get('Switches', 'library_greek_s') == 'False':
            self.mode_s = False
        # mode for index (viewer) tool
        if self.config.get('Switches', 'library_greek_v') == 'True':
            self.mode_v = True
        elif self.config.get('Switches', 'library_greek_v') == 'False':
            self.mode_v = False

        # style for slavonic viewer - slavonic or plain
        self.style_s = self.config.get('Style', 'default_style')
        # kill service tags in hip texts like {...}
        self.br_off = self.config.get('Style', 'brackets_off')

        if self.style_s == 'slavonic':
            self.plain = False
        elif self.style_s == 'plain':
            self.plain = True

        if self.br_off == 'True':
            self.brackets_off = True
        else:
            self.brackets_off = False

#        self.mode_v = self.config.get('Switches', 'library_greek_v')
#        self.mode_s = self.config.get('Switches', 'library_greek_s')

        self.window3 = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window3.set_resizable(True)

        # second parameter sets height of the whole window
        self.window3.set_size_request(950, 490)
        self.window3.set_border_width(3)
        self.window3.connect('destroy', self.destroy_cb)

        # common box for all the vidgets
        box1 = gtk.VBox(False, 0)
        accel_m = gtk.AccelGroup()
        action_g = gtk.ActionGroup('MenuBarAction')
        self.window3.add_accel_group(accel_m)

        self.action_fo = gtk.Action('OpenFile', '_Open', 'Open file', gtk.STOCK_OPEN)
        self.action_fs = gtk.Action('SaveFile', '_Save', 'Save file', gtk.STOCK_SAVE)

        action_g.add_action_with_accel(self.action_fo, None)
        action_g.add_action_with_accel(self.action_fs, None)

        self.action_fo.set_accel_group(accel_m)
        self.action_fs.set_accel_group(accel_m)

        self.action_fo.connect_accelerator()
        self.action_fs.connect_accelerator()

        box1.set_border_width(0)
        self.window3.add(box1)
        box1.show()

#        self.action_fo.connect('activate', self.open_file)
#        self.action_fs.connect('activate', self.save_file)
        


        # Search area
#        box3 = gtk.VBox(False, 3)
#        box3.set_border_width(1)
#        box1.pack_start(box3, True, True, 0)
#        box3.show()
        
        # zero vidget raw: menubar
        m_horiz = gtk.HBox(False, 0)
        box1.pack_start(m_horiz, False, False, 0)
        m_horiz.show()

        # first button in a menubar
        self.item1 = gtk.MenuItem('File')
        # submenu for first button
        menu_file = gtk.Menu()
        menu_file.set_accel_group(accel_m)

        self.item_open = gtk.MenuItem('Open file')
#        self.action_fo.connect_proxy(self.item_open)

        self.item_save = gtk.MenuItem('Save file')
#        self.action_fs.connect_proxy(self.item_save)

        menu_file.attach(self.item_open, 0, 1, 0, 1)
        menu_file.attach(self.item_save, 0, 1, 1, 2)
        self.item1.set_submenu(menu_file)

        self.item2 = gtk.MenuItem('Options')

        self.menu = gtk.MenuBar()

        self.menu.append(self.item1)
        self.menu.append(self.item2)
        m_horiz.pack_start(self.menu, False, False, 1)
        self.menu.show()
        self.item1.show()
        menu_file.show()
        self.item_open.show()
        self.item_save.show()
        self.item2.show()

#        self.item2.connect("activate", self.opt_wrap)

        # first vidget raw: search butt, entry, combo-box
        s_horiz = gtk.HBox(False, 0)
        box1.pack_start(s_horiz, False, False, 0)
        s_horiz.show()

        self.combo = gtk.combo_box_new_text()
        self.s_entry = gtk.Entry()
        self.s_entry.set_width_chars(50)
        self.s_button = gtk.Button('Search')

        self.gr_label1 = "Греч."
        self.gr_switch1 = gtk.Button(self.gr_label1)

        s_horiz.pack_start(self.combo, False, False, 1)
        self.combo.show()
 
        s_horiz.pack_start(self.s_entry, False, False, 1)
        self.s_entry.show()
        
        s_horiz.pack_start(self.s_button, False, False, 1)
        self.s_button.show()
       
        s_horiz.pack_end(self.gr_switch1, False, False, 1)
        self.gr_switch1.show()


        # second raw: progress bar, check buttons
        pr_horiz = gtk.HBox(False, 0)
        box1.pack_start(pr_horiz, False, False, 0)
        pr_horiz.show()

        self.pr_bar = gtk.ProgressBar()
        pr_horiz.pack_start(self.pr_bar, True, True, 1)
        self.pr_bar.show()

        self.toggle1 = gtk.CheckButton("Вкл. ударения")
        self.toggle2 = gtk.CheckButton("Учит. регистр")

        pr_horiz.pack_start(self.toggle1, False, False, 1)
        pr_horiz.pack_start(self.toggle2, False, False, 1)
        self.toggle1.show()
        self.toggle2.show()
        
        # Common horizontal box for book list and text area
        self.box2 = gtk.HBox(False, 0)
        self.box2.set_border_width(0)
        box1.pack_start(self.box2, True, True, 0)
        self.box2.show()
      
        # Book index
        box4 = gtk.VBox(False, 3)
        box4.set_border_width(1)
        self.box2.pack_start(box4, True, True, 0)
        box4.show()

        box4.set_size_request(100, 400)

        books_sw1 = gtk.ScrolledWindow()
        books_sw2 = gtk.ScrolledWindow()
        books_sw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        books_sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # Tree models
        self.model_sl = gtk.TreeStore(str, str)
        self.model_gr = gtk.TreeStore(str, str)

        self.tv1 = gtk.TreeView()
        self.tv2 = gtk.TreeView()
#        if self.mode_v:
#            self.tv1 = gtk.TreeView(self.model_gr)
#        else:
#            self.tv1 = gtk.TreeView(self.model_sl)

#        self.selection = self.tv1.get_selection()

#        self.modelfilter = self.model.filter_new()
#        self.tv1.set_model(self.modelfilter)

        books_sw1.add(self.tv1)
        books_sw2.add(self.tv2)

#####        self.box2.connect('key_press_event', self.note_cb)

        self.b_entry = gtk.Entry()
        self.b_entry.show()
#        self.b_entry.connect('key_press_event', self.search_cb)
        
        # greek renderers and columns
        self.cell_gr1 = gtk.CellRendererText()
        self.cell_gr2 = gtk.CellRendererText()
        self.column_gr1 = gtk.TreeViewColumn("Название книги", self.cell_gr1, text=0)
        self.column_gr2 = gtk.TreeViewColumn("Code", self.cell_gr2, text=1)
        # slavonic renderers and columns
        self.cell_sl1 = gtk.CellRendererText()
        self.cell_sl2 = gtk.CellRendererText()
        self.column_sl1 = gtk.TreeViewColumn("Название книги", self.cell_sl1, text=0)
        self.column_sl2 = gtk.TreeViewColumn("Code", self.cell_sl2, text=1)

#        self.tv1.set_search_column(2)

        # hide second column 
        self.column_gr2.set_visible(False)
        self.column_sl2.set_visible(False)

        books_sw1.show_all()
        books_sw2.show_all()
        self.tv1.show()
        self.tv2.show()
        box4.pack_start(books_sw1)

        self.tv1.grab_focus()

        box4.pack_start(self.b_entry, False, False, 0)

        # Text field
        box5 = gtk.VBox(False, 3)
        box5.set_border_width(1)
        self.box2.pack_start(box5, True, True, 0)
        box5.show()

        box5.set_size_request(500, 400)

        self.f_select = gtk.FontButton(fontname=None)
#        self.f_select.connect('font-set', self.font_cb)

#        self.check1 = gtk.CheckButton("вкл. юникод")
#        self.check1.connect("toggled", self.uni_out)

        self.entry = gtk.Entry()

        # notebook
#        self.note = gtk.Notebook()
#        self.note.set_tab_pos(gtk.POS_TOP)
#        self.note.show()
#        self.note.set_scrollable(True)
#        self.show_tabs = True
#        self.show_border = True

        # create first page. Todo: make it remember previously
        # closed pages. Have to use some function (load pickle). 
#        self.append_pg()

        self.f_select.show()
        self.entry.show()
#        self.entry.connect('key_press_event', self.search_cb)

#        self.textview.show()

#        self.box2.pack_start(self.entry, False, False, 0)

        l_horiz = gtk.HBox(False, 0)
        box5.pack_start(l_horiz, False, False, 0)
        l_horiz.show()

        self.gr_label2 = "Греч."
        self.gr_switch2 = gtk.Button(self.gr_label2)

        l_horiz.pack_start(self.f_select, False, False, 1)
        l_horiz.pack_end(self.gr_switch2, False, False, 1)
        self.gr_switch2.show()


#        self.tv1.connect('row-activated', self.key_press)
#        self.tv2.connect('row-activated', self.key_press)

#        if self.mode_v:
        self.lib_path1 = self.config.get('LibraryPaths', 'sl_path')
        self.lib_path2 = self.config.get('LibraryPaths', 'gr_path')

        self.book_lst1 = booklst.listbooks(self.lib_path1) # , False) # - чтобы не перечислять "лишние" (не описанные) файлы
        self.book_lst2 = booklst.listbooks(self.lib_path2) # , False) # - чтобы не перечислять "лишние" (не описанные) файлы
#        self.enc = 'utf-8'
#        self.gr_switch2.set_label("Слав.")
        self.model_sl = self.putdir(self.model_sl, booklst.listbooks(self.lib_path1))
        self.model_gr = self.putdir(self.model_gr, booklst.listbooks(self.lib_path2))
#        self.model_sl = self.putdir(self.model_sl, booklst.listbooks(self.config.get('LibraryPaths', 'sl_path')))

        self.tv1.append_column(self.column_sl1)
        self.tv1.append_column(self.column_sl2)
        self.tv1.set_model(self.model_sl)

        self.tv2.append_column(self.column_gr1)
        self.tv2.append_column(self.column_gr2)
        self.tv2.set_model(self.model_gr)

#        self.enc = 'cp1251'
#        self.gr_switch2.set_label("Греч.")

#        gtk.main_quit()
#        return False

        self.window3.show()

    def putdir(self, model, obj, parent=None):
        """
        Рекурсивная функция дла добавления элементов в дерево
        """
        for book in obj:
            iter = model.append(parent)
            model.set(iter, 0, book[1])
            model.set(iter, 1, book[0])
            if book[2]: # subdir
                self.putdir(model, book[2], iter)
        return model

    def destroy_cb(self, widget):
        gtk.main_quit()
        return False

if __name__ == '__main__':

    from optparse import OptionParser
    usage = "usage: %prog [options] dir"
    parser = OptionParser(usage=usage)

    parser.add_option("-c", "--config", dest="config", action="store_true", help="Path to config file")

    (options, args) = parser.parse_args()

    if options.config:
        if args:
            front = Mug(args[0])
        else:
            print "no path to config file given, exiting"
            sys.exit(0)
    else:
        # default path to config file
        front = Mug(os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc'))

    def main():
        gtk.main()
        return 0

    main()



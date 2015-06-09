#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import codecs
import re
import os
import sys

import hipconv
import ConfigParser
#import hipcomment
#import write_utf

#conv = hipconv.Repl()
#brac = hipcomment.Brackets()
#Writer = write_utf.write_gen()

def destroy_cb(widget):
    gtk.main_quit()
    return False

class Txt(gtk.TextView):
    """ Subclass of TextView
    
    """
    def __init__(self):

        gtk.TextView.__init__(self)

#        config = hip_config.Service('.hipsearch.config')

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc'))

        self.base_txt = ""
#        self.mode = config.default_style

        self.style_s = config.get('Style', 'default_style')
        self.sl_font = config.get('Fonts', 'sl_font')
        self.sl_font_prev = ''
        self.plain_font = 'Tahoma 16'

        # if style_s == True, have to use Process_s().style_txt()
        self.style_s = False

#        print 'font!!!', config.default_font
#        print 'def mode!!!', self.mode

class Mug:
    """ Mug of the main programm

    """
#    def __init__(self, config):
    def __init__(self):

#        self.plain = True
        # original plain text
#        self.base_txt = ""
        self.window3 = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window3.set_resizable(True)

        # second parameter sets height of the whole window
        self.window3.set_size_request(950, 490)
        self.window3.set_border_width(3)
        self.window3.connect('destroy', destroy_cb)

        # common box for all the vidgets
        box1 = gtk.VBox(False, 0)
        accel_m = gtk.AccelGroup()
        action_g = gtk.ActionGroup('MenuBarAction')

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
#        self.item_open.add_accelerator("activate", accel_m, ord('o'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.action_fo.connect_proxy(self.item_open)

        self.item_save = gtk.MenuItem('Save file')
#        self.item_save.add_accelerator("activate", accel_m, ord('s'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.action_fs.connect_proxy(self.item_save)

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

        # first vidget raw: search butt, entry, combo-box
        s_horiz = gtk.HBox(False, 0)
        box1.pack_start(s_horiz, False, False, 0)
        s_horiz.show()

        self.combo = gtk.combo_box_new_text()
        self.s_entry = gtk.Entry()
#        self.s_entry.set_max_length(50)
        self.s_entry.set_width_chars(50)
        self.s_button = gtk.Button('Search')

        s_horiz.pack_start(self.combo, False, False, 1)
        self.combo.show()
 
        s_horiz.pack_start(self.s_entry, False, False, 1)
        self.s_entry.show()
        
        s_horiz.pack_start(self.s_button, False, False, 1)
        self.s_button.show()

       
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
        
        # third raw: greek-slav buttons
        l_horiz = gtk.HBox(False, 0)
        box1.pack_start(l_horiz, False, False, 0)
        l_horiz.show()

        self.l_button = gtk.Button('Greek')
        l_horiz.pack_start(self.l_button, False, False, 1)

        self.l_button.show()

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

        books_sw = gtk.ScrolledWindow()
        books_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.model = gtk.TreeStore(str, str)
        self.tv = gtk.TreeView(self.model)
        self.selection = self.tv.get_selection()

#        self.modelfilter = self.model.filter_new()
#        self.tv.set_model(self.modelfilter)

        books_sw.add(self.tv)

        self.b_entry = gtk.Entry()
        self.b_entry.show()
#        self.b_entry.connect('key_press_event', self.search_cb)
        
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn("Название книги", cell1, text=0)
        self.column2 = gtk.TreeViewColumn("Code", cell2, text=1)

        self.tv.append_column(self.column)
        self.tv.append_column(self.column2)
#        self.tv.set_search_column(2)

        # hide second column 
        self.column2.set_visible(False)
        
        books_sw.show_all()
        self.tv.show()
        box4.pack_start(books_sw)

        self.tv.grab_focus()

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
        self.note = gtk.Notebook()
        self.note.set_tab_pos(gtk.POS_TOP)
        self.note.show()
        self.note.set_scrollable(True)
        self.show_tabs = True
        self.show_border = True

        # create first page. Todo: make it remember previously
        # closed pages. Have to use some function (load pickle). 
        self.append_pg()

        self.f_select.show()
        self.entry.show()
#        self.entry.connect('key_press_event', self.search_cb)

#        self.textview.show()

#        self.box2.pack_start(self.entry, False, False, 0)


        box5.pack_start(self.f_select, False, False, 0)
        box5.pack_start(self.note, True, True, 0)
        box5.pack_start(self.entry, False, False, 0)

        self.label = gtk.Label() 
        box1.pack_start(self.label, False, False, 0)
        self.label.show()

        self.label.set_text('Checking out flying soucers')

        self.window3.show()


        # current position in text
        self.pos = 0

        # regexp to check if the font is ucs-compatible
        # probably not a good idea, if there is some kind of 'kucs.ttf' out there...
        # well, in that case we'll make an exception.
        self.ucs_patt = re.compile(u'ucs', re.U | re.I)

    def append_pg(self, stl=None):
        # make new page in notebook
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#        textview = gtk.TextView()
        textview = Txt()
        textview.set_editable(False)
        textview.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        if stl:
            textview.style_s = True

#        textbuffer = textview.get_buffer()
        sw.add(textview)
        sw.show()
        textview.show()

#        label = gtk.Label(None)
#        label.show()
        self.note.append_page(sw, None)

        cur_pg = self.note.get_n_pages() - 1
        self.note.set_current_page(cur_pg)

#        cur_pg = self.note.get_cur_page()
        page = self.note.get_nth_page(cur_pg)
        child = page.get_children()[0]

        return [cur_pg, page, child]


    def append_search_pg(self):
        # make new page in notebook
       
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.model_s = gtk.ListStore(str, int, str, str)
        self.tvs = gtk.TreeView(self.model_s)
        self.selection = self.tvs.get_selection()

        self.modelfilter = self.model_s.filter_new()
#        self.modelfilter.set_visible_func(vis, self.small)
        self.tvs.set_model(self.modelfilter)

        sw.add(self.tvs)

        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn("File_path", cell1, text=3)
        self.column2 = gtk.TreeViewColumn("String", cell2, text=2)
        self.tvs.append_column(self.column)
        self.tvs.append_column(self.column2)
        self.tvs.set_search_column(2)
        
        sw.show_all()
        self.tvs.show()

#        label = gtk.Label(None)
#        label.show()
        self.note.append_page(sw, gtk.Label("search res"))

        cur_pg = self.note.get_n_pages() - 1
        self.note.set_current_page(cur_pg)

#        cur_pg = self.note.get_cur_page()
        page = self.note.get_nth_page(cur_pg)
        child = page.get_children()[0]

        return [cur_pg, page, child]

if __name__ == '__main__':
    argv = sys.argv

#    txt_win = Mug(config)
    txt_win = Mug()

    if len(argv) > 1:
        f_path = argv[1]

        fp = codecs.open(f_path, "rb", "cp1251")
        f_lines = fp.readlines()
        fp.close()
        # insert text
        text_ls = []
        txt = ''.join(f_lines)

        txt1 = txt_win.wrapper(txt)

        txt_win.ins_txt(txt1)

    def main():
        gtk.main()
        return 0

    main()

# TODO: make gtk.InfoBar or gtk.Statusbar (minor info)
# also gtk.StatusIcon
# gtk.OptionMenu
# gtk.Paned and VPaned
# gtk.SeparatorMenuItem

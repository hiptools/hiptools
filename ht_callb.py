#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import codecs
import re
import os
import sys
from xml.dom import minidom

import booklst
#import hiptools_g
import hipconv
import ConfigParser
import hipcomment
import write_utf
import options

conv = hipconv.Repl()
brac = hipcomment.Brackets()
Writer = write_utf.write_gen()


class Connect_ind:
    def __init__(self, mode=False):

        # In here we read config file, so every other class
        # (accept in options.py) has to use self.config

        self.config = ConfigParser.ConfigParser()
#        self.conf_path = os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc')
        self.config.read(self.conf_path)

#        # if mode == True - switched to greek, else - to slavonic
#        # mode for search tool
#        if self.config.get('Switches', 'library_greek_s') == 'True':
#            self.mode_s = True
#        elif self.config.get('Switches', 'library_greek_s') == 'False':
#            self.mode_s = False
#        # mode for index (viewer) tool
#        if self.config.get('Switches', 'library_greek_v') == 'True':
#            self.mode_v = True
#        elif self.config.get('Switches', 'library_greek_v') == 'False':
#            self.mode_v = False
#
#        # style for slavonic viewer - slavonic or plain
#        self.style_s = self.config.get('Style', 'default_style')
#        # kill service tags in hip texts like {...}
#        self.br_off = self.config.get('Style', 'brackets_off')
#

        # delete special tags at the beginning of HIP file
        self.del_header = 1
        self.exp_lines = []
#        self.base_dict = {}


        # regexps to find double new-lines and wrap the text
        self.split_parag = re.compile(u'(?:\r?\n){2,}', re.U)
        self.kill_rn = re.compile(u'(?:\r?\n)', re.U)

        # clean up xml tags in greek files (barbaric, fix it!)
        self.html_del = re.compile(r'<.*?>', re.S)

        # current position in text
        self.pos = 0

        # regexp to check if the font is ucs-compatible
        # probably not a good idea, if there is some kind of 'kucs.ttf' out there...
        # well, in that case we'll make an exception.
        self.ucs_patt = re.compile(u'ucs', re.U | re.I)


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

    def sw_mode(self, widget):
        '''callback for slav-greek switch in search and index'''

        # search area
        if widget == self.gr_switch1:
            if self.mode_s:
                self.mode_s = False
                self.gr_switch2.set_label("Слав.")
            else:
                self.mode_s = True
                self.gr_switch2.set_label("Греч.")
            print 'Greek in search:', self.mode_s

        # list area
        elif widget == self.gr_switch2:
            if not self.mode_v:
                self.gr_switch2.set_label("Слав.")

                self.tv.remove_column(self.column_sl1)
                self.tv.remove_column(self.column_sl2)
                self.tv.append_column(self.column_gr1)
                self.tv.append_column(self.column_gr2)

                self.tv.set_model(self.model_gr)

                self.mode_v = True
                self.enc = 'utf-8'

            else:
                self.gr_switch2.set_label("Греч.")

                self.tv.remove_column(self.column_gr1)
                self.tv.remove_column(self.column_gr2)
                self.tv.append_column(self.column_sl1)
                self.tv.append_column(self.column_sl2)

                self.tv.set_model(self.model_sl)
                
                self.mode_v = False
                self.enc = 'cp-1251'

            print 'Greek in index:', self.mode_v
#            self.tv.connect('row-activated', self.key_press)



############Options callbacks####################3
    def opt_wrap(self, widget):
        '''callback for Options menu item'''

        opt_w = options.Opt(self.config)
        # connect buttons
        opt_w.apply_bt.connect('activate', self.apply_op)

        # destroys main programm window. 
#        opt_w.cancel_bt.connect('activate', opt_w.destroy_cb)
        # Try to use main() loop to catch destruct signal?

    def apply_op(self, widget):
        '''callback for Apply button in Options dialog'''

        # write changes to config:
        with open(self.conf_path, 'wb') as configfile:
            self.config.write(configfile)

        # apply to widgets of main programm window:
        # combo-box slav:
        for x in range(len(self.combo_lst)):
            if self.config.get('SearchOptions', 'default_search_group') == self.combo_lst[x]:
                self.combo.set_active(x)
        # checkboxes:
        if self.config.get('SearchOptions', 'diacritics_on') == 'True':
            self.toggle1.set_active(True)
            self.stress_toggle = True 
        else:
            self.toggle1.set_active(False)
            self.stress_toggle = False 

        if self.config.get('SearchOptions', 'case_sensitive') == 'True':
            self.toggle2.set_active(True)
            self.case_sen = True
        else:
            self.toggle2.set_active(False)
            self.case_sen = False
    # TODO: make switch to choose hip-unicode       
################################################
    def open_file(self, item_open):
#        if keyname == "o" and event.state & gtk.gdk.CONTROL_MASK:
        dialog = gtk.FileChooserDialog("Open..", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

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

        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            f_name = dialog.get_filename()

            fp = codecs.open(f_name, "rb", "cp1251")
            lines = fp.readlines()
            fp.close()

            txt1 = self.wrapper(''.join(lines))
            self.get_txt(txt1, False)
            self.proc(txt1)
            self.style_txt()

        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()

    def save_file(self, item_save):
#        if keyname == "s"  and event.state & gtk.gdk.CONTROL_MASK:
        dialog = gtk.FileChooserDialog("Save..", None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        cur_pg = self.note.get_current_page()

        # child widget to current notebook page
        page = self.note.get_nth_page(cur_pg)
        self.textview = page.get_children()[0]

#        if self.textview.mode:
#            dialog.set_current_name('.hip')
#        else:
#            dialog.set_current_name('.txt')

        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            # child widget to current notebook page
            page = self.note.get_nth_page(cur_pg)
            self.textview = page.get_children()[0]
            self.textbuffer = self.textview.get_buffer()

            startiter, enditer = self.textbuffer.get_bounds()
            data = self.textbuffer.get_text(startiter, enditer).decode('utf8')
            Writer.write_line(dialog.get_filename(), data, "w", "cp1251")

        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()

    def wrapper(self, txt):
        ''' find double new-lines and wrap the text'''
        text_ls = []
        parts_ls = self.split_parag.split(txt)
        for part in parts_ls:
            part = self.kill_rn.sub(' ', part)
            text_ls.append(part)
        txt1 = '\n\n'.join(text_ls)

        return txt1

    def check_font(self, font):
        '''Change type of conversion according to chosen font-type'''

        if self.ucs_patt.search(font):
            self.uni = 'ucs'
        elif 'Old Standard' in font or 'Hirmos Ponomar' in font:
            self.uni = 'uni_csl'
        else:
            self.uni = 'uni'

#    def font_cb(self, f_button):
#        '''Callback to font-select dialog'''
#
#        font = f_button.get_font_name()
##        if debug:
##            print font
#
#        self.check_font(font)
#
#        self.sl_font = font
#
#        self.process()
#        self.style_txt()

    def key_press(self, tv, path, column):
        """Callback for Index"""
#        print 'current mode_v', self.mode_v

        model = tv.get_model()

        # expand paths that are not expanded,
        # collaps expanded (which are in exp_lines = expanded lines)
        if not path in self.exp_lines: 
            tv.expand_row(path, False)
            self.exp_lines.append(path)
        else:
            tv.collapse_row(path)
            self.exp_lines.remove(path)

        iter_cur = model.get_iter(path)

        # iter cur points to file, not directory
        if not model.iter_has_child(iter_cur):
            dir_name_x = ""
            dir_out = []
            iter_par_c = iter_cur
            f_name = model.get_value(iter_cur, 1)

            while True:
                iter_par_p = model.iter_parent(iter_par_c)
                dir_name_p = model.get_value(iter_par_p, 1)
                dir_out.append(dir_name_p)
                iter_par_c = iter_par_p
                if not model.iter_parent(iter_par_p):
                    break

            dir_out.reverse()

            if self.mode_v:
                lib_p = self.config.get('LibraryPaths', 'gr_path')
            else:
                lib_p = self.config.get('LibraryPaths', 'sl_path')

            f_path_list = [lib_p, '/']
            f_path_list.extend(dir_out)
            f_path_list.append(f_name)
            f_path = ''.join(f_path_list)

            print 'run', f_path
#            print 'enc', self.enc
            fp = codecs.open(f_path, "rb", self.enc)

            f_lines = fp.readlines()
            fp.close()
            
            if self.mode_v:
                xmldoc = minidom.parseString(f_lines[1] + '</document>')
                xml_nodes = xmldoc.getElementsByTagName('document')
                for item in xml_nodes:
                    t_name = item.getAttribute('title') 
                    break

            else:
            # aweful crutch: delete service tags in the beginning of the file
            # DO Something!
                if self.del_header:
                    for z in range(10):
                        if "<::" in f_lines[z]:
                            f_lines.pop(f_lines.index(f_lines[z]))
                t_name = model.get_value(iter_cur, 0)

            # create window to output selected text
#            txt_win = Show_text(self.mode)
#            txt_win.path1 = f_path
#
#            iter_par = self.model.iter_parent(iter_cur)
#            title = ' / '.join([self.model.get_value(iter_par, 0), t_name])
#
#            txt_win.window3.set_title(title)

 
            # insert text
            text_ls = []
            txt = ''.join(f_lines)

            parts_ls = self.split_parag.split(txt)
            for part in parts_ls:
                part = self.kill_rn.sub(' ', part)
                text_ls.append(part)
            txt1 = '\n\n'.join(text_ls)

            self.get_txt(txt1)
            self.proc()
            self.style_txt()

    def note_cb(self, widget, event):
        """Callback for notebook wid"""

        keyname = gtk.gdk.keyval_name(event.keyval)
#        print 'key', keyname, 'was pressed', event.keyval
        if keyname == "d" or keyname == "Cyrillic_ve" and event.state & gtk.gdk.CONTROL_MASK:

            cur_pg = self.note.get_current_page()

            # child widget to current notebook page
            page = self.note.get_nth_page(cur_pg)
            self.textview = page.get_children()[0]
            self.textbuffer = self.textview.get_buffer()

            # get visible area, get top line to return to after reload 
            temp_iter = self.textview.get_iter_at_location(0, self.textview.get_visible_rect()[1])
            self.pos = temp_iter.get_line()

            # if false change 'plain' to true and vsv
            if not self.textview.mode:
                self.textview.mode = True
            else:
                self.textview.mode = False

            if self.textview.style_s:
                pr_s.get_txt()
                pr_s.proc()
                pr_s.style_txt()
            else:
                pr_i.get_txt()
                pr_i.proc()
                pr_i.style_txt()

        if keyname == "t" or keyname == "Cyrillic_ie" and event.state & gtk.gdk.CONTROL_MASK:
                
            self.append_pg()
            cur_pg = self.note.get_n_pages() - 1
            self.note.set_current_page(cur_pg)

        if keyname == "w" or keyname == "Cyrillic_tse" and event.state & gtk.gdk.CONTROL_MASK:

            p_num = self.note.get_n_pages()
            if p_num > 1:
                self.note.remove_page(self.note.get_current_page())
                self.note.queue_draw_area(0,0,-1,-1)
            else:
                self.note.remove_page(self.note.get_current_page())
                self.note.queue_draw_area(0,0,-1,-1)
                self.append_pg()

        if keyname == "Tab" or keyname == "n" or keyname == "Cyrillic_te" and event.state & gtk.gdk.CONTROL_MASK:
            cur_pg = self.note.get_current_page()
            if cur_pg + 1 < self.note.get_n_pages():
                self.note.next_page()
            else:
                self.note.set_current_page(0)

        if keyname == "p" or keyname == "Cyrillic_ze" and event.state & gtk.gdk.CONTROL_MASK:
            cur_pg = self.note.get_current_page()
            if cur_pg > 0:
                self.note.prev_page()
            else:
                self.note.set_current_page(-1)

           
class Connect_sear:
    """ Callbacks and other methods for search dialog """

    def __init__(self):

        self.comm_lst = []
        self.pointer = 0

        self.combo_lst = ['Богослужебные', 'Свящ. Писание', 'Все книги', 'Четьи книги', 'Акафисты', 'Алфавит', 'Апостол', 'Часослов', 'Треодь цветная', 'Добротолюбие', 'Экзапостилларии', 'Евангелия', 'Ифика', 'Каноны', 'Молитвы на молебнах', 'Общая минея', 'Октоих', 'Пролог', 'Книга правил', 'Псалтырь', 'Треодь постная', 'Служебник', 'Типикон', 'Требник', 'Ветхий Завет', 'Минеи месячные']

        self.dicti = {'Богослужебные': ['akf','chs','ctr','kan','mol','obs','okt','psa','ptr','slu','tip','trb','min/aug','min/apr','min/dec','min/feb','min/jan','min/jul','min/jun','min/mar','min/may','min/nov','min/okt','min/sep'], 
        'Свящ. Писание': ['eua', 'aps', 'vzv'], 
        'Все книги': ['akf', 'alf', 'aps', 'chs', 'ctr', 'dbr', 'eua', 'ifi', 'kan', 'mol', 'obs', 'okt', 'prl', 'prv', 'psa', 'ptr', 'slu', 'tip', 'trb', 'vzv', 'min/aug','min/apr','min/dec','min/feb','min/jan','min/jul','min/jun','min/mar','min/may','min/nov','min/okt','min/sep'],
        'Четьи книги': ['alf', 'aps', 'dbr', 'eua', 'ifi', 'prl', 'prv', 'vzv'],        'Акафисты': ['akf'], 'Алфавит': ['alf'], 'Апостол': ['aps'], 'Часослов': ['chs'], 'Треодь цветная': ['ctr'], 'Добротолюбие': ['dbr'], 'Евангелия': ['eua'], 'Ифика': ['ifi'], 'Каноны': ['kan'], 'Молитвы на молебнах': ['mol'], 'Общая минея': ['obs'], 'Октоих': ['okt'], 'Пролог': ['prl'], 'Книга правил': ['prv'], 'Псалтырь': ['psa'], 'Треодь постная': ['ptr'], 'Служебник': ['slu'], 'Типикон': ['tip'], 'Требник': ['trb'], 'Ветхий Завет': ['vzv'], 'Минеи месячные': ['min/aug','min/apr','min/dec','min/feb','min/jan','min/jul','min/jun','min/mar','min/may','min/nov','min/okt','min/sep']}
 

    def case_switch(self, widget, data=None):

       if widget.get_active():
           self.case_sen = True
       else:
           self.case_sen = False
        
    def choose(self, widget):
        '''Chooses the books group'''

        get_name = widget.get_active_text() 

        for name in self.dicti:
            if get_name == name:
                self.books = self.dicti[name]

    def count_files(self, books):

        file_count = 0

        for book in books:
#        book = ''.join(["/usr/local/lib/hip-tools/hiplib/", book])

#            book = os.path.join(os.getcwd(), "hiplib", book)
            book = os.path.join(self.lib_path,  book)

 
            for file in os.listdir(book):
                if file.endswith('hip') or file.endswith('xml'):
                    file_count += 1

#        print file_count

        return file_count

    def f_search(self, books=None, s_word=None):
        '''main search function'''

        # number of 'hip' files in given group of books
        num_files = self.count_files(books)
        cur_file = 0

        res = []
        global count
        count = 0
        word = s_word.decode('utf-8')
#        word = word.lower()

                
        if word.startswith('\"'):
            word = word.replace('\"', '')
            patt = "\s" + word + "\s"
            patt = patt.decode('utf8')

#            print 'patt', patt
            regex = re.compile(patt, re.U)
                
        elif word.endswith('*'):
#        print 'w*'
            word = word.replace('*', '')
#        patt = word + ".*\s"
            patt = "\s" + word + ".*?\s"
#        print patt
            regex = re.compile(patt, re.U)

        elif word.startswith('*'):
            word = word.replace('*', '')
            patt = "\s\w+?" + word + "\s"
#        word = '\s\w+?гул[\s\n\.,;:!\?@"\']'
#        word = '\s\w+?[\s\n\.,;:!\?@"\']'
#        print patt
            regex = re.compile(patt, re.U)

        else:
            patt = word
            if not self.case_sen:
                regex = re.compile(patt, re.U | re.I)
            else:
                regex = re.compile(patt, re.U)

        for j in books:
#        j = ''.join(["/usr/local/lib/hip-tools/hiplib/", j])
            j = os.path.join(os.getcwd(), "hiplib", j)

            f_names = os.listdir(j)

            for i in f_names:
                if i.endswith('.hip'):
                    cur_file += 1
#                    perc = round(float(cur_file)/float(num_files), 1)

                    # calculate percent of work done so far
                    perc = float(cur_file)/float(num_files)
                    self.pr_bar.set_fraction(perc)
                    # these are nesessary to steal control from gtk main loop
                    # else progrees bar wont move untill job's done
                    while gtk.events_pending():
                        gtk.main_iteration()

                    file_path = os.path.join(j, i)
#                    print "file_path: ", file_path
                    fp = codecs.open(file_path, "rb", "cp1251")
                    f_lines = fp.readlines()
                    fp.close()

                    for str_num in range(len(f_lines)):
                        line = f_lines[str_num]

                        # clean all apostrophs (stresses) from searched text
                        if self.stress_toggle:
                            line = line.replace('\'', '')
                            line = line.replace('`', '')
                            line = line.replace('^', '')
                        if '%<' or '%>' in line:
#                            print line
                            line = line.replace('%<','')
                            line = line.replace('%>', '')
                        if regex.search(line):
                            count += 1
                            res.append((file_path, str_num, f_lines[str_num]))

        return res

    def ins(self, res):
        
        for i in res:
            iter = self.model_s.append()
            self.model_s.set(iter, 0, i[0])
            self.model_s.set(iter, 1, i[1])
            self.model_s.set(iter, 2, i[2])
            path_s_u = self.path2name(i[0]).decode('utf8')[:40]
            self.model_s.set(iter, 3, path_s_u)
#            self.model.set(iter, 3, path2name(i[0]))

    def manager_keys(self, widget, event):
        '''Bindings for main window'''

#        if event.state & gtk.gdk.CONTROL_MASK:
        keyname = gtk.gdk.keyval_name(event.keyval)

        if keyname == "Return":
#            print 'Return'
            self.search_it()

        if keyname == "Up":
            print 'Up'
#            if self.comm_lst:

            self.pointer += 1
            print 'pointer', self.pointer
            if self.pointer <= len(self.comm_lst):
                self.entry.set_text(self.comm_lst[len(self.comm_lst) - self.pointer])
            else:
                self.pointer == 1
                self.entry.set_text(self.comm_lst[len(self.comm_lst) - self.pointer])
 
        if keyname == "Down":
            print 'Down'

    def on_click(self, widget, iter, path):
        ''' callback, row in TreeView clicked '''

        selection = widget.get_selection()
        model, path = selection.get_selected_rows()
        # get iter in Viewer (found entries)
        iter_v = model.get_iter(path[0])
        file_path = model.get_value(iter_v, 0) 

        self.found_raw = model.get_value(iter_v, 1)    

        try:
            fp = codecs.open(file_path, "rb", "cp1251")
            f_lines = fp.readlines()
            fp.close()
        except IOError:
            print 'no such file found'

        txt_ins = ''.join(f_lines)

#        print txt_ins.decode('utf8')

        # create window to output selected text
#        p_list = self.append_pg()
#        txt_win.window3.set_title(face.path2name(file_path))

#        n_i.process(txt_ins)
#        self.style_txt()

        pr_s.get_txt(txt_ins, True)
        pr_s.proc()
        pr_s.style_txt()



    def path2name(self, f_path):
        ''' Convert given path to description string '''

        self.path_ls = []

        while(f_path):
            f_path, tail = os.path.split(f_path)
            if tail == 'hiplib':
                break
            self.path_ls.insert(0, tail)
                    
        self.desc_str = []
        self.walker(self.book_lst)
        res_str = ' / '.join(self.desc_str)

        return res_str

    def search_it(self, button=None):
        '''Main search interself'''

        self.s_word = self.s_entry.get_text()
        self.comm_lst.append(self.s_word)
#        print self.comm_lst

        # res - list of tuples, containing path, line_num, text
        res = self.f_search(self.books, self.s_word)
        if res:
            chars = 0

            # this piece should probably go to separate method
            # because it's used also in Connect_ind
            cur_pg = self.note.get_current_page()
            page = self.note.get_nth_page(cur_pg)
            self.textview = page.get_children()[0]
            if not isinstance(self.textview, gtk.TreeView):
                self.textbuffer = self.textview.get_buffer()
                chars = self.textbuffer.get_char_count()
            else:
                chars = 1

#            self.textbuffer = self.textview.get_buffer()

            if not chars:
                chars = self.textbuffer.get_char_count()
            if chars:
                p_list = self.append_search_pg()
                self.ins(res)
                p_list[2].connect('row-activated', self.on_click)
#                self.tvs.connect('row-activated', self.on_click)

            else:
                self.note.remove_page(cur_pg)
                self.note.queue_draw_area(0,0,-1,-1)
                p_list = self.append_search_pg()
                self.ins(res)
                p_list[2].connect('row-activated', self.on_click)

            cur_pg = self.note.get_n_pages() - 1
            self.note.set_current_page(cur_pg)

            self.label.set_text("Найдено " + str(count) + " совпадений")
#            self.label.set_justify(gtk.JUSTIFY_LEFT)

        else:
            print 'Didn\'t find anything, sorry.'
            Popup("Ничего не найдено")

    def stress(self, widget, data=None):

       if widget.get_active():
           self.stress_toggle = True 
       else:
           self.stress_toggle = False


    def walker(self, book_lst):
        '''recursive funstion for parsing through book list'''

        for book in book_lst:
            if self.path_ls:
                if self.path_ls[0] in book[0]:
                    out = self.path_ls.pop(0)
                    self.desc_str.append(book[1])
                    if book[2]:
                        self.walker(book[2])
            else:
                break

#    def wrap_search(self):
#        """ main method of the class """
#
#        for i in self.combo_lst: 
#            self.combo.append_text(i.strip())
#
#        self.combo.connect("changed", self.choose)       
#
#        for x in range(len(self.combo_lst)):
#            if self.config.get('SearchOptions', 'default_search_group') == self.combo_lst[x]:
#                self.combo.set_active(x)
#
#        # define checkboxes callbacks
#        self.toggle1.connect("toggled", self.stress)
#        self.toggle2.connect("toggled", self.case_switch)       
#
#        if self.config.get('SearchOptions', 'case_sensitive') == 'True':
#            self.toggle2.set_active(True)
#            self.case_sen = True
#        else:
#            self.toggle2.set_active(False)
#            self.case_sen = False
#
#        # check config for paramater
#        if self.config.get('SearchOptions', 'diacritics_on') == 'True':
#            self.toggle1.set_active(True)
#            self.stress_toggle = True
#        else:
#            self.toggle1.set_active(False)
#            self.stress_toggle = False
#
#        self.s_entry.connect('key_press_event', self.manager_keys)
# 
class Process:
    """ Make new tab, insert text, stylize 

    """
    def __init__(self):
        pass

    def scrolled(self, textv, steps, count, ext):
       self.scr = steps 
       # TODO: search res when scrolled give 4 args (TreeView)

    def get_txt(self, new_txt=None, stl=None):
        chars = 0
        cur_pg = self.note.get_current_page()
        # child widget to current notebook page
        page = self.note.get_nth_page(cur_pg)
        self.textview = page.get_children()[0]

        # current page's content is not search res treeview, but regular textview
        if not isinstance(self.textview, gtk.TreeView):
            self.textbuffer = self.textview.get_buffer()
            self.textview.connect('move-cursor', self.scrolled)

            chars = self.textbuffer.get_char_count()
        else:
            chars = 1
#        if name: 
#        self.note.set_tab_label_text(page, name)

        # call from index or search, not reload (ctl-d or ctl-r)
        if new_txt:
            # Chars - a trigger. If we got TreeView as a child, 
            # or if there's some text in TextView, we switch chars = 1 and make a new tab

            if not chars:
                chars = self.textbuffer.get_char_count()

            # Some text in old tab. Have to draw new.
            else:
                # style for search (green tag...)
                if stl:
                    self.append_pg(stl)
                else:
                    self.append_pg()

                cur_pg = self.note.get_n_pages() - 1
                self.note.set_current_page(cur_pg)

                page = self.note.get_nth_page(cur_pg)
                self.textview = page.get_children()[0]
                # get buffer of last page!
                self.textbuffer = self.textview.get_buffer()

            self.base_txt = new_txt
            self.textview.base_txt = self.base_txt
            self.textview.mode = self.plain

        else:
            startiter, enditer = self.textbuffer.get_bounds()

            # self.plain == True if we must convert to plain text
            # False if we have to make it into slavic
            # self.plain is switched in note_cb callback every time
            # we have to convert the contents (ctl-d)

            if not self.textview.mode:
                self.base_txt = self.textbuffer.get_text(startiter, enditer)
            else:
                self.base_txt = self.textview.base_txt

    def proc(self, new_txt=None):

        # if need to convert (plain to slavic)
        if not self.textview.mode:
            # parse comments. If to slavic text, wipe comments
            conv_txt = brac.repl_brac(self.base_txt, self.brackets_off)[0]
            # convert to slavonic typeset
            self.check_font(self.textview.sl_font)
#            print 'sl_font', self.textview.sl_font
            conv_txt = conv(conv_txt, self.uni)
            
            self.textbuffer.set_text(conv_txt)
            self.tag_table = self.textbuffer.get_tag_table()

            # have to 'remember' last used font.
            if self.textview.sl_font == self.textview.plain_font:
                self.textview.sl_font = self.textview.sl_font_prev

            # Here's patch by S. Maryasin, makes %<L%>etters red
            # преобразуем "костыльные" метки \1 и \2 в киноварь
            red = gtk.TextTag()
            self.tag_table.add(red)
            red.set_property("foreground", "red")
            i = self.textbuffer.get_start_iter()
            while i.get_char() != '\0':
                if i.get_char() == '\1': # начало выделения, %<
                    i.forward_char()
                    self.textbuffer.backspace(i, False, True) # удаляем метку
                    start = i.get_offset() # запоминаем позицию
                if i.get_char() == '\2': # конец выделения, %>
                    i.forward_char()
                    self.textbuffer.backspace(i, False, True)
                    self.textbuffer.apply_tag(red, self.textbuffer.get_iter_at_offset(start), i)
                i.forward_char() # next i
            # end of patch. See also changes in ucs8conv

        else:
            self.tag_table = self.textbuffer.get_tag_table()
            self.textbuffer.set_text(self.base_txt)
            self.textview.sl_font_prev = self.textview.sl_font
            self.textview.sl_font = self.textview.plain_font

        self.my_text = gtk.TextTag()
        self.tag_table.add(self.my_text)
#        self.style_txt()
        self.f_select.set_font_name(self.textview.sl_font)

        self.textview.place_cursor_onscreen()

    def style_txt(self):
        self.my_text.set_property("font", self.textview.sl_font)
        self.my_text.set_property("wrap-mode", gtk.WRAP_WORD)
#        self.my_text.set_property("wrap-mode", gtk.WRAP_CHAR)
        
        startiter, enditer = self.textbuffer.get_bounds()
        self.textbuffer.apply_tag(self.my_text, startiter, enditer)

        if self.pos:
            # put cursor at the start of the page
            zero_iter = self.textbuffer.get_iter_at_line(self.pos)
            zero_mark = self.textbuffer.create_mark(None, zero_iter)
#            self.textbuffer.place_cursor(zero_iter)
            self.textview.scroll_to_mark(zero_mark, 0.0, True, 0.0, 0.0)
#            self.textview.grab_focus()
        else:
            self.textbuffer.place_cursor(startiter)

#TODO: make hidden comments, so that one doesnt have to reload the page to see them

class Process_s(Process):
    def __init__(self):
        Process.__init__(self)
        self.scr = 0

    def scrolled(self, textv, steps, count, ext):
       self.scr = steps 
 
    def style_txt(self):
        # Have to change only this method, everything else is from hipview
        self.my_text.set_property("font", self.textview.sl_font)
        self.my_text.set_property("wrap-mode", gtk.WRAP_WORD)
        
        startiter, enditer = self.textbuffer.get_bounds()
        self.textbuffer.apply_tag(self.my_text, startiter, enditer)

        cur_iter = self.textbuffer.get_iter_at_line(self.pos)

#        if not self.pos:
#            cur_iter = self.textbuffer.get_iter_at_line(self.pos)
#        else:
#            # put cursor at the start of the page
#            self.textbuffer.place_cursor(startiter)
#            cur_iter = startiter

#        iter1 = self.textbuffer.get_iter_at_line_offset(face.new_win.found_raw, 0)
#        iter2 = self.textbuffer.get_iter_at_line_offset(face.new_win.found_raw + 1, 0)

        iter1 = self.textbuffer.get_iter_at_line_offset(conn_s.found_raw, 0)
        iter2 = self.textbuffer.get_iter_at_line_offset(conn_s.found_raw + 1, 0)

        self.found_text = gtk.TextTag()
        self.found_text.set_property("background", "green")
        self.tag_table.add(self.found_text)
        self.textbuffer.apply_tag(self.found_text, iter1, iter2)

#        if isinstance(widget, gtk.TreeView):

        if not self.scr:
            self.textbuffer.place_cursor(iter1)
            one = self.textbuffer.create_mark(None, iter1)
            self.textview.scroll_to_mark(one, 0.0, True, 0.0, 0.0)
#            self.textview.scroll_to_iter(iter1, 0.0, True, 0.0, 0.0)
            self.textview.grab_focus()
        else:
            self.textbuffer.place_cursor(cur_iter)
            cur_mark = self.textbuffer.create_mark(None, cur_iter)
            self.textview.scroll_to_mark(cur_mark, 0.0, True, 0.0, 0.0)
            self.textview.grab_focus()
#            print 'scrolled', self.scr

        self.scr = 0


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


# TODO: probably invoking other objects from Connect_ind()
# with config object as an arg - is a good idea
# on the other hand - cli version of index would need separate
# objects to import





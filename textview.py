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

        self.mode = Mode

        self.plain = True

        self.bmarks = os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'bookmarks')

        # path in greek_lib (or hip_lib) to find greek/slavonic parallel
        # the value is appointed in grindex (gr_search) to an existing gr_view.Text istance
        self.path1 = ""
        
#        print self.paral

        # original plain text
        self.base_txt = ""
        self.window3 = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window3.set_resizable(True)
        self.window3.set_border_width(10)
        self.window3.set_size_request(850, 400)

        self.window3.set_border_width(0)
#        self.window3.connect('key_press_event', self.redraw_cb)

        if __name__ == '__main__':
            self.window3.connect('destroy', destroy_cb)

        # main box
        box1 = gtk.VBox(False, 0)
        self.window3.add(box1)
        box1.show()

#        hbox1 =  gtk.HBox(False, 0)
#        hbox1.set_border_width(3)

#        box1.pack_start(hbox1, True, True, 0)
#        hbox1.show()

        self.panes = gtk.HPaned()

#        tree_box1 = gtk.VBox(False, 0)
#        tree_box1.set_border_width(3)
#        tree_box1.show()

        box2 = gtk.VBox(False, 3)
        box2.set_border_width(3)
        box2.show()

        box_combo = gtk.HBox(False, 3)
        box_combo.set_border_width(3)
        box_combo.show()
        box1.pack_start(box_combo, False, False, 0)
        

#        hbox1.pack_start(tree_box1, False, False, 1)
#        hbox1.pack_start(box2, True, True, 1)
        
#        tree_box1.set_size_request(200, 400)

        swt = gtk.ScrolledWindow()
        swt.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.model = gtk.TreeStore(str, str)
        self.tv = gtk.TreeView(self.model)
        self.selection = self.tv.get_selection()
        self.tv.connect('row-activated', self.tree_cb)

        swt.add(self.tv)

#        self.label = gtk.Label() 
        
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn("Содержание", cell1, text=0)
        self.column2 = gtk.TreeViewColumn("Code", cell2, text=1)

        self.tv.append_column(self.column)
        self.tv.append_column(self.column2)

        # hide second column 
        self.column2.set_visible(False)
        
        swt.show_all()
        self.tv.show()

#        tree_box1.pack_start(sw)


        self.f_select = gtk.FontButton(fontname=None)
        self.f_select.connect('font-set', self.font_cb)

        self.combo = gtk.combo_box_new_text()
        self.combo.connect("changed", self.choose)       

#        self.check1 = gtk.CheckButton("вкл. юникод")
#        self.check1.connect("toggled", self.uni_out)

        self.entry = gtk.Entry()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.connect('key_press_event', self.redraw_cb)
        self.textview = gtk.TextView()
        self.textview.set_editable(False)

        self.textbuffer = self.textview.get_buffer()
#        self.iter = gtk.TextIter(self.textbuffer)
        sw.add(self.textview)
        sw.show()
        self.f_select.show()
        self.combo.show()

        try:
            fp = codecs.open(self.bmarks, "rb", "utf-8")
            lines = fp.readlines()
            fp.close()
            for ln in lines:
                self.combo.append_text(ln)
        except IOError:
            print 'can not open bookmarks file at', self.bmarks



#        self.check1.show()
        self.entry.show()
        self.entry.connect('key_press_event', self.search_cb)

        self.textview.show()

        box_combo.pack_start(self.f_select, False, False, 0)
        box_combo.pack_start(self.combo, True, True, 0)
        box1.pack_start(self.panes, True, True, 0)
        box1.pack_start(self.entry, False, False, 0)
        self.panes.show()
 
        self.panes.pack1(swt, True, False)
        self.panes.pack2(sw, True, False)
        self.panes.set_position(150)

#        box2.pack_start(self.f_select, False, False, 0)
#        box2.pack_start(self.check1, False, False, 0)
#        box2.pack_start(sw)
#        box2.pack_start(self.entry, False, False, 0)

        self.window3.show()
        self.textview.grab_focus()

        # current position in text
        self.pos = 0

        # regexp to check if the font is ucs-compatible
        # probably not a good idea, if there is some kind of 'kucs.ttf' out there...
        # well, in that case we'll make an exception.
        self.ucs_patt = re.compile(u'ucs', re.U | re.I)

#        self.config = hip_config.Service(".hiptools.config")
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc'))

        # default font
        self.gr_font = self.config.get('Fonts', 'gr_font')
        self.sl_font = self.config.get('Fonts', 'sl_font')
        self.sl_font_prev = ''
        self.gr_font_prev = ''
        self.plain_font = 'Tahoma 16'
        self.sl_plain_font = 'Tahoma 16'
        self.gr_plain_font = 'Tahoma 16'

        if not self.mode:
            self.check_font(self.sl_font)

            if self.config.get('Style', 'default_style') == 'slavonic':
                self.plain = False
            elif self.config.get('Style', 'default_style') == 'plain':
                self.plain = True
        else:
            self.plain = False

        if self.config.get('Style', 'brackets_off') == 'True':
            self.brackets_off = True
        else:
            self.brackets_off = False

        # regexps to find double new-lines and wrap the text
        self.split_parag = re.compile(u'(?:\r?\n){2,}', re.U)
        self.kill_rn = re.compile(u'(?:\r?\n)', re.U)

        self.reg_r = re.compile(u'([%|#]<)(.+?)([%|#]>)', re.U)
#        self.reg_r = re.compile(u'(%<)(.+?)(%>)', re.U)
        self.reg_n = re.compile(u'([0-9]+)', re.U)

        self.html_del = re.compile(r'<.*?>', re.S)

        
    def check_font(self, font):
        '''Change type of conversion according to chosen font-type'''

        if self.ucs_patt.search(font):
            self.uni = 'ucs'
            print 'font', font
        elif 'Old Standard' in font or 'Hirmos Ponomar' in font:
            self.uni = 'uni_csl'
        else:
            self.uni = 'uni'

    def choose(self, widget):
        '''callback for combo box (bookmarks)'''

        get_name = widget.get_active_text().strip()
        bookm, num = get_name.split()
        print bookm, num
        txt_this = self.xml_open(bookm)

        self.path1 = bookm
        self.ins_txt_gr(txt_this)
#        print len(txt_this)

        bm_iter = self.textbuffer.get_iter_at_line(int(num))
#        print 'iter at', bm_iter.get_line()
        tmp_mk = self.textbuffer.create_mark(None, bm_iter, True)

#        self.textview.scroll_to_iter(bm_iter, 0.0, True, 0.0, 0.0)
        self.textview.scroll_to_mark(tmp_mk, 0.0, True, 0.0, 0.0)
        self.textbuffer.place_cursor(bm_iter)

    def tree_cb(self, tv, path, column):
        '''Callback for treeview, the "Contents" '''

        iter_cur = self.model.get_iter(path)
#        f_name = self.model.get_value(iter_cur, 1)
        val = self.model.get_value(iter_cur, 1)

        print val

        cur_mark = self.textbuffer.get_mark(val)
#        print cur_mark
        self.textview.scroll_to_mark(cur_mark, 0.0, True, 0.0, 0.0)
#            cur_iter = self.textbuffer.get_iter_at_line(self.pos)
        cur_iter = self.textbuffer.get_iter_at_mark(cur_mark)
        self.textbuffer.place_cursor(cur_iter)


#
#        # expand or collapse rows
#        if not path in self.exp_lines: 
#            tv.expand_row(path, False)
#            self.exp_lines.append(path)
#        else:
#            tv.collapse_row(path)
#            self.exp_lines.remove(path)
#
#        iter_cur = self.model.get_iter(path)
#
#        if not self.model.iter_has_child(iter_cur):
#            dir_name_x = ""
#            dir_out = []
#            iter_par_c = iter_cur
#            f_name = self.model.get_value(iter_cur, 1)
#
##            print self.model.get_value(iter_par_c, 1)
#
#            while True:
#                iter_par_p = self.model.iter_parent(iter_par_c)
#                dir_name_p = self.model.get_value(iter_par_p, 1)
#                dir_out.append(dir_name_p)
#                iter_par_c = iter_par_p
#                if not self.model.iter_parent(iter_par_p):
#                    break
#
#            dir_out.reverse()
#            f_path_list = [self.lib_path, '/']
#            f_path_list.extend(dir_out)
#            f_path_list.append(f_name)
#            f_path = ''.join(f_path_list)
#
#            print 'run', f_path
##            fp = codecs.open(f_path, "rb", self.enc)
#
##            f_lines = fp.readlines()
##            fp.close()
#
#            if self.mode:
#                t_name = ""
#                tree = ET.parse(f_path)
#                root = tree.getroot()
#                res = []
#                f_lines = []
#
##        for bk in root.iter('book'):
##        cnt = 0
#
##        for child in root:
##            print child.tag, child.attrib        
#                for bk in root.iter('span'):
#
##        for bk in root.iter('p'):
#                    for sec in bk.iter('span'):
#                        tit = sec.find('title')
#                        if tit: 
#                            print 'title', tit[0][0].text
#                            t_name = tit[0][0].text
#                        else:
#                            print 'no title'
#
#                        print sec.text
#                        f_lines.append(sec.text)
#
#            else:
#            # aweful crutch: delete service tags in the beginning of the file
#            # DO Something!
#                if self.del_header:
#                    for z in range(10):
#                        if "<::" in f_lines[z]:
#                            f_lines.pop(f_lines.index(f_lines[z]))
#                t_name = self.model.get_value(iter_cur, 0)
#
#
#            # create window to output selected text
#            txt_win = Show_text(self.mode)
#            txt_win.path1 = f_path
#
#            iter_par = self.model.iter_parent(iter_cur)
#            title = ' / '.join([self.model.get_value(iter_par, 0), t_name])
#
#            txt_win.window3.set_title(title)
#
#            # insert text
#            text_ls = []
#            txt = ''.join(f_lines)
#
#            parts_ls = self.split_parag.split(txt)
#            for part in parts_ls:
#                part = self.kill_rn.sub(' ', part)
#                text_ls.append(part)
#            txt1 = '\n\n'.join(text_ls)
#
#######            import pdb; pdb.set_trace()
#            if self.mode:
##                txt = self.html_del.sub('', txt)
#                txt_win.ins_txt_gr(f_lines)
#            else:
#                txt_win.ins_txt_hip(txt1)
##            txt_win.style_txt()
#
#

    def font_cb(self, f_button):
        '''Callback to font-select dialog'''

        font = f_button.get_font_name()
#        if debug:
#            print font
        if not self.mode:
            self.check_font(font)
            self.sl_font = font
            self.ins_txt_hip()
        else:
            self.gr_font = font
            self.ins_txt_gr()

        self.style_txt()

    def ins_txt_hip(self, new_txt=None):
            
        self.tag_table = self.textbuffer.get_tag_table()

        if new_txt:
            self.base_txt = new_txt
        if not self.plain: 
            
            self.base_txt = self.reg_n.sub("#<\\1#>", self.base_txt)

            # parse comments. If to slavic text, wipe comments
            conv_txt = brac.repl_brac(self.base_txt, self.brackets_off)[0]
            # convert to slavonic typeset
            print "unicode-ucs selector:", self.uni
            conv_txt = conv(conv_txt, self.uni)
#            self.textbuffer.set_text(conv_txt)

            # have to 'remember' last used font.
            if self.sl_font == self.plain_font:
                self.sl_font = self.sl_font_prev

            # check for %<.*%> tags (red ink)
            if self.reg_r.search(conv_txt):
                res = self.parse_red(conv_txt)
                self.textbuffer.set_text(self.text)

                for tg in res:
                    self.tag_table.add(tg[0])
                    st = self.textbuffer.get_iter_at_offset(tg[1])
                    en = self.textbuffer.get_iter_at_offset(tg[2])
                    self.textbuffer.apply_tag(tg[0], st, en)
#                    tg[0].set_priority(self.tag_table.get_size() - 1)
            else:
                self.textbuffer.set_text(conv_txt)

        else:
            self.textbuffer.set_text(self.base_txt)
            self.sl_font_prev = self.sl_font
            self.sl_font = self.plain_font

#        import pdb; pdb.set_trace()
        self.my_text = gtk.TextTag()
        self.tag_table.add(self.my_text)
        self.style_txt()  
        self.f_select.set_font_name(self.sl_font)

#        self.textview.scroll_to_iter(self.textbuffer.get_start_iter(), 0.0, True, 0.0, 0.0)
        self.textview.place_cursor_onscreen()

    def ins_txt_gr(self, f_lines=None):

#        if new_txt:
#            self.base_txt = new_txt
        if not self.plain: 

            # parse comments. If 2d argument True, wipe comments
#            conv_txt = brac.repl_brac(self.base_txt, True)[0]

#            conv_txt = brac.repl_brac(self.base_txt, self.brackets_off)[0]

            # cleanup all xml tags (untill they are shown correctly)
#            conv_txt = self.html_del.sub('', conv_txt)

            # convert to slavonic typeset
#            conv_txt = conv(conv_txt, self.uni)
#            conv_txt = conv(self.base_txt, self.uni)

#            self.textbuffer.set_text(conv_txt)
            if f_lines:
                st, end = self.textbuffer.get_bounds()
                self.textbuffer.delete(st, end)
                for i in range(len(f_lines)):
                    # insert line (paragraph) into TextView buffer. 
                    # have to be filter here - only allowed tags get through
#                    self.textbuffer.insert(self.textbuffer.get_end_iter(),f_lines[i][0])
                    self.textbuffer.insert(self.textbuffer.get_end_iter(),f_lines[i])

                    # set mark at the end of the paragraph
#                    if f_lines[i][1] and not i == len(f_lines) - 1:
                    if f_lines[i] and not i == len(f_lines) - 1:
                        self.textbuffer.create_mark(str(i), self.textbuffer.get_end_iter(), True)
#                self.mark = self.buffer.create_mark("End",self.buffer.get_end_iter(), False )

                        # fill in TreeView (side panel with 'Contents' of the page)
                        citer = self.model.append(None)
                        self.model.set(citer, 0, u'Часть ' + str(i+1))
#                    self.model.set(citer, 1, str(i+1))
                        self.model.set(citer, 1, str(i))

            # have to 'remember' last used font.
            if self.gr_font == self.plain_font:
                self.gr_font = self.gr_font_prev
        else:
            self.textbuffer.set_text(self.base_txt)
            self.gr_font_prev = self.gr_font
            self.gr_font = self.plain_font

        self.tag_table_gr = self.textbuffer.get_tag_table()
        self.my_text_gr = gtk.TextTag()
        self.tag_table_gr.add(self.my_text_gr)
        self.style_txt_gr()  
        self.f_select.set_font_name(self.gr_font)

#        while self.textbuffer.get_mark(str(cnt)):
#            marks_l.append(self.textbuffer.get_mark(str(cnt)))
#            cnt += 1
#            print 'count', cnt


           
    def parse_red(self, string):

        #ln = len(\\1)
        # substract this delta (sum of start and end tags lengths)
        # from start and end points, returned by finditer()
        # i.e.: %< ... %> ln1 = 0, ln2 = 4 (first pair)

        ln1 = 0
        ln2 = 4

        out = []

        self.text = self.reg_r.sub("\\2", string)

        grps = self.reg_r.finditer(string)
        for gr in grps:

            start = gr.start() - ln1
            end = gr.end() - ln2
            ln1 = ln2
            ln2 += 4

            tag = gtk.TextTag()

            if "%<" in gr.group(1):
#                print '%<'
                tag.set_property("foreground", "red")

            elif "#<" in gr.group(1):
#               print '#<'
                tag.set_property("font", "Sans Italic 12")
#                tag.set_property("foreground", "green")

            out.append([tag, start, end])

        return out


    def redraw_cb(self, widget, event):
        """Disable-enable converter for Text wid."""

        keyname = gtk.gdk.keyval_name(event.keyval)
#        print 'key', keyname, 'was pressed', event.keyval


        if keyname == "d" or keyname == "Cyrillic_ve" and event.state & gtk.gdk.CONTROL_MASK:

            temp_iter = self.textview.get_iter_at_location(0, self.textview.get_visible_rect()[1])

            self.pos = temp_iter.get_line()

            if not self.plain:
                self.plain = True
            else:
                self.plain = False

            self.ins_txt_hip(self.base_txt)

        elif keyname == "q" and event.state & gtk.gdk.CONTROL_MASK:
            startiter, enditer = self.textbuffer.get_bounds()
            txt = self.textbuffer.get_text(startiter, enditer).decode('utf8')
            out = slov.conv_str(txt)

            self.textbuffer.set_text(out)
            self.style_txt()

        elif keyname == "o":
            dialog = gtk.FileChooserDialog("Open..", None, 
                    gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, 
                        gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

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
                txt_win.ins_txt(txt1)

            elif response == gtk.RESPONSE_CANCEL:
                print 'Closed, no files selected'
            dialog.destroy()

        elif keyname == "s":
            dialog = gtk.FileChooserDialog("Save..", None, 
                    gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, 
                        gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))

            if self.plain:
                dialog.set_current_name('.hip')
            else:
                dialog.set_current_name('.txt')


            response = dialog.run()


            if response == gtk.RESPONSE_OK:

                startiter, enditer = self.textbuffer.get_bounds()
                data = self.textbuffer.get_text(startiter, enditer).decode('utf8')
                Writer.write_line(dialog.get_filename(), data, "w", "cp1251")

            elif response == gtk.RESPONSE_CANCEL:
                print 'Closed, no files selected'
            dialog.destroy()

        elif keyname == "i" and event.state & gtk.gdk.CONTROL_MASK:
            # write (manually find) new greek-slavonic parallel 
            if self.path1:
#                self.paral.get_par(self.path1)
                get_par.Par(self.mode).get_par(self.path1)
            else:
                print 'no local path found'


        elif keyname == "u" and event.state & gtk.gdk.CONTROL_MASK:
            print "try and find parallel"
            if self.path1:
                print self.path1
                op_path = get_par.Par(self.mode).open_par(self.path1).rstrip()
                print "op_path", op_path
                try:
                    if self.mode:
                        fp = codecs.open(op_path, "rb", "cp1251")
                    else:
#                        fp = codecs.open(op_path, "rb", "cp1251")
                        fp = codecs.open(op_path, "rb", "utf-8")
                    lines = fp.readlines()
                    fp.close()

                    txt = ''.join(lines)

                    if self.mode:
                        par_win = Show_text(False)
                        par_win.path1 = op_path
#                        par_win.mode=True
                        par_win.ins_txt_hip(txt)
                    else:
                        par_win = Show_text(True)
                        par_win.path1 = op_path
#                        par_win.mode=False
                        par_win.ins_txt_gr(txt)

#                    par_win.ins_txt(txt)
#                    par_win.style_txt()

                except IOError:
                    print 'can not open file parallel to', self.path1


            else:
                print 'no local path found'

        elif keyname == "b" and event.state & gtk.gdk.CONTROL_MASK:
            # add a bookmark
            book_name = ""
            temp_iter = self.textview.get_iter_at_location(0, self.textview.get_visible_rect()[1])
            # current position in text
            self.pos = temp_iter.get_line()
            print 'positon', self.pos

            bm_line = self.path1 + ' ' + str(self.pos)

            Writer.write_line(self.bmarks, bm_line + '\n', 'a')

            self.combo.append_text(bm_line)

#            tree = ET.parse(f_path)
#            root = tree.getroot()
#            # get filename from <document name> attribute
#            # Be careful! in some files there's no such attrib!
#            for att in root.attrib:
#                if att == 'name':
#                    book_name = ''.join([root.attrib['name'], '.xml'])
#                    print book_name
#            if not book_name:
#                print "didn't find any book name in <document> tag"
#
#            mord.combo.append_text(wd_path)

#        elif keyname == "n" and event.state & gtk.gdk.CONTROL_MASK:
#            # scroll to next mark
#
##            cur_iter = self.textbuffer.get_iter_at_line(self.pos)
##            self.textbuffer.place_cursor(cur_iter)
#            cur_mark = self.textbuffer.get_mark('3')
#            print cur_mark
#            self.textview.scroll_to_mark(cur_mark, 0.0, True, 0.0, 0.0)
##            cur_iter = self.textbuffer.get_iter_at_line(self.pos)
#            cur_iter = self.textbuffer.get_iter_at_mark(cur_mark)
#            self.textbuffer.place_cursor(cur_iter)

    def search_cb(self, widget, event):

        keyname = gtk.gdk.keyval_name(event.keyval)
        # search for given substring in buffer
        if keyname == "Return":
            self.search_str = widget.get_text()
            start_iter =  self.textbuffer.get_start_iter()
            found = start_iter.forward_search(self.search_str, 0, None) 
            if found:
                self.match_start, self.match_end = found #add this line to get self.match_start and match_end
                self.textbuffer.select_range(self.match_start, self.match_end)
                self.textview.scroll_to_iter(self.match_start, 0.0, True, 0.0, 1.0)
        elif keyname == "n" and event.state & gtk.gdk.CONTROL_MASK \
        or keyname == "Cyrillic_te" and event.state & gtk.gdk.CONTROL_MASK:
            try:
                start_iter = self.match_end
                found = start_iter.forward_search(self.search_str, 0, None) 
                if found:
                    self.match_start, self.match_end = found
                    self.textbuffer.select_range(self.match_start, self.match_end)
                    self.textview.scroll_to_iter(self.match_start, 0.0, True, 0.0, 1.0)
            except AttributeError:
                print 'no search results'
        elif keyname == "p" and event.state & gtk.gdk.CONTROL_MASK \
        or keyname == "Cyrillic_ze" and event.state & gtk.gdk.CONTROL_MASK:
            try:
                start_iter = self.match_start
                found = start_iter.backward_search(self.search_str, 0, None) 
                if found:
                    self.match_start, self.match_end = found
                    self.textbuffer.select_range(self.match_start, self.match_end)
                    self.textview.scroll_to_iter(self.match_start, 0.0, True, 0.0, 1.0)
            except AttributeError:
                print 'no search results'

    def style_txt_gr(self):

#        import pdb; pdb.set_trace()
        self.my_text_gr.set_property("font", self.gr_font)
# похоже, что затыка в Wrap_word
        self.my_text_gr.set_property("wrap-mode", gtk.WRAP_WORD)
#        self.my_text.set_property("wrap-mode", gtk.WRAP_CHAR)
        

        # do this, otherwise arabic numbers style will be overwritten
#        self.my_text.set_priority(0)

        startiter, enditer = self.textbuffer.get_bounds()
# здеся все сегфолтится. Гадство!
        self.textbuffer.apply_tag(self.my_text_gr, startiter, enditer)

        if self.pos:
            # put cursor at the start of the page
            zero_iter = self.textbuffer.get_iter_at_line(self.pos)
            zero_mark = self.textbuffer.create_mark(None, zero_iter)
#            self.textbuffer.place_cursor(zero_iter)
            self.textview.scroll_to_mark(zero_mark, 0.0, True, 0.0, 0.0)
            self.textview.grab_focus()
        else:
            self.textbuffer.place_cursor(startiter)


    def style_txt(self):

#        import pdb; pdb.set_trace()
        if self.mode:
            fnt = self.gr_font
        else:
            fnt = self.sl_font

        self.my_text.set_property("font", fnt)
# похоже, что затыка в Wrap_word
        self.my_text.set_property("wrap-mode", gtk.WRAP_WORD)
#        self.my_text.set_property("wrap-mode", gtk.WRAP_CHAR)
        

        # do this, otherwise arabic numbers style will be overwritten
#        self.my_text.set_priority(0)

        startiter, enditer = self.textbuffer.get_bounds()
# здеся все сегфолтится. Гадство!
        self.textbuffer.apply_tag(self.my_text, startiter, enditer)

        if self.pos:
            # put cursor at the start of the page
            zero_iter = self.textbuffer.get_iter_at_line(self.pos)
            zero_mark = self.textbuffer.create_mark(None, zero_iter)
#            self.textbuffer.place_cursor(zero_iter)
            self.textview.scroll_to_mark(zero_mark, 0.0, True, 0.0, 0.0)
            self.textview.grab_focus()
        else:
            self.textbuffer.place_cursor(startiter)


#TODO: make hidden comments, so that one doesnt have to reload the page to see them

    def wrapper(self, txt):

        text_ls = []

        parts_ls = self.split_parag.split(txt)
        for part in parts_ls:
            part = self.kill_rn.sub(' ', part)
            text_ls.append(part)
        txt1 = '\n\n'.join(text_ls)

        return txt1

    def xml_open(self, *args):
        t_name = ""
        tree = ET.parse(args[0])
        root = tree.getroot()
#        res = []
        f_lines = []

        head = root.find('header')
        # can't check 'head' the usual way - parser swears
        if ET.iselement(head):
            f_lines.append(head.text)

#        for att in root.attrib:
#            if att == 'title':
#                t_name = root.attrib['title']

        for bk in root.iter('span'):
            for sec in bk.iter('span'):
#                for s_att in sec.attrib:
#                    if s_att == 'number':
#                        flag = 1
#                        break
#                    else:
#                        flag = 0

                f_lines.append(sec.text)

#        return f_lines, root
        return f_lines



if __name__ == '__main__':

    global enc
    
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

#        if options.xml:

        txt_win = Show_text(True)
        txt_win.path1 = args[0]
        f_lines = txt_win.xml_open(args[0])
        txt_win.ins_txt_gr(f_lines)

#        else:
#            txt_win = Show_text(False)
#            fp = open(f_path)
#            lst = fp.readlines()
#            fp.close()
#
#            myslice = ''.join(lst[:10])
#            enc = chardet.detect(myslice)['encoding']
##        enc = 'cp1251'
#
#            if not enc:
#                enc = 'utf8'
#
#            out_doc = []
#            count = 0
#
#            for line in lst:
#                new_line = line.decode(enc)
#                out_doc.append(new_line)
#
#
#            txt = ''.join(out_doc)
#
#            txt = txt_win.wrapper(txt)
#
#            txt_win.ins_txt_hip(txt)
#


    else:
        print 'no arguments, exiting'
        sys.exit(0)

    def main():
        gtk.main()
        return 0

    main()
#TODO: сделай нормальную замену шрифта в греческом окне (C+u). Пока вылазят xml-тэги.

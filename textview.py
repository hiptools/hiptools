#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import codecs
import re
import os
import sys
#import chardet

# formerly - ucs8conv, renamed
import hipconv
import hip_config
# comment parser
import hipcomment
#import write_utf
import slovenize
import get_par

conv = hipconv.Repl()
brac = hipcomment.Brackets()
#Writer = write_utf.write_gen()
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

        box1 = gtk.VBox(False, 0)
        self.window3.add(box1)
        box1.show()

        box2 = gtk.VBox(False, 3)
        box2.set_border_width(3)
        box1.pack_start(box2, True, True, 0)
        box2.show()

        self.f_select = gtk.FontButton(fontname=None)
        self.f_select.connect('font-set', self.font_cb)

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
#        self.check1.show()
        self.entry.show()
        self.entry.connect('key_press_event', self.search_cb)

        self.textview.show()
        box2.pack_start(self.f_select, False, False, 0)
#        box2.pack_start(self.check1, False, False, 0)
        box2.pack_start(sw)
        box2.pack_start(self.entry, False, False, 0)

        self.window3.show()
        self.textview.grab_focus()

        # current position in text
        self.pos = 0

        # regexp to check if the font is ucs-compatible
        # probably not a good idea, if there is some kind of 'kucs.ttf' out there...
        # well, in that case we'll make an exception.
        self.ucs_patt = re.compile(u'ucs', re.U | re.I)

        self.config = hip_config.Service(".hiptools.config")

        # default font
        self.sl_font = self.config.sl_font
        self.gr_font = self.config.gr_font
        self.sl_font_prev = ''
        self.gr_font_prev = ''
        self.plain_font = 'Tahoma 16'
        self.sl_plain_font = 'Tahoma 16'
        self.gr_plain_font = 'Tahoma 16'

        if not self.mode:
            self.check_font(self.sl_font)

            if self.config.default_style == 'slavonic':
                self.plain = False
            elif self.config.default_style == 'plain':
                self.plain = True
        else:
            self.plain = False

        if self.config.brackets_off == 'True':
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

    def ins_txt_gr(self, new_txt=None):

        if new_txt:
            self.base_txt = new_txt
        if not self.plain: 
            # parse comments. If 2d argument True, wipe comments
#            conv_txt = brac.repl_brac(self.base_txt, True)[0]
            conv_txt = brac.repl_brac(self.base_txt, self.brackets_off)[0]

            # cleanup all xml tags (untill they are shown correctly)
            conv_txt = self.html_del.sub('', conv_txt)

            # convert to slavonic typeset
#            conv_txt = conv(conv_txt, self.uni)
#            conv_txt = conv(self.base_txt, self.uni)
            self.textbuffer.set_text(conv_txt)

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

        elif keyname == "u" and event.state & gtk.gdk.CONTROL_MASK:
            print "try and find parallel"
            if self.path1:
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


if __name__ == '__main__':

    global enc
    
    argv = sys.argv

#    config = hip_config.Service('.hipeditor.config')
    config = hip_config.Service('.hiptools.config')
    txt_win = Show_text(False)

    if len(argv) > 1:
        f_path = argv[1]

        fp = open(f_path)
        lst = fp.readlines()
        fp.close()

        slice = ''.join(lst[:10])
        enc = chardet.detect(slice)['encoding']
#        enc = 'cp1251'

        if not enc:
            enc = 'utf8'

        out_doc = []
        count = 0

        for line in lst:
            new_line = line.decode(enc)
            out_doc.append(new_line)

        txt = ''.join(out_doc)

        txt1 = txt_win.wrapper(txt)

        txt_win.ins_txt(txt1)

    def main():
        gtk.main()
        return 0

    main()
#TODO: сделай нормальную замену шрифта в греческом окне (C+u). Пока вылазят xml-тэги.

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

# formerly - ucs8conv, renamed
import hipconv
import ConfigParser
# comment parser
import hipcomment
#import write_utf
import slovenize
import get_par

conv = hipconv.Repl()
brac = hipcomment.Brackets()
#Writer = write_utf.write_gen()
slov = slovenize.Mn()

class Show_panes:
    """ text viewer 

    """
    def __init__(self, Mode=True):
        # mode=true means greek mode 

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.expanduser('~'), 'hiptoolsrc.bk2'))

        self.mode = Mode
        self.gr_font = config.get('Fonts', 'gr_font')
        self.sl_font = config.get('Fonts', 'sl_font')

        br_off = config.get('Style', 'brackets_off')

        if br_off == 'True':
            self.brackets_off = True
        else:
            self.brackets_off = False


        self.plain = True
        self.path1 = ""
        
#        print self.paral

        # original plain text
        self.base_txt = ""
        self.window3 = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window3.set_resizable(True)
        self.window3.set_border_width(10)
#        self.window3.set_size_request(950, 400)
        self.window3.fullscreen()

        self.window3.set_border_width(0)
#        self.window3.connect('key_press_event', self.redraw_cb)

        if __name__ == '__main__':
            self.window3.connect('destroy', self.destroy_cb)
        
        self.panes = gtk.HPaned()
        self.window3.add(self.panes)
        self.panes.show()

        self.sw1 = gtk.ScrolledWindow()
        self.sw2 = gtk.ScrolledWindow()

        self.sw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.tv1 = gtk.TextView()
        self.tv2 = gtk.TextView()
        self.tv1.set_editable(False)
        self.tv2.set_editable(False)

        self.buf1 = self.tv1.get_buffer()
        self.buf2 = self.tv2.get_buffer()

        self.sw1.add(self.tv1)
        self.sw2.add(self.tv2)

        self.tv1.show()
        self.tv2.show()

        self.sw1.show()
        self.sw2.show()

#        self.panes.add1(self.tv1)
#        self.panes.add2(self.tv2)
        self.panes.pack1(self.sw1, True, False)
        self.panes.pack2(self.sw2, True, False)
        self.panes.set_position(450)
        
#        box1 = gtk.VBox(False, 0)
#        self.window3.add(box1)
#        box1.show()

        self.window3.show()

    def destroy_cb(self, widget):
        gtk.main_quit()
        return False

    def add_to_pane(self, num, txt):
        # num - 0 left pane, 1 - right
        if num:
            self.buf1.set_text(txt)
        else:
            self.buf2.set_text(txt)

    def opener(self, md, f_path):

        fp = open(f_path)
        lst = fp.readlines()
        fp.close()
        if md:
            enc = 'utf-8'
        else:
            enc = 'cp1251'

        out_doc = []

        for line in lst:
            new_line = line.decode(enc)
            if not md:
                print self.brackets_off
                new_line = brac.repl_brac(new_line, self.brackets_off)[0]
                new_line = conv(new_line, 'ucs')
            out_doc.append(new_line)
        txt = ''.join(out_doc)

        return txt

    def style_hip(self):
        self.tag_table_sl = self.buf1.get_tag_table()
        self.my_text_sl = gtk.TextTag()
        self.tag_table_sl.add(self.my_text_sl)

        self.my_text_sl.set_property("font", self.sl_font)
        self.my_text_sl.set_property("wrap-mode", gtk.WRAP_WORD)

        startiter, enditer = self.buf1.get_bounds()
        self.buf1.apply_tag(self.my_text_sl, startiter, enditer)

    def style_gr(self):
        self.tag_table_gr = self.buf2.get_tag_table()
        self.my_text_gr = gtk.TextTag()
        self.tag_table_gr.add(self.my_text_gr)

        self.my_text_gr.set_property("font", self.gr_font)
        self.my_text_gr.set_property("wrap-mode", gtk.WRAP_WORD)

        startiter, enditer = self.buf2.get_bounds()
        self.buf2.apply_tag(self.my_text_gr, startiter, enditer)

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


if __name__ == '__main__':

#    global enc
    
    argv = sys.argv


    if len(argv) > 2:

        txt_win = Show_panes(False)

        f_path1 = argv[1]
        f_path2 = argv[2]

#            txt = txt_win.wrapper(txt)
        txt_win.add_to_pane(1, txt_win.opener(0, f_path1))
        txt_win.add_to_pane(0, txt_win.opener(1, f_path2))
        txt_win.style_hip()
        txt_win.style_gr()
    else:
        print 'not enough args, exiting'
        sys.exit(0)


    def main():
        gtk.main()
        return 0

    main()


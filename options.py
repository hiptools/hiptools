#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import codecs
import re
import os
import sys

import ConfigParser

class Opt:
    def __init__(self, widget):

        self.config = ConfigParser.ConfigParser()
        self.conf_path = os.path.join(os.path.expanduser('~'), '.config', 'hiptools', 'hiptoolsrc')
        self.config.read(self.conf_path)

        self.window3 = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window3.set_size_request(650, 400)
        self.window3.set_border_width(3)
        self.window3.set_title('Настроки')
#        self.window3.connect('destroy', self.destroy_cb)

        vbox = gtk.VBox(False, 3)
        self.window3.add(vbox)

        self.note = gtk.Notebook()
        self.note.set_tab_pos(gtk.POS_TOP)
        self.note.set_scrollable(True)
        self.show_tabs = True
        self.show_border = True

#        self.note.append_page()

        vbox.pack_start(self.note, True, True, 0)

        self.note.show()
        vbox.show()
        self.window3.show()

        lb0 = gtk.Label()
        lb0.show()

        lb1 = gtk.Label("Поиск в славянских текстах (группа по умолчанию)")
        lb1.show()
        lb2 = gtk.Label("Поиск в греческих текстах (группа по умолчанию)")
        lb2.show()
        
        vbox1 = gtk.VBox(False, 3)
        vbox1.show()

        vbox2 = gtk.VBox(False, 3)
        vbox2.show()

        hbox1 = gtk.HBox(False, 0)
        hbox2 = gtk.HBox(False, 0)
        hbox3 = gtk.HBox(False, 0)

        # Apply and Cancel buttons
        app = gtk.Button('Применить')
        can = gtk.Button('Закрыть')
        app.show()
        can.show()

        app.connect('clicked', self.apply_op)
#        can.connect('clicked', self.destroy_cb)

        sc1 = gtk.Label('Опции поиска')
        sc2 = gtk.Label('Шрифты')

        bt1 = gtk.CheckButton('Включить ударения')
        bt1.show()

        bt1.connect("toggled", self.w_stress)
        if self.config.get('SearchOptions', 'diacritics_off') =='False':
            bt1.set_active(True)

        self.combo1 = gtk.combo_box_new_text()
        self.combo1.show()

        self.combo2 = gtk.combo_box_new_text()
        self.combo2.show()

        vbox1.pack_start(lb0, False, False, 10)
        hbox1.pack_start(lb1, False, False, 0)
        hbox1.pack_start(self.combo1, False, False, 0)
#       hvbox1.pack_start(lb0, False, False, 10)
        hbox2.pack_start(lb2, False, False, 10)
        hbox2.pack_start(self.combo2, False, False, 0)

        vbox1.pack_start(hbox1, False, False, 0)
        hbox1.show()

        vbox1.pack_start(hbox2, False, False, 0)
        hbox2.show()

        vbox1.pack_start(bt1, False, False, 0)
        hbox3.pack_end(app, False, False, 0)
        hbox3.pack_end(can, False, False, 0)
        hbox3.show()
        vbox1.pack_end(hbox3, False, False, 0)

        self.note.append_page(vbox1, sc1)

        self.note.append_page(vbox2, sc2)

        self.combo1.connect("changed", self.choose)       
        self.combo2.connect("changed", self.choose)

        combo_sl = ['Богослужебные', 'Свящ. Писание', 'Все книги', 'Четьи книги', 'Акафисты', 'Алфавит', 'Апостол', 'Часослов', 'Треодь цветная', 'Добротолюбие', 'Экзапостилларии', 'Евангелия', 'Ифика', 'Каноны', 'Молитвы на молебнах', 'Общая минея', 'Октоих', 'Пролог', 'Книга правил', 'Псалтырь', 'Треодь постная', 'Служебник', 'Типикон', 'Требник', 'Ветхий Завет', 'Минеи месячные']
        combo_gr = ['All_services', 'All_read', 'Minologion_base', 'Minologion extra', 'Minologion all', 'Euhologion', 'Hieratikon', 'Octoechos', 'Orologion', 'Penticostartion', 'Triodion', 'Agia_grafh', 'Psalthrion', 'Zlat_Mat', 'Zlat_John']

        for group, vid, line in [[combo_sl, self.combo1, 'default_search_group'], [combo_gr, self.combo2, 'default_search_group_gr']]:

            self.combo_fill(group, vid, line)

    def __call__(self, widget):

        opt_win = Opt()
    
    def combo_fill(self, group, vid, line):

        for gr in group:
            vid.append_text(gr.strip())

            # default active item (index in combo_list)
        for z in range(len(group)):
            if self.config.get('SearchOptions', line) == group[z]:
                vid.set_active(z)

    def destroy_cb(self, widget):
        gtk.main_quit()
        return False

    def apply_op(self, widget):
        with open(self.conf_path, 'wb') as configfile:
            self.config.write(configfile)

    def choose(self, widget):
        if widget == self.combo1:
            line = 'default_search_group'
        elif widget == self.combo2:
            line = 'default_search_group_gr'

        get_name = widget.get_active_text() 
#        print get_name
        self.config.set('SearchOptions', line, get_name)

    def w_stress(self, widget, data=None):
        '''callback for checkbutton'''

        if widget.get_active():
            self.config.set('SearchOptions', 'diacritics_off', 'False')
        else:
            self.config.set('SearchOptions', 'diacritics_off', 'True')


if __name__ == '__main__':

    opt_win = Opt()

    def my_main():
        gtk.main()
        return 0

    my_main()




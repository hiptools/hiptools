#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

class B_list:
    def __init__(self):
        self.b_list = [["Gen", "Genesis", u"Бытие"],
        ["Exod", "Exodus", u"Исход"],
        ["Lev", "Leviticus", u"Левит"],
        ["Num", "Numbers", u"Числа"],
        ["Deut", "Deuteronomy", u"Второзаконие"],
        ["Josh", "Joshua", u"Иисус Навин"],
        ["Judg", "Judges", u"Судий"],
        ["Ruth", "Ruth", u"Руфь"],
        ["1Sam", "1 Samuel", u"1 Царств"],
        ["2Sam", "2 Samuel", u"2 Царств"],
        ["1Kgs", "1 Kings", u"3 Царств"],
        ["2Kgs", "2 Kings", u"4 Царств"],
        ["1Chr", "1 Chronicles", u"1 Паралипоменон"],
        ["2Chr", "2 Chronicles", u"2 Паралипоменон"],
        ["Ezra", "Ezra", u"Ездры"],
        ["Neh", "Nehemiah", u"Неемии"],
        ["Esth", "Esther", u"Эсфирь"],
        ["Job", "Job", u"Иов"],
        ["Ps", "Psalms", u"Псалтирь"],
        ["Prov", "Proverbs", u"Притчи"],
        ["Eccl", "Ecclesiastes", u"Экклезиаст"],
        ["Song", "Song of Solomon", u"Песнь песней"],
        ["Isa", "Isaiah", u"Исаия"],
        ["Jer", "Jeremiah", u"Иеремия"],
        ["Lam", "Lamentations", u"Плач Иеремии"],
        ["Ezek", "Ezekiel", u"Иезекииль"],
        ["Dan", "Daniel", u"Даниил"],
        ["Hos", "Hosea", u"Осия"],
        ["Joel", "Joel", u"Иоиль"],
        ["Amos", "Amos", u"Амос"],
        ["Obad", "Obadiah", u"Авдий"],
        ["Jonah", "Jonah", u"Иона"],
        ["Mic", "Micah", u"Михей"],
        ["Nah", "Nahum", u"Наум"],
        ["Hab", "Habakkuk", u"Аввакум"],
        ["Zeph", "Zephaniah", u"Софрония"],
        ["Hag", "Haggai", u"Аггей"],
        ["Zech", "Zechariah", u"Захария"],
        ["Mal", "Malachi", u"Малахия"],

        ["Matt", "Matthew", u"от Матфея"],
        ["Mark", "Mark", u"от Марка"],
        ["Luke", "Luke", u"от Луки"],
        ["John", "John", u"от Иоанна"],
        ["Acts", "Acts", u"Деяния"],
        ["Rom", "Romans", u"К Римлянам"],
        ["1Cor", "1 Corinthians", u"1 к Коринфянам"],
        ["2Cor", "2 Corinthians", u"2 к Коринфянам"],
        ["Gal", "Galatians", u"К Галатам"],
        ["Eph", "Ephesians", u"К Эфесянам"],
        ["Phil", "Philippians", u"К Филиппийцам"],
        ["Col", "Colossians", u"К Колоссянам"],
        ["1Thess", "1 Thessalonians", u"1 к Фессалоникийцам"],
        ["2Thess", "2 Thessalonians", u"2 к Фессалоникийцам"],
        ["1Tim", "1 Timothy", u"1 к Тимофею"],
        ["2Tim", "2 Timothy", u"2 к Тимофею"],
        ["Titus", "Titus", u"К Титу"],
        ["Phlm", "Philemon", u"К Филимону"],
        ["Heb", "Hebrews", u"К Евреям"],
        ["Jas", "James", u"Иакова"],
        ["1Pet", "1 Peter", u"1 Петра"],
        ["2Pet", "2 Peter", u"2 Петра"],
        ["1John", "1 John", u"1 Иоанна"],
        ["2John", "2 John", u"2 Иоанна"],
        ["3John", "3 John", u"3 Иоанна"],
        ["Jude", "Jude", u"Иуды"],
        ["Rev", "Revelation", u"Откровение"],

        ["Bar", "Baruch", u"Варух"],
        ["AddDan", "Additions to Daniel", u"Прибавления к Даниилу"],
        ["PrAzar", "Prayer of Azariah", u"Молива Азарии"],
        ["Bel", "Bel and the Dragon", u"Бел и дракон"],
        ["SgThree", "Song of the Three Young Men", u"Песнь трех отроков"],
        ["Sus", "Susanna", u"Сусанна"],
        ["1Esd", "1 Esdras", u"1 Ездры"],
        ["2Esd", "2 Esdras", u"2 Ездры"],
        ["AddEsth", "Additions to Esther", u"Добавления к Эсфири"],
        ["EpJer", "Epistle of Jeremiah", u"Послание Иеремии"],
        ["Jdt", "Judith", u"Иудифь"],
        ["1Macc", "1 Maccabees", u"1 Маккавеев"],
        ["2Macc", "2 Maccabees", u"2 Маккавеев"],
        ["3Macc", "3 Maccabees", u"3 Маккавеев"],
        ["4Macc", "4 Maccabees", u"4 Маккавеев"],
        ["PrMan", "Prayer of Manasseh", u"Молитва Манассии"],
        ["Sir", "Sirach/Ecclesiasticus", u"Премудрость Иисуса сына Сирахова"],
        ["Tob", "Tobit", u"Товит"],
        ["Wis", "Wisdom of Solomon", u"Премудрость Соломона"]]

    def eng_trans(self, name, flag=False):
        res = []
        for abbr, eng, rus in self.b_list:
            if flag:
                if name in rus.encode('utf8'):
                    res.append([abbr, eng, rus])
            else:
                if name in abbr:
                    res.append([abbr, eng, rus])
                
        return res

if __name__ == '__main__':
    from optparse import OptionParser
    usage = "usage: %prog [options] book name"
    parser = OptionParser(usage=usage)

    parser.add_option("-r", "--russian", dest="russian", action="store_true", help="Find English parallel")
    (options, args) = parser.parse_args()

    if args:
        bls = B_list()
        if options.russian:
            res = bls.eng_trans(args[0], True)
        else:
            res = bls.eng_trans(args[0], False)

        if res:
            for ent in res:
                print ent[0], ',',  ent[1], ',', ent[2]
        else:
            print 'could not find such a book'

    else:
        print 'no args, exiting'
        sys.exit(0)


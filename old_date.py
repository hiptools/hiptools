#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

class Old:
    def __init__(self):
        pass

    def visokos(self, year):
        # if a year is a leap-year, theres 29 days in feb
        if year % 4 == 0 and year % 100 !=0 or year % 400 == 0:
            # високос!
            return 29
        else:
            return 28

    def to_old(self, date):
        """ convert Gregorian date to old style """

        day = date[0]
        month = date[1]
        year = date[2]
        
        # still last year in old style
        if month == 1 and day < 14:
            year -= 1
        
        month_prev = month - 1
        if month_prev < 1:
            month_prev = 12
       
        m_d_list = [31, self.visokos(year), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  
        month_days = m_d_list[month_prev - 1]

        if day > 13:
            day = day - 13
            month_fin = month
        else:
            day = day - 13 + m_d_list[month_prev - 1]
            month_fin = month_prev
        return (day, month_fin, year)

    def to_new(self, date):
        """ convert old style date to Gregorian """

        day = date[0]
        month = date[1]
        year = date[2]
        
        a = (14 - month)//12
        y = year + 4800 - a
        m = month + (12 * a) - 3

        jdn = day + ((153 * m + 2) // 5) + (365 * y) + (y // 4) - 32083

        a = jdn + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153
        
        day = e - ((153 * m + 2) // 5) + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d - 4800 + (m // 10)

        return (day, month, year)

    
if __name__ == '__main__':
    argv = sys.argv
    if len(argv) > 1:
        date = [int(i) for i in argv[1].split('-')]
    else:
        print 'No args given, exiting'
        raise SystemExit
    Conv = Old()
#    new_date = Conv.to_old(date)
    new_date = Conv.to_new(date)
#    print '-'.join([str(i) for i in new_date])
    print [str(i) for i in new_date]


#!/usr/bin/env python
# -*- coding: utf-8 -*-

def listbooks(path, include_unknowns = True):
    """
    Возвращает объект вида:
    [
        ['file1', 'description of file 1'],
        ['file2', 'description of second file'],
        ['dir3/', 'its description', [...]],
    ]
    Список включает в себя существующие файлы из descript.ion
    и дополнительно отсутствующие в нём (если разрешено include_unknowns)
    """
    #print 'Loading',path
    import os, codecs

    desc = [] # возвращаемый результат
    
    exclude = ( # файлы, которые не будут включены в список
        'descript.ion',
        'info.txt',
        '.svn',
        'dir',
    )

    items = os.listdir(path) # список элементов папки
    dionpath = os.path.join(path, 'descript.ion')
    if os.path.exists(dionpath):
        dion = codecs.open(dionpath, 'r', 'utf-8') # файл описания
        for l in dion.readlines():
            if l.startswith('#'):
                continue # игнорируем комментарии
            key, val = l.split(' ', 1)
            key = key.strip()
            if key in items:
                desc.append([key, val.strip(), False])
                del items[items.index(key)]
            else:
                print 'Non-existing item in %s/descript.ion for %s' % (path, key)
        dion.close()
    if include_unknowns:
        for i in items: # остатки
            desc.append([i, i, False])

    # теперь рекурсивно добавляем информацию о вложенных папках
    for i in desc:
        if i[0] in exclude:
            del desc[desc.index(i)]
            continue
        subpath = os.path.join(path, i[0])
        if os.path.isdir(subpath):
            i[2] = listbooks(subpath, include_unknowns)
            i[0] = i[0] + '/'

    return desc

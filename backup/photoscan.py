"""
Основная задача - в одной указанной папке найти файлы, которых нет в другой указанной папке.
Также можно искать дубликаты.
"""

import os, shutil

def main():
    print('start')
    photos = []
    names = []
    #losts = []
    photos_qty = 0
    unique_qty = 0
    skiped_qty = 0
    lost_qty = 0
    newname_qty = 0
    with open('skiped.txt', 'w') as fs:
        fs.write('')
    with open('skiped.txt', encoding='utf-8', mode='a') as fs:
        for d, s, f in os.walk('d:/photo'):
            for ff in f:
                if (ff.upper() == 'THUMBS.DB'):
                    continue
                photos_qty += 1
                if ff.upper() not in names:
                    names.append(ff.upper())
                sz = os.path.getsize(d + '/' + ff)
                ss = ff.upper() + ';' + str(sz)
                if ss not in photos:
                    photos.append(ss)
                    unique_qty += 1
                else:
                    skiped_qty += 1
                    fs.write(ss + '\n')
    print('photos: {}'.format(photos_qty))
    print('unique: {}'.format(unique_qty))
    print('skiped: {}'.format(skiped_qty))
    for d, s, f in os.walk('C:/Users/Ruslan/Google Диск/Google Фото'):
        for ff in f:
            if (ff.upper() == 'THUMBS.DB'):
                continue
            sz = os.path.getsize(d + '/' + ff)
            ss = ff.upper() + ';' + str(sz)
            if ss not in photos:
                lost_qty += 1
                #if ff.upper() not in losts:
                #    losts.append(ff.upper())
                if ff.upper() not in names:
                    newname_qty += 1
                    shutil.copyfile(d + '/' + ff, 'losts/' + ff)
    #print('losts: {}'.format(len(losts)))
    print('lost: {}'.format(lost_qty))
    print('new name: {}'.format(newname_qty))
    input('>')

if __name__ == '__main__':
    main()






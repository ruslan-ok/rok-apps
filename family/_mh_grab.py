"""Obtaining family tree images from myheritage.com.
"""
import urllib.request

fname = 'xxx.ged'
pname = 'xxx/'

with open(fname, 'r', encoding='latin-1') as f:
    lines_qnt = 0
    links_qnt = 0
    s = ''
    while True:
        try:
            s = f.readline()
        except Exception as ex:
            print(ex)
            break
        if not s:
            break
        lines_qnt += 1
        if 'https://' in s:
            links_qnt += 1
            url = 'https://' + s.split('https://')[1]
            img = s.split('/')[-1]
            img = img.replace('\n', '')
            urllib.request.urlretrieve(url, pname + img)
            print('.', end='', flush=False)
            if links_qnt % 100 == 99:
                print('\n' + str(links_qnt+1))
    print(f'\n{lines_qnt=}, {links_qnt=}')
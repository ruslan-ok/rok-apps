import requests

def extract_get_params(request):
    q = request.GET.get('q')
    if not q:
        q = ''
    p = request.GET.get('page')
    if not p:
        p = ''
    ret = ''
    if q:
        ret += 'q={}'.format(q)
    if p:
        if q:
            ret += '&'
        ret += 'page={}'.format(p)
    if ret:
        ret = '?' + ret
    return ret



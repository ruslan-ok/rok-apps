# coding=UTF-8
from django.shortcuts import get_object_or_404, render
from django.template import loader

#============================================================================
def test_view(request):
    template = loader.get_template('test.html')
    c = RequestContext(request,{})
    return HttpResponse(template.render(c))
    #return render(request, 'test/test.html', {})

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Postcard

# Create your views here.

def page(request):
    postcards = Postcard.objects.filter(is_public=True)
    return render(request, 'cards/page.html', {'postcards': postcards})

def postcard(request, pk):
    postcards = [None, *Postcard.objects.filter(is_public=True), None]
    ids = [p.pk if p else None for p in postcards]
    try:
        index = ids.index(pk)
    except ValueError:
        raise Http404("Postcard not found")
    postcards = postcards[index-1:index+2]
    return render(request, 'cards/postcard.html', {'postcards': postcards})

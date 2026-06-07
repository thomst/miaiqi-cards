from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Gallery, Postcard


def postcard(request, gallery_id, postcard_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    postcard = get_object_or_404(Gallery.postcards.all(), id=postcard_id)
    postcards = [None, *gallery.postcards.all(), None]
    ids = [p.pk if p else None for p in postcards]
    index = ids.index(postcard_id)
    postcards = postcards[index-1:index+2]
    context = {
        'postcard': postcard,
        'postcards': postcards,
    }
    return render(request, 'pages/postcard.html', context)

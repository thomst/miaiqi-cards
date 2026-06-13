from django.shortcuts import get_object_or_404, render

from miaiqi_cards.website.models import Gallery
from miaiqi_cards.postcards.models import Postcard


def postcard(request, postcard_id, gallery_id=None):
    context = dict(postcard=get_object_or_404(Postcard, id=postcard_id))
    if gallery_id := request.GET.get('gallery_id'):
        gallery = get_object_or_404(Gallery, id=gallery_id)
        gallery_postcards = list(gallery.postcards.all())
        index = [p.pk for p in gallery_postcards].index(postcard_id)
        context['previous_postcard'] = [None, *gallery_postcards, None][index]
        context['next_postcard'] = [None, *gallery_postcards, None][index + 2]
        context['gallery'] = gallery
    return render(request, 'postcards/postcard.html', context)

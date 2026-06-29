from django.shortcuts import get_object_or_404, render
from .models import GallerySection
from .models import Postcard


def postcard(request, postcard_id):
    postcard = get_object_or_404(Postcard, id=postcard_id)
    context = dict(postcard=postcard)

    if section_id := request.GET.get('section_id'):
        section = get_object_or_404(GallerySection, id=section_id)
        postcards = list(section.postcards.all())
        context['section'] = section
    else:
        postcards = list(Postcard.objects.all())

    index = [p.pk for p in postcards].index(postcard_id)
    context['previous_postcard'] = [None, *postcards, None][index]
    context['next_postcard'] = [None, *postcards, None][index + 2]
    return render(request, 'postcards/postcard.html', context)

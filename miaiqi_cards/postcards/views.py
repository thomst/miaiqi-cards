from django.shortcuts import get_object_or_404, render
from ..website.models import MiaiqiCardsPage
from .models import GallerySection
from .models import Postcard


def postcard(request, postcard_id):
    postcards = Postcard.objects.all()
    postcard = get_object_or_404(Postcard, id=postcard_id)
    context = dict(postcard=postcard)

    try:
        page = MiaiqiCardsPage.objects.get(slug='home')
    except MiaiqiCardsPage.DoesNotExist:
        pass
    else:
        context['page'] = page
        gallery_sections = page.sections.instance_of(GallerySection)
        if gallery_sections:
            context['section'] = gallery_sections[0]
            postcards = gallery_sections[0].postcards.all()

    index = [p.pk for p in postcards].index(postcard_id)
    context['previous_postcard'] = [None, *postcards, None][index]
    context['next_postcard'] = [None, *postcards, None][index + 2]
    return render(request, 'postcards/postcard.html', context)

from django.http import HttpResponse
from simple_page.renderers import get_renderer
from .models import GalleryPage, PostcardPage


def gallery(request, **kwargs):
    if 'postcard_id' in kwargs:
        page = PostcardPage()
    else:
        page = GalleryPage()
    renderer_cls = get_renderer(page)
    return HttpResponse(renderer_cls(page, request, **kwargs).render())

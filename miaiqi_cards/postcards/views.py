from django.http import HttpResponse
from simple_page.renderers import get_renderer
from .models import GalleryPage, PostcardPage


def postcard_view(request, **kwargs):
    page = PostcardPage() if 'postcard_id' in kwargs else GalleryPage()
    renderer_cls = get_renderer(page)
    return HttpResponse(renderer_cls(page, request, **kwargs).render())

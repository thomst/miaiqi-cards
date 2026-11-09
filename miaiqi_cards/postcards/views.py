from django.http import HttpResponse
from simple_page.renderers import get_renderer
from .models import PostcardPage, PostcardSetPage


def postcard_view(request, **kwargs):
    page = PostcardPage() if 'postcard_id' in kwargs else PostcardSetPage()
    renderer_cls = get_renderer(page)
    return HttpResponse(renderer_cls(page, request, **kwargs).render())

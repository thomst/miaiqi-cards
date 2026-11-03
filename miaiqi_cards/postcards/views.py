from django.http import HttpResponse
from simple_page.renderers import get_renderer
from .models import PostcardPage


def gallery(request, **kwargs):
    page = PostcardPage()
    renderer_cls = get_renderer(page)
    return HttpResponse(renderer_cls(page, request, **kwargs).render())

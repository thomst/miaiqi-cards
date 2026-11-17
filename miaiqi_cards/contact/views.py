from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from .models import ContactSection
from .renderers import ContactRenderer


def get_renderer(request, contact_id):
    contact = get_object_or_404(ContactSection, pk=contact_id)
    return ContactRenderer(contact, None, None, request)


@require_http_methods(['GET'])
def form_view(request, contact_id):
    return HttpResponse(get_renderer(request, contact_id).get_form_html())


@require_POST
def submit_view(request, contact_id):
    return HttpResponse(get_renderer(request, contact_id).submit())

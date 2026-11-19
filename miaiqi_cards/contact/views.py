from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from .models import ContactSection
from .renderers import ContactRenderer


@require_GET
def form_view(request, section_id):
    contact = get_object_or_404(ContactSection, pk=section_id)
    renderer = ContactRenderer(contact, request)
    return HttpResponse(renderer.get_form_html())


@require_POST
def submit_view(request, section_id):
    contact = get_object_or_404(ContactSection, pk=section_id)
    renderer = ContactRenderer(contact, request)
    return HttpResponse(renderer.submit())

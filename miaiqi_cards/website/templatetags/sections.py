import re
from django import template
from django.utils.text import slugify

register = template.Library()


@register.filter
def as_html_id(section):
    return f"{slugify(section.title)}"


@register.filter
def as_html_class(section):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', type(section).__name__).lower()

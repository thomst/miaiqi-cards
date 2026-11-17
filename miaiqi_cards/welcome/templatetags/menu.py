from django import template

register = template.Library()


@register.inclusion_tag('menu.html')
def menu(section, nav=None):
    if nav:
        menu = [(s, nav) for s in getattr(section, nav).order_by('pagesection__index').select_subclasses()]
    else:
        menu = [
            *[(s, 'title_nav') for s in section.title_nav.order_by('pagesection__index').select_subclasses()],
            *[(s, 'postcard_nav') for s in section.postcard_nav.order_by('pagesection__index').select_subclasses()],
            *[(s, 'subtitle_nav') for s in section.subtitle_nav.order_by('pagesection__index').select_subclasses()]
        ]
    return dict(menu=menu)

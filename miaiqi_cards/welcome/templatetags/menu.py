from django import template

register = template.Library()


@register.inclusion_tag('menu.html')
def menu(section, nav=None):
    if nav:
        menu = [(s, nav) for s in getattr(section, nav).select_subclasses()]
    else:
        menu = [
            *[(s, 'title_nav') for s in section.title_nav.select_subclasses()],
            *[(s, 'postcard_nav') for s in section.postcard_nav.select_subclasses()],
            *[(s, 'subtitle_nav') for s in section.subtitle_nav.select_subclasses()]
        ]
    return dict(menu=menu)

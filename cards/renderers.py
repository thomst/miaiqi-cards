from simple_page import renderers
from .models import Gallery


@renderers.register(Gallery)
class GalleryRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['cards/css/gallery.css'])
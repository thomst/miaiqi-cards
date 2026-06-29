from simple_page import renderers
from . import models


@renderers.register(models.GallerySection)
class GalleryRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['miaiqi_cards/gallery.css'])

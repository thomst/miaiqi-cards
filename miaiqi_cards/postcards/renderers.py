from simple_page import renderers
from django.shortcuts import get_object_or_404
from . import models


@renderers.register(models.GallerySection)
class GalleryRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['miaiqi_cards/gallery.css'])


@renderers.register(models.GallerySection, page_type=models.PostcardPage)
class PostcardRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['miaiqi_cards/postcard.css'])

    def get_template_name(self):
        return 'sections/postcard_section.html'

    def get_context_data(self):
        context = super().get_context_data()
        postcards = self.section.postcards.all()
        postcard = get_object_or_404(postcards, id=self.params['postcard_id'])
        index = [p.pk for p in postcards].index(postcard.id)
        context['postcard'] = postcard
        context['previous_postcard'] = [None, *postcards, None][index]
        context['next_postcard'] = [None, *postcards, None][index + 2]
        return context

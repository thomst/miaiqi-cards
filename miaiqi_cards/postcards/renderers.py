from functools import cached_property

from simple_page import renderers
from django.http import Http404
from django.shortcuts import get_object_or_404
from miaiqi_cards.website.models import MiaiqiCardsPage
from . import models


@renderers.register(models.PostcardPage)
class PostcardPageRenderer(renderers.PageRenderer):
    class Media:
        css = dict(all=['css/footer.css'])

    def get_template_name(self):
        return 'pages/miaiqi_cards_page.html'

    def get_main_sections(self):
        slug = self.params.get('gallery_slug')
        return models.GallerySection.objects.filter(slug=slug)

    def get_footer_sections(self):
        return self.page.homepage.footer

    def get_context_data(self):
        context = super().get_context_data()
        self.page.title = context['regions']['main']['sections'][0].postcard.title
        self.page.description = self.page.homepage.description
        return context


@renderers.register(models.GallerySection, page_type=MiaiqiCardsPage)
class GalleryRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['css/gallery.css'])


@renderers.register(models.GallerySection, page_type=models.PostcardPage)
class PostcardRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['css/postcard.css'])

    def get_template_name(self):
        return 'sections/postcard_section.html'

    @cached_property
    def postcards(self):
        return self.section.postcards.all()

    @cached_property
    def postcard(self):
        if postcard_id := self.params.get('postcard_id'):
            return get_object_or_404(self.postcards, id=postcard_id)
        elif postcard := self.postcards.first():
            return postcard
        else:
            raise Http404

    def get_context_data(self):
        context = super().get_context_data()
        index = [p.pk for p in self.postcards].index(self.postcard.id)
        context['postcard'] = self.postcard
        context['previous_postcard'] = [None, *self.postcards, None][index]
        context['next_postcard'] = [None, *self.postcards, None][index + 2]
        return context

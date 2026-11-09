from functools import cached_property

from simple_page import renderers
from django.shortcuts import get_object_or_404
from miaiqi_cards.website.models import MiaiqiCardsPage
from . import models


@renderers.register(models.GallerySection, page_type=MiaiqiCardsPage)
class GalleryRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['css/gallery.css'])


@renderers.register(models.SetsSection, page_type=MiaiqiCardsPage)
class SetGalleryRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['css/sets.css'])


class PageMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page.title = self.main_section.title
        self.page.description = self.page.homepage.description

    def get_template_name(self):
        return 'pages/miaiqi_cards_page.html'

    def get_main_sections(self):
        return [self.main_section]

    def get_footer_sections(self):
        return self.page.homepage.footer


@renderers.register(models.GalleryPage)
class GalleryPageRenderer(PageMixin, renderers.PageRenderer):
    class Media:
        css = dict(all=['css/sections.css', 'css/footer.css'])

    @cached_property
    def main_section(self):
        slug = self.params.get('gallery_slug')
        return get_object_or_404(models.GallerySection.objects.all(), slug=slug)


@renderers.register(models.PostcardPage)
class PostcardPageRenderer(PageMixin, renderers.PageRenderer):
    class Media:
        css = dict(all=['css/footer.css'])

    @cached_property
    def main_section(self):
        postcard_id = self.params.get('postcard_id')
        return get_object_or_404(models.Postcard.objects.all(), id=postcard_id)


@renderers.register(models.Postcard, page_type=models.PostcardPage)
class PostcardRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['css/postcard.css'])

    def get_template_name(self):
        return 'sections/postcard_section.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['url_params'] = self.params
        return context


@renderers.register(models.GallerySection, page_type=models.GalleryPage)
class PostcardSetsRenderer(renderers.SectionRenderer):
    class Media:
        css = dict(all=['css/gallery.css'])

    def get_context_data(self):
        context = super().get_context_data()
        context['url_params'] = self.params
        return context

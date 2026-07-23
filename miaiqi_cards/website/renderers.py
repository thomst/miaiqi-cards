import random
from django import forms
from django.utils.text import slugify
from django.contrib.staticfiles.finders import find
from simple_page import renderers
from simple_page.models import Section
from . import models


@renderers.register(models.MiaiqiCardsPage)
class MiaiqiCardsPageRenderer(renderers.PageRenderer):
    class Media:
        css = dict(all=['miaiqi_cards/miaiqi_cards.css'])

    def get_welcome_postcard(self, context):
        for section_data in context['main']['sections']:
            if isinstance(section_data['obj'], models.WelcomeSection):
                return section_data['renderer'].postcard

    def get_context(self):
        context = super().get_context()
        context['welcome_postcard'] = self.get_welcome_postcard(context)
        return context


@renderers.register(models.WelcomeSection)
class WelcomeRenderer(renderers.SectionRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.postcard = random.choice(self.obj.postcards.all())

    def get_css_file(self):
        # Is there an extra css file for that postcard?
        path = f'miaiqi_cards/welcome/{slugify(self.postcard.title)}.css'
        if find(path):
            return path

    @property
    def media(self):
        css = dict(all=['miaiqi_cards/welcome.css'])
        if css_file := self.get_css_file():
            css['all'].append(css_file)
        return forms.Media(css=css)

    def get_context(self):
        context = super().get_context()
        get_child = lambda pk: Section.objects.get_subclass(pk=pk)
        context['title_ref'] = get_child(self.obj.title_ref.pk)
        context['subtitle_ref'] = get_child(self.obj.subtitle_ref.pk)
        context['postcard_ref'] = get_child(self.obj.postcard_ref.pk)
        context['postcard'] = self.postcard
        return context

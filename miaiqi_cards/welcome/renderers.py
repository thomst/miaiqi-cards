import random
from simple_page import renderers
from simple_page.models import Section
from django.shortcuts import get_object_or_404
from . import models


@renderers.register(models.WelcomeSection)
class WelcomeRenderer(renderers.SectionRenderer):

    class Media:
        css = dict(all=['miaiqi_cards/welcome.css'])

    def get_theme(self):
        if 'theme' in self.request.GET:
            return get_object_or_404(
                self.section.themes.all(),
                id=self.request.GET['theme']
                )
        else:
            random.seed(hash(self.request))
            return random.choice(self.section.themes.all())

    def get_template_name(self):
        template_name = super().get_template_name()
        if self.region == 'head':
            return f'{template_name}#head'
        else:
            return template_name

    def get_context(self):
        context = super().get_context()
        get_subclass = lambda pk: Section.objects.get_subclass(pk=pk)
        context['title_ref'] = get_subclass(self.section.title_ref.pk)
        context['subtitle_ref'] = get_subclass(self.section.subtitle_ref.pk)
        context['postcard_ref'] = get_subclass(self.section.postcard_ref.pk)
        context['theme'] = self.get_theme()
        return context

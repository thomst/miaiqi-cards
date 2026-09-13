from simple_page import renderers
from simple_page.models import Section
from django.shortcuts import get_object_or_404
from . import models


@renderers.register(models.WelcomeSection)
class WelcomeRenderer(renderers.SectionRenderer):

    class Media:
        css = dict(all=['miaiqi_cards/welcome.css'])

    def update_theme_id(self, theme):
        theme_ids = list(self.section.themes.values_list('id', flat=True))
        index = theme_ids.index(theme.id)
        next_index = (index + 1) % len(theme_ids)
        self.request.session['theme'] = theme_ids[next_index]

    def get_theme(self):
        if 'theme' in self.request.GET:
            theme = get_object_or_404(
                self.section.themes.all(),
                id=self.request.GET['theme']
                )
        elif 'theme' in self.request.session:
            theme = get_object_or_404(
                self.section.themes.all(),
                id=self.request.session['theme']
                )
        else:
            theme = self.section.themes.first()

        # Update the theme id in sessions once per request by skipping the head
        # region, which is rendered first.
        if not self.region == 'head':
            self.update_theme_id(theme)

        return theme

    def get_template_name(self):
        template_name = super().get_template_name()
        if self.region == 'head':
            return f'{template_name}#head'
        else:
            return template_name

    def get_context_data(self, **context):
        context = super().get_context_data(**context)
        get_subclass = lambda pk: Section.objects.get_subclass(pk=pk)
        context['title_ref'] = get_subclass(self.section.title_ref.pk)
        context['subtitle_ref'] = get_subclass(self.section.subtitle_ref.pk)
        context['postcard_ref'] = get_subclass(self.section.postcard_ref.pk)
        context['theme'] = self.get_theme()
        return context

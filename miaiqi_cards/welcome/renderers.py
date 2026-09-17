from simple_page import renderers
from simple_page.models import Section
from django.shortcuts import get_object_or_404
from . import models


def save_theme_to_session(get_theme):
    def wrapper(self):
        theme = get_theme(self)
        theme_ids = list(self.section.themes.values_list('id', flat=True))
        index = theme_ids.index(theme.id)
        next_index = (index + 1) % len(theme_ids)
        self.request.session['theme'] = theme_ids[next_index]
        return theme
    return wrapper


@renderers.register(models.WelcomeSection)
class WelcomeRenderer(renderers.SectionRenderer):

    class Media:
        css = dict(all=['miaiqi_cards/welcome.css'])

    @save_theme_to_session
    def get_theme(self):
        if 'theme' in self.request.GET:
            return get_object_or_404(
                self.section.themes.all(),
                id=self.request.GET['theme']
                )
        elif 'theme' in self.request.session:
            return get_object_or_404(
                self.section.themes.all(),
                id=self.request.session['theme']
                )
        else:
            return self.section.themes.first()

    def get_context_data(self):
        get_subclass = lambda s: Section.objects.get_subclass(pk=s.pk)
        context = super().get_context_data()
        context['theme'] = self.get_theme()
        context['title_ref'] = get_subclass(self.section.title_ref)
        context['subtitle_ref'] = get_subclass(self.section.subtitle_ref)
        context['postcard_ref'] = get_subclass(self.section.postcard_ref)
        return context

from django.apps import AppConfig


class WelcomeConfig(AppConfig):
    name = 'miaiqi_cards.welcome'

    def ready(self):
        import miaiqi_cards.welcome.renderers

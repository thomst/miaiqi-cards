from django.apps import AppConfig


class PostcardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'miaiqi_cards.postcards'

    def ready(self):
        import miaiqi_cards.postcards.renderers

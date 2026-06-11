from django.apps import AppConfig


class MiaiqiCardsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'miaiqi_cards_app'

    def ready(self):
        import miaiqi_cards_app.renderers

from django.apps import AppConfig


class ContactConfig(AppConfig):
    name = 'miaiqi_cards.contact'

    def ready(self):
        import miaiqi_cards.contact.renderers

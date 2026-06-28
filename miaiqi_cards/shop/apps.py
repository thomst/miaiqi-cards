from django.apps import AppConfig


class ShopConfig(AppConfig):
    name = 'miaiqi_cards.shop'

    def ready(self):
        import miaiqi_cards.shop.renderers

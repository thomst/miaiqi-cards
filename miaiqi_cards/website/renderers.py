from simple_page import renderers
from . import models


@renderers.register(models.MiaiqiCardsPage)
class MiaiqiCardsPageRenderer(renderers.PageRenderer):
    class Media:
        css = dict(all=['miaiqi_cards/miaiqi_cards.css'])

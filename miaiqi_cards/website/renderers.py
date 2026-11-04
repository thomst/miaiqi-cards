from simple_page import renderers
from . import models


@renderers.register(models.MiaiqiCardsPage)
class MiaiqiCardsPageRenderer(renderers.PageRenderer):
    class Media:
        css = dict(all=[
            'css/miaiqi_cards.css',
            'css/footer.css',
            ])

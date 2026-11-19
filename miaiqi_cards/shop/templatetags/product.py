from django import template
from cart.cart import CART_ID
from cart.models import Item
from miaiqi_cards.shop.models import Product

register = template.Library()


def get_quantity(request, product):
    """Return the quantity of the product in the open cart of the session."""
    session = getattr(request, 'session', None)
    cart_id = session.get(CART_ID) if session is not None else None
    if cart_id is None:
        return 0
    item = Item.objects.filter(
        cart_id=cart_id,
        cart__checked_out=False,
        product=product,
    ).first()
    return item.quantity if item else 0


@register.inclusion_tag('widgets/product_widget.html', takes_context=True)
def product_widget(context, content):
    """Render a small quantity widget for a postcard or postcard set.

    Nothing is rendered unless a shop is assigned to the gallery or sets section.
    """
    shop = context['page'].shop_section
    if not shop:
        return dict(product=None)
    try:
        product = Product.objects.get_from_content(content)
    except Product.DoesNotExist:
        return dict(product=None)
    quantity = get_quantity(context.get('request'), product)
    return dict(product=product, shop=shop, quantity=quantity)

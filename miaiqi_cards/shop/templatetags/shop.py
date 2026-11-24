from django import template
from django.utils.safestring import mark_safe
from cart.cart import CART_ID
from cart.models import Item
from miaiqi_cards.shop.models import Product

register = template.Library()


def get_item(request, product):
    """Return the item of the product in the open cart of the session (or None)."""
    session = getattr(request, 'session', None)
    cart_id = session.get(CART_ID) if session is not None else None
    if cart_id is None:
        return None
    return Item.objects.filter(
        cart_id=cart_id,
        cart__checked_out=False,
        product=product,
    ).first()


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
    item = get_item(context.get('request'), product)
    quantity = item.quantity if item else 0
    total_price = item.total_price if item else None
    return dict(product=product, shop=shop, quantity=quantity, total_price=total_price)


@register.simple_tag(takes_context=True)
def legal_form_label(context, field):
    """
    Render the label for a legal form field with a link to the corresponding
    document.
    """
    shop = context['shop']
    label = field.label_tag()
    link = '<a href="{}" target="_blank"><i>{}</i></a>'
    if field.name == 'ts_and_cs_confirmation':
        needle = 'AGBs'
        link = link.format(shop.terms_and_conditions.url, needle)
    elif field.name == 'cancellation_confirmation':
        needle = 'Widerrufsbelehrung'
        link = link.format(shop.cancellation_policy.url, needle)
    return mark_safe(label.replace(needle, link))

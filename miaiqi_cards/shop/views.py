from django.shortcuts import render
from django.shortcuts import get_object_or_404
from cart.cart import Cart, InvalidDiscountError
from miaiqi_cards.website.models import Shop
from .models import QuantityDiscount as QD
from .forms import EmailForm, CartItemFormset


def formset(request):
    cart = Cart(request)
    if cart.is_empty():
        formset = CartItemFormset(request.POST)
    else:
        initial = [dict(procuct=i.product, quantity=i.quantity) for i in cart]
        formset = CartItemFormset(initial=initial)
    return render(request, 'shop/formset.html', dict(formset=formset))


def checkout(request):
    price = get_object_or_404(Shop, pk=request.POST.get('shop_id')).price
    formset = CartItemFormset(request.POST)
    cart = Cart(request)

    # FIXME: Check if formset is not empty.
    if formset.is_valid():
        cart.clear()
        cart.add_bulk([dict(**d, unit_price=price) for d in formset.cleaned_data])

        # Apply quantity discount.
        for discount in QD.objects.all():
            try:
                cart.apply_discount(discount.code)
            except InvalidDiscountError:
                pass
            else:
                break

        return render(request, 'shop/cart.html', dict(cart=cart))

    else:
        return render(request, 'shop/formset.html', dict(formset=formset))


def buy(request):
    email_form = EmailForm(request.POST)
    cart = Cart(request)
    if email_form.is_valid():
        # TODO: Send confirmation email.
        cart.checkout()
        render(request, 'shop/confirmation.html', dict(email_address=email_form.email_address))

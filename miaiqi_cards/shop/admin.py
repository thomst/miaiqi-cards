from django.contrib import admin
from reorder_items_widget import ReorderItemsInline
from . import models
from .models import QuantityDiscount


@admin.register(models.QuantityDiscount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("code", "value", "min_cart_value")
    readonly_fields = ("current_uses",)
    fields = ["value", "min_cart_value"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(code__startswith=QuantityDiscount.CODE_PREFIX)


class PriceInline(admin.TabularInline):
    model = models.Price
    extra = 1
    fields = ['size', 'price']


@admin.register(models.ShopSection)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    inlines = [PriceInline]


from django.contrib import admin
from reorder_items_widget import ReorderItemsInline
from . import models


class PriceInline(admin.TabularInline):
    model = models.Price
    extra = 1
    fields = ['size', 'price']


@admin.register(models.ShopSection)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    inlines = [PriceInline]

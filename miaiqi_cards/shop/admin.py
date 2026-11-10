from django.contrib import admin
from . import models


@admin.register(models.ShopSection)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

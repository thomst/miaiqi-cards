from django.contrib import admin
from . import models


@admin.register(models.WelcomeSection)
class WelcomeSection(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(models.TextSection)
class TextSectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(models.GallerySection)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(models.ShopSection)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(models.FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ['name']

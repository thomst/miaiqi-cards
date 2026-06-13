from django.contrib import admin
from reorder_items_widget import ReorderItemsInline
from . import models


@admin.register(models.WelcomeSection)
class WelcomeSection(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(models.TextSection)
class TextSectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(models.FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ['title_view']

    def title_view(self, obj):
        return f"[{obj.pk}] obj.body."
    title_view.short_description = 'Footer Section'


class PostcardsInline(ReorderItemsInline):
    model = models.GalleryPostcard
    extra = 1
    fields = ['postcard']


@admin.register(models.Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    exclude = ['postcards']
    inlines = [PostcardsInline]

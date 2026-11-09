from reorder_items_widget import ReorderItemsInline
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from . import models


@admin.register(models.Postcard)
class PostcardAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_public', 'view_link']
    search_fields = ['title']

    def view_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Show</a>', url)
    view_link.short_description = 'Show'


class PostcardSetPostcardInline(ReorderItemsInline):
    model = models.PostcardSetPostcard
    extra = 1
    fields = ['postcard', 'index']
    fk_name = 'postcard_set'


@admin.register(models.PostcardSet)
class PostcardSetAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    prepopulated_fields = {"slug": ("title",)}
    exclude = ['postcards']
    inlines = [PostcardSetPostcardInline]


@admin.register(models.GallerySection)
class GallerySectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.SetsSection)
class SetsSectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    prepopulated_fields = {"slug": ("title",)}

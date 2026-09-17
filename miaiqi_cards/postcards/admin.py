from reorder_items_widget import ReorderItemsInline
from simple_page.admin import BasePageAdmin
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from . import models


@admin.register(models.PostcardPage)
class PostcardPageAdmin(BasePageAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title', 'slug']


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'original', 'large', 'medium', 'small']
    exclude = ['large', 'medium', 'small']


@admin.register(models.Postcard)
class PostcardAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_public', 'view_link']
    search_fields = ['title']

    def view_link(self, obj):
        url = reverse('postcard', kwargs=dict(postcard_id=obj.pk))
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Show</a>', url)
    view_link.short_description = 'Show'


class PostcardsInline(ReorderItemsInline):
    model = models.GalleryPostcard
    extra = 1
    fields = ['postcard']


@admin.register(models.GallerySection)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    exclude = ['postcards']
    inlines = [PostcardsInline]

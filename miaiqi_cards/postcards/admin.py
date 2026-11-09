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
        gallery = models.GallerySection.objects.first()
        kwargs = dict(gallery_slug=gallery.slug, postcard_id=obj.pk)
        url = reverse('postcard', kwargs=kwargs)
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
    prepopulated_fields = {"slug": ("title",)}
    exclude = ['postcards']
    inlines = [PostcardsInline]


class SetsGalleryInline(ReorderItemsInline):
    model = models.SetsGallery
    extra = 1
    fields = ['gallery']


@admin.register(models.SetsSection)
class SetsAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    prepopulated_fields = {"slug": ("title",)}
    exclude = ['galleries']
    inlines = [SetsGalleryInline]


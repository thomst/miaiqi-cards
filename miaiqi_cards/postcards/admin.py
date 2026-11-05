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
        page = models.PostcardPage.objects.first()
        url = reverse('postcard', kwargs=dict(slug=page.slug, postcard_id=obj.pk))
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


class PostcardSetsInline(ReorderItemsInline):
    model = models.GalleryPostcardSet
    extra = 1
    fields = ['postcard_set']


@admin.register(models.SetGallerySection)
class SetGalleryAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    exclude = ['postcard_sets']
    inlines = [PostcardSetsInline]


from django.contrib import admin
from django.db import models
from django.urls import reverse
from markdownx.admin import MarkdownxModelAdmin
from django.utils.html import format_html
from reorder_items_widget import ReorderItemsInline
from simple_page.admin import BasePageAdmin
from .models import Postcard, MiaiqiCardsPage, TextSection, FooterSection, Gallery, GalleryPostcard


@admin.register(TextSection)
class TextSectionAdmin(MarkdownxModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(FooterSection)
class FooterSectionAdmin(MarkdownxModelAdmin):
    list_display = ['title_view']

    def title_view(self, obj):
        return f"[{obj.pk}] obj.body."
    title_view.short_description = 'Footer Section'


class PostcardsInline(ReorderItemsInline):
    model = GalleryPostcard
    extra = 1
    fields = ['postcard']


@admin.register(Gallery)
class GalleryAdmin(MarkdownxModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    exclude = ['postcards']
    inlines = [PostcardsInline]


@admin.register(Postcard)
class PostcardAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'created_at', 'is_public', 'view_link']
    search_fields = ['title']

    def view_link(self, obj):
        gallery = obj.galleries.first()
        url = reverse('postcard', kwargs=dict(gallery_id=gallery.id, postcard_id=obj.id))
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Open</a>', url)
    view_link.short_description = 'Open in new tab'


@admin.register(MiaiqiCardsPage)
class MiaiqiCardsPageAdmin(BasePageAdmin):
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}

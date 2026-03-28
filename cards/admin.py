from django.contrib import admin
from .models import Postcard

# Register your models here.

from django.utils.html import format_html

@admin.register(Postcard)
class PostcardAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_public', 'view_link']
    search_fields = ['title']

    def view_link(self, obj):
        if not obj.pk:
            return '-'
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Open</a>', obj.get_absolute_url())
    view_link.short_description = 'Open in new tab'
